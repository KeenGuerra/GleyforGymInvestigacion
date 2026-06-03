# Guía de Instalación

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento describe el proceso completo para instalar y ejecutar el SistemaGimnasioGleyforGym en un entorno de desarrollo.

Incluye:

- PostgreSQL
- Backend FastAPI
- Frontend React
- Aplicación Flutter
- Cloudinary

---

# 2. Requisitos Previos

Antes de comenzar, verificar que se encuentren instalados los siguientes componentes.

## Backend

- Python 3.11 o superior
- Pip

Verificar:

```bash
python --version
pip --version
```

---

## Base de Datos

- PostgreSQL 16 o superior

Verificar:

```bash
psql --version
```

---

## Frontend

- Node.js 20 o superior
- npm

Verificar:

```bash
node -v
npm -v
```

---

## Flutter

- Flutter SDK

Verificar:

```bash
flutter --version
```

---

## Git

Verificar:

```bash
git --version
```

---

# 3. Clonar Repositorio

```bash
git clone URL_DEL_REPOSITORIO

cd gleyforgym
```

---

# 4. Configuración PostgreSQL

## Crear Base de Datos

Ingresar a PostgreSQL:

```sql
CREATE DATABASE gleyforgym;
```

---

## Verificar Base

```sql
\l
```

Debe aparecer:

```text
gleyforgym
```

---

# 5. Configuración Backend

Ubicación:

```text
backend
```

---

## Crear Entorno Virtual

```bash
cd backend

python -m venv venv
```

---

## Activar Entorno Virtual

### Windows

```bash
venv\Scripts\activate
```

---

### Linux

```bash
source venv/bin/activate
```

---

## Instalar Dependencias

```bash
pip install fastapi
pip install uvicorn
pip install sqlalchemy
pip install psycopg2-binary
pip install pydantic
pip install python-jose
pip install passlib
pip install bcrypt
pip install python-dotenv
pip install email-validator
pip install cloudinary
pip install python-multipart
```

---

## Crear Archivo .env

Ruta:

```text
backend/.env
```

Contenido:

```env
DATABASE_URL=postgresql://postgres:keen123@localhost:5432/gleyforgym

SECRET_KEY=clave_super_secreta_gleyforgym

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

---

## Ejecutar Backend

```bash
uvicorn app.main:app --reload
```

---

## Verificar Backend

Abrir:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 6. Configuración Frontend

Ubicación:

```text
web-admin
```

---

## Instalar Dependencias

```bash
npm install
```

---

## Dependencias Principales

```bash
npm install axios
npm install react-router-dom
npm install recharts
npm install react-icons
```

---

## Ejecutar Frontend

```bash
npm run dev
```

---

## Verificar Frontend

Abrir:

```text
http://localhost:5173
```

---

# 7. Configuración Flutter

Ubicación:

```text
mobile-app/gleyforgym_app
```

---

## Obtener Dependencias

```bash
flutter pub get
```

---

## Ejecutar Aplicación

```bash
flutter run
```

---

## Ejecutar en Chrome

```bash
flutter run -d chrome
```

---

# 8. Configuración Cloudinary

Crear cuenta:

```text
https://cloudinary.com
```

---

Obtener:

```text
Cloud Name
API Key
API Secret
```

---

Agregar al .env:

```env
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

---

# 9. Puertos Utilizados

| Servicio | Puerto |
|-----------|---------|
| PostgreSQL | 5432 |
| FastAPI | 8000 |
| React | 5173 |
| Flutter Web | Variable |

---

# 10. Verificación Completa

## Backend

Debe responder:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend

Debe responder:

```text
http://localhost:5173
```

---

## Flutter

Debe abrir:

```text
Login
```

---

## Base de Datos

Verificar conexión:

```sql
SELECT NOW();
```

---

# 11. Usuarios Iniciales

Ejemplo:

```text
ADMIN

Correo:
admin@gleyforgym.com

Contraseña:
Admin123*
```

---

# 12. Problemas Frecuentes

## Error

```text
venv\Scripts\activate no funciona
```

Solución:

Verificar que exista:

```text
backend/venv/Scripts/activate
```

Si no existe:

```bash
python -m venv venv
```

---

## Error

```text
Cloudinary Must supply api_key
```

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

- Backend encendido.
- CORS configurado.
- URL correcta.

---

## Error

```text
ModuleNotFoundError
```

Ejecutar:

```bash
pip install -r requirements.txt
```

---

## Error

```text
Port 8000 already in use
```

Finalizar proceso o utilizar:

```bash
uvicorn app.main:app --reload --port 8001
```

---

# 13. Orden Correcto de Ejecución

## Paso 1

Levantar PostgreSQL.

---

## Paso 2

Levantar Backend.

```bash
cd backend

venv\Scripts\activate

uvicorn app.main:app --reload
```

---

## Paso 3

Levantar Frontend.

```bash
cd web-admin

npm run dev
```

---

## Paso 4

Levantar Flutter.

```bash
cd mobile-app/gleyforgym_app

flutter run
```

---

# 14. Estado Actual

## Funcionalidades Disponibles

✅ Login

✅ Usuarios

✅ Clientes

✅ Membresías

✅ Pagos

✅ Asistencias

✅ Progreso

✅ Ejercicios

✅ Comidas

✅ IA Rutinas

✅ IA Nutrición

✅ Cloudinary

✅ Dashboards

---

## Próximas Funcionalidades

- Docker
- SaaS
- Reportes PDF
- Notificaciones
- Analítica Avanzada

---