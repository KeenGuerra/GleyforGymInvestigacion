# ROLES Y PERMISOS

# SistemaGimnasioGleyforGym

## Introducción

El SistemaGimnasioGleyforGym implementa un modelo de control de acceso basado en roles (RBAC - Role Based Access Control).

Cada usuario posee un único rol que determina las funcionalidades a las que puede acceder dentro de la plataforma.

Roles definidos:

* ADMIN
* ENTRENADOR
* CLIENTE

---

# ROL ADMIN

## Descripción

Es el rol con mayor nivel de acceso dentro del sistema.

Tiene la responsabilidad de administrar la información general del gimnasio, gestionar usuarios y supervisar las operaciones.

---

## Funciones Principales

* Administrar usuarios.
* Administrar clientes.
* Administrar entrenadores.
* Administrar membresías.
* Asignar membresías.
* Registrar pagos.
* Registrar asistencias.
* Gestionar progreso físico.
* Gestionar ejercicios.
* Gestionar comidas.
* Generar rutinas mediante IA.
* Generar nutrición mediante IA.
* Consultar reportes.

---

# ROL ENTRENADOR

## Descripción

Responsable del seguimiento físico y deportivo de los clientes.

No posee acceso a la administración de usuarios ni configuración del sistema.

---

## Funciones Principales

* Consultar clientes.
* Registrar progreso físico.
* Gestionar ejercicios.
* Gestionar comidas.
* Generar rutinas IA.
* Generar nutrición IA.
* Registrar asistencias.
* Consultar información deportiva.

---

# ROL CLIENTE

## Descripción

Usuario final del gimnasio.

Su acceso está limitado exclusivamente a la consulta de su propia información.

---

## Funciones Principales

* Consultar perfil.
* Consultar rutina.
* Consultar plan nutricional.
* Consultar progreso físico.
* Consultar membresía.
* Consultar pagos.

---

# Matriz General de Permisos

| Módulo                | ADMIN | ENTRENADOR | CLIENTE             |
| --------------------- | ----- | ---------- | ------------------- |
| Dashboard             | Sí    | Sí         | Sí                  |
| Usuarios              | Sí    | No         | No                  |
| Clientes              | Sí    | Sí         | No                  |
| Detalle Cliente       | Sí    | Sí         | No                  |
| Membresías            | Sí    | No         | No                  |
| Cliente Membresías    | Sí    | No         | No                  |
| Pagos                 | Sí    | No         | Solo lectura propia |
| Asistencias           | Sí    | Sí         | Solo lectura propia |
| Progreso              | Sí    | Sí         | Solo lectura propia |
| Ejercicios            | Sí    | Sí         | No                  |
| Comidas               | Sí    | Sí         | No                  |
| Rutinas               | Sí    | Sí         | Solo lectura propia |
| Nutrición             | Sí    | Sí         | Solo lectura propia |
| Configuración Sistema | Sí    | No         | No                  |

---

# Permisos por Operación

## Gestión de Usuarios

| Acción    | ADMIN | ENTRENADOR | CLIENTE |
| --------- | ----- | ---------- | ------- |
| Crear     | Sí    | No         | No      |
| Consultar | Sí    | No         | No      |
| Editar    | Sí    | No         | No      |
| Eliminar  | Sí    | No         | No      |

---

## Gestión de Clientes

| Acción     | ADMIN | ENTRENADOR | CLIENTE |
| ---------- | ----- | ---------- | ------- |
| Crear      | Sí    | No         | No      |
| Consultar  | Sí    | Sí         | No      |
| Editar     | Sí    | Sí         | No      |
| Desactivar | Sí    | No         | No      |

---

## Gestión de Membresías

| Acción     | ADMIN | ENTRENADOR | CLIENTE |
| ---------- | ----- | ---------- | ------- |
| Crear      | Sí    | No         | No      |
| Editar     | Sí    | No         | No      |
| Desactivar | Sí    | No         | No      |
| Consultar  | Sí    | Sí         | Sí      |

---

## Gestión de Pagos

| Acción    | ADMIN | ENTRENADOR | CLIENTE      |
| --------- | ----- | ---------- | ------------ |
| Registrar | Sí    | No         | No           |
| Editar    | Sí    | No         | No           |
| Consultar | Sí    | No         | Solo propios |

---

## Gestión de Asistencias

| Acción    | ADMIN | ENTRENADOR | CLIENTE      |
| --------- | ----- | ---------- | ------------ |
| Registrar | Sí    | Sí         | No           |
| Consultar | Sí    | Sí         | Solo propias |

---

## Gestión de Progreso

| Acción    | ADMIN | ENTRENADOR | CLIENTE     |
| --------- | ----- | ---------- | ----------- |
| Registrar | Sí    | Sí         | No          |
| Editar    | Sí    | Sí         | No          |
| Consultar | Sí    | Sí         | Solo propio |

---

## Gestión de Ejercicios

| Acción     | ADMIN | ENTRENADOR | CLIENTE |
| ---------- | ----- | ---------- | ------- |
| Crear      | Sí    | Sí         | No      |
| Editar     | Sí    | Sí         | No      |
| Desactivar | Sí    | Sí         | No      |
| Consultar  | Sí    | Sí         | No      |

---

## Gestión de Comidas

| Acción     | ADMIN | ENTRENADOR | CLIENTE |
| ---------- | ----- | ---------- | ------- |
| Crear      | Sí    | Sí         | No      |
| Editar     | Sí    | Sí         | No      |
| Desactivar | Sí    | Sí         | No      |
| Consultar  | Sí    | Sí         | No      |

---

## Gestión de Rutinas

| Acción     | ADMIN | ENTRENADOR | CLIENTE     |
| ---------- | ----- | ---------- | ----------- |
| Generar IA | Sí    | Sí         | No          |
| Consultar  | Sí    | Sí         | Solo propia |
| Eliminar   | Sí    | Sí         | No          |

---

## Gestión Nutricional

| Acción     | ADMIN | ENTRENADOR | CLIENTE     |
| ---------- | ----- | ---------- | ----------- |
| Generar IA | Sí    | Sí         | No          |
| Consultar  | Sí    | Sí         | Solo propia |
| Eliminar   | Sí    | Sí         | No          |

---

# Restricciones de Seguridad

## RS-001

Los usuarios CLIENTE únicamente podrán acceder a información asociada a su propio id_cliente.

---

## RS-002

Los usuarios ENTRENADOR no podrán administrar usuarios del sistema.

---

## RS-003

Los usuarios ENTRENADOR no podrán asignar roles.

---

## RS-004

Los usuarios CLIENTE no podrán registrar información de otros clientes.

---

## RS-005

Los usuarios CLIENTE no podrán modificar pagos, membresías o rutinas.

---

## RS-006

Todas las operaciones protegidas requerirán un token JWT válido.

---

## RS-007

Las rutas protegidas deberán validar el rol antes de permitir el acceso.

---

# Correspondencia con Frontend

## ADMIN

Acceso permitido:

* DashboardAdmin
* Usuarios
* Clientes
* DetalleCliente
* Membresias
* ClienteMembresias
* Pagos
* Asistencias
* Progreso
* Ejercicios
* Comidas
* Rutinas
* DetalleRutina
* Nutricion

---

## ENTRENADOR

Acceso permitido:

* DashboardEntrenador
* Clientes
* DetalleCliente
* Asistencias
* Progreso
* Ejercicios
* Comidas
* Rutinas
* DetalleRutina
* Nutricion

---

## CLIENTE

Acceso permitido:

* DashboardCliente
* MiPerfil
* MiRutina
* MiNutricion
* MiProgreso
* MiMembresia
* MisPagos
* DetalleRutina

---

# Resumen

La seguridad del sistema se basa en:

1. Autenticación mediante JWT.
2. Control de acceso por roles.
3. Uso obligatorio de id_cliente para operaciones de negocio.
4. Restricción de acceso a información propia para clientes.
5. Validación de permisos tanto en frontend como en backend.
