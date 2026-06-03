# Arquitectura Móvil

# SistemaGimnasioGleyforGym

## 1. Introducción

La aplicación móvil del SistemaGimnasioGleyforGym está desarrollada utilizando Flutter.

Su objetivo es proporcionar a los clientes del gimnasio acceso rápido y seguro a su información personal, rutinas de entrenamiento, planes nutricionales, pagos y progreso físico desde dispositivos móviles.

La aplicación consume los servicios REST expuestos por FastAPI.

---

## 2. Tecnologías Utilizadas

| Componente | Tecnología |
|------------|------------|
| Framework Móvil | Flutter |
| Lenguaje | Dart |
| Comunicación API | HTTP |
| Backend Consumido | FastAPI |
| Autenticación | JWT |
| Base de Datos | PostgreSQL (a través de API) |

---

## 3. Estructura General

```text
mobile-app
│
└── gleyforgym_app
    │
    └── lib
        │
        ├── main.dart
        │
        ├── services
        │   └── api_service.dart
        │
        └── screens
            ├── login_screen.dart
            ├── home_screen.dart
            ├── rutinas_screen.dart
            ├── nutricion_screen.dart
            ├── pagos_screen.dart
            ├── progreso_screen.dart
            └── membresia_screen.dart
```

---

## 4. Arquitectura de la Aplicación

La aplicación sigue una arquitectura basada en capas.

```text
┌───────────────────────┐
│       Screens         │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│      Api Service      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│      FastAPI API      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│      PostgreSQL       │
└───────────────────────┘
```

---

## 5. Pantallas del Sistema

### login_screen.dart

Responsabilidades:

- Iniciar sesión.
- Consumir `/usuarios/login`.
- Obtener JWT.
- Obtener rol.
- Obtener id_usuario.

---

### home_screen.dart

Responsabilidades:

- Menú principal.
- Acceso a módulos.
- Navegación general.

---

### rutinas_screen.dart

Responsabilidades:

- Consultar rutina del cliente.
- Mostrar ejercicios.
- Mostrar series.
- Mostrar repeticiones.
- Mostrar videos.

Endpoint utilizado:

```text
GET /rutinas/cliente/{id_cliente}
```

---

### nutricion_screen.dart

Responsabilidades:

- Consultar plan nutricional.
- Mostrar comidas.
- Mostrar calorías.
- Mostrar macronutrientes.

Endpoint utilizado:

```text
GET /nutricion/cliente/{id_cliente}
```

---

### pagos_screen.dart

Responsabilidades:

- Mostrar historial de pagos.

Endpoint utilizado:

```text
GET /pagos/cliente/{id_cliente}
```

---

### progreso_screen.dart

Responsabilidades:

- Mostrar evolución física.
- Mostrar historial de registros.

Endpoint utilizado:

```text
GET /progreso/cliente/{id_cliente}
```

---

### membresia_screen.dart

Responsabilidades:

- Mostrar membresía actual.
- Mostrar fechas.
- Mostrar precio asignado.
- Mostrar estado.

Endpoint utilizado:

```text
GET /cliente-membresias/cliente/{id_cliente}
```

---

## 6. Servicio de Comunicación

### api_service.dart

Responsable de:

- Realizar peticiones HTTP.
- Gestionar autenticación.
- Centralizar llamadas al backend.

Ejemplo:

```dart
final response = await http.get(
  Uri.parse('$baseUrl/clientes')
);
```

---

## 7. Flujo de Autenticación

### Paso 1

El cliente ingresa:

```text
Correo
Contraseña
```

---

### Paso 2

Flutter consume:

```text
POST /usuarios/login
```

---

### Paso 3

El backend retorna:

```json
{
  "token": "...",
  "usuario": {
    "id_usuario": 1,
    "rol": "CLIENTE"
  }
}
```

---

### Paso 4

La aplicación almacena:

```text
token
id_usuario
rol
```

---

### Paso 5

Obtiene el cliente asociado:

```text
GET /clientes/usuario/{id_usuario}
```

---

### Paso 6

Obtiene:

```text
id_cliente
```

---

### Paso 7

Utiliza id_cliente para:

- Rutinas
- Nutrición
- Pagos
- Progreso
- Membresías

---

## 8. Regla Principal

### Correcto

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

### Incorrecto

```text
Login
   ↓
id_usuario
   ↓
Usar id_usuario para rutinas
```

Esto está prohibido por las reglas del sistema.

---

## 9. Seguridad

La aplicación móvil utiliza:

### JWT

Para autenticación.

### HTTPS

Para futuras implementaciones en producción.

### Control de Roles

Actualmente:

```text
CLIENTE
```

---

## 10. Funcionalidades Disponibles

### Perfil

- Consultar información personal.

### Rutinas

- Consultar rutina actual.
- Consultar detalle de ejercicios.
- Consultar videos.

### Nutrición

- Consultar plan nutricional.
- Consultar comidas recomendadas.

### Pagos

- Consultar historial de pagos.

### Progreso

- Consultar evolución física.

### Membresía

- Consultar estado.
- Consultar fechas.
- Consultar precio asignado.

---

## 11. Estado Actual

### Implementado

✅ Login

✅ Navegación básica

✅ Integración con API

✅ Rutinas

✅ Nutrición

✅ Pagos

✅ Progreso

✅ Membresías

---

## Mejoras Futuras

- Notificaciones Push
- Descarga PDF
- Gráficos estadísticos
- Recordatorios de entrenamiento
- Recordatorios nutricionales
- Registro biométrico
- Integración con wearables

---

## 12. Consideraciones Importantes

La aplicación móvil no accede directamente a PostgreSQL.

Todo acceso a datos se realiza mediante:

```text
Flutter
    ↓
FastAPI
    ↓
PostgreSQL
```

Esto garantiza:

- Seguridad
- Escalabilidad
- Mantenibilidad
- Compatibilidad SaaS

---