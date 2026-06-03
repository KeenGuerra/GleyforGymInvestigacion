# Arquitectura de Base de Datos

# SistemaGimnasioGleyforGym

## 1. Introducción

La base de datos del SistemaGimnasioGleyforGym está implementada utilizando PostgreSQL.

Su función principal es almacenar la información administrativa, deportiva y nutricional del gimnasio, garantizando integridad, consistencia y trazabilidad.

La estructura sigue un modelo relacional normalizado.

---

## 2. Motor de Base de Datos

| Característica | Valor |
|---------------|--------|
| Motor | PostgreSQL |
| Versión Recomendada | PostgreSQL 16+ |
| Puerto | 5432 |
| Base de Datos | gleyforgym |
| ORM | SQLAlchemy |

---

## 3. Modelo General

```text
USUARIOS
    │
    │ 1:1
    ▼
CLIENTES
    │
    ├───────────────┐
    │               │
    ▼               ▼
ASISTENCIAS      PROGRESO
    │
    │
    ▼
CLIENTE_MEMBRESIAS
    │
    ▼
MEMBRESIAS

CLIENTE_MEMBRESIAS
    │
    ▼
PAGOS

CLIENTES
    │
    ├─────────────┐
    │             │
    ▼             ▼
RUTINAS      PLANES_NUTRICIONALES
    │             │
    ▼             ▼
RUTINA_EJERCICIOS PLAN_COMIDAS

EJERCICIOS
COMIDAS
```

---

# 4. Tablas del Sistema

Actualmente el sistema posee:

```text
1. usuarios
2. clientes
3. membresias
4. cliente_membresias
5. pagos
6. asistencias
7. progreso
8. ejercicios
9. rutinas
10. rutina_ejercicios
11. comidas
12. planes_nutricionales
13. plan_comidas
```

Total:

```text
13 tablas principales
```

---

# 5. Tabla Usuarios

## Propósito

Gestionar acceso y autenticación.

## Campos

| Campo | Tipo |
|---------|---------|
| id_usuario | SERIAL PK |
| correo | VARCHAR |
| password_hash | TEXT |
| rol | VARCHAR |
| estado | VARCHAR |
| fecha_creacion | TIMESTAMP |

## Reglas

- Correo único.
- Contraseña encriptada.
- Rol obligatorio.

---

# 6. Tabla Clientes

## Propósito

Almacenar información real del socio.

## Campos

| Campo | Tipo |
|---------|---------|
| id_cliente | SERIAL PK |
| id_usuario | INTEGER FK |
| dni | VARCHAR |
| nombres | VARCHAR |
| apellidos | VARCHAR |
| telefono | VARCHAR |
| fecha_nacimiento | DATE |
| sexo | VARCHAR |
| direccion | TEXT |
| edad | INTEGER |
| peso | DOUBLE PRECISION |
| estatura | DOUBLE PRECISION |
| objetivo | VARCHAR |
| nivel | VARCHAR |
| restricciones_medicas | TEXT |
| fecha_registro | TIMESTAMP |
| estado | VARCHAR |

## Reglas

- DNI único.
- Edad calculada automáticamente.
- Relación con usuario.

---

# 7. Tabla Membresias

## Propósito

Gestionar planes del gimnasio.

## Campos

| Campo | Tipo |
|---------|---------|
| id_membresia | SERIAL PK |
| nombre | VARCHAR |
| descripcion | TEXT |
| duracion_dias | INTEGER |
| precio | DOUBLE PRECISION |
| beneficios | TEXT |
| estado | VARCHAR |

## Reglas

- Duración > 0.
- Precio > 0.

---

# 8. Tabla Cliente_Membresias

## Propósito

Relacionar clientes con planes.

## Campos

| Campo | Tipo |
|---------|---------|
| id_cliente_membresia | SERIAL PK |
| id_cliente | INTEGER FK |
| id_membresia | INTEGER FK |
| fecha_inicio | DATE |
| fecha_fin | DATE |
| precio_asignado | DOUBLE PRECISION |
| estado | VARCHAR |

## Estados

```text
ACTIVA
PAUSADA
TERMINADA
CANCELADA
```

## Regla Crítica

```text
precio_asignado
congela el precio histórico.
```

---

# 9. Tabla Pagos

## Propósito

Registrar pagos realizados.

## Campos

| Campo | Tipo |
|---------|---------|
| id_pago | SERIAL PK |
| id_cliente_membresia | INTEGER FK |
| monto | DOUBLE PRECISION |
| metodo_pago | VARCHAR |
| fecha_pago | TIMESTAMP |
| estado | VARCHAR |
| observacion | TEXT |

---

# 10. Tabla Asistencias

## Propósito

Controlar ingresos al gimnasio.

## Campos

| Campo | Tipo |
|---------|---------|
| id_asistencia | SERIAL PK |
| id_cliente | INTEGER FK |
| fecha | DATE |
| hora_entrada | TIME |
| hora_salida | TIME |
| observacion | TEXT |

---

# 11. Tabla Progreso

## Propósito

Registrar evolución física.

## Campos

| Campo | Tipo |
|---------|---------|
| id_progreso | SERIAL PK |
| id_cliente | INTEGER FK |
| peso | DOUBLE PRECISION |
| porcentaje_grasa | DOUBLE PRECISION |
| masa_grasa | DOUBLE PRECISION |
| masa_magra | DOUBLE PRECISION |
| medida_pecho | DOUBLE PRECISION |
| medida_cintura | DOUBLE PRECISION |
| medida_brazo_izquierdo | DOUBLE PRECISION |
| medida_brazo_derecho | DOUBLE PRECISION |
| medida_pierna_izquierda | DOUBLE PRECISION |
| medida_pierna_derecha | DOUBLE PRECISION |
| fecha_registro | TIMESTAMP |
| observacion | TEXT |

---

# 12. Tabla Ejercicios

## Propósito

Catálogo para IA de rutinas.

## Campos

| Campo | Tipo |
|---------|---------|
| id_ejercicio | SERIAL PK |
| nombre | VARCHAR |
| grupo_muscular | VARCHAR |
| nivel | VARCHAR |
| objetivo | VARCHAR |
| descripcion | TEXT |
| instrucciones | TEXT |
| video_url | TEXT |
| cloudinary_public_id | TEXT |
| estado | VARCHAR |

---

# 13. Tabla Rutinas

## Propósito

Almacenar rutinas generadas.

## Campos

| Campo | Tipo |
|---------|---------|
| id_rutina | SERIAL PK |
| id_cliente | INTEGER FK |
| nombre | VARCHAR |
| objetivo | VARCHAR |
| nivel | VARCHAR |
| descripcion | TEXT |
| dias_semana | INTEGER |
| generada_por_ia | BOOLEAN |
| fecha_creacion | TIMESTAMP |
| estado | VARCHAR |

---

# 14. Tabla Rutina_Ejercicios

## Propósito

Detalle de ejercicios de una rutina.

## Campos

| Campo | Tipo |
|---------|---------|
| id_rutina_ejercicio | SERIAL PK |
| id_rutina | INTEGER FK |
| id_ejercicio | INTEGER FK |
| nombre_ejercicio | VARCHAR |
| grupo_muscular | VARCHAR |
| series | INTEGER |
| repeticiones | INTEGER |
| descanso_segundos | INTEGER |
| dia_semana | INTEGER |
| orden | INTEGER |

---

# 15. Tabla Comidas

## Propósito

Catálogo nutricional.

## Campos

| Campo | Tipo |
|---------|---------|
| id_comida_catalogo | SERIAL PK |
| nombre | VARCHAR |
| tipo_comida | VARCHAR |
| descripcion | TEXT |
| calorias | DOUBLE PRECISION |
| proteinas | DOUBLE PRECISION |
| carbohidratos | DOUBLE PRECISION |
| grasas | DOUBLE PRECISION |
| objetivo | VARCHAR |
| estado | VARCHAR |

---

# 16. Tabla Planes_Nutricionales

## Propósito

Planes generados por IA.

## Campos

| Campo | Tipo |
|---------|---------|
| id_plan | SERIAL PK |
| id_cliente | INTEGER FK |
| objetivo | VARCHAR |
| calorias_diarias | DOUBLE PRECISION |
| proteinas | DOUBLE PRECISION |
| carbohidratos | DOUBLE PRECISION |
| grasas | DOUBLE PRECISION |
| restricciones | TEXT |
| generada_por_ia | BOOLEAN |
| fecha_creacion | TIMESTAMP |
| estado | VARCHAR |

---

# 17. Tabla Plan_Comidas

## Propósito

Detalle de comidas del plan nutricional.

## Campos

| Campo | Tipo |
|---------|---------|
| id_comida | SERIAL PK |
| id_plan | INTEGER FK |
| tipo_comida | VARCHAR |
| descripcion | TEXT |
| calorias_aprox | DOUBLE PRECISION |
| hora_recomendada | VARCHAR |

---

# 18. Relaciones Críticas

## Relación Usuario → Cliente

```text
usuarios.id_usuario
        │
        ▼
clientes.id_usuario
```

Cardinalidad:

```text
1 Usuario → 1 Cliente
```

---

## Relación Cliente → Membresías

```text
clientes
      │
      ▼
cliente_membresias
      │
      ▼
membresias
```

Cardinalidad:

```text
N:M
```

---

## Relación Cliente → Rutinas

```text
1 Cliente
      │
      ▼
N Rutinas
```

---

## Relación Cliente → Nutrición

```text
1 Cliente
      │
      ▼
N Planes Nutricionales
```

---

# 19. Regla Principal del Modelo

```text
usuarios = acceso

clientes = negocio
```

Todos los procesos utilizan:

- id_cliente

Nunca:

- id_usuario

para:

- Rutinas
- Nutrición
- Pagos
- Asistencias
- Progreso
- Membresías

---

# 20. Estado Actual

## Implementado

✅ PostgreSQL  
✅ SQLAlchemy  
✅ 13 tablas  
✅ Relaciones definidas  
✅ Precio congelado  
✅ Estados de membresía  
✅ Históricos  
✅ IA Rutinas  
✅ IA Nutrición

## Futuro

- Multi gimnasio (SaaS)
- Auditoría
- Logs
- Particionado
- Replicación

---