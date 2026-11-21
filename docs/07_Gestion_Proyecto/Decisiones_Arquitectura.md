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

# DA-014

## Zona Horaria Fija en vez de `zoneinfo`

### Fecha

2026-11 (sexta iteración de consolidación)

### Decisión

Se detectó que el backend calculaba "hoy"/"ahora" con `date.today()`/`datetime.now()` sin zona horaria (hora del servidor, UTC en Render) y el frontend con `new Date().toISOString()` (siempre UTC), lo que adelantaba un día cualquier fecha calculada en la noche de Perú. Se centralizó el cálculo en un módulo nuevo, `backend/app/zona_horaria.py` (`hoy()`/`ahora()`), y en una función nueva del frontend, `obtenerFechaLocalISO()`.

Se usa un offset fijo (`timezone(timedelta(hours=-5))`) en vez de `zoneinfo.ZoneInfo("America/Lima")`, a propósito: Perú no tiene horario de verano, así que el offset nunca cambia, y esto evita depender de que el sistema operativo tenga instalada la base de datos de husos horarios IANA (en Windows no viene por defecto y rompe `ZoneInfo` con `ZoneInfoNotFoundError` si falta el paquete `tzdata`).

El primer reemplazo cubrió `date.today()`/`datetime.now()` dentro de las funciones de `app/routes/`, pero no los *defaults* de columna de `app/models.py` (`Column(DateTime, default=datetime.now)`, 21 columnas, entre ellas `Venta.fecha_venta`): esa llamada se ejecuta al insertar, con el reloj del servidor, sin pasar por ninguna función de ruta. El hueco no se notó en pruebas locales (la hora de la máquina coincide con la de Perú lo bastante seguido) y recién se manifestó en GitHub Actions (UTC) como una corrida de CI fallida entre las ~19:00 y medianoche hora de Perú; se corrigió reemplazando esos `default`/`onupdate` por `zona_horaria.ahora`, y se agregaron las pruebas correspondientes en `test_backend.py`/`test_comercio.py` (que antes construían sus propias fechas de referencia con `date.today()`/`datetime.now()`, con el mismo problema).

---

### Justificación

Un offset fijo es correcto para Perú específicamente y no introduce una dependencia nueva (`tzdata`) ni un comportamiento distinto entre el entorno de desarrollo (Windows) y producción (Render, Linux).

---

# DA-015

## Configuración del Sitio como Fila Única

### Fecha

2026-11 (sexta iteración de consolidación)

### Decisión

Los datos de contacto, redes sociales, mapa y logo del gimnasio, antes escritos directamente en el código del frontend, pasan a una tabla propia (`configuracion_sitio`) con una única fila (`id=1`), siguiendo el mismo patrón "obtener o crear" ya usado para los avisos sembrados (`seed_avisos_iniciales`).

---

### Justificación

El gimnasio es una sola entidad de negocio: no hay necesidad de modelar varias configuraciones, y una fila única simplifica tanto el backend (`GET`/`PUT /configuracion/` sin identificador en la URL) como el frontend (un solo formulario, sin selector).

---

# Estado

## Vigentes

✅ DA-001 a DA-015

---

## Próximas Decisiones

- Dockerización.
- SaaS Multi Gimnasio.
- Machine Learning.
- Multi Tenant.
- Microservicios.

---