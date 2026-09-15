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
backend/app/pagos_gateway/__init__.py → singleton `gateway`, punto único de cambio
```

Falta:

1. Escribir una clase nueva (ej. `CulqiGateway`) que implemente `crear_checkout()` y `consultar_estado()`.
2. Reemplazar `gateway = MockGateway()` por `gateway = CulqiGateway()` en `pagos_gateway/__init__.py:7`. Las rutas de `pagos.py`/`ventas.py` no necesitan cambios.
3. Configurar credenciales reales como variable de entorno (nunca hardcodeadas).
4. Validar la firma/secreto del webhook en `routes/webhooks.py` — hoy solo lo dispara el flujo mock, sin verificación de origen. Una pasarela real permitiría que cualquiera llame al webhook y falsifique un pago si no se valida la firma.

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

Sigue en 0% de cobertura, tanto backend como frontend — es la parte del sistema que maneja dinero y stock con menos pruebas:

```text
Backend sin tests:
  backend/app/routes/categorias.py
  backend/app/routes/productos.py
  backend/app/routes/proveedores.py
  backend/app/routes/compras.py
  backend/app/routes/inventario.py
  backend/app/routes/ventas.py

Frontend sin tests:
  web-admin/src/pages/Categorias.jsx
  web-admin/src/pages/Productos.jsx
  web-admin/src/pages/Proveedores.jsx
  web-admin/src/pages/Compras.jsx
  web-admin/src/pages/Inventario.jsx
  web-admin/src/pages/Ventas.jsx
  web-admin/src/pages/Tienda.jsx
```

Alcance sugerido para cuando se retome: tests de humo backend (CRUD básico + reglas de stock/lotes) y un test por página en frontend, siguiendo el mismo patrón usado en el resto del proyecto (`vi.mock` de `api`, `render` + `waitFor`).

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

`docs/03_Analisis/Requerimientos_Funcionales.md` (RF-001 a RF-175) no incluye ningún requerimiento para el módulo de Comercio (categorías/productos/proveedores/compras/inventario/ventas) ni para Avisos — ambos módulos ya están en producción pero se agregaron como extensión de alcance sin quedar documentados como RF formales. Vale la pena agregarlos si el documento de requerimientos se usa como referencia para la tesis.

---

# Fuera de este documento

No se repiten aquí las brechas ya resueltas en las tres rondas de revisión anteriores: RBAC completo, motor de IA real (restricciones médicas + fórmula Mifflin-St Jeor), auditoría y trazabilidad, autogestión de contraseñas + reset por admin, Avisos editables desde el panel, KPI de asistencias en el dashboard, y paginación en los listados de mayor volumen.

---
