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

> **Actualizado 2026-09**: la versión anterior de este documento no incluía las páginas de Comercio, Avisos, ni los archivos de tests/hooks/constants reales.

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
│   ├── hooks
│   │   └── useClienteActual.js   # resuelve id_cliente del CLIENTE logueado, usado en 6 páginas "Mi*"
│   │
│   ├── constants
│   │
│   ├── utils
│   │   └── exportarCsv.js
│   │
│   ├── components
│   │   ├── Layout.jsx
│   │   ├── Navbar.jsx            # nav público (Inicio/Avisos/Tienda)
│   │   └── ProtectedRoute.jsx
│   │
│   ├── pages
│   │   ├── Inicio.jsx
│   │   ├── Login.jsx
│   │   ├── ResetPassword.jsx
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
│   │   ├── Avisos.jsx            # vista pública
│   │   ├── GestionAvisos.jsx     # gestión ADMIN
│   │   ├── Tienda.jsx            # vista pública del catálogo de productos
│   │   ├── Categorias.jsx
│   │   ├── Productos.jsx
│   │   ├── Proveedores.jsx
│   │   ├── Compras.jsx
│   │   ├── Inventario.jsx
│   │   ├── Ventas.jsx
│   │   ├── MiPerfil.jsx
│   │   ├── MiRutina.jsx
│   │   ├── MiNutricion.jsx
│   │   ├── MiProgreso.jsx
│   │   ├── MiMembresia.jsx
│   │   ├── MisPagos.jsx
│   │   └── NotFound.jsx
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
│
└── package.json
```

> No existen páginas `Entrenadores.jsx` ni `Auditoria.jsx` (ver sección 13, "Futuro").

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

### Rutas Públicas (ampliación 2026-09)

```text
/reset-password
/tienda
/avisos
```

---

### Rutas Comercio (solo ADMIN)

```text
/categorias
/productos
/proveedores
/compras
/inventario
/ventas
```

---

### Rutas Avisos (solo ADMIN)

```text
/gestion-avisos
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

> Corregido 2026-09: la URL base **no está hardcodeada**, se lee de la variable de entorno `VITE_API_URL` (ver `render.yaml` y `.env.example`).

```javascript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});
```

---

## 6. Gestión de Sesión

Después del login se almacena en `localStorage` (no `sessionStorage`):

```javascript
localStorage.setItem("token", token);
localStorage.setItem("rol", rol);
localStorage.setItem("id_usuario", id_usuario);
localStorage.setItem("correo", correo);
```

El interceptor de respuesta de `api.js` reacciona solo ante **401** (token ausente/inválido/expirado o usuario desactivado): limpia `localStorage` y redirige a `/login`. Un **403** (rol sin permiso, con sesión válida) no cierra la sesión.

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
- GestionAvisos
- Categorias, Productos, Proveedores, Compras, Inventario, Ventas

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
✅ Dashboard Admin / Entrenador / Cliente
✅ ProtectedRoute + Navbar público
✅ Layout global
✅ CRUDs completos
✅ Integración IA
✅ Cloudinary
✅ Módulo Comercio (Categorías, Productos, Proveedores, Compras, Inventario, Ventas, Tienda pública)
✅ Avisos (público + gestión ADMIN)
✅ Autogestión de contraseña (ResetPassword.jsx)
✅ Hook compartido `useClienteActual`
✅ 31 archivos `*.test.jsx` (Vitest + @testing-library/react)

### Futuro

- Exportación PDF de rutinas/planes nutricionales (hoy solo comprobantes de pago)
- Notificaciones de vencimiento de membresía
- Página propia para gestión de Entrenadores (hoy vía `Usuarios.jsx`)
- Página propia para consultar Auditoría (hoy solo API)
- Tests para `Navbar.jsx`, `NotFound.jsx` y todo el módulo Comercio (0% de cobertura frontend, ver `Pendientes.md` P-04/P-08)
- Tema claro/oscuro dinámico
- CI/CD (no existe `.github/workflows`)

---