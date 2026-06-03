# Manual de Usuario Administrador

# SistemaGimnasioGleyforGym

## 1. Introducción

El presente manual describe el uso de las funcionalidades disponibles para el rol Administrador dentro del SistemaGimnasioGleyforGym.

El administrador posee acceso completo a los módulos administrativos, deportivos y nutricionales del sistema.

---

# 2. Acceso al Sistema

## Paso 1

Abrir el navegador.

---

## Paso 2

Ingresar a:

```text
http://localhost:5173
```

---

## Paso 3

Presionar:

```text
Iniciar Sesión
```

---

## Paso 4

Ingresar:

```text
Correo
Contraseña
```

---

## Paso 5

Presionar:

```text
Ingresar
```

---

## Resultado Esperado

El sistema redirige al:

```text
Dashboard Administrador
```

---

# 3. Dashboard Administrador

## Objetivo

Visualizar información general del gimnasio.

---

## Funcionalidades

- Acceso rápido a módulos.
- Gestión administrativa.
- Gestión deportiva.
- Gestión nutricional.

---

# 4. Gestión de Usuarios

## Objetivo

Administrar accesos al sistema.

---

## Acceder

Menú:

```text
Usuarios
```

---

## Crear Usuario

### Paso 1

Presionar:

```text
Nuevo Usuario
```

---

### Paso 2

Completar:

```text
Correo
Contraseña
Rol
Estado
```

---

### Paso 3

Guardar.

---

## Editar Usuario

Seleccionar:

```text
Editar
```

Modificar datos.

Guardar cambios.

---

## Eliminar Usuario

Seleccionar:

```text
Eliminar
```

Confirmar acción.

---

## Roles Disponibles

```text
ADMIN
ENTRENADOR
CLIENTE
```

---

# 5. Gestión de Clientes

## Objetivo

Administrar la información de los socios.

---

## Acceder

Menú:

```text
Clientes
```

---

## Registrar Cliente

Completar:

```text
DNI
Nombres
Apellidos
Teléfono
Fecha Nacimiento
Sexo
Dirección
Peso
Estatura
Objetivo
Nivel
Restricciones Médicas
```

---

## Importante

La edad se calcula automáticamente.

No debe ingresarse manualmente.

---

## Editar Cliente

Seleccionar:

```text
Editar
```

Actualizar información.

Guardar.

---

## Desactivar Cliente

Seleccionar:

```text
Desactivar
```

---

## Resultado

```text
Cliente = INACTIVO
Usuario = INACTIVO
```

---

# 6. Detalle de Cliente

## Objetivo

Consultar información completa del cliente.

---

## Información Disponible

### Datos personales

```text
DNI
Nombre
Edad
Teléfono
Objetivo
Nivel
```

---

### Membresía

```text
Plan
Precio Asignado
Estado
Fechas
```

---

### Pagos

Historial completo.

---

### Asistencias

Historial completo.

---

### Progreso

```text
Peso
% Grasa
Masa Magra
Brazo Izquierdo
Brazo Derecho
Pierna Izquierda
Pierna Derecha
```

---

### Rutinas

Rutinas asignadas.

---

### Nutrición

Planes nutricionales generados.

---

# 7. Gestión de Membresías

## Objetivo

Administrar planes del gimnasio.

---

## Acceder

Menú:

```text
Membresías
```

---

## Crear Membresía

Completar:

```text
Nombre
Descripción
Duración
Precio
Beneficios
Estado
```

---

## Beneficios

Ingresar uno por línea.

Ejemplo:

```text
Acceso ilimitado

Evaluación física

Rutina personalizada
```

---

## Editar Membresía

Modificar datos.

Guardar.

---

# 8. Asignación de Membresías

## Objetivo

Asignar planes a clientes.

---

## Acceder

Menú:

```text
Cliente Membresías
```

---

## Asignar

Seleccionar:

```text
Cliente
Plan
```

Guardar.

---

## Resultado

El sistema genera automáticamente:

```text
Fecha Inicio
Fecha Fin
Precio Asignado
```

---

## Estados Disponibles

```text
ACTIVA
PAUSADA
TERMINADA
CANCELADA
```

---

## Pausar

Presionar:

```text
Pausar
```

---

## Reactivar

Presionar:

```text
Reactivar
```

---

# 9. Gestión de Pagos

## Objetivo

Registrar pagos realizados.

---

## Acceder

Menú:

```text
Pagos
```

---

## Registrar Pago

Completar:

```text
Cliente
Monto
Método Pago
Observación
```

Guardar.

---

## Consultar Pagos

Visualizar:

```text
Fecha
Monto
Estado
Método
```

---

# 10. Gestión de Asistencias

## Objetivo

Controlar ingresos al gimnasio.

---

## Registrar

Completar:

```text
Cliente
Fecha
Hora Entrada
Hora Salida
```

Guardar.

---

## Consultar

Visualizar historial completo.

---

# 11. Gestión de Progreso

## Objetivo

Registrar evolución física.

---

## Registrar

Completar:

```text
Peso
% Grasa
Masa Grasa
Masa Magra
Pecho
Cintura
Brazo Izquierdo
Brazo Derecho
Pierna Izquierda
Pierna Derecha
Observación
```

Guardar.

---

## Consultar

Visualizar histórico completo.

---

# 12. Gestión de Ejercicios

## Objetivo

Administrar catálogo utilizado por la IA.

---

## Crear Ejercicio

Completar:

```text
Nombre
Grupo Muscular
Nivel
Objetivo
Descripción
Instrucciones
Estado
Video
```

Guardar.

---

## Resultado

El video se almacena en Cloudinary.

---

# 13. Gestión de Comidas

## Objetivo

Administrar catálogo nutricional.

---

## Crear Comida

Completar:

```text
Nombre
Tipo Comida
Descripción
Calorías
Proteínas
Carbohidratos
Grasas
Objetivo
Estado
```

Guardar.

---

# 14. Generación de Rutinas IA

## Objetivo

Generar rutinas automáticamente.

---

## Acceder

Menú:

```text
Rutinas
```

---

## Generar

Seleccionar cliente.

Presionar:

```text
Generar Rutina IA
```

---

## Resultado

La rutina se genera utilizando:

```text
Objetivo
Nivel
Datos físicos
Ejercicios activos
```

---

# 15. Generación de Nutrición IA

## Objetivo

Generar planes nutricionales automáticamente.

---

## Acceder

Menú:

```text
Nutrición
```

---

## Generar

Seleccionar cliente.

Presionar:

```text
Generar Nutrición IA
```

---

## Resultado

El sistema utiliza:

```text
Peso
Estatura
Objetivo
Restricciones
Comidas activas
```

---

# 16. Cierre de Sesión

## Paso 1

Presionar:

```text
Cerrar Sesión
```

---

## Resultado

El sistema elimina:

```text
token
rol
id_usuario
correo
```

del navegador.

---

# 17. Buenas Prácticas

## Clientes

Verificar información antes de guardar.

---

## Membresías

No modificar precios históricos.

---

## Rutinas

Verificar que existan ejercicios activos.

---

## Nutrición

Verificar que existan comidas activas.

---

# 18. Restricciones Importantes

## Regla Principal

```text
usuarios = acceso

clientes = negocio
```

---

## Nunca

Utilizar:

```text
id_usuario
```

para procesos del gimnasio.

---

## Siempre

Utilizar:

```text
id_cliente
```

---

# 19. Módulos Disponibles para Administrador

✅ Dashboard

✅ Usuarios

✅ Clientes

✅ Detalle Cliente

✅ Membresías

✅ Cliente Membresías

✅ Pagos

✅ Asistencias

✅ Progreso

✅ Ejercicios

✅ Comidas

✅ Rutinas IA

✅ Nutrición IA

---

# 20. Versión

```text
SistemaGimnasioGleyforGym
Versión 2.0 Web
```

---