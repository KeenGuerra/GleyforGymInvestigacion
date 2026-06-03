# Manual de Usuario Entrenador

# SistemaGimnasioGleyforGym

## 1. Introducción

El presente manual describe las funcionalidades disponibles para el rol Entrenador dentro del SistemaGimnasioGleyforGym.

El entrenador tiene acceso a los módulos relacionados con el seguimiento deportivo y nutricional de los clientes.

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
Dashboard Entrenador
```

---

# 3. Dashboard Entrenador

## Objetivo

Visualizar accesos rápidos a los módulos deportivos.

---

## Funcionalidades

- Consultar clientes.
- Registrar asistencias.
- Registrar progreso físico.
- Gestionar ejercicios.
- Gestionar comidas.
- Generar rutinas IA.
- Generar nutrición IA.

---

# 4. Gestión de Clientes

## Objetivo

Consultar información de los clientes.

---

## Acceder

Menú:

```text
Clientes
```

---

## Funcionalidades

### Consultar Clientes

Visualizar:

```text
DNI
Nombre
Edad
Objetivo
Nivel
Estado
```

---

### Buscar Cliente

Filtrar por:

```text
Nombre
DNI
Estado
```

---

### Ver Detalle

Presionar:

```text
Detalle
```

---

## Información Disponible

### Datos Personales

```text
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
Estado
Fecha Inicio
Fecha Fin
```

---

### Progreso

Historial físico completo.

---

### Rutinas

Rutinas generadas.

---

### Nutrición

Planes nutricionales registrados.

---

# 5. Gestión de Asistencias

## Objetivo

Registrar el ingreso y salida de los clientes.

---

## Acceder

Menú:

```text
Asistencias
```

---

## Registrar Asistencia

Completar:

```text
Cliente
Fecha
Hora Entrada
Hora Salida
Observación
```

Guardar.

---

## Consultar Asistencias

Visualizar historial completo.

---

# 6. Gestión de Progreso

## Objetivo

Registrar y consultar la evolución física de los clientes.

---

## Acceder

Menú:

```text
Progreso
```

---

## Registrar Progreso

Completar:

```text
Peso
Porcentaje Grasa
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

## Consultar Historial

Visualizar:

```text
Fecha
Peso
Porcentaje Grasa
Medidas Corporales
```

---

# 7. Gestión de Ejercicios

## Objetivo

Administrar el catálogo de ejercicios utilizado por la IA.

---

## Acceder

Menú:

```text
Ejercicios
```

---

## Registrar Ejercicio

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

## Editar Ejercicio

Modificar información.

Guardar cambios.

---

## Desactivar Ejercicio

Cambiar estado a:

```text
INACTIVO
```

---

# 8. Gestión de Comidas

## Objetivo

Administrar el catálogo nutricional utilizado por la IA.

---

## Acceder

Menú:

```text
Comidas
```

---

## Registrar Comida

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

## Editar Comida

Actualizar información.

Guardar.

---

## Desactivar Comida

Cambiar estado a:

```text
INACTIVO
```

---

# 9. Generación de Rutinas IA

## Objetivo

Generar rutinas personalizadas para los clientes.

---

## Acceder

Menú:

```text
Rutinas
```

---

## Generar Rutina

Seleccionar cliente.

Presionar:

```text
Generar Rutina IA
```

---

## Información Utilizada

```text
Objetivo
Nivel
Peso
Estatura
Ejercicios Activos
```

---

## Resultado

La rutina queda registrada en el sistema.

---

# 10. Generación de Nutrición IA

## Objetivo

Generar planes nutricionales personalizados.

---

## Acceder

Menú:

```text
Nutrición
```

---

## Generar Plan

Seleccionar cliente.

Presionar:

```text
Generar Nutrición IA
```

---

## Información Utilizada

```text
Peso
Estatura
Objetivo
Restricciones Médicas
Comidas Activas
```

---

## Resultado

El plan nutricional queda almacenado en el sistema.

---

# 11. Cierre de Sesión

## Paso 1

Presionar:

```text
Cerrar Sesión
```

---

## Resultado

Se eliminan:

```text
token
rol
id_usuario
correo
```

del navegador.

---

# 12. Buenas Prácticas

## Progreso

Registrar mediciones periódicamente.

---

## Rutinas

Verificar disponibilidad de ejercicios activos.

---

## Nutrición

Mantener actualizado el catálogo de comidas.

---

## Asistencias

Registrar horarios reales de ingreso y salida.

---

# 13. Restricciones del Rol

El entrenador NO puede:

❌ Gestionar usuarios

❌ Gestionar membresías

❌ Registrar pagos

❌ Modificar configuraciones del sistema

---

# 14. Módulos Disponibles

✅ Dashboard Entrenador

✅ Clientes

✅ Asistencias

✅ Progreso

✅ Ejercicios

✅ Comidas

✅ Rutinas IA

✅ Nutrición IA

---

# 15. Versión

```text
SistemaGimnasioGleyforGym
Versión 2.0 Web
```

---