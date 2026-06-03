# Convenciones de Código

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento define los estándares de desarrollo que deben seguir todos los colaboradores del proyecto SistemaGimnasioGleyforGym.

El objetivo es garantizar:

- Consistencia.
- Legibilidad.
- Mantenibilidad.
- Escalabilidad.
- Calidad del código.

---

# 2. Convenciones Generales

## Idioma

Todo el código deberá escribirse en:

```text
Español
```

Excepto:

- Librerías.
- Frameworks.
- Dependencias externas.

---

## Nombres Descriptivos

### Correcto

```python
obtener_cliente()

registrar_pago()

generar_rutina()
```

---

### Incorrecto

```python
a()

x()

func1()
```

---

# 3. Convenciones Backend

## Archivos

Formato:

```text
snake_case
```

Ejemplos:

```text
cliente_membresias.py

recomendador_nutricion.py

ia_rutina.py
```

---

## Variables

Formato:

```python
snake_case
```

Ejemplos:

```python
id_cliente

fecha_inicio

precio_asignado

masa_magra
```

---

## Funciones

Formato:

```python
verbo_accion_objeto
```

Ejemplos:

```python
obtener_cliente()

crear_membresia()

actualizar_pago()

generar_plan_nutricional()
```

---

## Constantes

Formato:

```python
MAYUSCULAS
```

Ejemplo:

```python
SECRET_KEY

ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES
```

---

## Clases

Formato:

```python
PascalCase
```

Ejemplos:

```python
Cliente

Usuario

PlanNutricional
```

---

# 4. Convenciones SQLAlchemy

## Modelos

Formato:

```python
PascalCase
```

Ejemplo:

```python
class Cliente(Base):
```

---

## Tablas

Formato:

```python
snake_case
```

Ejemplos:

```python
usuarios

clientes

cliente_membresias

planes_nutricionales
```

---

## Claves Primarias

Formato:

```text
id_nombre_tabla
```

Ejemplos:

```text
id_usuario

id_cliente

id_membresia

id_pago
```

---

## Claves Foráneas

Utilizar exactamente:

```text
id_usuario

id_cliente

id_membresia
```

---

# 5. Convenciones FastAPI

## Routers

Un archivo por módulo.

Ejemplo:

```text
usuarios.py

clientes.py

pagos.py
```

---

## Prefijos

Formato:

```python
prefix="/clientes"
```

---

## Endpoints

Utilizar sustantivos.

### Correcto

```http
GET /clientes

POST /clientes

GET /clientes/{id}
```

---

### Incorrecto

```http
GET /obtenerClientes

POST /crearCliente
```

---

# 6. Convenciones React

## Componentes

Formato:

```text
PascalCase
```

Ejemplos:

```text
Clientes.jsx

MiRutina.jsx

DetalleCliente.jsx
```

---

## Hooks

Formato:

```javascript
useAlgo()
```

Ejemplos:

```javascript
useState()

useEffect()
```

---

## Variables

Formato:

```javascript
camelCase
```

Ejemplos:

```javascript
idCliente

precioAsignado

fechaInicio
```

---

## Funciones

Formato:

```javascript
camelCase
```

Ejemplos:

```javascript
obtenerClientes()

guardarPago()

cargarRutina()
```

---

# 7. Convenciones Flutter

## Archivos

Formato:

```text
snake_case
```

Ejemplos:

```text
login_screen.dart

rutinas_screen.dart

api_service.dart
```

---

## Clases

Formato:

```dart
PascalCase
```

Ejemplos:

```dart
LoginScreen

RutinasScreen

ApiService
```

---

## Variables

Formato:

```dart
camelCase
```

Ejemplos:

```dart
idCliente

fechaInicio

precioAsignado
```

---

# 8. Convenciones de Base de Datos

## Estados

### Usuarios

```text
ACTIVO
INACTIVO
```

---

### Clientes

```text
ACTIVO
INACTIVO
```

---

### Membresías

```text
ACTIVA
PAUSADA
TERMINADA
CANCELADA
```

---

## No utilizar

```text
VENCIDA
```

---

# 9. Regla Crítica del Proyecto

## Correcto

```text
usuarios = login

clientes = negocio
```

---

## Flujo Obligatorio

```text
id_usuario
      ↓
GET /clientes/usuario/{id_usuario}
      ↓
id_cliente
      ↓
Procesos del gimnasio
```

---

# 10. Campos Críticos

## Precio Histórico

Siempre usar:

```text
precio_asignado
```

Nunca:

```text
membresia.precio
```

para membresías ya asignadas.

---

## Edad

Nunca ingresar manualmente.

Siempre calcular desde:

```text
fecha_nacimiento
```

---

# 11. Convenciones Git

## Branches

Formato:

```text
feature/nombre-modulo
```

Ejemplos:

```text
feature/frontend

feature/backend

feature/mobile

feature/ia
```

---

## Commits

Formato:

```text
tipo: descripción
```

Ejemplos:

```bash
feat: agregar dashboard admin

fix: corregir login

docs: actualizar arquitectura

refactor: optimizar consultas
```

---

# 12. Comentarios

Comentar únicamente lógica compleja.

### Correcto

```python
# Calcula edad automáticamente
```

---

### Incorrecto

```python
# Variable edad
edad = 25
```

---

# 13. Buenas Prácticas

## Backend

- Validar datos con Pydantic.
- No repetir código.
- Usar funciones reutilizables.

---

## Frontend

- Componentes pequeños.
- Evitar duplicación.
- Centralizar llamadas API.

---

## Base de Datos

- Mantener integridad referencial.
- Utilizar claves foráneas.
- Evitar datos duplicados.

---

# 14. Checklist Antes de Commit

Verificar:

- Código compila.
- No existen errores.
- Se respetan nombres definidos.
- No existen credenciales expuestas.
- Se respetó la regla usuario/cliente.
- Se probó la funcionalidad.

---

# 15. Estado Actual

Estas convenciones aplican a:

✅ Backend FastAPI

✅ PostgreSQL

✅ React

✅ Flutter

✅ IA

✅ Cloudinary

y deberán mantenerse en futuras versiones del SistemaGimnasioGleyforGym.

---