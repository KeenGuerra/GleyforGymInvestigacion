# Manual de Usuario Cliente

# SistemaGimnasioGleyforGym

## 1. Introducción

El presente manual describe las funcionalidades disponibles para el rol Cliente dentro del SistemaGimnasioGleyforGym.

El cliente puede consultar su información personal, rutinas de entrenamiento, planes nutricionales, membresías, pagos y progreso físico.

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
Dashboard Cliente
```

---

# 3. Dashboard Cliente

## Objetivo

Visualizar un resumen rápido de la información personal.

---

## Información Disponible

- Perfil.
- Rutina actual.
- Plan nutricional.
- Progreso físico.
- Membresía activa.
- Historial de pagos.

---

# 4. Mi Perfil

## Objetivo

Consultar la información personal registrada.

---

## Acceder

Menú:

```text
Mi Perfil
```

---

## Información Mostrada

### Datos Personales

```text
DNI
Nombres
Apellidos
Teléfono
Sexo
Dirección
```

---

### Datos Físicos

```text
Edad
Peso
Estatura
Objetivo
Nivel
```

---

### Restricciones Médicas

```text
Restricciones registradas
```

---

## Importante

La edad es calculada automáticamente por el sistema.

---

# 5. Mi Rutina

## Objetivo

Consultar la rutina asignada.

---

## Acceder

Menú:

```text
Mi Rutina
```

---

## Información Mostrada

### Rutina

```text
Nombre
Objetivo
Nivel
Fecha Creación
```

---

### Ejercicios

```text
Nombre
Grupo Muscular
Series
Repeticiones
Descanso
Día
```

---

### Videos

Cada ejercicio puede incluir:

```text
Video demostrativo
```

proporcionado desde Cloudinary.

---

## Beneficios

Permite seguir correctamente la rutina indicada por el entrenador o por la IA.

---

# 6. Mi Nutrición

## Objetivo

Consultar el plan nutricional asignado.

---

## Acceder

Menú:

```text
Mi Nutrición
```

---

## Información Mostrada

### Plan Nutricional

```text
Objetivo
Calorías Diarias
Proteínas
Carbohidratos
Grasas
```

---

### Comidas

```text
Desayuno
Media Mañana
Almuerzo
Merienda
Cena
```

---

### Horarios

```text
Hora Recomendada
```

---

## Beneficios

Permite seguir una alimentación adecuada según el objetivo físico.

---

# 7. Mi Progreso

## Objetivo

Consultar la evolución física.

---

## Acceder

Menú:

```text
Mi Progreso
```

---

## Información Mostrada

### Historial

```text
Fecha
Peso
Porcentaje Grasa
Masa Grasa
Masa Magra
```

---

### Medidas Corporales

```text
Pecho
Cintura
Brazo Izquierdo
Brazo Derecho
Pierna Izquierda
Pierna Derecha
```

---

## Nuevo Registro

Si el sistema lo permite, el cliente podrá registrar:

```text
Nuevo Progreso
```

mediante el botón:

```text
+ Nuevo Registro
```

---

## Beneficios

Permite monitorear avances y cambios físicos.

---

# 8. Mi Membresía

## Objetivo

Consultar el estado de la membresía.

---

## Acceder

Menú:

```text
Mi Membresía
```

---

## Información Mostrada

### Plan

```text
Nombre
Descripción
Beneficios
```

---

### Fechas

```text
Fecha Inicio
Fecha Fin
```

---

### Precio

```text
Precio Asignado
```

---

### Estado

```text
ACTIVA
PAUSADA
TERMINADA
CANCELADA
```

---

## Importante

El precio mostrado corresponde al:

```text
precio_asignado
```

registrado cuando se contrató la membresía.

---

# 9. Mis Pagos

## Objetivo

Consultar pagos realizados.

---

## Acceder

Menú:

```text
Mis Pagos
```

---

## Información Mostrada

### Historial

```text
Fecha
Monto
Método de Pago
Estado
Observación
```

---

## Beneficios

Permite verificar el estado financiero de la membresía.

---

# 10. Cierre de Sesión

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

# 11. Buenas Prácticas

## Rutina

Seguir las series y repeticiones indicadas.

---

## Nutrición

Respetar horarios y cantidades recomendadas.

---

## Progreso

Registrar mediciones periódicamente.

---

## Membresía

Revisar fechas de vencimiento y estado.

---

# 12. Restricciones del Rol

El cliente NO puede:

❌ Gestionar usuarios

❌ Gestionar clientes

❌ Gestionar membresías

❌ Registrar pagos administrativos

❌ Crear ejercicios

❌ Crear comidas

❌ Generar rutinas IA

❌ Generar nutrición IA

---

# 13. Módulos Disponibles

✅ Dashboard Cliente

✅ Mi Perfil

✅ Mi Rutina

✅ Mi Nutrición

✅ Mi Progreso

✅ Mi Membresía

✅ Mis Pagos

---

# 14. Preguntas Frecuentes

### ¿Por qué no veo mi rutina?

Posibles causas:

- No existe una rutina generada.
- La rutina fue eliminada.
- Ocurrió un error de sincronización.

---

### ¿Por qué no veo mi plan nutricional?

Posibles causas:

- No existe un plan generado.
- El plan fue eliminado.

---

### ¿Por qué mi membresía aparece pausada?

El administrador suspendió temporalmente la membresía.

---

### ¿Por qué cambió el precio del plan actual pero yo sigo viendo otro monto?

Porque el sistema utiliza:

```text
precio_asignado
```

y conserva el valor histórico de contratación.

---

# 15. Versión

```text
SistemaGimnasioGleyforGym
Versión 2.0 Web
```

---