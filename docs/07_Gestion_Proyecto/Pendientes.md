# Pendientes del Proyecto

# SistemaGimnasioGleyforGym

## Introducción

Este documento lista todo lo que falta para considerar completo el sistema web (backend FastAPI + frontend web-admin). No incluye la aplicación móvil (Flutter), que se gestiona aparte.

Se generó tras completar tres rondas de revisión y corrección sobre el código (RBAC, motor de IA real, auditoría, autogestión de contraseñas, Avisos editables, KPIs de asistencia, paginación), verificando directamente contra el código actual — no contra supuestos ni documentación antigua.

Cada punto cita el archivo (y línea, cuando aplica) donde se verificó.

---

# Prioridad Alta

## P-01 Verificación de correo al registrarse

~~Resuelto (2026-11)~~: `Usuario` ahora tiene `correo_verificado`, `token_verificacion` y `token_verificacion_expira`. Al crear cualquier usuario (`POST /clientes/`, `POST /usuarios/`, `POST /entrenadores/`) se genera un token y se envía un correo de confirmación (`enviar_verificacion_correo()` en `app/correo.py`). Nueva página pública `web-admin/src/pages/VerificarCorreo.jsx` (ruta `/verificar-correo?token=...`) que confirma el correo automáticamente al abrirse. **Decisión de alcance**: no se bloquea el login de cuentas no verificadas — el campo solo registra el estado, para no romper el flujo actual (las cuentas de clientes/entrenadores las crea el staff del gimnasio, no es un auto-registro público).

---

## P-02 Conectar una pasarela de pago real

La arquitectura ya está lista:

```text
backend/app/pagos_gateway/base.py     → interfaz GatewayPago (ABC)
backend/app/pagos_gateway/mock.py     → MockGateway (simulación en memoria)
backend/app/pagos_gateway/culqi.py    → CulqiGateway (esqueleto, ver abajo)
backend/app/pagos_gateway/__init__.py → singleton `gateway`, punto único de cambio
```

**Avance (2026-11)**: se creó una cuenta real de Culqi (RUC de pruebas, panel DEVS) y se probó `CulqiGateway` contra el sandbox real, no solo simulado. Esto reveló dos diferencias con el esqueleto original:

1. La API de Órdenes exige además `client_details` (nombres, apellidos, correo, teléfono) y `expiration_date` — ya corregido en `culqi.py`. Por eso `GatewayPago.crear_checkout()` ahora recibe un tercer parámetro `cliente: dict`, y `pagos.py`/`ventas.py` arman ese dict desde `Cliente`/`Usuario` antes de llamar al gateway (sí fue necesario tocar las rutas, a diferencia de lo asumido originalmente).
2. La orden creada **no tiene un `checkout_url` genérico**: el cliente paga con el link de PagoEfectivo (`url_pe`) o escaneando el QR de Yape (`qr`) — ambos ya mapeados en el resultado de `crear_checkout()` (`url_checkout` + `qr_yape`).

`backend/tests/test_culqi_gateway.py` (12 pruebas) actualizado para reflejar el formato real. Aún con la llamada HTTP simulada en las pruebas, pero verificado manualmente contra `api.culqi.com` con las llaves de prueba.

**Sin confirmar todavía**: completar un pago real de prueba de punta a punta (pagar la orden y ver si `consultar_estado()`/el webhook realmente reportan "paid"/"completed" como se asume) — solo se probó crear y consultar una orden en estado "pending".

**Avance (2026-11, continuación)**: se construyó la pantalla de checkout en el frontend. `web-admin/src/components/CheckoutModal.jsx` (nuevo) muestra el link de pago (`url_checkout`) y el QR de Yape (`qr_yape`) devueltos por el backend. Conectado en:
- `Pagos.jsx`: botón "Cobrar" en cada pago con estado `PENDIENTE`, llama a `POST /pagos/{id}/checkout`.
- `Tienda.jsx` (pestaña "Mis pedidos"): botón "Pagar ahora" en cada pedido `PENDIENTE`, llama a `POST /ventas/{id}/checkout`.

Pruebas agregadas en `Pagos.test.jsx` y `Tienda.test.jsx` para ambos flujos (éxito y error). Suite de frontend: 42 archivos / 220 pruebas.

**Avance (2026-11, continuación 2) — los puntos 2 y 3 de abajo ya están resueltos**: `pagos_gateway/__init__.py` elige automáticamente `CulqiGateway` si `CULQI_SECRET_KEY` está configurada, o `MockGateway` si no (CI y cualquier máquina sin esa variable siguen sin cambios). `routes/webhooks.py` ya no confía en el campo `resultado` del payload cuando el gateway activo es real: solo lo usa para extraer el ID de la transacción (probando varias formas razonables — `id_transaccion_externa`, `data.object.id`, `data.id`, `object.id`, `id`, ya que Culqi no documenta públicamente el formato exacto de su webhook) y siempre revalida el estado llamando a `gateway.consultar_estado()` contra la API de Culqi antes de aplicar cualquier cambio. El secreto del webhook (`WEBHOOK_SECRET`) se acepta también por query string (`?secret=...`), porque el panel de Culqi no permite configurar headers personalizados en la URL de destino.

En autorrevisión antes de la primera prueba real se corrigieron dos bugs: `CulqiGateway.consultar_estado()` no manejaba un 404 de Culqi (orden no encontrada) y `_extraer_id_transaccion()` priorizaba el `id` de primer nivel del payload antes que las rutas anidadas, al revés de la convención común de webhooks (estilo Stripe) donde el nivel superior suele ser el ID del *evento*, no del recurso.

**Avance (2026-11, continuación 3) — bugs reales encontrados en la primera prueba real (no simulada)**: al intentar pagar de verdad desde "Mi Membresía" se encontraron y corrigieron tres problemas que solo aparecen contra la API real de Culqi (nunca los hubiera detectado el webhook simulado):
1. Culqi rechaza la orden con 400 si el teléfono del cliente llega vacío o mal formado — ahora `iniciar_checkout_pago`/`iniciar_checkout_venta` exigen un teléfono de exactamente 9 dígitos (Perú) antes de llamar a Culqi, con un mensaje claro en vez de un 500 genérico.
2. Culqi exige que `order_number` sea único **para siempre en toda la cuenta** (no solo en nuestra BD) — reintentar "Completar pago" sobre el mismo Pago/Venta volvía a llamar a `crear_checkout()` con la misma referencia y Culqi la rechazaba. Se agregó `GatewayPago.obtener_checkout()` para recuperar la orden ya creada en vez de crear una nueva (checkout idempotente).
3. La referencia (`pago-<id>`/`venta-<id>`) se arma solo con el ID autoincremental de nuestra BD, que no es único entre entornos/pruebas distintas contra la misma cuenta de Culqi — chocó con una orden de pruebas anteriores. Se agregó un sufijo aleatorio a la referencia.

Falta:

1. Completar un pago de prueba real de punta a punta (QR de Yape sandbox, número de prueba `900 000 001` + cualquier código de 6 dígitos, o PagoEfectivo) contra el backend desplegado, y confirmar que el webhook real de Culqi llega con un formato que `_extraer_id_transaccion()` reconoce. **Sigue siendo lo único sin confirmar** — ya se corrigieron los bugs que impedían siquiera llegar a generar la orden de pago (ver arriba), pero aún no se completó un pago hasta el final (escanear el QR/pagar y que el webhook confirme).

Decisión ya tomada: **Culqi** es la opción recomendada para Perú (soporte Yape, sandbox gratuito, onboarding simple) frente a Niubiz/Izipay (más burocrático), MercadoPago (menos adopción de Yape) o Stripe (no opera en Perú/soles).

---

## P-03 Envío real de correo

~~Resuelto (2026-11)~~: `backend/app/correo.py` con `enviar_correo()` probado primero con Gmail SMTP (`smtplib`), que funcionó enviando un correo real desde una máquina local. Al desplegar a producción (Render) se confirmó que las conexiones SMTP salientes a `smtp.gmail.com` no se completan (timeout, probado en los puertos 465 y 587) — limitación del hosting, no de las credenciales. Se reemplazó por la API HTTPS de Brevo (`BREVO_API_KEY`/`BREVO_SENDER_EMAIL`/`BREVO_SENDER_NAME`, opcionales — sin ellas sigue solo logueando, como antes), que sí funciona porque usa el puerto 443 (nunca bloqueado). El correo remitente debe verificarse una vez en el panel de Brevo (Senders) antes de poder usarse. Conectado en `solicitar_reset_password` (recuperación de contraseña) y reutilizado por `enviar_verificacion_correo()` (P-01). El envío ya no propaga errores (se loguea y sigue, igual que `registrar_auditoria()`) para no colgar ni tumbar la operación principal si el correo falla. Pruebas en `backend/tests/test_correo.py` (4 pruebas, con la llamada HTTP simulada).

---

## P-04 Cobertura de tests del módulo de Comercio

~~Resuelto (2026-11)~~: backend y frontend tienen ahora pruebas dedicadas. Backend: `backend/tests/test_comercio.py` (10 pruebas) eleva `categorias.py` 37%→88%, `proveedores.py` 43%→86%, `compras.py` 20%→83%, `ventas.py` 17%→69%, `inventario.py` 26%→56%, `productos.py` 23%→48%. Frontend: un archivo `*.test.jsx` por página (`Categorias`, `Productos`, `Proveedores`, `Compras`, `Inventario`, `Ventas`, `Tienda`) eleva esos siete archivos de un rango de 1.3%-2.8% a 87.9%-100%, y la cobertura total de frontend de 78.21% a 94.33%.

---

## P-19 Compra de membresía por autoservicio

~~Resuelto (2026-11)~~: antes solo ADMIN/ENTRENADOR podían asignar una membresía (`POST /cliente-membresias/`). Se agregó `POST /cliente-membresias/comprar` para que el propio socio compre un plan, siguiendo el mismo patrón solicitar → pagar → confirmar por webhook que ya usan las ventas de la tienda (ver P-02). Al comprar se crean una `ClienteMembresia` y un `Pago` en estado `PENDIENTE`; el webhook activa la membresía (con fechas reales, `fecha_inicio`/`fecha_fin` recalculadas al confirmarse) cuando el pago queda `PAGADO`, o la deja `CANCELADA` si queda `FALLIDO` (para poder reintentar). Se bloquea con 409 comprar un nuevo plan mientras ya hay uno `ACTIVA`/`PAUSADA`/`PENDIENTE`.

En el frontend, `MiMembresia.jsx` ahora muestra los planes disponibles con botón "Comprar" cuando el socio no tiene membresía, y "Completar pago" (reutilizando `CheckoutModal.jsx` ya existente) cuando hay un pago pendiente. Backend: 142→149 pruebas (7 nuevas en `test_compra_membresia.py`). Frontend: 48→50 archivos / 277→288 pruebas.

Sigue pendiente de la misma confirmación que P-02: un pago real de punta a punta todavía no se ha completado para este flujo.

---

## P-20 Bug: error de login silencioso (la sesión se cerraba ante cualquier 401)

~~Resuelto (2026-11)~~: el interceptor de respuesta de axios (`web-admin/src/api/api.js`) trataba cualquier 401 como "la sesión expiró" y hacía `localStorage.clear()` + `location.href = "/login"` (recarga completa de la página) — incluido el 401 que devuelve `POST /usuarios/login` cuando la contraseña es incorrecta. Eso borraba el mensaje de error que `Login.jsx` sí llegaba a poner (`setError("Correo o contraseña incorrectos")`) antes de que se viera, porque toda la página se remontaba. Por eso el síntoma reportado era "no dice nada, solo recarga".

Ahora el interceptor solo cierra sesión si **ya había** un token guardado antes de la petición; un 401 de un endpoint público (login, etc.) ya no dispara nada y cada pantalla muestra su propio error, como estaba pensado. Se revisaron además `Registro.jsx` y `ResetPassword.jsx` (no tenían este bug, ya validan y muestran errores correctamente) y se encontró el mismo patrón de fondo (catch que solo hacía `console.error`, sin avisar al usuario) en los tres dashboards (`DashboardAdmin.jsx`, `DashboardCliente.jsx`, `DashboardEntrenador.jsx`) — corregido en la misma pasada (ver P-21).

---

## P-21 Bootstrap para alertas/toasts

~~Resuelto (2026-11)~~: se agregó Bootstrap (`bootstrap` + `sass` como dependencias) a pedido, pero **solo** los componentes de alerta/toast, importados vía Sass en `web-admin/src/styles/bootstrap-custom.scss` — deliberadamente sin `reboot` (resetea tipografía/body global) ni `grid`/`buttons`/`card`/`badge`. La app ya tiene su propio tema (`index.css`, ~2185 líneas) con clases como `.btn-primary`/`.card`/`.badge`, los mismos nombres que usa Bootstrap por defecto; importarlo completo habría roto esa UI existente. Nuevo hook `useToast.js` + componente `ToastFeedback.jsx` (auto-cierre manejado por `setTimeout` en React, sin depender del runtime JS de Bootstrap), usados en los tres dashboards para avisar cuando falla la carga inicial (ver P-20).

---

## P-22 Checklist para pasar a la cuenta real de Culqi (producción)

El gimnasio pagará en persona con un POS físico aparte (no integrado a este sistema — hoy esas ventas se anotan a mano), pero quiere usar su **cuenta real de Culqi** para las compras desde la web (Tienda + Mi Membresía) en vez de la cuenta de pruebas (sandbox) usada hasta ahora. El código no distingue entre sandbox/real (usa la misma URL de Culqi, solo cambia según el prefijo de la llave), pero faltan pasos operativos antes de activarlo:

1. **Reemplazar las llaves en Render**: `CULQI_SECRET_KEY`/`CULQI_PUBLIC_KEY` en el dashboard del backend tienen hoy las llaves de sandbox (`sk_test_.../pk_test_...`) — cambiarlas por las llaves reales (`sk_live_.../pk_live_...`) de la cuenta del gimnasio.
2. **Volver a registrar el webhook en el ambiente de Producción de Culqi**: el webhook (Crear Webhook → Órdenes → status/changed → `.../webhooks/pagos?secret=...`) se configuró en la pestaña de Desarrollo — Culqi separa Desarrollo/Producción y no traslada la configuración sola. Si se olvida este paso, los pagos reales no activarían la membresía/venta automáticamente (quedarían como PENDIENTE para siempre).
3. **Cancelar los `Pago`/`Venta`/`ClienteMembresia` que quedaron PENDIENTE de las pruebas con sandbox** antes de lanzar — sus `id_transaccion_externa` son de órdenes `ord_test_...` que no existen para la cuenta real, así que mejor no dejarlos sueltos confundiendo al staff.
4. **Probar con un monto real pequeño** (ej. S/ 1) antes de anunciarlo a los socios, para confirmar que el webhook llega y activa correctamente con dinero de verdad — mismo patrón que se usó en sandbox (ver P-02), pero esta vez si se cobra.

No se resuelve nada de esto todavía — queda anotado para cuando el gimnasio tenga lista su cuenta real de Culqi (KYC/verificación de negocio aprobada por Culqi, que es un trámite del lado del gimnasio, no de este código).

---

# Prioridad Media

## P-05 Alertas de vencimiento de membresía

~~Resuelto (2026-11)~~: `DashboardAdmin.jsx` ahora muestra una tarjeta "Membresías por vencer" con las membresías `ACTIVA` cuya `fecha_fin` cae en los próximos 7 días, usando datos que `GET /cliente-membresias/` ya devolvía. Sin cambios de backend. La notificación por correo queda pendiente de P-03.

---

## P-06 Exportación/impresión PDF de rutinas y planes nutricionales

~~Resuelto (2026-11)~~: se agregaron `generar_pdf_rutina()` y `generar_pdf_plan_nutricional()` en `backend/app/recibos.py` (mismo patrón de `reportlab` que el recibo de pago), expuestas en `GET /rutinas/{id}/pdf` y `GET /nutricion/{id}/pdf` (mismo control de acceso ADMIN/ENTRENADOR o el cliente dueño). Botón "Descargar PDF" agregado en `DetalleRutina.jsx`, `MiRutina.jsx`, `Nutricion.jsx` y `MiNutricion.jsx`.

---

## P-07 Reportes operativos consolidados

~~Resuelto (2026-11)~~: nuevos `GET /reportes/ingresos` y `GET /reportes/asistencias` (por rango `desde`/`hasta`, agrupados por día). Nueva página `web-admin/src/pages/Reportes.jsx` (ruta `/reportes`, solo ADMIN) con selector de fechas, tablas por día y exportación a CSV reutilizando `exportarCsv.js`.

---

## P-08 Tests de `Navbar.jsx` y `NotFound.jsx`

~~Resuelto (2026-11)~~: se agregaron `Navbar.test.jsx` (7 pruebas) y `NotFound.test.jsx` (1 prueba). Ambos componentes quedan en 100% de cobertura.

---

## P-09 CI/CD

~~Resuelto (2026-11)~~: se agregó `.github/workflows/tests.yml` con dos jobs (`backend`: `pytest`; `frontend`: `npm run lint` + `npm run test`) que corren en cada push/PR a `main`. Verificado que la suite de backend pasa sin `backend/.env` presente, igual que correrá en CI.

---

## P-10 Rate limiting de login solo en memoria

`backend/app/rate_limit.py` limita los intentos de login (5 intentos / 15 min) pero el conteo vive en memoria del proceso — es correcto para el despliegue actual (un solo worker en Render), pero si el backend se escala a múltiples workers, cada uno llevaría su propio conteo independiente.

**Decisión (2026-11)**: no se resuelve ahora. Se retoma junto con la migración de todo el despliegue a un VPS de Hostinger (pendiente, ver P-16): ahí sí tendría sentido correr varios workers para aprovechar el servidor, y ese es el momento correcto para agregar Redis y resolver esto de una vez, en vez de hacerlo ahora sin necesidad real.

---

## P-11 Password de desarrollo local hardcodeada

~~Resuelto (2026-11)~~: `DEFAULT_DB_URL` en `create_db.py` ahora lee de la variable de entorno opcional `DEFAULT_DB_URL` (con un default genérico `postgres:postgres`, ya no la contraseña real que se reutilizaba). Producción sigue sin verse afectada (usa `DATABASE_URL` inyectada por Render).

---

## P-18 Sin página en web-admin para Entrenadores ni Auditoría

~~Resuelto (2026-11)~~: se agregaron `web-admin/src/pages/Entrenadores.jsx` (CRUD completo) y `Auditoria.jsx` (vista de solo lectura con filtro por entidad), con sus rutas `/entrenadores` y `/auditoria` (solo ADMIN) y los enlaces correspondientes en el sidebar, cada una con su archivo de pruebas.

---

# Prioridad Baja

## P-12 Migrar `class Config:` a `ConfigDict` (Pydantic v2)

~~Resuelto (2026-11)~~: las 26 clases `class Config: from_attributes = True` en `schemas.py` se migraron a `model_config = ConfigDict(from_attributes=True)`. Sin warnings de deprecación de Pydantic en la suite de tests.

---

## P-13 Dockerización

~~Resuelto (2026-11)~~: `backend/Dockerfile`, `web-admin/Dockerfile` (build multi-stage con nginx) y `docker-compose.yml` en la raíz (`db` + `backend` + `frontend`, con healthcheck de PostgreSQL). Probado de punta a punta con `docker compose up --build`: las tres migraciones/seeds de `create_db.py` corren solas, y un login real contra `POST /usuarios/login` devuelve 200 con el admin sembrado. No reemplaza el despliegue de `render.yaml`, es solo para desarrollo local reproducible.

---

## P-15 Backups automatizados propios

El respaldo de la base de datos depende enteramente del plan gestionado de PostgreSQL en Render. No hay un `pg_dump` automatizado ni almacenado fuera de Render.

**Decisión (2026-11)**: no se resuelve ahora — hoy el entorno de Render es de desarrollo (los datos no tienen valor real todavía), así que no se justifica construir una solución de backups para un entorno que se va a reemplazar. Se implementa como parte de la migración a Hostinger (ver P-16), definiendo ahí la estrategia real para el entorno de producción final (backup nativo de Hostinger o `pg_dump` programado dentro del VPS).

---

## P-16 Riesgos del plan gratuito de Render

El despliegue actual usa el plan **free** de Render (`render.yaml`): esto implica *cold starts* tras períodos de inactividad y que la base de datos free expira a los 90 días si no se actualiza a un plan pago. Es un riesgo operativo real mientras el proyecto siga en este tier, independiente del código de la aplicación.

**Incidente (2026-11)**: ya ocurrió una vez — la base de datos expiró y se recreó vía "Manual Sync" del Blueprint, sin pérdida relevante porque el entorno sigue siendo de desarrollo. Puede volver a pasar cada 90 días mientras no se resuelva.

**Decisión (2026-11)**: no se paga un plan superior en Render. En vez de eso, se migrará **todo el despliegue** (backend + base de datos) a un **VPS de Hostinger** de pago, reutilizando `docker-compose.yml` (P-13). Queda pendiente de que el usuario compre el plan VPS (y, idealmente, un dominio propio para poder habilitar HTTPS con Let's Encrypt). Esta migración queda para el final del backlog; P-10 y P-15 se resuelven junto con ella.

---

## P-17 Documentar formalmente el módulo de Comercio y Avisos

~~Resuelto (2026-09)~~: `Requerimientos_Funcionales.md` ya incluye RF-176 a RF-226 cubriendo Entrenadores, Avisos, Auditoría y los seis submódulos de Comercio (categorías, productos, proveedores, compras, inventario, ventas).

---

# Fuera de este documento

No se repiten aquí las brechas ya resueltas en las tres rondas de revisión anteriores: RBAC completo, motor de IA real (restricciones médicas + fórmula Mifflin-St Jeor), auditoría y trazabilidad, autogestión de contraseñas + reset por admin, Avisos editables desde el panel, KPI de asistencias en el dashboard, y paginación en los listados de mayor volumen.

---
