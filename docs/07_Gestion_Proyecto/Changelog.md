# Changelog del Proyecto

# SistemaGimnasioGleyforGym

## 1. Introducción

El changelog documenta todos los cambios, mejoras, correcciones y nuevas funcionalidades que se han realizado en cada versión del sistema.

---

# 2. Versiones

## v1.0

**Fecha:** Inicio del proyecto

**Cambios:**

- Creación del repositorio.
- Diseño de base de datos inicial.
- CRUD básico de Clientes y Usuarios.
- Login básico.
- Dashboard inicial.

---

## v1.5

**Fecha:** Desarrollo backend inicial

**Cambios:**

- Implementación de JWT para autenticación.
- Validación de contraseñas con bcrypt.
- Separación de usuarios y clientes.
- CRUD de Membresías.
- CRUD de Cliente Membresías.

---

## v2.0 Web

**Fecha:** Integración completa web

**Cambios:**

- Implementación de FastAPI completo.
- Integración con PostgreSQL.
- CRUD de Pagos, Asistencias y Progreso.
- IA Rutinas básica.
- IA Nutrición básica.
- Subida de videos a Cloudinary.
- Dashboards Admin, Entrenador y Cliente.
- Landing pública moderna.
- ProtectedRoute para roles.
- Edad calculada automáticamente.
- Precio congelado en membresías asignadas.
- Pausa y reactivación de membresías.
- Medidas físicas detalladas (brazo/pierna izquierda/derecha).
- Gestión de ejercicios y comidas con estado activo/inactivo.

---

## v2.1

**Fecha:** Mejoras en interfaz y reportes

**Cambios:**

- Mejora de dashboard Admin con gráficos.
- Mejora de dashboard Entrenador y Cliente.
- Visualización completa de DetalleCliente.
- Exportación PDF para rutinas y planes nutricionales (parcial).
- Alertas de membresía próxima a vencer.
- Optimización de vistas React y formularios.

---

## v2.5

**Fecha:** App móvil Flutter

**Cambios:**

- Implementación de Flutter base para clientes.
- Integración con backend FastAPI.
- Visualización de Mi Perfil, Mi Rutina, Mi Nutrición, Mi Progreso, Mi Membresía y Mis Pagos.
- Consumo de IA desde la app.
- Botón + Nuevo registro para progreso.
- Corrección de rutas y permisos por rol.

---

## v2.6

**Fecha:** 1 de Junio de 2026 (Estabilización, Integración y Corrección de Bugs)

**Cambios:**

- **Backend (FastAPI & SQLAlchemy)**:
  - Corregido error `AttributeError` en `/clientes/{id_cliente}/detalle` al resolver medidas obsoletas (`medida_brazo` / `medida_pierna`) reemplazándolas con el conjunto detallado (`medida_brazo_izquierdo`, `medida_brazo_derecho`, `medida_pierna_izquierda`, `medida_pierna_derecha`).
  - Corregida omisión del campo `beneficios` en la creación de membresías (endpoint `POST /membresias/`).
  - Añadida propiedad dinámica `nombre_membresia` al modelo `ClienteMembresia` expuesta en `ClienteMembresiaResponse` para facilitar la visualización directa del nombre de plan en la app de Flutter y el frontend web.
  - Sincronización y consistencia en los comentarios de estado del modelo de membresías en `models.py`.
- **App Móvil (Flutter)**:
  - Implementada la pantalla de detalles de rutinas (`RutinaDetalleScreen`) que expone los ejercicios ordenados con sus series, repeticiones, tiempo de descanso y video demostrativo de Cloudinary.
  - Integrada la navegación interactiva a `RutinaDetalleScreen` al pulsar sobre cualquier rutina de la lista.
  - Corregido el acceso a la propiedad `masa_muscular` (cambiado a `masa_magra`) y habilitada la visualización completa de medidas físicas detalladas (pecho, cintura, brazos y piernas) en la pantalla de progreso.
  - Habilitada la visualización del nombre de plan de membresía real (`nombre_membresia`) en lugar del identificador numérico.
- **Calidad y Documentación**:
  - Actualización exhaustiva de los manuales, guías y casos de prueba del proyecto bajo la norma ISO 9001.

---

## v3.0 (Futuro)

**Objetivo:**

- IA avanzada para rutinas y nutrición.
- Analítica predictiva.
- Notificaciones inteligentes.
- Optimización UI/UX web y móvil.
- Dashboard completo con métricas deportivas y financieras.

---

## v4.0 (Futuro)

**Objetivo:**

- Plataforma SaaS multi gimnasio.
- Gestión de gimnasios independientes.
- Pagos recurrentes y facturación SaaS.
- Administración global con super administrador.
- Escalabilidad y despliegue en nube.

---

# 3. Convenciones del Changelog

- Las versiones se enumeran de manera ascendente.
- Cada versión incluye: fecha, cambios y mejoras.
- Se documenta tanto funcionalidades nuevas como correcciones.
- Cambios futuros se documentan como objetivos o milestones.

---

# 4. Estado Actual

**Versión Actual: v2.6**

**Fecha:** 1 de Junio de 2026

**Notas:**

- Sistema web completamente funcional y libre de bugs críticos.
- App Flutter estabilizada y con pantallas de detalle e historial robustos.
- IA básica operativa y probada.
- Documentación e integración de calidad completadas bajo normas ISO 9001.