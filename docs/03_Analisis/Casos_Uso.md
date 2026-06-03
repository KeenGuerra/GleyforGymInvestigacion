# CASOS DE USO

# SistemaGimnasioGleyforGym

## Introducción

Los casos de uso describen las interacciones entre los actores del sistema y las funcionalidades ofrecidas por la plataforma.

Actores principales:

* Administrador
* Entrenador
* Cliente
* Sistema IA

---

# CU-001 Iniciar Sesión

## Actor Principal

Usuario

## Objetivo

Permitir el acceso seguro al sistema.

## Precondiciones

* El usuario debe estar registrado.
* El usuario debe encontrarse activo.

## Flujo Principal

1. El usuario ingresa correo electrónico.
2. El usuario ingresa contraseña.
3. El sistema valida credenciales.
4. El sistema genera JWT.
5. El sistema identifica el rol.
6. El sistema redirige al dashboard correspondiente.

## Postcondiciones

* Usuario autenticado.

---

# CU-002 Gestionar Usuarios

## Actor Principal

Administrador

## Objetivo

Administrar usuarios del sistema.

## Funcionalidades

* Registrar usuario.
* Consultar usuario.
* Modificar usuario.
* Activar usuario.
* Desactivar usuario.
* Eliminar usuario.

## Postcondiciones

* Información actualizada.

---

# CU-003 Gestionar Clientes

## Actor Principal

Administrador

## Objetivo

Administrar clientes del gimnasio.

## Funcionalidades

* Registrar cliente.
* Actualizar cliente.
* Consultar cliente.
* Buscar cliente.
* Activar cliente.
* Desactivar cliente.

## Reglas Asociadas

RN-001
RN-002
RN-006
RN-008

---

# CU-004 Gestionar Membresías

## Actor Principal

Administrador

## Objetivo

Administrar planes de membresía.

## Funcionalidades

* Registrar membresía.
* Modificar membresía.
* Activar membresía.
* Desactivar membresía.
* Gestionar beneficios.

---

# CU-005 Asignar Membresía

## Actor Principal

Administrador

## Objetivo

Asignar una membresía a un cliente.

## Flujo Principal

1. Seleccionar cliente.
2. Seleccionar membresía.
3. Calcular fecha inicio.
4. Calcular fecha fin.
5. Registrar precio_asignado.
6. Guardar asignación.

## Reglas Asociadas

RN-015
RN-016
RN-017

---

# CU-006 Gestionar Pagos

## Actor Principal

Administrador

## Objetivo

Administrar pagos registrados.

## Funcionalidades

* Registrar pago.
* Consultar pago.
* Modificar pago.
* Consultar historial financiero.

---

# CU-007 Gestionar Asistencias

## Actor Principal

Administrador / Entrenador

## Objetivo

Registrar y consultar asistencias.

## Funcionalidades

* Registrar asistencia.
* Consultar asistencia.
* Consultar historial.

---

# CU-008 Gestionar Progreso Físico

## Actor Principal

Entrenador

## Objetivo

Registrar y monitorear el progreso físico de los clientes.

## Funcionalidades

* Registrar evaluación.
* Actualizar evaluación.
* Consultar historial.
* Analizar evolución.

---

# CU-009 Gestionar Ejercicios

## Actor Principal

Administrador / Entrenador

## Objetivo

Administrar el catálogo de ejercicios.

## Funcionalidades

* Registrar ejercicio.
* Actualizar ejercicio.
* Subir video.
* Activar ejercicio.
* Desactivar ejercicio.

---

# CU-010 Gestionar Comidas

## Actor Principal

Administrador / Entrenador

## Objetivo

Administrar el catálogo nutricional.

## Funcionalidades

* Registrar comida.
* Actualizar comida.
* Activar comida.
* Desactivar comida.

---

# CU-011 Generar Rutina IA

## Actor Principal

Administrador / Entrenador

## Actor Secundario

Sistema IA

## Objetivo

Generar una rutina personalizada.

## Flujo Principal

1. Seleccionar cliente.
2. Analizar objetivo.
3. Analizar nivel.
4. Seleccionar ejercicios activos.
5. Generar rutina.
6. Registrar rutina.

## Reglas Asociadas

RN-033
RN-034

---

# CU-012 Generar Nutrición IA

## Actor Principal

Administrador / Entrenador

## Actor Secundario

Sistema IA

## Objetivo

Generar un plan nutricional personalizado.

## Flujo Principal

1. Seleccionar cliente.
2. Analizar peso.
3. Analizar estatura.
4. Analizar restricciones.
5. Seleccionar comidas activas.
6. Generar plan.

## Reglas Asociadas

RN-035
RN-036

---

# CU-013 Consultar Perfil Cliente

## Actor Principal

Cliente

## Objetivo

Visualizar información personal.

---

# CU-014 Consultar Rutina Cliente

## Actor Principal

Cliente

## Objetivo

Visualizar rutina asignada.

---

# CU-015 Consultar Nutrición Cliente

## Actor Principal

Cliente

## Objetivo

Visualizar plan nutricional asignado.

---

# CU-016 Consultar Membresía Cliente

## Actor Principal

Cliente

## Objetivo

Visualizar membresía actual.

---

# CU-017 Consultar Pagos Cliente

## Actor Principal

Cliente

## Objetivo

Visualizar historial de pagos.

---

# CU-018 Dashboard Administrativo

## Actor Principal

Administrador

## Objetivo

Visualizar indicadores generales del gimnasio.

---

# CU-019 Dashboard Entrenador

## Actor Principal

Entrenador

## Objetivo

Visualizar información deportiva de clientes.

---

# CU-020 Dashboard Cliente

## Actor Principal

Cliente

## Objetivo

Visualizar resumen personal de actividades.
