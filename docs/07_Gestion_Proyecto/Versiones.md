# Registro de Versiones del Sistema

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento resume cada versión del sistema, indicando los módulos implementados, funcionalidades y mejoras principales.

---

# 2. Versiones

## v1.0 – Inicio del Proyecto

**Fecha:** Inicio de desarrollo

**Módulos Implementados:**

- Usuarios
- Clientes
- Login básico
- Dashboard inicial
- CRUD básico Clientes y Usuarios

**Notas:**

- Primer diseño de base de datos.
- Funcionalidades mínimas para pruebas internas.

---

## v1.5 – Backend Inicial

**Fecha:** Desarrollo inicial backend

**Módulos Implementados:**

- Autenticación JWT
- Validación contraseñas con bcrypt
- CRUD Membresías
- CRUD Cliente Membresías
- Separación de usuarios y clientes

**Notas:**

- Integración básica con PostgreSQL.
- Implementación de reglas de negocio principales.

---

## v2.0 Web – Integración Completa

**Fecha:** Implementación web completa

**Módulos Implementados:**

- Backend FastAPI completo
- CRUD de Pagos, Asistencias, Progreso
- Gestión de Ejercicios y Comidas
- Dashboards Admin, Entrenador, Cliente
- IA Rutinas y Nutrición básicas
- Subida de videos a Cloudinary
- Landing pública moderna
- ProtectedRoute y control de roles
- Edad automática
- Precio congelado en membresías asignadas
- Pausa y reactivación de membresías
- Medidas físicas detalladas

**Notas:**

- Sistema web funcional para todos los roles.
- Documentación técnica inicial disponible.

---

## v2.1 – Mejoras en Interfaz y Reportes

**Fecha:** Post web completo

**Módulos Mejorados:**

- Dashboard Admin, Entrenador y Cliente con gráficos
- Visualización completa de DetalleCliente
- Exportación parcial de PDFs para rutinas y nutrición
- Alertas de membresías próximas a vencer
- Optimización de vistas y formularios React

---

## v2.5 – App Móvil Flutter

**Fecha:** Desarrollo Flutter

**Módulos Implementados:**

- Mi Perfil
- Mi Rutina
- Mi Nutrición
- Mi Progreso
- Mi Membresía
- Mis Pagos
- Consumo de IA desde la app
- Botón + Nuevo registro para progreso
- Corrección de rutas y permisos por rol

---

## v2.6 – Estabilización, Integración y Corrección de Bugs

**Fecha:** 1 de Junio de 2026

**Módulos e Integraciones:**

- **Backend (FastAPI & SQLAlchemy)**:
  - Parche del bug en `/clientes/{id_cliente}/detalle` que fallaba al leer atributos de medidas obsoletos.
  - Habilitación del campo `beneficios` en la creación de membresías.
  - Implementación de la propiedad dinámica `nombre_membresia` y su serialización.
- **App Móvil (Flutter)**:
  - Nueva pantalla interactiva de detalle de rutinas y ejercicios (`RutinaDetalleScreen`).
  - Navegación al detalle de rutinas.
  - Corrección de variable `masa_muscular` a `masa_magra` e inclusión de desglose detallado de medidas físicas en la pantalla de progreso.
  - Visualización del nombre de plan en la membresía.
- **Documentación ISO 9001**:
  - Actualización de manuales técnicos, operativos y guías de pruebas.

---

## v3.0 – Futuro (Planeado)

**Objetivo:**

- IA avanzada para rutinas y nutrición
- Analítica predictiva
- Notificaciones inteligentes
- Optimización UI/UX web y móvil
- Dashboard completo con métricas deportivas y financieras

---

## v4.0 – Futuro (Planeado)

**Objetivo:**

- Plataforma SaaS multi gimnasio
- Gestión de gimnasios independientes
- Pagos recurrentes y facturación SaaS
- Administración global con super administrador
- Escalabilidad y despliegue en nube

---

# 3. Convenciones de Versionado

- Las versiones se enumeran ascendentemente.
- Cada versión incluye fecha, módulos y notas.
- Cambios futuros se documentan como objetivos o milestones.

---

# 4. Estado Actual

**Versión Actual: v2.6**

**Notas:**

- Sistema web completamente funcional y libre de bugs críticos.
- App Flutter estabilizada y con pantallas de detalle e historial robustos.
- IA básica operativa y probada.
- Documentación e integración de calidad completadas bajo normas ISO 9001.