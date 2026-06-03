# Manual del Desarrollador

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento sirve como guía para desarrolladores que participen en el mantenimiento, mejora o expansión del SistemaGimnasioGleyforGym.

Describe la arquitectura, convenciones, estructura de carpetas, flujo de trabajo y reglas fundamentales del proyecto.

---

# 2. Información General

## Nombre del Proyecto

SistemaGimnasioGleyforGym

---

## Tecnologías Principales

| Componente | Tecnología |
|------------|------------|
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Base de Datos | PostgreSQL |
| Frontend | React + Vite |
| App Móvil | Flutter |
| Seguridad | JWT |
| Multimedia | Cloudinary |
| IA | Python |

---

# 3. Arquitectura General

```text
React
   │
   ▼
FastAPI
   │
   ▼
PostgreSQL

Flutter
   │
   ▼
FastAPI

Cloudinary
   │
   ▼
Videos Ejercicios
```

---

# 4. Estructura del Proyecto

```text
gleyforgym
│
├── backend
├── web-admin
├── mobile-app
├── docs
└── database
```

---

# 5. Estructura Backend

```text
backend
│
├── app
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   │
│   ├── routes
│   └── ia
│
├── .env
└── requirements.txt
```

---

# 6. Estructura Frontend

```text
web-admin
│
├── src
│   ├── api
│   ├── assets
│   ├── components
│   ├── pages
│   ├── App.jsx
│   └── main.jsx
```

---

# 7. Estructura Flutter

```text
mobile-app
│
└── gleyforgym_app
    │
    ├── services
    │   └── api_service.dart
    └── screens
        ├── home_screen.dart
        ├── login_screen.dart
        ├── membresia_screen.dart
        ├── nutricion_screen.dart
        ├── pagos_screen.dart
        ├── progreso_screen.dart
        ├── rutinas_screen.dart
        └── rutina_detalle_screen.dart
```

---

# 8. Regla Más Importante

Nunca confundir:

```text
usuarios
```

con

```text
clientes
```

---

## Correcto

```text
usuarios = acceso al sistema

clientes = negocio del gimnasio
```

---

## Flujo Obligatorio

```text
Login
   ↓
id_usuario
   ↓
GET /clientes/usuario/{id_usuario}
   ↓
id_cliente
   ↓
Procesos del gimnasio
```

---

# 9. Procesos que Deben Utilizar id_cliente

Siempre:

```text
Rutinas
Nutrición
Pagos
Asistencias
Progreso
Membresías
```

Nunca:

```text
id_usuario
```

---

# 10. Variables de Entorno

Ubicación:

```text
backend/.env
```

Configuración:

```env
DATABASE_URL=postgresql://postgres:keen123@localhost:5432/gleyforgym

SECRET_KEY=clave_super_secreta_gleyforgym

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

---

# 11. Levantar Backend

```bash
cd backend

venv\Scripts\activate

uvicorn app.main:app --reload
```

Acceso:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 12. Levantar Frontend

```bash
cd web-admin

npm install

npm run dev
```

Acceso:

```text
http://localhost:5173
```

---

# 13. Levantar Flutter

```bash
cd mobile-app/gleyforgym_app

flutter pub get

flutter run
```

---

# 14. Crear un Nuevo Endpoint

## Paso 1

Crear función en:

```text
routes
```

Ejemplo:

```python
@router.get("/clientes")
def obtener_clientes():
    pass
```

---

## Paso 2

Registrar router en:

```python
main.py
```

```python
app.include_router(...)
```

---

## Paso 3

Validar en Swagger.

---

# 15. Crear una Nueva Pantalla React

## Paso 1

Crear archivo:

```text
src/pages
```

Ejemplo:

```text
NuevaVista.jsx
```

---

## Paso 2

Registrar ruta:

```jsx
<Route path="/nueva-ruta" />
```

---

## Paso 3

Agregar opción al menú.

---

# 16. Crear una Nueva Tabla

## Paso 1

Agregar modelo en:

```text
models.py
```

---

## Paso 2

Agregar schemas.

```text
schemas.py
```

---

## Paso 3

Agregar router.

```text
routes/
```

---

## Paso 4

Registrar router.

```text
main.py
```

---

# 17. Convenciones de Código

## Python

### Variables

```python
nombre_cliente
fecha_inicio
precio_asignado
```

---

### Funciones

```python
obtener_cliente()

crear_rutina()

generar_plan()
```

---

## React

### Componentes

```jsx
Clientes.jsx

MiRutina.jsx

DetalleCliente.jsx
```

---

### Hooks

```jsx
useEffect()

useState()
```

---

# 18. Convenciones de Base de Datos

## Claves Primarias

```text
id_usuario

id_cliente

id_membresia
```

---

## Claves Foráneas

```text
id_usuario

id_cliente

id_membresia
```

---

## Estados

Utilizar:

```text
ACTIVO
INACTIVO
```

---

Membresías:

```text
ACTIVA
PAUSADA
TERMINADA
CANCELADA
```

---

No utilizar:

```text
VENCIDA
```

---

# 19. Reglas de Negocio Críticas

## Edad

No se ingresa manualmente.

Se calcula desde:

```text
fecha_nacimiento
```

---

## Precio Histórico

Siempre utilizar:

```text
precio_asignado
```

Nunca:

```text
membresia.precio
```

para membresías antiguas.

---

## IA

Solo utilizar:

```text
ejercicios activos

comidas activas
```

---

# 20. Flujo Git Recomendado

```text
main
│
├── develop
│
├── feature/frontend
├── feature/backend
├── feature/mobile
└── feature/ia
```

---

# 21. Checklist Antes de Subir Cambios

Verificar:

- Backend compila.
- Frontend compila.
- Flutter compila.
- No hay errores en Swagger.
- No hay credenciales expuestas.
- No se rompió la regla usuario/cliente.

---

# 22. Problemas Frecuentes

## Error

```text
Cloudinary Must supply api_key
```

Solución:

Verificar:

```env
CLOUDINARY_URL
```

---

## Error

```text
Failed to fetch
```

Verificar:

```python
CORS
```

---

## Error

```text
401 Unauthorized
```

Verificar:

```text
JWT
```

---

## Error

```text
404 Not Found
```

Verificar:

```text
Router registrado
```

---

# 23. Estado Actual

## Implementado

✅ Backend FastAPI

✅ PostgreSQL

✅ React

✅ Flutter

✅ JWT

✅ Cloudinary

✅ IA Rutinas

✅ IA Nutrición

✅ Dashboards

✅ CRUDs completos

---

## Futuro

- Docker
- SaaS Multi Gimnasio
- Reportes PDF
- Notificaciones
- Analítica avanzada
- Machine Learning

---

# 24. Contacto del Proyecto

Proyecto académico y de investigación enfocado en la automatización de gimnasios mediante tecnologías web, móviles e inteligencia artificial.

Sistema:

```text
SistemaGimnasioGleyforGym
```

Versión actual:

```text
v2.6
```

---