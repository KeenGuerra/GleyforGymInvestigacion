# Arquitectura Frontend

# SistemaGimnasioGleyforGym

## 1. Introducción

El frontend del SistemaGimnasioGleyforGym está desarrollado utilizando React y Vite.

Su objetivo es proporcionar una interfaz moderna, intuitiva y responsiva para los diferentes usuarios del sistema.

La aplicación web permite la gestión administrativa, deportiva y nutricional del gimnasio mediante una interfaz centralizada.

---

## 2. Tecnologías Utilizadas

| Componente | Tecnología |
|------------|------------|
| Framework Frontend | React |
| Bundler | Vite |
| Navegación | React Router DOM |
| Consumo API | Axios |
| Gráficos | Recharts |
| Iconografía | React Icons |
| Estilos | CSS3 |

---

## 3. Estructura General

```text
web-admin
│
├── src
│   │
│   ├── api
│   │   └── api.js
│   │
│   ├── assets
│   │   ├── logo-gleyforgym.jpeg
│   │   ├── gym-hero.jpeg
│   │   └── icono.png
│   │
│   ├── components
│   │   ├── Layout.jsx
│   │   └── ProtectedRoute.jsx
│   │
│   ├── pages
│   │   ├── Inicio.jsx
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── DashboardAdmin.jsx
│   │   ├── DashboardEntrenador.jsx
│   │   ├── DashboardCliente.jsx
│   │   ├── Usuarios.jsx
│   │   ├── Clientes.jsx
│   │   ├── DetalleCliente.jsx
│   │   ├── Membresias.jsx
│   │   ├── ClienteMembresias.jsx
│   │   ├── Pagos.jsx
│   │   ├── Asistencias.jsx
│   │   ├── Progreso.jsx
│   │   ├── Ejercicios.jsx
│   │   ├── Comidas.jsx
│   │   ├── Rutinas.jsx
│   │   ├── DetalleRutina.jsx
│   │   ├── Nutricion.jsx
│   │   ├── MiPerfil.jsx
│   │   ├── MiRutina.jsx
│   │   ├── MiNutricion.jsx
│   │   ├── MiProgreso.jsx
│   │   ├── MiMembresia.jsx
│   │   └── MisPagos.jsx
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
│
└── package.json
```

---

## 4. Arquitectura de Navegación

La aplicación utiliza React Router DOM para gestionar la navegación.

### Rutas Públicas

```text
/
```

Página principal del gimnasio.

---

```text
/login
```

Pantalla de autenticación.

---

### Rutas Protegidas

Accesibles únicamente mediante JWT válido.

```text
/dashboard
```

---

```text
/usuarios
```

---

```text
/clientes
```

---

```text
/clientes/:id/detalle
```

---

```text
/membresias
```

---

```text
/cliente-membresias
```

---

```text
/pagos
```

---

```text
/asistencias
```

---

```text
/progreso
```

---

```text
/ejercicios
```

---

```text
/comidas
```

---

```text
/rutinas
```

---

```text
/rutinas/:id/detalle
```

---

```text
/nutricion
```

---

```text
/mi-perfil
```

---

```text
/mi-rutina
```

---

```text
/mi-nutricion
```

---

```text
/mi-progreso
```

---

```text
/mi-membresia
```

---

```text
/mis-pagos
```

---

## 5. Componentes Globales

### Layout.jsx

Responsable de:

- Sidebar
- Navegación
- Menú por rol
- Encabezado general

---

### ProtectedRoute.jsx

Responsable de:

- Validar token JWT
- Validar rol
- Restringir acceso

---

### api.js

Responsable de:

- Configuración Axios
- URL base
- Interceptor JWT

```javascript
const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});
```

---

## 6. Gestión de Sesión

Después del login se almacena:

```javascript
localStorage.setItem("token", token);
localStorage.setItem("rol", rol);
localStorage.setItem("id_usuario", id_usuario);
localStorage.setItem("correo", correo);
```

---

## 7. Control de Acceso

### Rol ADMIN

Acceso a:

- DashboardAdmin
- Usuarios
- Clientes
- Membresias
- ClienteMembresias
- Pagos
- Asistencias
- Progreso
- Ejercicios
- Comidas
- Rutinas
- Nutricion

---

### Rol ENTRENADOR

Acceso a:

- DashboardEntrenador
- Clientes
- Asistencias
- Progreso
- Ejercicios
- Comidas
- Rutinas
- Nutricion

---

### Rol CLIENTE

Acceso a:

- DashboardCliente
- MiPerfil
- MiRutina
- MiNutricion
- MiProgreso
- MiMembresia
- MisPagos

---

## 8. Landing Page

### Inicio.jsx

Componentes principales:

- Navbar
- Hero principal
- Membresías dinámicas
- Beneficios
- Contacto
- Redes sociales
- Ubicación
- Footer

---

## 9. Flujo de Login

```text
Usuario
   ↓
Login.jsx
   ↓
POST /usuarios/login
   ↓
JWT
   ↓
LocalStorage
   ↓
Dashboard según rol
```

---

## 10. Flujo Cliente

```text
Login
   ↓
id_usuario
   ↓
GET /clientes/usuario/{id_usuario}
   ↓
id_cliente
   ↓
Rutinas
Nutrición
Pagos
Progreso
Membresía
```

---

## 11. Diseño Visual

Tema principal:

```text
Modo Oscuro
```

Color principal:

```text
#ff6600
```

Características:

- Diseño responsivo
- Cards modernas
- Tablas administrativas
- Sidebar fijo
- Navegación intuitiva

---

## 12. Comunicación con Backend

Todas las solicitudes utilizan:

```text
Axios
```

Formato:

```javascript
api.get("/clientes/");
api.post("/pagos/");
api.put("/clientes/1");
api.delete("/membresias/1");
```

---

## 13. Estado Actual

### Implementado

✅ Login por roles  
✅ Landing pública  
✅ Dashboard Admin  
✅ Dashboard Entrenador  
✅ Dashboard Cliente  
✅ ProtectedRoute  
✅ Layout global  
✅ CRUDs completos  
✅ Integración IA  
✅ Cloudinary

### Futuro

- Gráficos avanzados
- Exportación PDF
- Notificaciones
- Tema claro/oscuro dinámico
- Dashboard analítico

---