# REQUERIMIENTOS NO FUNCIONALES

# SistemaGimnasioGleyforGym

## Introducción

Los requerimientos no funcionales describen las características de calidad que debe cumplir el SistemaGimnasioGleyforGym para garantizar un funcionamiento eficiente, seguro, escalable y mantenible.

Estos requerimientos se encuentran alineados con el modelo de calidad ISO/IEC 25010.

---

# 1. SEGURIDAD

## RNF-001 Autenticación obligatoria

El sistema deberá requerir autenticación para acceder a los módulos protegidos.

Prioridad: Alta.

---

## RNF-002 Uso de JWT

La autenticación deberá implementarse utilizando JSON Web Token (JWT).

Prioridad: Alta.

---

## RNF-003 Contraseñas encriptadas

Las contraseñas deberán almacenarse utilizando algoritmos de cifrado seguros mediante bcrypt.

Prioridad: Alta.

---

## RNF-004 Control de acceso por roles

El sistema deberá restringir funcionalidades según el rol asignado al usuario.

Roles:

* ADMIN
* ENTRENADOR
* CLIENTE

Prioridad: Alta.

---

## RNF-005 Protección de rutas

Todas las rutas protegidas deberán validar la autenticidad del token antes de procesar solicitudes.

Prioridad: Alta.

---

## RNF-006 Protección de datos personales

El sistema deberá proteger la información personal de los clientes contra accesos no autorizados.

Prioridad: Alta.

---

# 2. RENDIMIENTO

## RNF-007 Tiempo de respuesta

Las operaciones normales del sistema deberán responder en menos de 3 segundos.

Prioridad: Alta.

---

## RNF-008 Consultas optimizadas

Las consultas frecuentes deberán utilizar índices en la base de datos.

Prioridad: Alta.

---

## RNF-009 Manejo eficiente de recursos

El sistema deberá optimizar el uso de memoria y procesamiento para evitar degradación del servicio.

Prioridad: Media.

---

## RNF-010 Carga concurrente

El sistema deberá soportar múltiples usuarios conectados simultáneamente.

Prioridad: Media.

---

# 3. DISPONIBILIDAD

## RNF-011 Disponibilidad del sistema

La plataforma deberá estar disponible al menos el 99% del tiempo operativo.

Prioridad: Alta.

---

## RNF-012 Recuperación ante fallos

El sistema deberá permitir la recuperación de la información mediante copias de seguridad.

Prioridad: Alta.

---

## RNF-013 Integridad de datos

Las transacciones deberán preservar la consistencia de los datos almacenados.

Prioridad: Alta.

---

# 4. USABILIDAD

## RNF-014 Interfaz intuitiva

La interfaz deberá ser sencilla y comprensible para usuarios sin conocimientos técnicos.

Prioridad: Alta.

---

## RNF-015 Diseño responsivo

La interfaz web deberá adaptarse a diferentes tamaños de pantalla.

Prioridad: Alta.

---

## RNF-016 Navegación consistente

Todos los módulos deberán mantener una estructura visual uniforme.

Prioridad: Alta.

---

## RNF-017 Retroalimentación al usuario

El sistema deberá mostrar mensajes claros de éxito, advertencia y error.

Prioridad: Alta.

---

# 5. COMPATIBILIDAD

## RNF-018 Compatibilidad con navegadores modernos

El sistema web deberá funcionar correctamente en:

* Google Chrome
* Microsoft Edge
* Mozilla Firefox

Prioridad: Alta.

---

## RNF-019 Compatibilidad móvil

La aplicación Flutter deberá funcionar en dispositivos Android modernos.

Prioridad: Alta.

---

## RNF-020 Integración con PostgreSQL

El sistema deberá ser compatible con PostgreSQL como motor de base de datos principal.

Prioridad: Alta.

---

# 6. MANTENIBILIDAD

## RNF-021 Arquitectura modular

El sistema deberá estar organizado en módulos independientes para facilitar el mantenimiento.

Prioridad: Alta.

---

## RNF-022 Separación de responsabilidades

Backend, frontend, base de datos e inteligencia artificial deberán mantenerse desacoplados.

Prioridad: Alta.

---

## RNF-023 Código documentado

Los componentes críticos deberán incluir documentación técnica.

Prioridad: Media.

---

## RNF-024 Facilidad de actualización

El sistema deberá permitir agregar nuevos módulos sin afectar los existentes.

Prioridad: Alta.

---

# 7. ESCALABILIDAD

## RNF-025 Preparación para SaaS

La arquitectura deberá permitir evolucionar hacia un modelo SaaS multiempresa.

Prioridad: Alta.

---

## RNF-026 Escalabilidad horizontal

La aplicación deberá permitir futuras implementaciones distribuidas.

Prioridad: Media.

---

## RNF-027 Crecimiento de usuarios

El sistema deberá soportar el crecimiento progresivo de clientes y registros históricos.

Prioridad: Alta.

---

# 8. MULTIMEDIA

## RNF-028 Integración con Cloudinary

Los videos de ejercicios deberán almacenarse en Cloudinary.

Prioridad: Alta.

---

## RNF-029 Optimización multimedia

Los archivos multimedia deberán almacenarse externamente para reducir la carga de la base de datos.

Prioridad: Alta.

---

# 9. INTELIGENCIA ARTIFICIAL

## RNF-030 Uso de datos reales

Los módulos de inteligencia artificial deberán generar recomendaciones utilizando información real almacenada en la base de datos.

Prioridad: Alta.

---

# Resumen

El sistema deberá garantizar:

* Seguridad mediante JWT y bcrypt.
* Protección de información sensible.
* Disponibilidad continua.
* Buen rendimiento.
* Escalabilidad SaaS.
* Compatibilidad multiplataforma.
* Integración con Cloudinary.
* Arquitectura mantenible.
* Inteligencia artificial basada en datos reales.

Estos requerimientos complementan los requerimientos funcionales y definen la calidad esperada del SistemaGimnasioGleyforGym.
