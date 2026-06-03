# Troubleshooting

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento reúne los problemas más frecuentes que pueden ocurrir durante el uso, desarrollo, instalación o despliegue del SistemaGimnasioGleyforGym.

Incluye soluciones recomendadas para Backend, Frontend, PostgreSQL, Flutter, Cloudinary y autenticación JWT.

---

# 2. Problemas de Backend

## Error

```text
ModuleNotFoundError
```

### Ejemplo

```text
ModuleNotFoundError: No module named 'fastapi'
```

### Causa

Dependencias no instaladas.

### Solución

Activar entorno virtual:

```bash
venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## Error

```text
Could not import module app.main
```

### Causa

Ruta incorrecta.

### Solución

Ubicarse dentro de:

```text
backend
```

y ejecutar:

```bash
uvicorn app.main:app --reload
```

---

## Error

```text
Address already in use
```

### Causa

Puerto ocupado.

### Solución

Verificar procesos:

```bash
netstat -ano | findstr :8000
```

Finalizar proceso:

```bash
taskkill /PID numeroPID /F
```

O utilizar otro puerto:

```bash
uvicorn app.main:app --reload --port 8001
```

---

# 3. Problemas PostgreSQL

## Error

```text
connection refused
```

### Causa

PostgreSQL apagado.

### Solución

Verificar servicio PostgreSQL.

Windows:

```text
services.msc
```

Buscar:

```text
postgresql
```

Iniciar servicio.

---

## Error

```text
database "gleyforgym" does not exist
```

### Solución

Crear base:

```sql
CREATE DATABASE gleyforgym;
```

---

## Error

```text
password authentication failed
```

### Causa

Usuario o contraseña incorrectos.

### Solución

Verificar:

```env
DATABASE_URL
```

Ejemplo:

```env
DATABASE_URL=postgresql://postgres:keen123@localhost:5432/gleyforgym
```

---

# 4. Problemas .env

## Error

```text
DATABASE_URL = None
```

### Causa

Variables no cargadas.

### Solución

Verificar:

```text
backend/.env
```

Debe existir:

```env
DATABASE_URL=postgresql://postgres:keen123@localhost:5432/gleyforgym
```

---

## Error

```text
.env no funciona
```

### Causa

Archivo incorrecto.

### Incorrecto

```text
.env.txt
```

### Correcto

```text
.env
```

---

# 5. Problemas JWT

## Error

```text
401 Unauthorized
```

### Causa

Token inválido o expirado.

### Solución

Cerrar sesión.

Iniciar sesión nuevamente.

---

## Error

```text
Token missing
```

### Causa

No existe token en localStorage.

### Solución

Verificar login.

---

## Verificar

Abrir consola:

```javascript
localStorage.getItem("token")
```

---

# 6. Problemas React

## Error

```text
Failed to fetch
```

### Causa

Backend apagado.

### Solución

Verificar:

```text
http://127.0.0.1:8000/docs
```

---

## Error

```text
Cannot GET /ruta
```

### Causa

Ruta React incorrecta.

### Solución

Verificar:

```jsx
<Route path="..." />
```

---

## Error

```text
Module not found
```

### Solución

Instalar dependencias:

```bash
npm install
```

---

## Error

```text
react-icons no encontrado
```

### Solución

```bash
npm install react-icons
```

---

# 7. Problemas Flutter

## Error

```text
flutter no se reconoce como comando
```

### Solución Temporal

```bash
D:\flutter\bin\flutter run -d chrome
```

---

### Solución Permanente

Agregar:

```text
D:\flutter\bin
```

al PATH de Windows.

---

## Error

```text
No devices found
```

### Solución

Verificar:

```bash
flutter devices
```

---

## Error

```text
pubspec.yaml dependencies not found
```

### Solución

```bash
flutter pub get
```

---

# 8. Problemas Cloudinary

## Error

```text
Must supply api_key
```

### Causa

Cloudinary mal configurado.

### Solución

Verificar:

```env
CLOUDINARY_URL
```

Ejemplo:

```env
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

---

## Error

```text
Upload failed
```

### Causa

Archivo inválido.

### Solución

Verificar:

- Tamaño del archivo.
- Formato permitido.
- Conexión a internet.

---

# 9. Problemas de IA

## Error

```text
No se genera rutina
```

### Posibles Causas

No existen ejercicios activos.

---

### Solución

Verificar:

```text
Ejercicios
```

Estado:

```text
ACTIVO
```

---

## Error

```text
No se genera nutrición
```

### Posibles Causas

No existen comidas activas.

### Solución

Verificar:

```text
Comidas
```

Estado:

```text
ACTIVO
```

---

# 10. Problemas de Membresías

## Error

```text
Precio incorrecto
```

### Causa

Uso de precio actual.

### Solución

Siempre utilizar:

```text
precio_asignado
```

---

## Error

```text
Estado VENCIDA
```

### Solución

Actualizar a:

```text
TERMINADA
```

---

# 11. Problemas de Clientes

## Error

```text
Edad incorrecta
```

### Solución

Verificar:

```text
fecha_nacimiento
```

La edad no debe editarse manualmente.

---

## Error

```text
Cliente sin usuario
```

### Solución

Verificar relación:

```text
usuarios.id_usuario
        ↓
clientes.id_usuario
```

---

# 12. Problemas de Permisos

## Error

```text
No puedo acceder a una pantalla
```

### Causa

Rol sin permisos.

### Solución

Verificar:

```text
ADMIN
ENTRENADOR
CLIENTE
```

y configuración de:

```text
ProtectedRoute.jsx
```

---

# 13. Problemas Git

## Error

```text
Merge conflict
```

### Solución

Resolver conflictos manualmente.

---

Actualizar rama:

```bash
git pull origin develop
```

---

## Error

```text
Push rejected
```

### Solución

Actualizar:

```bash
git pull
```

Luego:

```bash
git push
```

---

# 14. Verificaciones Rápidas

## Backend

```text
http://127.0.0.1:8000/docs
```

Debe abrir Swagger.

---

## Frontend

```text
http://localhost:5173
```

Debe mostrar Login o Inicio.

---

## PostgreSQL

```sql
SELECT NOW();
```

Debe responder correctamente.

---

## Flutter

```bash
flutter doctor
```

Debe mostrar:

```text
No issues found
```

---

# 15. Regla Más Importante

## Nunca confundir

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
Login
   ↓
id_usuario
   ↓
GET /clientes/usuario/{id_usuario}
   ↓
id_cliente
```

---

## Incorrecto

```text
Login
   ↓
id_usuario
   ↓
Rutinas
```

---

# 16. Contacto Técnico

Proyecto:

```text
SistemaGimnasioGleyforGym
```

Versión:

```text
2.0 Web
```

Documentación relacionada:

```text
Manual_Desarrollador.md
Guia_Instalacion.md
Guia_Despliegue.md
FAQ.md
```

---