# Registro de Decisiones de Arquitectura

# SistemaGimnasioGleyforGym

## Introducción

Este documento registra las decisiones arquitectónicas más importantes tomadas durante el desarrollo del SistemaGimnasioGleyforGym.

Su objetivo es conservar el contexto técnico detrás de cada decisión y evitar cambios que comprometan la estabilidad del sistema.

---

# DA-001

## Separar Usuarios y Clientes

### Fecha

Versión 1.0

### Decisión

Separar:

```text
usuarios
```

de

```text
clientes
```

---

### Justificación

Un usuario representa acceso al sistema.

Un cliente representa un socio real del gimnasio.

---

### Beneficios

- Separación de responsabilidades.
- Flexibilidad.
- Soporte para múltiples roles.

---

### Regla Crítica

```text
usuarios = acceso

clientes = negocio
```

---

# DA-002

## Utilizar id_cliente en Procesos del Gimnasio

### Fecha

Versión 1.0

### Decisión

Utilizar:

```text
id_cliente
```

para:

- Rutinas
- Nutrición
- Pagos
- Asistencias
- Progreso
- Membresías

---

### No utilizar

```text
id_usuario
```

---

### Justificación

El negocio gira alrededor del cliente.

---

# DA-003

## Selección de FastAPI

### Fecha

Versión 1.0

### Decisión

Backend implementado con:

```text
FastAPI
```

---

### Justificación

- Alto rendimiento.
- Swagger automático.
- Fácil integración con IA.
- Validación mediante Pydantic.

---

# DA-004

## Selección de PostgreSQL

### Fecha

Versión 1.0

### Decisión

Utilizar:

```text
PostgreSQL
```

---

### Justificación

- Relaciones complejas.
- Integridad referencial.
- Escalabilidad.

---

# DA-005

## Selección de React

### Fecha

Versión 1.0

### Decisión

Frontend desarrollado con:

```text
React + Vite
```

---

### Justificación

- Componentización.
- Rapidez.
- Amplio ecosistema.

---

# DA-006

## Selección de Flutter

### Fecha

Versión 1.5

### Decisión

Aplicación móvil desarrollada con:

```text
Flutter
```

---

### Justificación

- Código único.
- Android.
- iOS.
- Web.

---

# DA-007

## Implementación JWT

### Fecha

Versión 1.5

### Decisión

Autenticación mediante:

```text
JWT
```

---

### Justificación

- Stateless.
- Escalable.
- Compatible con Web y Flutter.

---

# DA-008

## Implementación Cloudinary

### Fecha

Versión 2.0

### Decisión

Videos almacenados en:

```text
Cloudinary
```

---

### Justificación

- Evitar almacenamiento local.
- Mejor rendimiento.
- CDN integrada.

---

# DA-009

## IA Basada en Reglas

### Fecha

Versión 2.0

### Decisión

La IA utiliza:

```text
Reglas de negocio
+
Selección inteligente
```

---

### Justificación

- Menor complejidad.
- Fácil mantenimiento.
- Resultados consistentes.

---

### Evolución Futura

```text
Machine Learning
Modelos Predictivos
```

---

# DA-010

## Precio Histórico de Membresías

### Fecha

Versión 2.0

### Decisión

Agregar:

```text
precio_asignado
```

en:

```text
cliente_membresias
```

---

### Justificación

Conservar el precio original contratado.

---

# DA-011

## Edad Automática

### Fecha

Versión 2.0

### Decisión

Calcular edad desde:

```text
fecha_nacimiento
```

---

### Justificación

Evitar inconsistencias.

---

# DA-012

## Estados de Membresía

### Fecha

Versión 2.0

### Decisión

Estados oficiales:

```text
ACTIVA
PAUSADA
TERMINADA
CANCELADA
```

---

### Eliminado

```text
VENCIDA
```

---

# DA-013

## Medidas Corporales Detalladas

### Fecha

Versión 2.0

### Decisión

Separar:

```text
Brazo Izquierdo
Brazo Derecho

Pierna Izquierda
Pierna Derecha
```

---

### Justificación

Mayor precisión en seguimiento físico.

---

# Estado

## Vigentes

✅ DA-001 a DA-013

---

## Próximas Decisiones

- Dockerización.
- SaaS Multi Gimnasio.
- Machine Learning.
- Multi Tenant.
- Microservicios.

---