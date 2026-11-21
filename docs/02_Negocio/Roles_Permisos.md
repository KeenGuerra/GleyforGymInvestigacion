# ROLES Y PERMISOS

# SistemaGimnasioGleyforGym

## Introducción

El SistemaGimnasioGleyforGym implementa un modelo de control de acceso basado en roles (RBAC - Role Based Access Control).

Cada usuario posee un único rol que determina las funcionalidades a las que puede acceder dentro de la plataforma.

Roles definidos:

* ADMIN
* ENTRENADOR
* RECEPCIONISTA
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

# ROL RECEPCIONISTA

## Descripción

Staff de mostrador. Atiende el registro de clientes, las asistencias, la asignación de membresías a un cliente ya registrado, los pagos y las ventas directas.

No tiene acceso a la definición de planes de membresía, al seguimiento deportivo (progreso, ejercicios, comidas, rutinas, nutrición), a los reportes, ni al resto del módulo de Comercio (categorías, productos, proveedores, compras, inventario) más allá de la búsqueda de un producto por código de barras al vender.

---

## Funciones Principales

* Registrar y consultar clientes (alta, búsqueda, baja lógica).
* Registrar asistencias.
* Asignar una membresía a un cliente ya registrado.
* Registrar y confirmar pagos.
* Registrar ventas de mostrador.

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

| Módulo                | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE             |
| --------------------- | ----- | ---------- | -------------- | ------------------- |
| Dashboard             | Sí    | Sí         | Sí             | Sí                  |
| Usuarios              | Sí    | No         | No             | No                  |
| Clientes              | Sí    | Sí         | Sí             | No                  |
| Detalle Cliente       | Sí    | Sí         | Sí             | No                  |
| Membresías            | Sí    | No         | No             | No                  |
| Cliente Membresías    | Sí    | No         | Sí             | No                  |
| Pagos                 | Sí    | No         | Sí             | Solo lectura propia |
| Asistencias           | Sí    | Sí         | Sí             | Solo lectura propia |
| Progreso              | Sí    | Sí         | No             | Solo lectura propia |
| Ejercicios            | Sí    | Sí         | No             | No                  |
| Comidas               | Sí    | Sí         | No             | No                  |
| Rutinas               | Sí    | Sí         | No             | Solo lectura propia |
| Nutrición             | Sí    | Sí         | No             | Solo lectura propia |
| Reportes              | Sí    | Sí         | No             | No                  |
| Configuración Sistema | Sí    | No         | No             | No                  |
| Entrenadores (ficha)  | Sí    | No         | No             | No                  |
| Avisos (gestión)      | Sí    | No         | No             | No (solo lectura pública, sin login) |
| Auditoría             | Sí    | No         | No             | No                  |
| Categorías            | Sí    | No         | No             | No                  |
| Productos             | Sí    | No         | Solo búsqueda por código de barras al vender | Solo lectura pública (`/tienda`, solo activos) |
| Proveedores           | Sí    | No         | No             | No                  |
| Compras               | Sí    | No         | No             | No                  |
| Inventario            | Sí    | No         | No             | No                  |
| Ventas                | Sí    | No         | Sí (venta de mostrador) | Solo sus propios pedidos (`/ventas/solicitar`, `/ventas/mis-pedidos`) |

> **Nota (verificado en código, 2026-11):** `Entrenadores.jsx` y `Auditoria.jsx` ya tienen página propia en el panel (rutas `/entrenadores` y `/auditoria`, solo ADMIN) — la brecha backend↔frontend que señalaba la versión anterior de esta nota quedó resuelta (ver `Pendientes.md`, P-18).

---

# Permisos por Operación

## Gestión de Usuarios

| Acción    | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE |
| --------- | ----- | ---------- | -------------- | ------- |
| Crear     | Sí    | No         | No             | No      |
| Consultar | Sí    | No         | No             | No      |
| Editar    | Sí    | No         | No             | No      |
| Eliminar  | Sí    | No         | No             | No      |

---

## Gestión de Clientes

| Acción     | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE |
| ---------- | ----- | ---------- | -------------- | ------- |
| Crear      | Sí    | No         | Sí             | No      |
| Consultar  | Sí    | Sí         | Sí             | No      |
| Editar     | Sí    | Sí         | Sí             | No      |
| Desactivar | Sí    | No         | Sí             | No      |

---

## Gestión de Membresías

| Acción     | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE |
| ---------- | ----- | ---------- | -------------- | ------- |
| Crear      | Sí    | No         | No             | No      |
| Editar     | Sí    | No         | No             | No      |
| Desactivar | Sí    | No         | No             | No      |
| Consultar  | Sí    | Sí         | Sí             | Sí      |

---

## Gestión de Cliente-Membresías (asignación)

| Acción    | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE |
| --------- | ----- | ---------- | -------------- | ------- |
| Asignar a un cliente ya registrado | Sí | No | Sí | No |
| Consultar | Sí | No | Sí | Solo propia |

---

## Gestión de Pagos

| Acción    | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE      |
| --------- | ----- | ---------- | -------------- | ------------ |
| Registrar | Sí    | No         | Sí             | No           |
| Confirmar (autoservicio) | Sí | No | Sí | No      |
| Editar    | Sí    | No         | No             | No           |
| Consultar | Sí    | No         | Sí             | Solo propios |

---

## Gestión de Asistencias

| Acción    | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE      |
| --------- | ----- | ---------- | -------------- | ------------ |
| Registrar | Sí    | Sí         | Sí             | No           |
| Consultar | Sí    | Sí         | Sí             | Solo propias |

---

## Gestión de Progreso

| Acción    | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE     |
| --------- | ----- | ---------- | -------------- | ----------- |
| Registrar | Sí    | Sí         | No             | No          |
| Editar    | Sí    | Sí         | No             | No          |
| Consultar | Sí    | Sí         | No             | Solo propio |

---

## Gestión de Ejercicios

| Acción     | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE |
| ---------- | ----- | ---------- | -------------- | ------- |
| Crear      | Sí    | Sí         | No             | No      |
| Editar     | Sí    | Sí         | No             | No      |
| Desactivar | Sí    | Sí         | No             | No      |
| Consultar  | Sí    | Sí         | No             | No      |

---

## Gestión de Comidas

| Acción     | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE |
| ---------- | ----- | ---------- | -------------- | ------- |
| Crear      | Sí    | Sí         | No             | No      |
| Editar     | Sí    | Sí         | No             | No      |
| Desactivar | Sí    | Sí         | No             | No      |
| Consultar  | Sí    | Sí         | No             | No      |

---

## Gestión de Rutinas

| Acción     | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE     |
| ---------- | ----- | ---------- | -------------- | ----------- |
| Generar IA | Sí    | Sí         | No             | No          |
| Consultar  | Sí    | Sí         | No             | Solo propia |
| Eliminar   | Sí    | Sí         | No             | No          |

---

## Gestión Nutricional

| Acción     | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE     |
| ---------- | ----- | ---------- | -------------- | ----------- |
| Generar IA | Sí    | Sí         | No             | No          |
| Consultar  | Sí    | Sí         | No             | Solo propia |
| Eliminar   | Sí    | Sí         | No             | No          |

---

## Gestión Comercial (Categorías, Productos, Proveedores, Compras, Inventario, Ventas)

| Acción              | ADMIN | ENTRENADOR | RECEPCIONISTA | CLIENTE |
| -------------------- | ----- | ---------- | -------------- | ------- |
| Crear/Editar/Eliminar categoría, producto o proveedor | Sí | No | No | No |
| Ver productos disponibles (tienda pública) | Sí | Sí | Sí | Sí (sin login) |
| Buscar producto por código de barras al vender | Sí | No | Sí | No |
| Registrar/confirmar/anular compra | Sí | No | No | No |
| Consultar/ajustar inventario, lotes, alertas | Sí | No | No | No |
| Registrar venta directa (mostrador) | Sí | No | Sí | No |
| Solicitar compra desde la Tienda | No | No | No | Sí (rol CLIENTE autenticado) |
| Consultar "mis pedidos" | No | No | No | Solo propios |
| Anular venta | Sí | Sí (permitido por el backend, sin ruta propia en el frontend) | Sí | No |

---

## Gestión de Avisos

| Acción    | ADMIN | ENTRENADOR | CLIENTE / Público |
| --------- | ----- | ---------- | ------------------ |
| Crear/Editar/Eliminar | Sí | No | No |
| Consultar (activos)   | Sí | Sí | Sí, sin autenticación |

---

## Gestión de Configuración del Sitio

| Acción    | ADMIN | ENTRENADOR | CLIENTE / Público |
| --------- | ----- | ---------- | ------------------ |
| Editar (datos de contacto, redes sociales, logo) | Sí | No | No |
| Consultar | Sí | Sí | Sí, sin autenticación |

---

## Gestión de Entrenadores y Auditoría

| Acción    | ADMIN | ENTRENADOR | CLIENTE |
| --------- | ----- | ---------- | ------- |
| CRUD ficha de entrenador (`Entrenadores.jsx`) | Sí | No | No |
| Consultar registros de auditoría (`Auditoria.jsx`, solo lectura) | Sí | No | No |

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
* GestionAvisos
* Categorias
* Productos
* Proveedores
* Compras
* Inventario
* Ventas
* Configuracion
* Entrenadores
* Auditoria
* Reportes

> `Entrenadores.jsx` (CRUD completo de la ficha de entrenador) y `Auditoria.jsx` (vista de solo lectura, con filtro por entidad) ya existen como páginas propias del panel, en las rutas `/entrenadores` y `/auditoria` (verificado 2026-11, ver `Pendientes.md`, P-18). La creación del *usuario* con rol ENTRENADOR sigue haciéndose desde `Usuarios.jsx`, como antes — lo que cambió es que la ficha de entrenador (DNI, especialidad, teléfono, estado) ya tiene su propia pantalla.

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
* Reportes

---

## RECEPCIONISTA

Acceso permitido:

* DashboardRecepcionista
* Clientes
* DetalleCliente
* Asistencias
* ClienteMembresias
* Pagos
* Ventas

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
