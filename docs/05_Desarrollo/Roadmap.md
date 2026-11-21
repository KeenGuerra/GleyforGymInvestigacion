# Roadmap del Proyecto

# SistemaGimnasioGleyforGym

## Información General

**Proyecto:** SistemaGimnasioGleyforGym

**Versión Actual:** 2.0 Web

**Objetivo General:**

Automatizar los procesos administrativos y deportivos del gimnasio GLEYFORGYM mediante una plataforma web, móvil e inteligencia artificial adaptativa para la generación de rutinas y planes nutricionales personalizados.

---

# Estado General del Proyecto

> **Nota (revisión posterior, 20/11/2026):** este roadmap se actualizó por última vez tras la sexta iteración de consolidación sobre el sistema web (backend + web-admin). El detalle punto por punto de lo que queda pendiente hoy está en [`docs/07_Gestion_Proyecto/Pendientes.md`](../07_Gestion_Proyecto/Pendientes.md).

## Avance Global

| Módulo | Estado |
|----------|----------|
| Base de Datos | ✅ Completo |
| Backend FastAPI | ✅ Completo |
| Autenticación JWT | ✅ Completo |
| Gestión de Usuarios | ✅ Completo (incluye autogestión de contraseña y reset por admin) |
| Gestión de Clientes | ✅ Completo (con búsqueda, filtros y paginación backend) |
| Gestión de Membresías | ✅ Completo |
| Gestión de Pagos | ✅ Completo (Yape/Plin/efectivo, confirmado a mano por el staff — ver Pendientes.md, P-02) |
| Gestión de Asistencias | ✅ Completo |
| Gestión de Progreso | ✅ Completo |
| Gestión de Ejercicios | ✅ Completo |
| Gestión de Comidas | ✅ Completo |
| IA Rutinas | ✅ Completo |
| IA Nutrición | ✅ Completo |
| Cloudinary | ✅ Completo |
| Landing Pública | ✅ Completo |
| Avisos (horarios/coaches/eventos) | ✅ Completo (editable desde el panel, con imagen opcional) |
| Configuración del sitio (contacto, redes sociales, logo) | ✅ Completo (editable desde el panel, antes fijo en el código) |
| Módulo de Comercio (productos/categorías/proveedores/compras/inventario/ventas) | ✅ Completo, con cobertura de tests dedicada (ver Pendientes.md, P-04) |
| Auditoría y trazabilidad | ✅ Completo |
| Dashboard Admin | ✅ Completo (KPIs incluyendo asistencias del día/mes) |
| Dashboard Entrenador | ✅ Completo |
| Dashboard Cliente | ✅ Completo |
| Reportes PDF | ✅ Completo (recibos de pago, boletas de venta, y PDF de rutinas/planes nutricionales) |
| Reportes operativos consolidados | ✅ Completo (ingresos, asistencias, compras, resumen general, productos más vendidos, Excel general del negocio) |
| Paginación en listados | ✅ Completo (clientes, pagos, ventas, productos) |
| Flutter Base | 🟡 Parcial |
| Pasarela de pago | ✅ Descartada a propósito — todo pago es por Yape/Plin/Efectivo, confirmado a mano por el staff |
| Envío real de correo | ✅ Completo (API HTTPS de Brevo, ver Pendientes.md, P-03) |
| Verificación de correo al registrarse | ✅ Completo (ver Pendientes.md, P-01) |
| Docker (desarrollo local) | ✅ Completo (`docker-compose.yml`, no reemplaza el despliegue en Render, ver Pendientes.md, P-13) |
| CI/CD | ✅ Completo (GitHub Actions, `pytest` + `npm run lint`/`test` en cada push/PR, ver Pendientes.md, P-09) |
| Migración a VPS propio | ❌ Pendiente — bloqueada a que se compre el plan (ver Pendientes.md, P-16) |
| SaaS Multi Gimnasio | ❌ Pendiente (visión a largo plazo, sin trabajo iniciado) |

---

# Versión 2.0 Web

## Objetivo

Consolidar una plataforma web completamente funcional para la administración integral del gimnasio.

---

## Funcionalidades Terminadas

### Seguridad

- Login JWT.
- Roles.
- Control de acceso.
- Hash de contraseñas.

---

### Administración

- Usuarios.
- Clientes.
- Membresías.
- Pagos.
- Asistencias.

---

### Entrenamiento

- Ejercicios.
- Rutinas.
- Videos Cloudinary.

---

### Nutrición

- Catálogo de comidas.
- Planes nutricionales.

---

### Inteligencia Artificial

- Generación de rutinas.
- Generación nutricional.

---

### Cliente

- Mi perfil.
- Mi rutina.
- Mi nutrición.
- Mi progreso.
- Mi membresía.
- Mis pagos.

---

# Versión 2.1

## Objetivo

Mejorar la experiencia de usuario y optimizar la administración.

---

## Completado

### Dashboard

- ✅ Gráficos con Recharts.
- ✅ Indicadores financieros.
- ✅ Métricas deportivas (KPI de asistencias hoy/mes).

---

### Clientes

- ✅ Historial completo en DetalleCliente.
- ✅ Filtros avanzados (búsqueda y estado, resueltos en backend).
- ✅ Exportación de información (CSV).
- ✅ Paginación.

---

## Completado (post-2.1)

### Membresías

- ✅ Tarjeta "Membresías por vencer" en el dashboard admin.
- ✅ Recordatorio por WhatsApp (enlace `wa.me` prellenado, confirmado por el staff) desde `Reportes.jsx`.

(Ver `docs/07_Gestion_Proyecto/Pendientes.md`, punto P-05. El envío por WhatsApp sigue siendo manual-asistido a propósito, no automático — ver el detalle de esa decisión en Pendientes.md.)

---

### Nutrición

- ✅ Exportación PDF (`GET /nutricion/{id}/pdf`), botón "Descargar PDF" en `Nutricion.jsx`/`MiNutricion.jsx`.

(Ver Pendientes.md, punto P-06.)

---

### Rutinas

- ✅ Exportación PDF (`GET /rutinas/{id}/pdf`), botón "Descargar PDF" en `DetalleRutina.jsx`/`MiRutina.jsx`.

(Mismo caso que Nutrición. Ver Pendientes.md, punto P-06.)

---

# Versión 2.5

## Objetivo

Fortalecer la aplicación móvil.

---

## Flutter

### Completar Pantallas

- Mejorar Home.
- Mejorar Navegación.
- Mejorar Diseño.

---

### Agregar Funcionalidades

- Notificaciones.
- Historial de progreso.
- Descarga PDF.
- Recordatorios.

---

### Integraciones

- Cloudinary.
- Dashboard móvil.

---

# Versión 3.0

## Objetivo

Transformar GLEYFORGYM en una plataforma inteligente de nueva generación.

---

## Inteligencia Artificial Avanzada

### Rutinas

- Ajustes automáticos.
- Recomendaciones adaptativas.
- Evolución automática.

---

### Nutrición

- Ajustes automáticos.
- Recomendaciones inteligentes.
- Optimización continua.

---

### Analítica

- Predicción de resultados.
- Seguimiento automático.
- Alertas inteligentes.

---

# Versión 4.0

## Objetivo

Convertir el sistema en una plataforma SaaS multi gimnasio.

---

## Multi Empresa

### Gestión de Gimnasios

- Registro de gimnasios.
- Configuración independiente.
- Personalización.

---

### Facturación

- Planes SaaS.
- Suscripciones.
- Pagos recurrentes.

---

### Administración Global

- Super Administrador.
- Panel global.
- Métricas generales.

---

# Dockerización

## Completado (desarrollo local)

~~Resuelto~~ (ver `Pendientes.md`, P-13): `backend/Dockerfile`, `web-admin/Dockerfile` (build multi-stage con nginx) y `docker-compose.yml` en la raíz (`db` + `backend` + `frontend`, con healthcheck de PostgreSQL). Probado de punta a punta con `docker compose up --build`. No reemplaza el despliegue de `render.yaml` — es solo para desarrollo local reproducible.

- ✅ Backend: Dockerfile.
- ✅ Frontend: Dockerfile (multi-stage, nginx).
- ✅ Base de datos: contenedor PostgreSQL con healthcheck.
- ✅ Orquestación: Docker Compose.

---

# Calidad de Software

## Estado

- ✅ Backend: 200 pruebas (pytest) cubriendo usuarios, clientes, membresías, pagos, asistencias, progreso, ejercicios, comidas, rutinas/nutrición IA, auditoría, seguridad, Comercio y zona horaria.
- ✅ Frontend: 410 pruebas (Vitest + Testing Library) en 56 archivos, cubriendo todas las páginas de administración y del panel del cliente.
- ✅ **Módulo de Comercio con cobertura dedicada**: `categorias`, `productos`, `proveedores`, `compras`, `inventario`, `ventas` (backend y frontend). Ver `docs/07_Gestion_Proyecto/Pendientes.md`, punto P-04.
- ✅ `Navbar.jsx` y `NotFound.jsx` tienen test (100% de cobertura). Ver Pendientes.md, punto P-08.
- ✅ CI/CD en GitHub Actions corre toda la suite en cada push/PR a `main`. Ver Pendientes.md, punto P-09.

(Conteos verificados el 20/11/2026; ver `Intervencion_Metodologica.md`, Tabla 12, para el detalle y la fecha de la próxima medición.)

### Cobertura

Objetivo:

```text
>80%
```

Alcanzado en todos los módulos con test, incluido Comercio (ver `Intervencion_Metodologica.md`, Tabla 11 y sección 6.2, para el desglose por archivo).

---

# Seguridad

## Implementado

- ✅ Auditoría y trazabilidad (`RegistroAuditoria`, RF-165).
- ✅ Rate limiting de intentos de login (en memoria, por proceso — ver Pendientes.md punto P-10 sobre su límite conocido).
- ✅ Revalidación de sesión contra la base de datos en cada request protegido.

## Futuro

### Mejoras

- Refresh Tokens.
- Logs centralizados / monitoreo (Sentry u otro APM) — sin pendiente abierto todavía, se evaluaría junto con la migración a VPS (ver Pendientes.md, P-16).

---

# Infraestructura

## Futuro

### Despliegue

Decisión ya tomada (ver Pendientes.md, P-16): migrar backend y base de datos a un **VPS de Hostinger**, reutilizando `docker-compose.yml`, en vez de pagar un plan superior de Render. Resuelve de paso el límite del rate limiter en memoria (P-10) y la falta de backups propios (P-15), que se implementan junto con esta migración. Queda pendiente de que el usuario compre el plan VPS (y, idealmente, un dominio propio para HTTPS con Let's Encrypt) — no tiene fecha porque depende de esa compra, no de trabajo de desarrollo.

---

# Prioridad Actual

Ver el detalle completo, con archivos y líneas citadas, en [`docs/07_Gestion_Proyecto/Pendientes.md`](../07_Gestion_Proyecto/Pendientes.md). A noviembre de 2026, todos los puntos de prioridad Alta y Media de este roadmap ya están resueltos (verificación de correo, envío real de correo, cobertura de tests de Comercio, alertas de vencimiento, PDF de rutinas/nutrición, reportes operativos, tests de `Navbar.jsx`/`NotFound.jsx`, CI/CD). Lo que queda abierto:

## Media-Baja (bloqueado por una compra, no por desarrollo)

1. Migración del despliegue a un VPS de Hostinger (Pendientes.md, P-16) — bloqueada a que el usuario compre el plan.
2. Resolver el rate limiting de login en memoria con Redis (P-10) y los backups automatizados propios (P-15) — ambos se implementan junto con el punto 1.

---

## Baja

1. Facturación electrónica SUNAT — evaluada y descartada por ahora; se reconsideraría solo si el volumen de ventas/pagos del gimnasio creciera lo suficiente (Pendientes.md, P-24).
2. Monitoreo y tracking de errores (Sentry u otro APM).
3. SaaS Multi Gimnasio.
4. Machine Learning / Wearables.

---

# Próximo Sprint Recomendado

No queda ningún sprint de desarrollo bloqueando el núcleo funcional: todo lo que dependía solo de código ya está resuelto (ver "Prioridad Actual" arriba). El único trabajo real pendiente depende de una decisión/compra del usuario, no de una tarea de desarrollo lista para tomar:

## Sprint recomendado: migración a VPS

### Objetivo

Eliminar los riesgos operativos del plan gratuito de Render (*cold start*, expiración de la base de datos a los 90 días — ver `Intervencion_Metodologica.md`, sección 9.3) migrando a un VPS de Hostinger.

### Tareas

- Comprar el plan VPS (y, idealmente, un dominio propio).
- Desplegar con `docker-compose.yml` (ya probado en local, ver Pendientes.md P-13).
- Configurar HTTPS (Let's Encrypt) y las variables de entorno de producción.
- Resolver junto con esta migración: Redis para el rate limiter de login (P-10) y backups automatizados propios (P-15).

Mientras no se compre el VPS, no hay ningún otro sprint de desarrollo priorizado — el sistema está funcionalmente completo para el alcance definido en el Plan de Tesis.

---

# Estado Actual

## Versión

```text
SistemaGimnasioGleyforGym v2.0 Web — sexta iteración de consolidación (20/11/2026)
```

## Progreso Estimado

```text
Núcleo funcional (backend + web-admin): completo, incluidos Comercio, Avisos
(con imagen), Configuración del sitio, Entrenadores y Auditoría.
Pendiente: solo la migración de infraestructura a un VPS propio (bloqueada a
que se compre el plan) y, a futuro, facturación electrónica SUNAT si el
volumen de ventas lo llegara a exigir.
```

## Próxima Meta

```text
Migrar el despliegue (backend + base de datos) a un VPS de Hostinger, para
eliminar el cold start y la expiración de la base de datos gratuita de Render.
```

---