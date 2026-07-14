import React, { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import logo from "../assets/icono.png";
import { FaBars, FaTimes } from "react-icons/fa";

export default function Layout() {
  const navigate = useNavigate();
  const rol = localStorage.getItem("rol");
  const correo = localStorage.getItem("correo");
  const [menuOpen, setMenuOpen] = useState(false);

  const cerrarSesion = () => {
    localStorage.clear();
    navigate("/");
  };

  let inicial = "C";
  if (rol === "ADMIN") {
    inicial = "A";
  } else if (rol === "ENTRENADOR") {
    inicial = "E";
  }

  let tituloPanel = "Panel cliente";
  if (rol === "ADMIN") {
    tituloPanel = "Panel administrativo";
  } else if (rol === "ENTRENADOR") {
    tituloPanel = "Panel entrenador";
  }

  return (
    <div className="layout">
      {/* Mobile Top Bar */}
      <header className="mobile-header">
        <button className="menu-toggle" onClick={() => setMenuOpen(true)}>
          <FaBars />
        </button>
        <div className="mobile-logo" onClick={() => navigate("/")}>
          <img src={logo} alt="GleyforGym Logo" />
          <span>GLEYFORGYM</span>
        </div>
      </header>

      {/* Overlay Backdrop */}
      {menuOpen && (
        <div className="sidebar-overlay" onClick={() => setMenuOpen(false)} />
      )}

      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <div className="sidebar-brand">
          <div className="brand-icon">
            <img src={logo} alt="GleyforGym" />
          </div>

          <div>
            <h2>GLEYFORGYM</h2>
            <span>Sistema de gestión</span>
          </div>

          <button className="sidebar-close" onClick={() => setMenuOpen(false)}>
            <FaTimes />
          </button>
        </div>

        <nav className="sidebar-menu" onClick={() => setMenuOpen(false)}>
          <NavLink to="/dashboard">Panel principal</NavLink>

          {rol === "ADMIN" && (
            <>
              <p className="menu-label">Administración</p>
              <NavLink to="/clientes">Clientes</NavLink>
              <NavLink to="/usuarios">Usuarios</NavLink>
              <NavLink to="/membresias">Planes</NavLink>
              <NavLink to="/cliente-membresias">Asignar membresía</NavLink>
              <NavLink to="/pagos">Pagos</NavLink>
              <NavLink to="/asistencias">Asistencias</NavLink>
              <NavLink to="/progreso">Progreso</NavLink>

              <p className="menu-label">IA y contenido</p>
              <NavLink to="/ejercicios">Ejercicios</NavLink>
              <NavLink to="/comidas">Comidas</NavLink>
              <NavLink to="/rutinas">Rutinas IA</NavLink>
              <NavLink to="/nutricion">Nutrición IA</NavLink>

              <p className="menu-label">Comercio</p>
              <NavLink to="/categorias">Categorías</NavLink>
              <NavLink to="/productos">Productos</NavLink>
              <NavLink to="/proveedores">Proveedores</NavLink>
              <NavLink to="/compras">Compras</NavLink>
              <NavLink to="/inventario">Inventario</NavLink>
              <NavLink to="/ventas">Ventas</NavLink>
            </>
          )}

          {rol === "ENTRENADOR" && (
            <>
              <p className="menu-label">Entrenamiento</p>
              <NavLink to="/clientes">Clientes</NavLink>
              <NavLink to="/asistencias">Asistencias</NavLink>
              <NavLink to="/progreso">Progreso</NavLink>
              <NavLink to="/ejercicios">Ejercicios</NavLink>
              <NavLink to="/comidas">Comidas</NavLink>
              <NavLink to="/rutinas">Rutinas IA</NavLink>
              <NavLink to="/nutricion">Nutrición IA</NavLink>
            </>
          )}

          {rol === "CLIENTE" && (
            <>
              <p className="menu-label">Mi cuenta</p>
              <NavLink to="/mi-perfil">Mi perfil</NavLink>
              <NavLink to="/mi-rutina">Mi rutina</NavLink>
              <NavLink to="/mi-nutricion">Mi nutrición</NavLink>
              <NavLink to="/mi-progreso">Mi progreso</NavLink>
              <NavLink to="/mi-membresia">Mi membresía</NavLink>
              <NavLink to="/mis-pagos">Mis pagos</NavLink>
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="profile-avatar">{inicial}</div>

            <div>
              <strong>{rol}</strong>
              <small>{correo || "usuario@gleyforgym.com"}</small>
            </div>
          </div>

          <button className="btn-secondary" onClick={cerrarSesion}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="contenido">
        <header className="page-header-pro">
          <div>
            <span className="badge">{rol}</span>

            <h1>{tituloPanel}</h1>

            <p>Gestiona los módulos principales de GleyforGym.</p>
          </div>

          <button className="btn-primary" onClick={() => navigate("/")}>
            Ir al inicio
          </button>
        </header>

        <section className="page-container">
          <Outlet />
        </section>
      </main>
    </div>
  );
}