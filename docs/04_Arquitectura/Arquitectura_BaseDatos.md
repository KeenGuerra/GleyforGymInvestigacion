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

> **Actualizado 2026-09** tras verificar contra `backend/app/models.py`. La versión anterior de este documento listaba solo 13 tablas; el sistema real ya tiene 26.

Actualmente el sistema posee:

```text
1. usuarios
2. clientes
3. entrenadores
4. membresias
5. cliente_membresias
6. pagos
7. asistencias
8. progreso
9. ejercicios
10. rutinas
11. rutina_ejercicios
12. comidas
13. planes_nutricionales
14. plan_comidas
15. categorias
16. productos
17. proveedores
18. compras
19. detalle_compras
20. inventario
21. lotes
22. movimientos_stock
23. ventas
24. detalle_ventas
25. registros_auditoria
26. avisos
```

Total:

```text
26 tablas principales
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

# 17.1. Tabla Entrenadores

## Propósito

Ficha propia del entrenador (mismo patrón que usuarios↔clientes).

## Campos

| Campo | Tipo |
|---------|---------|
| id_entrenador | SERIAL PK |
| id_usuario | INTEGER FK (unique) |
| dni | VARCHAR(8) UNIQUE |
| nombres | VARCHAR |
| apellidos | VARCHAR |
| telefono | VARCHAR |
| especialidad | VARCHAR |
| estado | VARCHAR |

---

# 17.2. Tablas de Gestión Comercial (Comercio)

> Módulo completo en producción, no documentado en la versión anterior de este archivo.

## Categorias

| Campo | Tipo |
|---------|---------|
| id_categoria | SERIAL PK |
| nombre | VARCHAR(100) UNIQUE |
| descripcion | TEXT |
| estado | VARCHAR(20) |
| fecha_creacion | TIMESTAMP |

## Productos

| Campo | Tipo |
|---------|---------|
| id_producto | SERIAL PK |
| id_categoria | INTEGER FK |
| nombre | VARCHAR(150) |
| descripcion | TEXT |
| imagen_url | TEXT |
| cloudinary_public_id | VARCHAR(255) |
| precio_compra | DOUBLE PRECISION |
| precio_venta | DOUBLE PRECISION |
| unidad_medida | VARCHAR(30) |
| stock_minimo | DOUBLE PRECISION |
| controla_lote | BOOLEAN |
| controla_vencimiento | BOOLEAN |
| estado | VARCHAR(20) |
| fecha_creacion | TIMESTAMP |

## Proveedores

| Campo | Tipo |
|---------|---------|
| id_proveedor | SERIAL PK |
| razon_social | VARCHAR(150) |
| ruc | VARCHAR(20) |
| telefono | VARCHAR(20) |
| correo | VARCHAR(100) |
| direccion | VARCHAR(200) |
| contacto | VARCHAR(100) |
| estado | VARCHAR(20) |
| fecha_creacion | TIMESTAMP |

## Compras

| Campo | Tipo |
|---------|---------|
| id_compra | SERIAL PK |
| id_proveedor | INTEGER FK |
| id_usuario | INTEGER FK |
| fecha_compra | TIMESTAMP |
| subtotal / igv / total | DOUBLE PRECISION |
| estado | VARCHAR(20) — PENDIENTE, CONFIRMADA, ANULADA |
| observaciones | TEXT |
| created_at / updated_at | TIMESTAMP |

## Detalle_Compras

| Campo | Tipo |
|---------|---------|
| id_detalle_compra | SERIAL PK |
| id_compra | INTEGER FK |
| id_producto | INTEGER FK |
| cantidad | DOUBLE PRECISION |
| precio_unitario | DOUBLE PRECISION |
| subtotal | DOUBLE PRECISION |

## Inventario

| Campo | Tipo |
|---------|---------|
| id_inventario | SERIAL PK |
| id_producto | INTEGER FK UNIQUE |
| stock_actual | DOUBLE PRECISION |
| stock_minimo | DOUBLE PRECISION |
| ultimo_costo | DOUBLE PRECISION |
| fecha_actualizacion | TIMESTAMP |

## Lotes

| Campo | Tipo |
|---------|---------|
| id_lote | SERIAL PK |
| id_producto | INTEGER FK |
| numero_lote | VARCHAR(50) |
| cantidad | DOUBLE PRECISION |
| fecha_vencimiento | DATE |
| fecha_ingreso | TIMESTAMP |
| estado | VARCHAR(20) — ACTIVO, VENCIDO, AGOTADO |

## Movimientos_Stock

| Campo | Tipo |
|---------|---------|
| id_movimiento | SERIAL PK |
| id_producto | INTEGER FK |
| id_lote | INTEGER FK (nullable) |
| tipo_movimiento | VARCHAR(30) — ENTRADA, ENTRADA_COMPRA, SALIDA_VENTA, ENTRADA_ANULACION_VENTA, SALIDA_ANULACION_COMPRA, AJUSTE |
| referencia_tipo / referencia_id | VARCHAR(30) / INTEGER |
| cantidad | DOUBLE PRECISION |
| costo_unitario | DOUBLE PRECISION |
| descripcion | TEXT |
| id_usuario | INTEGER FK |
| fecha_movimiento | TIMESTAMP |

## Ventas

| Campo | Tipo |
|---------|---------|
| id_venta | SERIAL PK |
| id_cliente | INTEGER FK (nullable) |
| id_usuario | INTEGER FK |
| fecha_venta | TIMESTAMP |
| subtotal / descuento / total | DOUBLE PRECISION |
| metodo_pago | VARCHAR(50) |
| estado | VARCHAR(20) — PENDIENTE, CONFIRMADA, ANULADA, FALLIDA |
| id_transaccion_externa | VARCHAR(100) |
| created_at / updated_at | TIMESTAMP |

## Detalle_Ventas

| Campo | Tipo |
|---------|---------|
| id_detalle_venta | SERIAL PK |
| id_venta | INTEGER FK |
| id_producto | INTEGER FK |
| id_lote | INTEGER FK (nullable) |
| cantidad | DOUBLE PRECISION |
| precio_unitario / descuento / subtotal | DOUBLE PRECISION |

---

# 17.3. Tabla Registros_Auditoria

## Propósito

Trazabilidad de operaciones críticas (RN-039/RN-043).

## Campos

| Campo | Tipo |
|---------|---------|
| id_registro | SERIAL PK |
| id_usuario | INTEGER FK (nullable) |
| correo_usuario | VARCHAR — copia al momento del evento |
| accion | VARCHAR(30) — CREAR, EDITAR, ANULAR, CONFIRMAR, LOGIN_FALLIDO... |
| entidad | VARCHAR(50) |
| id_entidad | INTEGER |
| detalle | VARCHAR |
| fecha | TIMESTAMP |

---

# 17.4. Tabla Avisos

## Propósito

Comunicados públicos editables desde el panel (RN-042). Antes era contenido estático en el frontend.

## Campos

| Campo | Tipo |
|---------|---------|
| id_aviso | SERIAL PK |
| titulo | VARCHAR(150) |
| contenido | TEXT |
| tipo | VARCHAR(30) — HORARIO, COACHES, BAILE, COMUNICADO, EVENTO |
| fecha_evento | DATE (solo si tipo=EVENTO) |
| estado | VARCHAR |
| fecha_creacion | TIMESTAMP |

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

## Relación Comercial (Compras/Ventas → Inventario)

```text
compras ──confirmar──> movimientos_stock ──> inventario (aumenta stock)
ventas  ──confirmar──> movimientos_stock ──> inventario (disminuye stock)
```

El stock nunca se edita directamente (RN-045): solo cambia por movimientos generados por compras/ventas confirmadas o ajustes manuales.

---

# 20. Estado Actual

## Implementado

✅ PostgreSQL
✅ SQLAlchemy
✅ 26 tablas (verificado 2026-09 contra `backend/app/models.py`)
✅ Relaciones definidas
✅ Precio congelado
✅ Estados de membresía
✅ Históricos
✅ IA Rutinas
✅ IA Nutrición
✅ Auditoría (tabla `registros_auditoria`, ya implementada — corrige la versión anterior de este documento que la listaba como "futuro")
✅ Módulo Comercio completo (categorías, productos, proveedores, compras, inventario con lotes/movimientos, ventas)
✅ Avisos editables desde el panel
✅ Ficha propia de Entrenadores (tabla `entrenadores`)

## Futuro

- Multi gimnasio (SaaS)
- Particionado
- Replicación
- Página propia en `web-admin` para Entrenadores y para Auditoría (hoy solo existen como API, ver `Roles_Permisos.md`)

---