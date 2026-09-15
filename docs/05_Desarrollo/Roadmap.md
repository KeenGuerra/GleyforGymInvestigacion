# Roadmap del Proyecto

# SistemaGimnasioGleyforGym

## Información General

**Proyecto:** SistemaGimnasioGleyforGym

**Versión Actual:** 2.0 Web

**Objetivo General:**

Automatizar los procesos administrativos y deportivos del gimnasio GLEYFORGYM mediante una plataforma web, móvil e inteligencia artificial adaptativa para la generación de rutinas y planes nutricionales personalizados.

---

# Estado General del Proyecto

> **Nota (revisión posterior):** este roadmap fue actualizado tras completarse tres rondas de revisión y corrección sobre el sistema web (backend + web-admin). El detalle punto por punto de lo que queda pendiente hoy está en [`docs/07_Gestion_Proyecto/Pendientes.md`](../07_Gestion_Proyecto/Pendientes.md).

## Avance Global

| Módulo | Estado |
|----------|----------|
| Base de Datos | ✅ Completo |
| Backend FastAPI | ✅ Completo |
| Autenticación JWT | ✅ Completo |
| Gestión de Usuarios | ✅ Completo (incluye autogestión de contraseña y reset por admin) |
| Gestión de Clientes | ✅ Completo (con búsqueda, filtros y paginación backend) |
| Gestión de Membresías | ✅ Completo |
| Gestión de Pagos | ✅ Completo (arquitectura de pasarela lista, ver Pendientes.md) |
| Gestión de Asistencias | ✅ Completo |
| Gestión de Progreso | ✅ Completo |
| Gestión de Ejercicios | ✅ Completo |
| Gestión de Comidas | ✅ Completo |
| IA Rutinas | ✅ Completo |
| IA Nutrición | ✅ Completo |
| Cloudinary | ✅ Completo |
| Landing Pública | ✅ Completo |
| Avisos (horarios/coaches/eventos) | ✅ Completo (editable desde el panel, antes era estático) |
| Módulo de Comercio (productos/categorías/proveedores/compras/inventario/ventas) | ✅ Completo funcionalmente — ⚠️ sin cobertura de tests, ver Pendientes.md |
| Auditoría y trazabilidad | ✅ Completo |
| Dashboard Admin | ✅ Completo (KPIs incluyendo asistencias del día/mes) |
| Dashboard Entrenador | ✅ Completo |
| Dashboard Cliente | ✅ Completo |
| Reportes PDF | ✅ Completo (recibos de pago) — reportes operativos consolidados y PDF de rutinas/nutrición siguen pendientes |
| Paginación en listados | ✅ Completo (clientes, pagos, ventas, productos) |
| Flutter Base | 🟡 Parcial |
| Pasarela de pago real (Culqi) | ❌ Pendiente (arquitectura lista, falta activar) |
| Envío real de correo (SMTP) | ❌ Pendiente (arquitectura lista, falta proveedor) |
| Verificación de correo al registrarse | ❌ Pendiente |
| Docker | ❌ Pendiente |
| CI/CD | ❌ Pendiente |
| SaaS Multi Gimnasio | ❌ Pendiente |

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

## Pendiente

### Membresías

- Alertas de vencimiento.
- Alertas de renovación.

(No se detectó ningún job/notificación de vencimiento en el código; solo existe el cambio automático de estado a TERMINADA. Ver `docs/07_Gestion_Proyecto/Pendientes.md`, punto P-05.)

---

### Nutrición

- Exportación PDF.
- Impresión de planes.

(Solo existe PDF para recibos de pago, no para planes nutricionales. Ver Pendientes.md, punto P-06.)

---

### Rutinas

- Exportación PDF.
- Impresión de rutinas.

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

## Pendiente

### Backend

- Dockerfile.

---

### Frontend

- Dockerfile.

---

### Base de Datos

- Contenedor PostgreSQL.

---

### Orquestación

- Docker Compose.

---

# Calidad de Software

## Estado

- ✅ Backend: 55 tests (pytest) cubriendo usuarios, clientes, membresías, pagos, asistencias, progreso, ejercicios, comidas, rutinas/nutrición IA, auditoría y seguridad.
- ✅ Frontend: 143 tests (Vitest + Testing Library) cubriendo la mayoría de páginas de administración y del panel del cliente.
- ❌ **Módulo de Comercio sin cobertura**: `categorias`, `productos`, `proveedores`, `compras`, `inventario`, `ventas` (backend y frontend) siguen en 0%. Ver `docs/07_Gestion_Proyecto/Pendientes.md`, punto P-04 (prioridad Alta).
- ❌ `Navbar.jsx` y `NotFound.jsx` tampoco tienen test. Ver Pendientes.md, punto P-08.

### Cobertura

Objetivo:

```text
>80%
```

Alcanzado en los módulos con test (ver detalle arriba); el módulo de Comercio es la brecha real pendiente para llegar a ese objetivo en todo el sistema.

---

# Seguridad

## Implementado

- ✅ Auditoría y trazabilidad (`RegistroAuditoria`, RF-165).
- ✅ Rate limiting de intentos de login (en memoria, por proceso — ver Pendientes.md punto P-10 sobre su límite conocido).
- ✅ Revalidación de sesión contra la base de datos en cada request protegido.

## Futuro

### Mejoras

- Refresh Tokens.
- Logs centralizados / monitoreo (Sentry u otro APM). Ver Pendientes.md, punto P-14.

---

# Infraestructura

## Futuro

### Despliegue

- VPS.
- AWS.
- Azure.
- Railway.
- Render.

---

# Prioridad Actual

Ver el detalle completo, con archivos y líneas citadas, en [`docs/07_Gestion_Proyecto/Pendientes.md`](../07_Gestion_Proyecto/Pendientes.md). Resumen:

## Alta

1. Verificación de correo al registrarse.
2. Conectar una pasarela de pago real (Culqi recomendado).
3. Envío real de correo (SMTP/SendGrid/Mailgun).
4. Cobertura de tests del módulo de Comercio.

---

## Media

1. Alertas de vencimiento de membresía.
2. Exportación PDF de rutinas y planes nutricionales.
3. Reportes operativos consolidados.
4. Tests de `Navbar.jsx` y `NotFound.jsx`.
5. CI/CD (ejecución automática de tests en cada push/PR).

---

## Baja

1. Migrar `class Config:` a `ConfigDict` en los schemas (Pydantic v2).
2. Dockerización (backend, frontend, PostgreSQL, compose).
3. Monitoreo y tracking de errores (Sentry u otro).
4. Backups automatizados propios (hoy dependen del plan gestionado de Render).
5. SaaS Multi Gimnasio.
6. Machine Learning / Wearables.

---

# Próximo Sprint Recomendado

## Sprint 1

### Objetivo

Cerrar las integraciones externas que ya tienen la arquitectura lista.

### Tareas

- Conectar Culqi como pasarela de pago real.
- Configurar un proveedor SMTP y activar el envío real de correo (recuperación de contraseña + verificación de cuenta).

---

## Sprint 2

### Objetivo

Cerrar la brecha de calidad más grande del sistema.

### Tareas

- Tests de humo backend para el módulo de Comercio.
- Tests de página para Categorías, Productos, Proveedores, Compras, Inventario, Ventas, Tienda, Navbar y NotFound.

---

## Sprint 3

### Objetivo

Funcionalidades pendientes que el usuario notaría.

### Tareas

- Alertas de vencimiento de membresía.
- Exportación PDF de rutinas y nutrición.
- Reportes operativos consolidados.

---

# Estado Actual

## Versión

```text
SistemaGimnasioGleyforGym v2.0 Web — tras 3 rondas de revisión y corrección
```

## Progreso Estimado

```text
Núcleo funcional (backend + web-admin): completo.
Pendiente: integraciones externas (pago, correo), cobertura de tests de Comercio,
verificación de correo, e infraestructura (Docker/CI-CD/monitoreo).
```

## Próxima Meta

```text
Conectar pasarela de pago real y SMTP; cerrar cobertura de tests de Comercio.
```

---