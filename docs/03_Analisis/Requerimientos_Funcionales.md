# REQUERIMIENTOS FUNCIONALES

# SistemaGimnasioGleyforGym

## Introducción

Los requerimientos funcionales describen las acciones que el SistemaGimnasioGleyforGym debe permitir realizar a los usuarios según su rol dentro de la plataforma. Estos requerimientos están organizados por módulos para facilitar su análisis, desarrollo, validación y posterior prueba.

---

# MÓDULO 1: USUARIOS

## RF-001 Registrar usuario

El sistema deberá permitir al administrador registrar nuevos usuarios para acceder a la plataforma.

Entradas:

* Correo electrónico
* Contraseña
* Rol
* Estado

Proceso:

1. Validar que el correo no esté registrado.
2. Validar que la contraseña no esté vacía.
3. Encriptar la contraseña.
4. Registrar el usuario en la base de datos.

Salida:

* Usuario registrado correctamente.

Prioridad: Alta.

---

## RF-002 Validar correo único

El sistema deberá validar que no existan dos usuarios con el mismo correo electrónico.

Prioridad: Alta.

---

## RF-003 Encriptar contraseña

El sistema deberá almacenar las contraseñas usando un algoritmo de encriptación seguro.

Prioridad: Alta.

---

## RF-004 Iniciar sesión

El sistema deberá permitir que los usuarios inicien sesión mediante correo y contraseña.

Entradas:

* Correo electrónico
* Contraseña

Salida:

* Token JWT
* Datos del usuario
* Rol del usuario

Prioridad: Alta.

---

## RF-005 Validar credenciales

El sistema deberá validar que el correo y la contraseña ingresados sean correctos antes de permitir el acceso.

Prioridad: Alta.

---

## RF-006 Generar token JWT

El sistema deberá generar un token JWT cuando el inicio de sesión sea correcto.

Prioridad: Alta.

---

## RF-007 Guardar datos de sesión en frontend

El frontend deberá guardar en localStorage el token, rol, correo e id_usuario del usuario autenticado.

Prioridad: Alta.

---

## RF-008 Consultar usuarios

El sistema deberá permitir al administrador consultar la lista de usuarios registrados.

Prioridad: Alta.

---

## RF-009 Consultar usuario por ID

El sistema deberá permitir consultar la información de un usuario específico mediante id_usuario.

Prioridad: Media.

---

## RF-010 Actualizar usuario

El sistema deberá permitir al administrador modificar los datos de un usuario.

Prioridad: Alta.

---

## RF-011 Cambiar estado de usuario

El sistema deberá permitir activar o desactivar usuarios.

Estados válidos:

* ACTIVO
* INACTIVO

Prioridad: Alta.

---

## RF-012 Eliminar usuario

El sistema deberá permitir al administrador eliminar usuarios cuando corresponda.

Prioridad: Media.

---

## RF-013 Asignar rol a usuario

El sistema deberá permitir asignar un rol a cada usuario.

Roles válidos:

* ADMIN
* ENTRENADOR
* CLIENTE

Prioridad: Alta.

---

## RF-014 Validar acceso por rol

El sistema deberá permitir el acceso a módulos según el rol del usuario.

Prioridad: Alta.

---

## RF-015 Cerrar sesión

El frontend deberá permitir cerrar sesión eliminando los datos almacenados en localStorage.

Prioridad: Alta.

---

# MÓDULO 2: CLIENTES

## RF-016 Registrar cliente

El sistema deberá permitir registrar clientes del gimnasio.

Entradas:

* DNI
* Nombres
* Apellidos
* Contacto
* Fecha de nacimiento
* Sexo
* Dirección
* Objetivo
* Nivel
* Restricciones médicas
* Usuario asociado

Prioridad: Alta.

---

## RF-017 Validar DNI único

El sistema deberá validar que no existan dos clientes con el mismo DNI.

Prioridad: Alta.

---

## RF-018 Asociar cliente con usuario

El sistema deberá permitir asociar un cliente con un usuario de rol CLIENTE.

Prioridad: Alta.

---

## RF-019 Calcular edad automáticamente

El sistema deberá calcular la edad del cliente usando su fecha de nacimiento.

Prioridad: Alta.

---

## RF-020 Consultar clientes

El sistema deberá permitir consultar la lista de clientes registrados.

Prioridad: Alta.

---

## RF-021 Consultar cliente por ID

El sistema deberá permitir consultar la información de un cliente específico mediante id_cliente.

Prioridad: Alta.

---

## RF-022 Consultar cliente por usuario

El sistema deberá permitir obtener el cliente asociado a un usuario mediante id_usuario.

Ruta clave:

GET /clientes/usuario/{id_usuario}

Prioridad: Alta.

---

## RF-023 Actualizar cliente

El sistema deberá permitir actualizar la información personal y deportiva del cliente.

Prioridad: Alta.

---

## RF-024 Activar cliente

El sistema deberá permitir cambiar el estado de un cliente a ACTIVO.

Prioridad: Alta.

---

## RF-025 Desactivar cliente

El sistema deberá permitir cambiar el estado de un cliente a INACTIVO.

Prioridad: Alta.

---

## RF-026 Sincronizar estado cliente-usuario

Cuando un cliente sea activado o desactivado, el usuario asociado deberá actualizarse al mismo estado.

Prioridad: Alta.

---

## RF-027 Consultar detalle completo del cliente

El sistema deberá permitir consultar el detalle completo del cliente, incluyendo membresía, pagos, asistencias, progreso, rutinas y nutrición.

Prioridad: Alta.

---

## RF-028 Mostrar datos deportivos del cliente

El sistema deberá mostrar objetivo, nivel, peso, estatura y restricciones médicas cuando estén registrados.

Prioridad: Media.

---

## RF-029 Validar cliente activo

El sistema deberá validar que ciertos procesos solo se realicen para clientes activos.

Procesos afectados:

* Asistencias
* Membresías
* Rutinas
* Nutrición
* Progreso

Prioridad: Alta.

---

## RF-030 Buscar cliente

El sistema deberá permitir buscar clientes por nombres, apellidos o DNI.

Prioridad: Media.

---

## RF-031 Filtrar clientes por estado

El sistema deberá permitir filtrar clientes por estado ACTIVO o INACTIVO.

Prioridad: Media.

---

## RF-032 Mostrar historial del cliente

El sistema deberá permitir visualizar el historial relacionado al cliente.

Incluye:

* Membresías
* Pagos
* Asistencias
* Progreso
* Rutinas
* Nutrición

Prioridad: Alta.

---

## RF-033 Mostrar perfil del cliente autenticado

El sistema deberá permitir que el cliente visualice su propio perfil.

Prioridad: Alta.

---

## RF-034 Restringir acceso a otros clientes

El sistema deberá impedir que un usuario CLIENTE consulte información de otros clientes.

Prioridad: Alta.

---

## RF-035 Mantener integridad del cliente

El sistema deberá evitar eliminar información relacionada al cliente si existen registros históricos importantes.

Prioridad: Alta.

---

# MÓDULO 3: MEMBRESÍAS

## RF-036 Registrar membresía

El sistema deberá permitir registrar nuevos planes de membresía.

Entradas:

* Nombre
* Descripción
* Duración en días
* Precio
* Beneficios
* Estado

Prioridad: Alta.

---

## RF-037 Validar duración de membresía

El sistema deberá validar que la duración de la membresía sea mayor que cero.

Prioridad: Alta.

---

## RF-038 Validar precio de membresía

El sistema deberá validar que el precio de la membresía sea mayor que cero.

Prioridad: Alta.

---

## RF-039 Consultar membresías

El sistema deberá permitir consultar las membresías registradas.

Prioridad: Alta.

---

## RF-040 Consultar membresías activas

El sistema deberá permitir mostrar únicamente las membresías activas en la landing pública.

Prioridad: Alta.

---

## RF-041 Consultar membresía por ID

El sistema deberá permitir consultar una membresía específica mediante id_membresia.

Prioridad: Media.

---

## RF-042 Actualizar membresía

El sistema deberá permitir actualizar los datos de una membresía.

Prioridad: Alta.

---

## RF-043 Activar membresía

El sistema deberá permitir activar una membresía previamente desactivada.

Prioridad: Media.

---

## RF-044 Desactivar membresía

El sistema deberá permitir desactivar una membresía que ya no se ofrece.

Prioridad: Media.

---

## RF-045 Gestionar beneficios de membresía

El sistema deberá permitir registrar y modificar beneficios de cada membresía.

Prioridad: Alta.

---

## RF-046 Mostrar beneficios de membresía

El sistema deberá mostrar los beneficios de cada membresía en el frontend.

Prioridad: Alta.

---

## RF-047 Mostrar membresías en landing

El sistema deberá mostrar los planes activos en la página de inicio pública.

Prioridad: Alta.

---

## RF-048 Evitar eliminación de membresías asignadas

El sistema deberá evitar eliminar membresías que ya estén asociadas a clientes, salvo que se use desactivación lógica.

Prioridad: Alta.

---

## RF-049 Mantener historial de membresías

El sistema deberá conservar el historial de membresías asignadas a los clientes.

Prioridad: Alta.

---

## RF-050 Permitir consulta de membresías por roles

El sistema deberá permitir que ADMIN, ENTRENADOR y CLIENTE consulten información básica de membresías según sus permisos.

Prioridad: Media.


# REQUERIMIENTOS FUNCIONALES

# PARTE 2

---

# MÓDULO 4: CLIENTE MEMBRESÍAS

## RF-051 Asignar membresía a cliente

El sistema deberá permitir asignar una membresía a un cliente registrado.

Prioridad: Alta.

---

## RF-052 Seleccionar cliente

El sistema deberá permitir seleccionar un cliente existente para asignarle una membresía.

Prioridad: Alta.

---

## RF-053 Seleccionar plan

El sistema deberá permitir seleccionar una membresía existente al momento de realizar una asignación.

Prioridad: Alta.

---

## RF-054 Calcular fecha inicio

El sistema deberá establecer automáticamente la fecha actual como fecha de inicio de la membresía.

Prioridad: Alta.

---

## RF-055 Calcular fecha fin

El sistema deberá calcular automáticamente la fecha de finalización utilizando la duración de la membresía seleccionada.

Fórmula:

Fecha Fin = Fecha Inicio + Duración del Plan

Prioridad: Alta.

---

## RF-056 Registrar precio asignado

El sistema deberá almacenar el precio vigente de la membresía en el campo precio_asignado al momento de la asignación.

Prioridad: Alta.

---

## RF-057 Mantener precio histórico

Los cambios futuros en el precio de la membresía no deberán afectar asignaciones ya realizadas.

Prioridad: Alta.

---

## RF-058 Consultar membresías asignadas

El sistema deberá permitir consultar todas las membresías asignadas a los clientes.

Prioridad: Alta.

---

## RF-059 Consultar membresías por cliente

El sistema deberá permitir consultar las membresías asociadas a un cliente específico.

Prioridad: Alta.

---

## RF-060 Actualizar estado de membresía

El sistema deberá permitir modificar el estado de una membresía asignada.

Estados válidos:

* ACTIVA
* PAUSADA
* TERMINADA
* CANCELADA

Prioridad: Alta.

---

## RF-061 Pausar membresía

El sistema deberá permitir pausar temporalmente una membresía.

Prioridad: Alta.

---

## RF-062 Reactivar membresía

El sistema deberá permitir reactivar una membresía previamente pausada.

Prioridad: Alta.

---

## RF-063 Cancelar membresía

El sistema deberá permitir cancelar una membresía asignada.

Prioridad: Media.

---

## RF-064 Finalizar membresía automáticamente

El sistema deberá cambiar automáticamente el estado de la membresía a TERMINADA cuando la fecha actual supere la fecha fin.

Prioridad: Alta.

---

## RF-065 Mostrar membresía actual del cliente

El sistema deberá permitir que el cliente visualice su membresía activa, incluyendo precio_asignado y estado.

Prioridad: Alta.

---

# MÓDULO 5: PAGOS

## RF-066 Registrar pago

El sistema deberá permitir registrar pagos asociados a una membresía asignada.

Prioridad: Alta.

---

## RF-067 Asociar pago a cliente

Todo pago deberá estar asociado a un cliente existente.

Prioridad: Alta.

---

## RF-068 Asociar pago a membresía

Todo pago deberá estar asociado a una membresía asignada.

Prioridad: Alta.

---

## RF-069 Registrar método de pago

El sistema deberá permitir registrar el método de pago utilizado.

Ejemplos:

* Efectivo
* Transferencia
* Yape
* Plin

Prioridad: Media.

---

## RF-070 Registrar observaciones

El sistema deberá permitir registrar observaciones relacionadas al pago.

Prioridad: Baja.

---

## RF-071 Consultar pagos

El sistema deberá permitir consultar todos los pagos registrados.

Prioridad: Alta.

---

## RF-072 Consultar pagos por cliente

El sistema deberá permitir consultar los pagos asociados a un cliente específico.

Prioridad: Alta.

---

## RF-073 Consultar historial de pagos

El sistema deberá mostrar el historial completo de pagos realizados por un cliente.

Prioridad: Alta.

---

## RF-074 Validar monto positivo

El sistema deberá validar que el monto ingresado sea mayor que cero.

Prioridad: Alta.

---

## RF-075 Modificar pago

El sistema deberá permitir actualizar la información de un pago.

Prioridad: Media.

---

## RF-076 Eliminar pago

El sistema deberá permitir eliminar registros de pago cuando corresponda.

Prioridad: Media.

---

## RF-077 Mostrar pagos al cliente

El sistema deberá permitir que el cliente visualice únicamente sus propios pagos.

Prioridad: Alta.

---

## RF-078 Restringir pagos de otros clientes

El sistema deberá impedir que un cliente consulte pagos pertenecientes a otros clientes.

Prioridad: Alta.

---

## RF-079 Mostrar estado de pago

El sistema deberá permitir visualizar el estado actual de cada pago registrado.

Prioridad: Media.

---

## RF-080 Generar historial financiero

El sistema deberá mantener un historial financiero completo de los pagos registrados.

Prioridad: Alta.

---

# MÓDULO 6: ASISTENCIAS

## RF-081 Registrar asistencia

El sistema deberá permitir registrar asistencias de clientes al gimnasio.

Prioridad: Alta.

---

## RF-082 Registrar fecha de asistencia

El sistema deberá almacenar automáticamente la fecha de asistencia.

Prioridad: Alta.

---

## RF-083 Registrar hora de ingreso

El sistema deberá registrar la hora de ingreso del cliente.

Prioridad: Alta.

---

## RF-084 Registrar hora de salida

El sistema deberá permitir registrar la hora de salida del cliente.

Prioridad: Media.

---

## RF-085 Asociar asistencia a cliente

Toda asistencia deberá estar asociada a un cliente registrado.

Prioridad: Alta.

---

## RF-086 Consultar asistencias

El sistema deberá permitir consultar todas las asistencias registradas.

Prioridad: Alta.

---

## RF-087 Consultar asistencias por cliente

El sistema deberá permitir consultar las asistencias de un cliente específico.

Prioridad: Alta.

---

## RF-088 Consultar historial de asistencias

El sistema deberá mostrar el historial completo de asistencias de un cliente.

Prioridad: Alta.

---

## RF-089 Mostrar asistencias al cliente

El sistema deberá permitir que el cliente visualice únicamente sus propias asistencias.

Prioridad: Alta.

---

## RF-090 Mantener historial de asistencias

El sistema deberá conservar los registros históricos de asistencia para análisis futuros.

Prioridad: Alta.


# REQUERIMIENTOS FUNCIONALES

# PARTE 3

---

# MÓDULO 7: PROGRESO FÍSICO

## RF-091 Registrar progreso físico

El sistema deberá permitir registrar información relacionada con la evolución física de un cliente.

Prioridad: Alta.

---

## RF-092 Asociar progreso a cliente

Todo registro de progreso deberá estar asociado a un cliente existente.

Prioridad: Alta.

---

## RF-093 Registrar peso

El sistema deberá permitir registrar el peso corporal del cliente.

Prioridad: Alta.

---

## RF-094 Registrar porcentaje de grasa

El sistema deberá permitir registrar el porcentaje de grasa corporal.

Prioridad: Alta.

---

## RF-095 Registrar masa grasa

El sistema deberá permitir registrar la masa grasa corporal.

Prioridad: Media.

---

## RF-096 Registrar masa magra

El sistema deberá permitir registrar la masa magra corporal.

Prioridad: Media.

---

## RF-097 Registrar medida de pecho

El sistema deberá permitir registrar la medida del pecho.

Prioridad: Alta.

---

## RF-098 Registrar medida de cintura

El sistema deberá permitir registrar la medida de la cintura.

Prioridad: Alta.

---

## RF-099 Registrar brazo izquierdo

El sistema deberá permitir registrar la medida del brazo izquierdo.

Prioridad: Alta.

---

## RF-100 Registrar brazo derecho

El sistema deberá permitir registrar la medida del brazo derecho.

Prioridad: Alta.

---

## RF-101 Registrar pierna izquierda

El sistema deberá permitir registrar la medida de la pierna izquierda.

Prioridad: Alta.

---

## RF-102 Registrar pierna derecha

El sistema deberá permitir registrar la medida de la pierna derecha.

Prioridad: Alta.

---

## RF-103 Registrar observaciones

El sistema deberá permitir registrar observaciones relacionadas con la evaluación física.

Prioridad: Media.

---

## RF-104 Registrar fecha de evaluación

El sistema deberá almacenar automáticamente la fecha del registro de progreso.

Prioridad: Alta.

---

## RF-105 Consultar progreso físico

El sistema deberá permitir consultar los registros de progreso físico de un cliente.

Prioridad: Alta.

---

## RF-106 Consultar historial de progreso

El sistema deberá mostrar el historial cronológico completo de registros físicos.

Prioridad: Alta.

---

## RF-107 Actualizar registro de progreso

El sistema deberá permitir actualizar registros de progreso previamente almacenados.

Prioridad: Media.

---

## RF-108 Eliminar registro de progreso

El sistema deberá permitir eliminar registros de progreso cuando corresponda.

Prioridad: Baja.

---

## RF-109 Mostrar progreso al cliente

El sistema deberá permitir que el cliente visualice únicamente sus propios registros de progreso.

Prioridad: Alta.

---

## RF-110 Generar análisis histórico

El sistema deberá permitir analizar la evolución física del cliente mediante registros históricos.

Prioridad: Media.

---

# MÓDULO 8: EJERCICIOS

## RF-111 Registrar ejercicio

El sistema deberá permitir registrar ejercicios dentro del catálogo general.

Prioridad: Alta.

---

## RF-112 Registrar grupo muscular

El sistema deberá permitir asociar cada ejercicio a un grupo muscular.

Ejemplos:

* Pecho
* Espalda
* Piernas
* Hombros
* Bíceps
* Tríceps
* Abdomen

Prioridad: Alta.

---

## RF-113 Registrar nivel del ejercicio

El sistema deberá permitir definir el nivel recomendado del ejercicio.

Valores posibles:

* PRINCIPIANTE
* INTERMEDIO
* AVANZADO

Prioridad: Media.

---

## RF-114 Registrar objetivo del ejercicio

El sistema deberá permitir definir el objetivo principal del ejercicio.

Ejemplos:

* Fuerza
* Hipertrofia
* Resistencia
* Pérdida de grasa

Prioridad: Alta.

---

## RF-115 Registrar descripción

El sistema deberá permitir registrar una descripción general del ejercicio.

Prioridad: Media.

---

## RF-116 Registrar instrucciones

El sistema deberá permitir registrar instrucciones detalladas de ejecución.

Prioridad: Alta.

---

## RF-117 Subir video de ejercicio

El sistema deberá permitir subir videos asociados al ejercicio.

Prioridad: Alta.

---

## RF-118 Almacenar video en Cloudinary

Los videos deberán almacenarse en Cloudinary.

Prioridad: Alta.

---

## RF-119 Guardar URL del video

El sistema deberá almacenar únicamente la URL y el identificador del recurso multimedia.

Prioridad: Alta.

---

## RF-120 Consultar ejercicios

El sistema deberá permitir consultar todos los ejercicios registrados.

Prioridad: Alta.

---

## RF-121 Consultar ejercicio por ID

El sistema deberá permitir consultar un ejercicio específico mediante su identificador.

Prioridad: Alta.

---

## RF-122 Actualizar ejercicio

El sistema deberá permitir modificar la información de un ejercicio.

Prioridad: Alta.

---

## RF-123 Activar ejercicio

El sistema deberá permitir activar ejercicios.

Prioridad: Media.

---

## RF-124 Desactivar ejercicio

El sistema deberá permitir desactivar ejercicios.

Prioridad: Media.

---

## RF-125 Utilizar ejercicios activos en IA

La inteligencia artificial únicamente podrá utilizar ejercicios con estado ACTIVO.

Prioridad: Alta.

---

# MÓDULO 9: COMIDAS

## RF-126 Registrar comida

El sistema deberá permitir registrar alimentos y comidas dentro del catálogo nutricional.

Prioridad: Alta.

---

## RF-127 Registrar tipo de comida

El sistema deberá permitir clasificar la comida según su momento de consumo.

Valores:

* DESAYUNO
* MEDIA MAÑANA
* ALMUERZO
* MERIENDA
* CENA

Prioridad: Alta.

---

## RF-128 Registrar calorías

El sistema deberá permitir registrar las calorías aproximadas de cada comida.

Prioridad: Alta.

---

## RF-129 Registrar proteínas

El sistema deberá permitir registrar la cantidad de proteínas.

Prioridad: Alta.

---

## RF-130 Registrar carbohidratos

El sistema deberá permitir registrar la cantidad de carbohidratos.

Prioridad: Alta.

---

## RF-131 Registrar grasas

El sistema deberá permitir registrar la cantidad de grasas.

Prioridad: Alta.

---

## RF-132 Consultar comidas

El sistema deberá permitir consultar el catálogo nutricional.

Prioridad: Alta.

---

## RF-133 Actualizar comida

El sistema deberá permitir modificar la información de una comida.

Prioridad: Alta.

---

## RF-134 Activar o desactivar comida

El sistema deberá permitir activar o desactivar comidas del catálogo.

Prioridad: Media.

---

## RF-135 Utilizar comidas activas en IA

La inteligencia artificial nutricional únicamente podrá utilizar comidas que se encuentren activas.

Prioridad: Alta.


# REQUERIMIENTOS FUNCIONALES

# PARTE 4

---

# MÓDULO 10: RUTINAS IA

## RF-136 Generar rutina mediante IA

El sistema deberá generar rutinas personalizadas utilizando inteligencia artificial.

Prioridad: Alta.

---

## RF-137 Analizar objetivo del cliente

La inteligencia artificial deberá analizar el objetivo registrado del cliente para construir la rutina.

Ejemplos:

* Ganar masa muscular
* Perder grasa
* Mejorar resistencia
* Mantener condición física

Prioridad: Alta.

---

## RF-138 Analizar nivel del cliente

La inteligencia artificial deberá considerar el nivel físico registrado.

Valores:

* PRINCIPIANTE
* INTERMEDIO
* AVANZADO

Prioridad: Alta.

---

## RF-139 Analizar datos físicos

La inteligencia artificial deberá utilizar los datos físicos registrados para generar recomendaciones.

Prioridad: Alta.

---

## RF-140 Seleccionar ejercicios activos

La inteligencia artificial deberá seleccionar únicamente ejercicios con estado ACTIVO.

Prioridad: Alta.

---

## RF-141 Generar estructura semanal

El sistema deberá generar una distribución semanal de entrenamiento.

Prioridad: Alta.

---

## RF-142 Asignar series y repeticiones

La inteligencia artificial deberá definir series, repeticiones y descansos para cada ejercicio.

Prioridad: Alta.

---

## RF-143 Registrar rutina generada

El sistema deberá almacenar la rutina generada en la base de datos.

Prioridad: Alta.

---

## RF-144 Consultar rutina por cliente

El sistema deberá permitir consultar las rutinas asociadas a un cliente específico.

Prioridad: Alta.

---

## RF-145 Mostrar rutina al cliente

El sistema deberá permitir que el cliente visualice su rutina personalizada.

Prioridad: Alta.

---

# MÓDULO 11: NUTRICIÓN IA

## RF-146 Generar plan nutricional mediante IA

El sistema deberá generar planes nutricionales personalizados utilizando inteligencia artificial.

Prioridad: Alta.

---

## RF-147 Analizar peso y estatura

La inteligencia artificial deberá utilizar peso y estatura para calcular requerimientos nutricionales.

Prioridad: Alta.

---

## RF-148 Analizar objetivo nutricional

La inteligencia artificial deberá considerar el objetivo físico registrado del cliente.

Prioridad: Alta.

---

## RF-149 Analizar restricciones médicas

La inteligencia artificial deberá considerar restricciones médicas registradas.

Prioridad: Alta.

---

## RF-150 Seleccionar comidas activas

La inteligencia artificial deberá utilizar únicamente comidas activas del catálogo.

Prioridad: Alta.

---

## RF-151 Calcular requerimientos nutricionales

El sistema deberá calcular calorías, proteínas, carbohidratos y grasas recomendadas.

Prioridad: Alta.

---

## RF-152 Generar distribución de comidas

El sistema deberá generar una distribución diaria de comidas.

Prioridad: Alta.

---

## RF-153 Registrar plan nutricional

El sistema deberá almacenar el plan nutricional generado.

Prioridad: Alta.

---

## RF-154 Consultar nutrición por cliente

El sistema deberá permitir consultar los planes nutricionales asociados a un cliente.

Prioridad: Alta.

---

## RF-155 Mostrar nutrición al cliente

El sistema deberá permitir que el cliente visualice su plan nutricional personalizado.

Prioridad: Alta.

---

# MÓDULO 12: SEGURIDAD Y CONTROL DE ACCESO

## RF-156 Autenticar usuarios

El sistema deberá autenticar usuarios mediante correo y contraseña.

Prioridad: Alta.

---

## RF-157 Generar token JWT

El sistema deberá generar un token JWT después de una autenticación exitosa.

Prioridad: Alta.

---

## RF-158 Validar token JWT

El backend deberá validar el token JWT en todas las rutas protegidas.

Prioridad: Alta.

---

## RF-159 Restringir acceso por rol

El sistema deberá restringir el acceso a módulos según el rol del usuario.

Prioridad: Alta.

---

## RF-160 Proteger rutas frontend

El frontend deberá impedir el acceso a rutas no autorizadas.

Prioridad: Alta.

---

## RF-161 Validar sesión activa

El sistema deberá verificar la validez de la sesión antes de permitir operaciones protegidas.

Prioridad: Alta.

---

## RF-162 Cerrar sesión

El sistema deberá permitir finalizar la sesión del usuario.

Prioridad: Alta.

---

## RF-163 Registrar permisos por rol

El sistema deberá asociar permisos específicos a cada rol.

Prioridad: Alta.

---

## RF-164 Impedir acceso no autorizado

El sistema deberá bloquear accesos no autorizados a recursos protegidos.

Prioridad: Alta.

---

## RF-165 Mantener trazabilidad de accesos

El sistema deberá permitir conservar información relacionada con los accesos al sistema.

Prioridad: Media.

---

# MÓDULO 13: DASHBOARD Y REPORTES

## RF-166 Mostrar dashboard administrativo

El sistema deberá mostrar un panel principal para administradores.

Prioridad: Alta.

---

## RF-167 Mostrar dashboard entrenador

El sistema deberá mostrar un panel principal para entrenadores.

Prioridad: Alta.

---

## RF-168 Mostrar dashboard cliente

El sistema deberá mostrar un panel principal para clientes.

Prioridad: Alta.

---

## RF-169 Mostrar indicadores generales

El dashboard deberá mostrar indicadores relevantes para cada rol.

Prioridad: Alta.

---

## RF-170 Mostrar cantidad de clientes

El sistema deberá mostrar el total de clientes registrados.

Prioridad: Media.

---

## RF-171 Mostrar membresías activas

El sistema deberá mostrar el número de membresías activas.

Prioridad: Media.

---

## RF-172 Mostrar estadísticas de pagos

El sistema deberá mostrar información relacionada con pagos registrados.

Prioridad: Media.

---

## RF-173 Mostrar estadísticas de asistencias

El sistema deberá mostrar información relacionada con asistencias registradas.

Prioridad: Media.

---

## RF-174 Mostrar progreso general

El sistema deberá permitir visualizar indicadores relacionados con el progreso físico de los clientes.

Prioridad: Media.

---

## RF-175 Generar reportes operativos

El sistema deberá permitir generar reportes para apoyar la toma de decisiones.

Prioridad: Media.
