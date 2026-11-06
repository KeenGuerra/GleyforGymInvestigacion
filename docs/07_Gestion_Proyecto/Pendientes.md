# Pendientes del Proyecto

# SistemaGimnasioGleyforGym

## Introducción

Este documento lista todo lo que falta para considerar completo el sistema web (backend FastAPI + frontend web-admin). No incluye la aplicación móvil (Flutter), que se gestiona aparte.

Se generó tras completar tres rondas de revisión y corrección sobre el código (RBAC, motor de IA real, auditoría, autogestión de contraseñas, Avisos editables, KPIs de asistencia, paginación), verificando directamente contra el código actual — no contra supuestos ni documentación antigua.

Cada punto cita el archivo (y línea, cuando aplica) donde se verificó.

---

# Prioridad Alta

## P-01 Verificación de correo al registrarse

No existe campo `correo_verificado` ni flujo de confirmación. Un usuario puede registrarse con cualquier correo, válido o no, sin que el sistema lo confirme.

Bloqueado por: P-03 (envío real de correo), si se decide verificar por email.

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

TODO explícito en el código:

```text
backend/app/routes/usuarios.py:301
# TODO: reemplazar por un envío real (SMTP/SendGrid/Mailgun) cuando
# el proyecto tenga un proveedor de correo configurado.
```

Hoy el "envío" de recuperación de contraseña solo queda registrado en un log (`logger.info`), no llega ningún correo real. Falta:

1. Elegir proveedor (SendGrid, Mailgun, o SMTP directo de un dominio propio).
2. Implementar el envío real en el punto ya marcado.
3. Reutilizar esa misma infraestructura para P-01 si se decide verificar correo por email.

---

## P-04 Cobertura de tests del módulo de Comercio

~~Resuelto (2026-11)~~: backend y frontend tienen ahora pruebas dedicadas. Backend: `backend/tests/test_comercio.py` (10 pruebas) eleva `categorias.py` 37%→88%, `proveedores.py` 43%→86%, `compras.py` 20%→83%, `ventas.py` 17%→69%, `inventario.py` 26%→56%, `productos.py` 23%→48%. Frontend: un archivo `*.test.jsx` por página (`Categorias`, `Productos`, `Proveedores`, `Compras`, `Inventario`, `Ventas`, `Tienda`) eleva esos siete archivos de un rango de 1.3%-2.8% a 87.9%-100%, y la cobertura total de frontend de 78.21% a 94.33%.

---

# Prioridad Media

## P-05 Alertas de vencimiento de membresía

No se encontró ningún job ni notificación que avise antes de que una membresía expire. Lo único automático hoy es el cambio de estado a `TERMINADA` cuando la fecha ya pasó (tarea periódica en el `lifespan` de `main.py`). Faltaría una notificación (en la UI del admin, o por correo una vez resuelto P-03) unos días antes del vencimiento.

---

## P-06 Exportación/impresión PDF de rutinas y planes nutricionales

Solo existe generación de PDF para recibos de pago (`backend/app/recibos.py`, con `reportlab`). Rutinas y planes nutricionales no tienen equivalente. Se podría reutilizar el mismo patrón de `recibos.py`.

---

## P-07 Reportes operativos consolidados

Hoy solo hay exportación CSV de clientes (`web-admin/src/utils/exportarCsv.js`) y los KPIs del dashboard. No hay un reporte descargable que consolide, por ejemplo, ingresos por rango de fechas o asistencia por período.

---

## P-08 Tests de `Navbar.jsx` y `NotFound.jsx`

Confirmado en la auditoría de esta sesión: ninguno de los dos tiene archivo de test, a diferencia de `Layout.jsx` y `ProtectedRoute.jsx`, que sí lo tienen.

---

## P-09 CI/CD

No existe carpeta `.github/workflows`. Los tests (`pytest`, `npm run test`) y el lint solo corren cuando alguien los ejecuta manualmente, como en cada ronda de revisión de esta sesión. Un workflow simple que corra ambas suites en cada push/PR evitaría que una regresión llegue a `main` sin detectarse.

---

## P-10 Rate limiting de login solo en memoria

`backend/app/rate_limit.py` limita los intentos de login (5 intentos / 15 min) pero el conteo vive en memoria del proceso — es correcto para el despliegue actual (un solo worker en Render), pero si el backend se escala a múltiples workers, cada uno llevaría su propio conteo independiente. Ya está documentado como limitación aceptada en el propio código; solo requeriría acción (ej. Redis) si se decide escalar horizontalmente.

---

## P-11 Password de desarrollo local hardcodeada

```text
backend/create_db.py:12
DEFAULT_DB_URL = "postgresql://postgres:keen123@localhost:5432/postgres"
```

Es un valor por defecto solo para bootstrap local (producción usa `DATABASE_URL` inyectada por Render, ver `render.yaml`), pero conviene no reutilizar esa contraseña en ningún entorno real ni futuro proyecto.

---

## P-18 Sin página en web-admin para Entrenadores ni Auditoría

~~Resuelto (2026-11)~~: se agregaron `web-admin/src/pages/Entrenadores.jsx` (CRUD completo) y `Auditoria.jsx` (vista de solo lectura con filtro por entidad), con sus rutas `/entrenadores` y `/auditoria` (solo ADMIN) y los enlaces correspondientes en el sidebar, cada una con su archivo de pruebas.

---

# Prioridad Baja

## P-12 Migrar `class Config:` a `ConfigDict` (Pydantic v2)

Alrededor de 20 clases en `backend/app/schemas.py` siguen usando el estilo de configuración de Pydantic v1 (`class Config:`). Hoy solo genera un warning de deprecación bajo Pydantic 2.13; no rompe nada, pero habrá que migrarlo a `model_config = ConfigDict(...)` antes de que el proyecto actualice a Pydantic v3.

---

## P-13 Dockerización

No hay `Dockerfile` para backend ni frontend, ni `docker-compose.yml`. El despliegue depende 100% de los buildpacks nativos de Render (`render.yaml`). Sería útil para desarrollo local reproducible y para portar el despliegue a otro proveedor en el futuro.

---

## P-14 Monitoreo y tracking de errores

No hay Sentry ni ninguna herramienta equivalente de APM. El logging es puntual (`logging` usado solo en `main.py`, `routes/productos.py` y `routes/usuarios.py`), sin agregación central ni alertas.

---

## P-15 Backups automatizados propios

El respaldo de la base de datos depende enteramente del plan gestionado de PostgreSQL en Render. No hay un `pg_dump` automatizado ni almacenado fuera de Render.

---

## P-16 Riesgos del plan gratuito de Render

El despliegue actual usa el plan **free** de Render (`render.yaml`): esto implica *cold starts* tras períodos de inactividad y que la base de datos free expira a los 90 días si no se actualiza a un plan pago. Es un riesgo operativo real mientras el proyecto siga en este tier, independiente del código de la aplicación.

---

## P-17 Documentar formalmente el módulo de Comercio y Avisos

~~Resuelto (2026-09)~~: `Requerimientos_Funcionales.md` ya incluye RF-176 a RF-226 cubriendo Entrenadores, Avisos, Auditoría y los seis submódulos de Comercio (categorías, productos, proveedores, compras, inventario, ventas).

---

# Fuera de este documento

No se repiten aquí las brechas ya resueltas en las tres rondas de revisión anteriores: RBAC completo, motor de IA real (restricciones médicas + fórmula Mifflin-St Jeor), auditoría y trazabilidad, autogestión de contraseñas + reset por admin, Avisos editables desde el panel, KPI de asistencias en el dashboard, y paginación en los listados de mayor volumen.

---
