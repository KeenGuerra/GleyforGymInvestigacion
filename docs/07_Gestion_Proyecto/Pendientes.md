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

Falta:

1. Completar un pago de prueba real (QR de Yape sandbox o PagoEfectivo) y confirmar el webhook/estado "pagado".
2. Reemplazar `gateway = MockGateway()` por `gateway = CulqiGateway()` en `pagos_gateway/__init__.py:7` una vez confirmado el punto 1.
3. Adaptar `routes/webhooks.py`: hoy asume el formato propio de `MockGateway` (`id_transaccion_externa` + `resultado`) y confía en ese campo sin verificarlo contra el proveedor. El webhook real de Culqi llega con su propio formato de evento — hay que leerlo y, por seguridad, revalidar el estado llamando a `gateway.consultar_estado()` en vez de confiar directamente en el payload entrante (si no, cualquiera podría llamar a esa URL y falsificar un pago).

Decisión ya tomada: **Culqi** es la opción recomendada para Perú (soporte Yape, sandbox gratuito, onboarding simple) frente a Niubiz/Izipay (más burocrático), MercadoPago (menos adopción de Yape) o Stripe (no opera en Perú/soles).

---

## P-03 Envío real de correo (SMTP)

~~Resuelto (2026-11)~~: nuevo `backend/app/correo.py` con `enviar_correo()`, usando Gmail SMTP (`smtplib`, puerto 465 SSL) con las credenciales opcionales `GMAIL_USER`/`GMAIL_APP_PASSWORD` (sin ellas, sigue solo logueando, como antes). Probado con un envío real: el correo llegó correctamente a la bandeja de entrada. Conectado en `solicitar_reset_password` (recuperación de contraseña) y reutilizado por `enviar_verificacion_correo()` (P-01). Pruebas en `backend/tests/test_correo.py` (3 pruebas, con la llamada SMTP simulada).

---

## P-04 Cobertura de tests del módulo de Comercio

~~Resuelto (2026-11)~~: backend y frontend tienen ahora pruebas dedicadas. Backend: `backend/tests/test_comercio.py` (10 pruebas) eleva `categorias.py` 37%→88%, `proveedores.py` 43%→86%, `compras.py` 20%→83%, `ventas.py` 17%→69%, `inventario.py` 26%→56%, `productos.py` 23%→48%. Frontend: un archivo `*.test.jsx` por página (`Categorias`, `Productos`, `Proveedores`, `Compras`, `Inventario`, `Ventas`, `Tienda`) eleva esos siete archivos de un rango de 1.3%-2.8% a 87.9%-100%, y la cobertura total de frontend de 78.21% a 94.33%.

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
