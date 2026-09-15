# Arquitectura Backend

# SistemaGimnasioGleyforGym

## 1. Introducción

El backend del SistemaGimnasioGleyforGym está desarrollado utilizando FastAPI y sigue una arquitectura modular orientada a servicios.

Su responsabilidad principal es centralizar la lógica de negocio, gestionar la persistencia de datos, exponer APIs REST y controlar la seguridad mediante JWT.

---

## 2. Tecnologías Utilizadas

| Componente | Tecnología |
|------------|------------|
| Framework Backend | FastAPI |
| ORM | SQLAlchemy |
| Base de Datos | PostgreSQL |
| Seguridad | JWT |
| Hash de Contraseñas | Bcrypt |
| Variables de Entorno | Python Dotenv |
| Validación de Datos | Pydantic |
| Multimedia | Cloudinary |
| Servidor Local | Uvicorn |

---

## 3. Estructura del Backend

> **Actualizado 2026-09**: la versión anterior de este documento solo listaba 10 routers. El backend real tiene 21 routers + submódulo `ia/`, más módulos de soporte (`pagos_gateway/`, `rate_limit.py`, `recibos.py`, `auditoria.py`) que no estaban documentados.

```text
backend
│
├── app
│   │
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── constants.py
│   ├── config.py
│   ├── auditoria.py          # helper para registrar auditoría (RN-039/RN-043)
│   ├── rate_limit.py         # limitador de intentos de login en memoria
│   ├── recibos.py            # generación de PDF de comprobantes (reportlab)
│   │
│   ├── pagos_gateway
│   │   ├── base.py           # interfaz GatewayPago (ABC)
│   │   ├── mock.py           # MockGateway (simulación en memoria)
│   │   └── __init__.py       # singleton `gateway`, único punto de cambio a un proveedor real
│   │
│   ├── routes
│   │   ├── usuarios.py
│   │   ├── clientes.py
│   │   ├── entrenadores.py
│   │   ├── membresias.py
│   │   ├── cliente_membresias.py
│   │   ├── pagos.py
│   │   ├── asistencias.py
│   │   ├── progreso.py
│   │   ├── rutinas.py
│   │   ├── nutricion.py
│   │   ├── ejercicios.py
│   │   ├── comidas.py
│   │   ├── avisos.py
│   │   ├── auditoria.py
│   │   ├── categorias.py
│   │   ├── productos.py
│   │   ├── proveedores.py
│   │   ├── compras.py
│   │   ├── inventario.py
│   │   ├── ventas.py
│   │   ├── reportes.py
│   │   ├── webhooks.py
│   │   │
│   │   └── ia
│   │       ├── ia_rutina.py
│   │       └── ia_nutricion.py
│   │
│   └── ia
│       ├── rutina
│       │   ├── recomendador_rutinas.py
│       │   └── reglas_rutinas.py
│       │
│       └── nutricion
│           ├── calculos_nutricion.py
│           ├── planes_comida.py
│           └── recomendador_nutricion.py
│
├── tests
│   ├── conftest.py
│   ├── test_backend.py       # 48 funciones test_ (TestClient sobre SQLite)
│   └── test_crud.py          # 7 funciones test_
│
├── .env
└── venv
```

---

## 4. Responsabilidad de Cada Archivo

### main.py

Responsable de:

- Crear la aplicación FastAPI.
- Configurar CORS.
- Registrar routers.
- Exponer endpoints principales.

---

### database.py

Responsable de:

- Crear conexión con PostgreSQL.
- Configurar SQLAlchemy.
- Gestionar sesiones de base de datos.

---

### models.py

Responsable de:

- Definir las tablas del sistema.
- Representar entidades mediante clases SQLAlchemy.

---

### schemas.py

Responsable de:

- Validar datos de entrada y salida.
- Definir DTOs mediante Pydantic.

---

### security.py

Responsable de:

- Hash de contraseñas.
- Generación de JWT.
- Validación de JWT.
- Autenticación.

---

## 5. Arquitectura por Capas

```text
┌─────────────────────┐
│      Frontend       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       Router        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Lógica Negocio    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    SQLAlchemy ORM   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     PostgreSQL      │
└─────────────────────┘
```

---

## 6. Módulos del Sistema

### Usuarios

Responsable de:

- Registro.
- Login.
- Roles.
- Seguridad.

Endpoints:

```text
POST /usuarios/
GET /usuarios/
GET /usuarios/{id_usuario}
PUT /usuarios/{id_usuario}
DELETE /usuarios/{id_usuario}
POST /usuarios/login
```

---

### Clientes

Responsable de:

- Gestión de clientes.
- Relación usuario-cliente.

Endpoints:

```text
GET /clientes/
POST /clientes/
PUT /clientes/{id_cliente}
DELETE /clientes/{id_cliente}
GET /clientes/{id_cliente}/detalle
GET /clientes/usuario/{id_usuario}
```

---

### Membresías

Responsable de:

- Gestión de planes.
- Beneficios.

Endpoints:

```text
GET /membresias/
POST /membresias/
PUT /membresias/{id_membresia}
DELETE /membresias/{id_membresia}
```

---

### Cliente Membresías

Responsable de:

- Asignación de planes.
- Precio congelado.
- Estados.

Endpoints:

```text
GET /cliente-membresias/
POST /cliente-membresias/
GET /cliente-membresias/cliente/{id_cliente}
PUT /cliente-membresias/{id_cliente_membresia}
DELETE /cliente-membresias/{id_cliente_membresia}
```

---

### Pagos

Responsable de:

- Registro financiero.

Endpoints:

```text
GET /pagos/
POST /pagos/
GET /pagos/cliente/{id_cliente}
PUT /pagos/{id_pago}
DELETE /pagos/{id_pago}
```

---

### Asistencias

Responsable de:

- Control de ingreso.

Endpoints:

```text
GET /asistencias/
POST /asistencias/
GET /asistencias/cliente/{id_cliente}
PUT /asistencias/{id_asistencia}
DELETE /asistencias/{id_asistencia}
```

---

### Progreso

Responsable de:

- Seguimiento físico.

Endpoints:

```text
GET /progreso/
POST /progreso/
GET /progreso/cliente/{id_cliente}
PUT /progreso/{id_progreso}
DELETE /progreso/{id_progreso}
```

---

### Ejercicios

Responsable de:

- Catálogo de ejercicios.
- Cloudinary.

Endpoints:

```text
GET /ejercicios/
POST /ejercicios/
GET /ejercicios/{id_ejercicio}
PUT /ejercicios/{id_ejercicio}
DELETE /ejercicios/{id_ejercicio}
```

---

### Comidas

Responsable de:

- Catálogo nutricional.

Endpoints:

```text
GET /comidas/
POST /comidas/
GET /comidas/{id_comida}
PUT /comidas/{id_comida}
DELETE /comidas/{id_comida}
```

---

### Rutinas IA

Responsable de:

- Generación automática de rutinas.

Endpoint:

```text
POST /ia/rutina/generar/{id_cliente}
```

---

### Nutrición IA

Responsable de:

- Generación automática de planes nutricionales.

Endpoint:

```text
POST /ia/nutricion/generar/{id_cliente}
```

---

### Entrenadores

> Módulo real, no documentado en la versión anterior. Sin página propia en `web-admin` (ver `Roles_Permisos.md`).

Endpoints:

```text
GET /entrenadores/
POST /entrenadores/
GET /entrenadores/{id_entrenador}
PUT /entrenadores/{id_entrenador}
DELETE /entrenadores/{id_entrenador}
```

---

### Avisos

Responsable de: comunicados públicos editables (RN-042). Reemplaza el contenido antes hardcodeado en `Avisos.jsx`.

Endpoints:

```text
GET /avisos/            (público, sin JWT)
POST /avisos/           (ADMIN)
PUT /avisos/{id_aviso}  (ADMIN)
DELETE /avisos/{id_aviso} (ADMIN)
```

---

### Auditoría

Responsable de: trazabilidad de operaciones críticas (RN-039/RN-043). Sin página propia en `web-admin`.

Endpoint:

```text
GET /auditoria/  (ADMIN)
```

---

### Comercio: Categorías, Productos, Proveedores

Endpoints:

```text
POST/GET/PUT/DELETE /categorias/ , /categorias/{id_categoria}
POST/GET/PUT/DELETE /productos/  , /productos/{id_producto}
GET /productos/disponibles        (público, sin JWT — para /tienda)
POST/GET/PUT/DELETE /proveedores/ , /proveedores/{id_proveedor}
```

---

### Comercio: Compras

Endpoints:

```text
POST /compras/
GET /compras/
GET /compras/{id_compra}
POST /compras/{id_compra}/confirmar   # genera movimiento ENTRADA_COMPRA
POST /compras/{id_compra}/anular      # revierte el stock si estaba confirmada
```

---

### Comercio: Inventario

Endpoints:

```text
GET /inventario/
GET /inventario/{id_producto}
GET /inventario/movimientos/
POST /inventario/ajustes
GET /inventario/alertas/stock
GET /inventario/alertas/vencimiento
POST /inventario/lotes
GET /inventario/lotes/
```

---

### Comercio: Ventas

Endpoints:

```text
POST /ventas/                      # venta directa (mostrador)
GET /ventas/
GET /ventas/resumen
GET /ventas/reporte
GET /ventas/mis-pedidos            # CLIENTE, solo lo propio
POST /ventas/solicitar             # CLIENTE, crea venta PENDIENTE desde /tienda
POST /ventas/{id_venta}/checkout   # inicia pago con la pasarela configurada
GET /ventas/{id_venta}
POST /ventas/{id_venta}/anular     # revierte el stock si estaba confirmada
POST /ventas/{id_venta}/confirmar
```

---

### Reportes

Endpoint:

```text
GET /reportes/kpis   # consolida clientes activos, recaudación, rutinas IA, progreso promedio
```

---

### Webhooks

Endpoint:

```text
POST /webhooks/pagos   # notificación asíncrona de la pasarela de pagos
```

Nota: hoy sin validación de firma/origen para un proveedor real (ver `Pendientes.md` P-02); solo lo dispara `MockGateway`.

---

## 7. Flujo de Autenticación

```text
Usuario
   ↓
POST /usuarios/login
   ↓
Validar correo
   ↓
Validar contraseña
   ↓
Generar JWT
   ↓
Retornar Token
   ↓
Frontend almacena token
   ↓
Acceso autorizado
```

---

## 8. Variables de Entorno

Archivo:

```text
backend/.env
```

Contenido:

```env
DATABASE_URL=postgresql://postgres:keen123@localhost:5432/gleyforgym

CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME

SECRET_KEY=clave_super_secreta_gleyforgym

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 9. Seguridad

### JWT

Protege:

- Usuarios
- Clientes
- Pagos
- Rutinas
- Nutrición

---

### Bcrypt

Protege:

- Contraseñas

---

### Roles

Roles soportados:

```text
ADMIN
ENTRENADOR
CLIENTE
```

---

## 10. Reglas Críticas

### Regla 1

```text
usuarios = login
clientes = negocio
```

---

### Regla 2

```text
Todos los procesos usan id_cliente
```

---

### Regla 3

```text
No usar id_usuario para
rutinas, pagos, progreso,
nutrición o membresías
```

---

### Regla 4

```text
precio_asignado conserva
el precio histórico
```

---

## 11. Estado Actual

### Implementado

- FastAPI
- PostgreSQL
- JWT
- SQLAlchemy
- Cloudinary
- IA Rutinas
- IA Nutrición
- CRUDs completos
- Auditoría (`registros_auditoria` + `routes/auditoria.py` — ya implementada, corrige la versión anterior que la listaba como "futuro")
- Módulo Comercio completo (categorías, productos, proveedores, compras, inventario con lotes/movimientos, ventas)
- Avisos editables
- Rate limiting de login (`rate_limit.py`, 5 intentos / 15 min, en memoria)
- Pasarela de pagos con patrón strategy (`pagos_gateway/`), hoy con `MockGateway`
- Generación de PDF de comprobantes (`recibos.py`, reportlab)
- 48 tests en `test_backend.py` + 7 en `test_crud.py` (pytest + pytest-cov)

### Futuro

- Docker
- Logs avanzados / APM (Sentry u otro)
- SaaS Multi Gimnasio
- Microservicios
- Pasarela de pago real (Culqi) en vez de `MockGateway` (ver `Pendientes.md` P-02)
- Página propia en `web-admin` para Entrenadores y Auditoría

---