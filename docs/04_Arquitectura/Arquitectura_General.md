# Arquitectura General

# SistemaGimnasioGleyforGym

## 1. Introducción

El SistemaGimnasioGleyforGym es una plataforma integral para la gestión administrativa y deportiva de gimnasios.

La solución está compuesta por:

- Aplicación Web Administrativa
- Aplicación Móvil para Clientes
- API REST
- Base de Datos PostgreSQL
- Módulo de Inteligencia Artificial
- Servicio Multimedia Cloudinary

La arquitectura sigue un modelo multicapa orientado a servicios.

---

## 2. Objetivo de la Arquitectura

La arquitectura busca:

- Separar responsabilidades.
- Facilitar el mantenimiento.
- Mejorar la escalabilidad.
- Permitir integración futura SaaS.
- Centralizar la lógica de negocio.
- Reutilizar servicios entre Web y Flutter.

---

## 3. Arquitectura General del Sistema

```text
+------------------------------------------------+
|                 CLIENTES WEB                   |
|                  React + Vite                  |
+------------------------+-----------------------+
                         |
                         |
                         v
+------------------------------------------------+
|                 API REST                        |
|                  FastAPI                        |
+------------------------------------------------+
| Usuarios | Clientes | Pagos | Rutinas | IA     |
+------------------------------------------------+
                         |
                         |
                         v
+------------------------------------------------+
|              PostgreSQL Database               |
+------------------------------------------------+

                         ^
                         |
                         |
+------------------------------------------------+
|                 Flutter App                    |
|              Aplicación Móvil                  |
+------------------------------------------------+

                         |
                         v

+------------------------------------------------+
|                Cloudinary                      |
|          Videos de Ejercicios                  |
+------------------------------------------------+
```

---

## 4. Capas de la Arquitectura

La solución se encuentra dividida en cinco capas principales.

### 4.1 Capa de Presentación

Responsable de la interacción con los usuarios.

**Tecnologías**

- React
- Flutter

**Funciones**

- Formularios
- Dashboards
- Consultas
- Visualización de rutinas
- Visualización de nutrición
- Gestión de membresías

---

### 4.2 Capa de Servicios

Implementada mediante FastAPI.

**Funciones**

- Exposición de APIs REST
- Validación de solicitudes
- Control de acceso
- Comunicación con la base de datos
- Integración con IA

---

### 4.3 Capa de Negocio

Contiene las reglas principales del gimnasio.

**Ejemplos**

- Cálculo automático de edad
- Precio congelado de membresías
- Gestión de membresías
- Gestión de pagos
- Generación de rutinas IA
- Generación de nutrición IA

---

### 4.4 Capa de Datos

Implementada mediante PostgreSQL.

**Funciones**

- Persistencia de información
- Integridad de datos
- Relaciones entre entidades
- Históricos de operaciones

---

### 4.5 Capa Externa

Servicios externos integrados al sistema.

**Componentes**

- Cloudinary
- Futuras APIs externas

---

## 5. Componentes Principales

### Frontend Web

**Tecnologías**

- React
- Vite
- Axios
- React Router DOM

**Responsabilidades**

- Administración del gimnasio
- Gestión deportiva
- Dashboards
- Gestión de usuarios
- Gestión de clientes

---

### Backend

**Tecnologías**

- FastAPI
- SQLAlchemy
- JWT
- Passlib
- Bcrypt

**Responsabilidades**

- Lógica de negocio
- Seguridad
- APIs REST
- Integración con IA

---

### Base de Datos

**Tecnología**

- PostgreSQL

**Responsabilidades**

- Almacenamiento de datos
- Integridad referencial
- Históricos de información

---

### Aplicación Móvil

**Tecnología**

- Flutter

**Responsabilidades**

- Consulta de perfil
- Consulta de rutinas
- Consulta de nutrición
- Consulta de pagos
- Consulta de membresías

---

### Inteligencia Artificial

**Tecnología**

- Python

**Responsabilidades**

- Generación de rutinas personalizadas
- Generación de planes nutricionales
- Recomendaciones automáticas

---

### Multimedia

**Tecnología**

- Cloudinary

**Responsabilidades**

- Almacenamiento de videos
- Distribución optimizada de contenido multimedia

---

## 6. Flujo General del Sistema

### Login

```text
Usuario
   ↓
React / Flutter
   ↓
POST /usuarios/login
   ↓
JWT
   ↓
Dashboard correspondiente
```

---

### Generación de Rutina IA

```text
Cliente
   ↓
Objetivo
Nivel
Datos físicos
   ↓
IA Rutina
   ↓
Catálogo Ejercicios
   ↓
Rutina Generada
   ↓
Base de Datos
```

---

### Generación de Nutrición IA

```text
Cliente
   ↓
Peso
Estatura
Restricciones
   ↓
IA Nutrición
   ↓
Catálogo Comidas
   ↓
Plan Nutricional
   ↓
Base de Datos
```

---

## 7. Tecnologías Utilizadas

| Componente | Tecnología |
|------------|------------|
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Base de Datos | PostgreSQL |
| Frontend | React + Vite |
| Aplicación Móvil | Flutter |
| Seguridad | JWT |
| Contraseñas | Bcrypt |
| Multimedia | Cloudinary |
| IA | Python |

---

## 8. Beneficios de la Arquitectura

- Arquitectura modular.
- Fácil mantenimiento.
- Escalable.
- Preparada para SaaS.
- Compatible con Web y Móvil.
- Integración sencilla con IA.
- Integración multimedia desacoplada.
- Reutilización de servicios.
- Mayor seguridad mediante JWT.

---

## 9. Consideraciones Importantes

### Regla Principal

```text
usuarios = acceso al sistema
clientes = negocio del gimnasio
```

### Flujo Correcto

```text
login
  ↓
id_usuario
  ↓
GET /clientes/usuario/{id_usuario}
  ↓
id_cliente
  ↓
Procesos del gimnasio
```

### Procesos que utilizan id_cliente

- Membresías
- Pagos
- Asistencias
- Progreso
- Rutinas
- Nutrición

---

## 10. Estado Actual

### Implementado

- Backend FastAPI
- PostgreSQL
- React + Vite
- Flutter (base)
- JWT
- Cloudinary
- IA Rutinas
- IA Nutrición
- Dashboards por rol
- CRUDs principales

### Futuro

- SaaS Multi Gimnasio
- Docker
- Reportes PDF
- Notificaciones
- Métricas avanzadas
- Despliegue en nube

---