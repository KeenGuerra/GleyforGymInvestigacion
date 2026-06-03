# Casos de Prueba

# SistemaGimnasioGleyforGym

## Introducción

Los casos de prueba permiten verificar el correcto funcionamiento de las funcionalidades implementadas en el sistema.

Cada caso de prueba valida uno o varios requerimientos funcionales y casos de uso.

---

# MÓDULO: AUTENTICACIÓN

## CP-001 Login Correcto

### Objetivo

Validar el acceso al sistema con credenciales válidas.

### Precondiciones

- Usuario registrado.
- Usuario activo.

### Datos de Entrada

```text
Correo: admin@gleyforgym.com
Contraseña: Admin123*
```

### Resultado Esperado

```text
Login exitoso.
Generación de JWT.
Redirección al dashboard.
```

### Estado

Pendiente

---

## CP-002 Login Incorrecto

### Objetivo

Validar rechazo de credenciales inválidas.

### Datos de Entrada

```text
Correo: admin@gleyforgym.com
Contraseña: 123456
```

### Resultado Esperado

```text
401 Unauthorized
```

### Estado

Pendiente

---

## CP-003 Usuario Inactivo

### Objetivo

Verificar que usuarios inactivos no puedan ingresar.

### Resultado Esperado

```text
Acceso denegado.
```

### Estado

Pendiente

---

# MÓDULO: CLIENTES

## CP-004 Registrar Cliente

### Objetivo

Validar creación de cliente.

### Resultado Esperado

```text
Cliente registrado correctamente.
```

### Estado

Pendiente

---

## CP-005 Calcular Edad Automáticamente

### Objetivo

Validar cálculo automático de edad.

### Entrada

```text
Fecha nacimiento:
2000-01-01
```

### Resultado Esperado

```text
Edad calculada automáticamente.
```

### Estado

Pendiente

---

## CP-006 Modificar Cliente

### Objetivo

Validar actualización de información.

### Resultado Esperado

```text
Datos actualizados.
```

### Estado

Pendiente

---

## CP-007 Desactivar Cliente

### Objetivo

Validar cambio de estado.

### Resultado Esperado

```text
Cliente INACTIVO.
Usuario INACTIVO.
```

### Estado

Pendiente

---

## CP-008 Consultar Detalle Cliente

### Objetivo

Validar visualización de detalle.

### Resultado Esperado

```text
Información completa mostrada.
```

### Estado

Pendiente

---

# MÓDULO: MEMBRESÍAS

## CP-009 Crear Membresía

### Objetivo

Validar registro de plan.

### Resultado Esperado

```text
Plan registrado.
```

### Estado

Pendiente

---

## CP-010 Editar Membresía

### Resultado Esperado

```text
Plan actualizado.
```

---

## CP-011 Registrar Beneficios

### Resultado Esperado

```text
Beneficios almacenados.
```

---

## CP-012 Mostrar Membresías en Landing

### Resultado Esperado

```text
Planes visibles.
```

---

# MÓDULO: CLIENTE MEMBRESÍAS

## CP-013 Asignar Membresía

### Resultado Esperado

```text
Asignación creada.
```

---

## CP-014 Calcular Fecha Fin

### Resultado Esperado

```text
fecha_fin = fecha_inicio + duración
```

---

## CP-015 Registrar Precio Asignado

### Resultado Esperado

```text
Precio congelado correctamente.
```

---

## CP-016 Pausar Membresía

### Resultado Esperado

```text
Estado = PAUSADA
```

---

## CP-017 Reactivar Membresía

### Resultado Esperado

```text
Estado = ACTIVA
```

---

## CP-018 Finalización Automática

### Resultado Esperado

```text
Estado = TERMINADA
```

---

# MÓDULO: PAGOS

## CP-019 Registrar Pago

### Resultado Esperado

```text
Pago registrado.
```

---

## CP-020 Validar Monto Positivo

### Resultado Esperado

```text
Monto > 0
```

---

## CP-021 Consultar Pagos

### Resultado Esperado

```text
Historial mostrado.
```

---

## CP-022 Consultar Mis Pagos

### Resultado Esperado

```text
Cliente visualiza pagos.
```

---

# MÓDULO: ASISTENCIAS

## CP-023 Registrar Asistencia

### Resultado Esperado

```text
Asistencia registrada.
```

---

## CP-024 Consultar Asistencias

### Resultado Esperado

```text
Listado mostrado.
```

---

## CP-025 Consultar Mis Asistencias

### Resultado Esperado

```text
Historial visible.
```

---

# MÓDULO: PROGRESO

## CP-026 Registrar Progreso

### Resultado Esperado

```text
Registro guardado.
```

---

## CP-027 Registrar Medidas Corporales

### Resultado Esperado

```text
Brazo y pierna izquierda/derecha guardados.
```

---

## CP-028 Consultar Historial Progreso

### Resultado Esperado

```text
Historial visible.
```

---

## CP-029 Visualizar Mi Progreso

### Resultado Esperado

```text
Cliente visualiza progreso.
```

---

# MÓDULO: EJERCICIOS

## CP-030 Registrar Ejercicio

### Resultado Esperado

```text
Ejercicio registrado.
```

---

## CP-031 Subir Video Cloudinary

### Resultado Esperado

```text
video_url generado.
```

---

## CP-032 Consultar Ejercicios

### Resultado Esperado

```text
Listado mostrado.
```

---

# MÓDULO: COMIDAS

## CP-033 Registrar Comida

### Resultado Esperado

```text
Comida registrada.
```

---

## CP-034 Registrar Macronutrientes

### Resultado Esperado

```text
Proteínas, grasas y carbohidratos guardados.
```

---

## CP-035 Consultar Comidas

### Resultado Esperado

```text
Listado mostrado.
```

---

# MÓDULO: IA RUTINAS

## CP-036 Generar Rutina IA

### Resultado Esperado

```text
Rutina creada.
```

---

## CP-037 Validar Objetivo

### Resultado Esperado

```text
La rutina considera el objetivo.
```

---

## CP-038 Validar Nivel

### Resultado Esperado

```text
La rutina considera el nivel.
```

---

## CP-039 Validar Ejercicios Activos

### Resultado Esperado

```text
Solo ejercicios activos.
```

---

## CP-040 Visualizar Mi Rutina

### Resultado Esperado

```text
Cliente visualiza rutina.
```

---

# MÓDULO: IA NUTRICIÓN

## CP-041 Generar Nutrición IA

### Resultado Esperado

```text
Plan generado.
```

---

## CP-042 Validar Restricciones Médicas

### Resultado Esperado

```text
Restricciones respetadas.
```

---

## CP-043 Validar Comidas Activas

### Resultado Esperado

```text
Solo comidas activas.
```

---

## CP-044 Visualizar Mi Nutrición

### Resultado Esperado

```text
Cliente visualiza plan.
```

---

# MÓDULO: SEGURIDAD

## CP-045 Validar JWT

### Resultado Esperado

```text
Acceso autorizado.
```

---

## CP-046 Token Inválido

### Resultado Esperado

```text
401 Unauthorized
```

---

## CP-047 Acceso por Rol

### Resultado Esperado

```text
Módulos restringidos correctamente.
```

---

# MÓDULO: DASHBOARDS

## CP-048 Dashboard Admin

### Resultado Esperado

```text
Indicadores visibles.
```

---

## CP-049 Dashboard Entrenador

### Resultado Esperado

```text
Clientes visibles.
```

---

## CP-050 Dashboard Cliente

### Resultado Esperado

```text
Resumen personal visible.
```

---

# NUEVOS CASOS DE PRUEBA: ESTABILIZACIÓN V2.6

## CP-051 Detalle de Cliente sin AttributeError

### Objetivo
Validar que el endpoint `/clientes/{id_cliente}/detalle` retorne la respuesta completa (incluyendo el último progreso) de forma exitosa sin arrojar excepciones de atributos inexistentes.

### Resultado Esperado
```text
HTTP 200 OK.
JSON estructurado conteniendo "medida_brazo_izquierdo", "medida_brazo_derecho", "medida_pierna_izquierda" y "medida_pierna_derecha" en la sección de ultimo_progreso.
```

---

## CP-052 Persistencia de Beneficios en Membresías

### Objetivo
Validar que al registrar una nueva membresía se almacene correctamente el campo descriptivo de beneficios en la base de datos PostgreSQL.

### Resultado Esperado
```text
Membresía creada con el campo "beneficios" persistido correctamente.
```

---

## CP-053 Visualización de Detalles de Rutina en Flutter

### Objetivo
Validar que el usuario pueda pulsar en una rutina dentro de la lista de rutinas en la app de Flutter y navegar a la pantalla `RutinaDetalleScreen` con el desglose de ejercicios.

### Resultado Esperado
```text
Carga exitosa del listado de ejercicios, series, repeticiones, descanso y botón de visualización de video explicativo.
```

---

## CP-054 Visualización de Medidas y Masa Magra en Progreso Móvil

### Objetivo
Verificar que la pantalla de progreso en Flutter lea la variable `masa_magra` de forma correcta (eliminando la variable no existente `masa_muscular`) y muestre de forma ordenada las medidas de pecho, cintura, brazos y piernas.

### Resultado Esperado
```text
Las tarjetas del historial exponen el peso, porcentaje de grasa, masa magra y las medidas corporales detalladas sin valores nulos imprevistos.
```

---

## CP-055 Nombre de Plan Descriptivo en Membresías de Flutter

### Objetivo
Asegurar que la pantalla de membresía de Flutter muestre el nombre comercial del plan asignado (`nombre_membresia`) en lugar del simple ID numérico.

### Resultado Esperado
```text
Visualización de textos claros tipo "Plan Gold", "Plan Estudiante" en el listado de membresías.
```

---

# Resumen

## Total de Casos de Prueba

```text
55
```

## Cobertura

```text
Login
Usuarios
Clientes
Membresías
Pagos
Asistencias
Progreso
Ejercicios
Comidas
IA Rutinas
IA Nutrición
Seguridad
Dashboards
Nuevos Parches v2.6
```

## Estado Actual

```text
Pruebas ejecutadas y aprobadas en entorno local v2.6.
```

---