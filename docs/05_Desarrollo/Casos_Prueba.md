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

# NUEVOS CASOS DE PRUEBA: MÓDULOS SIN DOCUMENTAR (2026-09)

> Agregado tras verificar contra código real que estos módulos están en producción (`backend/app/routes/`) pero no tenían casos de prueba formales. Referencia cruzada: `Pendientes.md` P-04 (0% de cobertura automatizada en Comercio, tanto backend como frontend).

# MÓDULO: ENTRENADORES

## CP-056 Registrar Entrenador

### Objetivo
Validar que el administrador pueda registrar un entrenador con usuario y ficha asociados.

### Resultado Esperado
```text
HTTP 201. Usuario creado con rol ENTRENADOR y ficha en tabla entrenadores.
```

---

## CP-057 Desactivar Entrenador sin Perder Historial

### Objetivo
Validar que al desactivar un entrenador no se eliminen las rutinas/planes que generó.

### Resultado Esperado
```text
Entrenador en estado INACTIVO. Rutinas/planes previamente generados se conservan.
```

---

# MÓDULO: AVISOS

## CP-058 Listar Avisos Públicos sin Autenticación

### Objetivo
Validar que `GET /avisos/` responda sin requerir JWT.

### Resultado Esperado
```text
HTTP 200. Solo avisos en estado ACTIVO.
```

---

## CP-059 Crear/Editar/Eliminar Aviso Solo ADMIN

### Objetivo
Validar que ENTRENADOR y CLIENTE reciban 403 al intentar crear, editar o eliminar un aviso.

### Resultado Esperado
```text
HTTP 403 para ENTRENADOR/CLIENTE. HTTP 200/201 para ADMIN.
```

---

# MÓDULO: AUDITORÍA

## CP-060 Registro Automático de Operación Crítica

### Objetivo
Validar que una operación crítica (ej. anular un pago) genere un registro en `registros_auditoria` con usuario, entidad y fecha.

### Resultado Esperado
```text
Nuevo registro visible en GET /auditoria/ inmediatamente después de la operación.
```

---

## CP-061 Consulta de Auditoría Solo ADMIN

### Objetivo
Validar que ENTRENADOR y CLIENTE no puedan consultar `GET /auditoria/`.

### Resultado Esperado
```text
HTTP 403 para ENTRENADOR/CLIENTE.
```

---

# MÓDULO: COMERCIO — CATEGORÍAS Y PRODUCTOS

## CP-062 Crear Categoría Duplicada

### Objetivo
Validar que no se puedan crear dos categorías con el mismo nombre (`nombre` es `unique`).

### Resultado Esperado
```text
HTTP 400/409 en el segundo intento con nombre repetido.
```

---

## CP-063 Listar Productos Disponibles en Tienda Pública

### Objetivo
Validar que `GET /productos/disponibles` solo devuelva productos ACTIVOS con stock > 0, sin requerir JWT.

### Resultado Esperado
```text
HTTP 200. Ningún producto inactivo o sin stock aparece en la respuesta.
```

---

## CP-064 Desactivar Producto Conserva Historial

### Objetivo
Validar que desactivar un producto no elimine sus compras/ventas ya registradas.

### Resultado Esperado
```text
Producto en estado INACTIVO. Historial de compras/ventas intacto.
```

---

# MÓDULO: COMERCIO — PROVEEDORES Y COMPRAS

## CP-065 Registrar y Confirmar Compra Actualiza Inventario

### Objetivo
Validar que al confirmar una compra PENDIENTE se genere un movimiento ENTRADA_COMPRA y aumente el stock del producto.

### Resultado Esperado
```text
Compra en estado CONFIRMADA. Stock del producto incrementado según cantidad comprada. Movimiento visible en GET /inventario/movimientos/.
```

---

## CP-066 Anular Compra Confirmada Revierte Stock

### Objetivo
Validar que anular una compra ya confirmada descuente el stock que había ingresado.

### Resultado Esperado
```text
Compra en estado ANULADA. Stock del producto reducido en la misma cantidad que había ingresado.
```

---

# MÓDULO: COMERCIO — INVENTARIO

## CP-067 Alerta de Stock Bajo

### Objetivo
Validar que `GET /inventario/alertas/stock` liste solo productos con stock_actual menor a stock_minimo.

### Resultado Esperado
```text
HTTP 200. Solo aparecen productos por debajo de su umbral configurado.
```

---

## CP-068 Alerta de Vencimiento de Lotes

### Objetivo
Validar que `GET /inventario/alertas/vencimiento` liste lotes vencidos o próximos a vencer.

### Resultado Esperado
```text
HTTP 200. Lotes con fecha_vencimiento pasada o próxima aparecen marcados.
```

---

## CP-069 Ajuste Manual de Stock Requiere Descripción

### Objetivo
Validar que `POST /inventario/ajustes` exija una descripción/motivo del ajuste.

### Resultado Esperado
```text
HTTP 422 si falta la descripción. HTTP 200/201 con movimiento tipo AJUSTE si se envía completa.
```

---

# MÓDULO: COMERCIO — VENTAS Y CHECKOUT

## CP-070 Venta Directa Descuenta Stock

### Objetivo
Validar que registrar una venta confirmada genere un movimiento SALIDA_VENTA y descuente el stock correspondiente.

### Resultado Esperado
```text
Stock del producto reducido según cantidad vendida. Movimiento visible en historial.
```

---

## CP-071 Cliente Solicita Compra desde Tienda

### Objetivo
Validar que un CLIENTE autenticado pueda crear una venta en estado PENDIENTE desde `POST /ventas/solicitar` y luego verla en `GET /ventas/mis-pedidos`.

### Resultado Esperado
```text
Venta creada con id_cliente del solicitante. Visible únicamente en sus propios "mis pedidos", no en los de otro cliente.
```

---

## CP-072 Anular Venta Revierte Stock

### Objetivo
Validar que anular una venta confirmada devuelva el stock descontado.

### Resultado Esperado
```text
Venta en estado ANULADA. Stock del producto restaurado.
```

---

# MÓDULO: WEBHOOKS Y PASARELA DE PAGOS

## CP-073 Webhook Actualiza Estado de Venta/Pago

### Objetivo
Validar que `POST /webhooks/pagos` con un payload simulado (MockGateway) actualice el estado de la venta/pago asociado.

### Resultado Esperado
```text
Venta/pago pasa de PENDIENTE a CONFIRMADA (o FALLIDA según el payload).
```

### Nota
No existe aún validación de firma/origen del webhook contra un proveedor real (Culqi u otro) — ver `Pendientes.md` P-02. Este caso valida el flujo con `MockGateway`, no la seguridad del webhook en producción.

---

# Resumen

## Total de Casos de Prueba

```text
73
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
Entrenadores
Avisos
Auditoría
Comercio (Categorías, Productos, Proveedores, Compras, Inventario, Ventas)
Webhooks y Pasarela de Pagos
```

## Estado Actual

```text
CP-001 a CP-055: pruebas ejecutadas y aprobadas en entorno local v2.6.
CP-056 a CP-073: casos de prueba redactados 2026-09 a partir del código real; sin automatización todavía.

Cobertura real medida 2026-09 (pytest --cov, no repetir cifras de memoria):
- Cobertura total del backend: 81% (55 tests, 3113 statements).
- Módulos "clásicos" (usuarios, clientes, membresías, pagos, asistencias, progreso,
  ejercicios, comidas, rutinas/nutrición IA, avisos, auditoría): 87%-100%.
- Módulo Comercio, sin tests dedicados: categorias.py 37%, proveedores.py 43%,
  inventario.py 26%, productos.py 23%, compras.py 20%, ventas.py 17%.
  No es exactamente "0%" como decía Pendientes.md P-04 (algunas líneas se ejecutan
  al registrar las rutas en main.py al arrancar la app), pero no hay ninguna
  función test_ que ejercite su lógica de negocio — la brecha real es la ausencia
  de pruebas dedicadas, no la cobertura de línea en sí.
```

---