# REGLAS DE NEGOCIO

# SistemaGimnasioGleyforGym

## Introducción

Las reglas de negocio establecen las restricciones, políticas y condiciones que deben cumplirse dentro del SistemaGimnasioGleyforGym para garantizar la integridad de la información, la correcta ejecución de los procesos y el cumplimiento de los objetivos del gimnasio.

---

# RN-001 Separación entre Usuarios y Clientes

Los usuarios representan las credenciales de acceso al sistema.

Los clientes representan a las personas reales que reciben los servicios del gimnasio.

Un usuario no necesariamente debe ser cliente.

Ejemplos:

* Un administrador posee usuario pero no cliente.
* Un entrenador posee usuario pero no cliente.
* Un cliente posee usuario y cliente.

---

# RN-002 Uso obligatorio de id_cliente

Todos los procesos operativos y deportivos del gimnasio deben utilizar el identificador del cliente.

Se prohíbe utilizar id_usuario para procesos de negocio.

Procesos afectados:

* Membresías
* Pagos
* Asistencias
* Progreso físico
* Rutinas
* Nutrición

---

# RN-003 Relación Usuario-Cliente

Un cliente puede estar asociado a un único usuario.

Un usuario puede estar asociado como máximo a un cliente.

Relación:

1 usuario ↔ 1 cliente

---

# RN-004 Correo único

No pueden existir dos usuarios registrados con el mismo correo electrónico.

---

# RN-005 DNI único

No pueden existir dos clientes registrados con el mismo número de documento de identidad.

---

# RN-006 Cálculo automático de edad

La edad no debe ser ingresada manualmente.

La edad será calculada automáticamente a partir de la fecha de nacimiento registrada.

---

# RN-007 Fecha de nacimiento obligatoria

Todo cliente debe registrar una fecha de nacimiento válida para permitir el cálculo automático de edad.

---

# RN-008 Sincronización de estados

Cuando un cliente cambia a estado INACTIVO, el usuario asociado también deberá cambiar automáticamente a estado INACTIVO.

Cuando un cliente cambia a estado ACTIVO, el usuario asociado también deberá cambiar automáticamente a estado ACTIVO.

---

# RN-009 Estados válidos de usuario

Los únicos estados válidos para los usuarios son:

* ACTIVO
* INACTIVO

---

# RN-010 Estados válidos de cliente

Los únicos estados válidos para los clientes son:

* ACTIVO
* INACTIVO

---

# RN-011 Gestión de membresías

Las membresías representan los planes ofrecidos por el gimnasio.

Una membresía puede ser asignada a múltiples clientes.

---

# RN-012 Duración obligatoria

Toda membresía debe poseer una duración expresada en días.

La duración debe ser mayor que cero.

---

# RN-013 Precio obligatorio

Toda membresía debe poseer un precio mayor a cero.

---

# RN-014 Beneficios de membresía

Cada membresía podrá contener una lista de beneficios descriptivos.

Los beneficios son informativos para el cliente.

---

# RN-015 Precio congelado

Cuando una membresía es asignada a un cliente, el precio vigente del plan deberá almacenarse en el campo precio_asignado.

Posteriores modificaciones al precio del plan no deberán afectar asignaciones anteriores.

---

# RN-016 Fecha inicio automática

Al asignar una membresía, la fecha de inicio deberá establecerse automáticamente con la fecha actual del sistema.

---

# RN-017 Fecha fin automática

La fecha fin deberá calcularse automáticamente utilizando:

fecha_inicio + duración_días

---

# RN-018 Estados válidos de membresía asignada

Los únicos estados válidos son:

* ACTIVA
* PAUSADA
* TERMINADA
* CANCELADA

---

# RN-019 Estado TERMINADA

Una membresía deberá cambiar automáticamente a estado TERMINADA cuando la fecha actual supere la fecha fin registrada.

---

# RN-020 Estado PAUSADA

Una membresía podrá ser pausada temporalmente por un administrador.

---

# RN-021 Registro obligatorio de pagos

Todo pago deberá estar asociado a una membresía asignada.

---

# RN-022 Monto positivo

El monto registrado en un pago deberá ser mayor que cero.

---

# RN-023 Registro de asistencias

Las asistencias únicamente podrán registrarse para clientes activos.

---

# RN-024 Historial de asistencias

Las asistencias registradas no deberán eliminarse físicamente para preservar el historial del cliente.

---

# RN-025 Registro de progreso físico

Todo registro de progreso deberá estar asociado a un cliente existente.

---

# RN-026 Medidas corporales

El sistema deberá almacenar las medidas corporales por lado para mejorar la precisión del seguimiento físico.

Campos:

* medida_brazo_izquierdo
* medida_brazo_derecho
* medida_pierna_izquierda
* medida_pierna_derecha

---

# RN-027 Historial de progreso

Los registros de progreso físico deberán conservarse para permitir análisis históricos.

---

# RN-028 Gestión de ejercicios

Los ejercicios registrados conforman el catálogo oficial utilizado por la inteligencia artificial para generar rutinas.

---

# RN-029 Video de ejercicios

Los videos de ejercicios deberán almacenarse en Cloudinary.

La base de datos únicamente almacenará:

* video_url
* cloudinary_public_id

---

# RN-030 Ejercicios activos

La inteligencia artificial solo podrá utilizar ejercicios que se encuentren en estado ACTIVO.

---

# RN-031 Gestión de comidas

Las comidas registradas conforman el catálogo oficial utilizado por la inteligencia artificial nutricional.

---

# RN-032 Comidas activas

La inteligencia artificial solo podrá utilizar comidas que se encuentren en estado ACTIVO.

---

# RN-033 Generación de rutinas mediante IA

Las rutinas deberán generarse utilizando:

* Objetivo del cliente.
* Nivel del cliente.
* Datos físicos registrados.
* Catálogo de ejercicios.

---

# RN-034 Cliente obligatorio para IA de rutinas

No podrá generarse una rutina para un cliente inexistente.

---

# RN-035 Generación de nutrición mediante IA

Los planes nutricionales deberán generarse utilizando:

* Objetivo.
* Peso.
* Estatura.
* Restricciones médicas.
* Catálogo de comidas.

---

# RN-036 Cliente obligatorio para IA nutricional

No podrá generarse un plan nutricional para un cliente inexistente.

---

# RN-037 Seguridad mediante JWT

Todos los módulos protegidos deberán requerir autenticación mediante JWT.

---

# RN-038 Control de acceso por roles

El acceso a funcionalidades deberá estar restringido según el rol del usuario.

Roles:

* ADMIN
* ENTRENADOR
* CLIENTE

---

# RN-039 Registro de auditoría lógica

Las operaciones críticas deberán conservar la trazabilidad de los datos para permitir auditorías futuras.

---

# RN-040 Escalabilidad SaaS

La arquitectura del sistema deberá permitir futuras adaptaciones para operar bajo un modelo SaaS orientado a múltiples gimnasios.

---

# Resumen de Reglas Críticas

Las reglas más importantes del sistema son:

1. usuarios ≠ clientes
2. Todo proceso utiliza id_cliente
3. Edad calculada automáticamente
4. Precio congelado mediante precio_asignado
5. Estados válidos de membresía controlados
6. Rutinas IA basadas en ejercicios activos
7. Nutrición IA basada en comidas activas
8. Seguridad mediante JWT
9. Control de acceso por roles
10. Preparación para arquitectura SaaS
