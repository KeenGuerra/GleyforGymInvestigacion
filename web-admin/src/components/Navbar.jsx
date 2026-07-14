import React from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import logoGleyforGym from "../assets/logo-gleyforgym.jpeg";

export default function Navbar({ cartCount = 0, onCartClick }) {
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem("token");
  const rol = localStorage.getItem("rol");
  const isLoggedIn = !!token;

  const path = location.pathname;

  const irAcceso = () => {
    navigate(isLoggedIn ? "/dashboard" : "/login");
  };

  const navLinks = [
    { label: "Inicio", to: "/" },
    { label: "Avisos", to: "/avisos" },
    { label: "Tienda", to: "/tienda" },
  ];

  if (isLoggedIn) {
    navLinks.push({ label: "Panel", to: "/dashboard" });
  }

  return (
    <header className="public-navbar">
      <button
        className="public-brand-logo"
        onClick={() => navigate("/")}
        style={{ background: "none", border: "none", padding: 0, cursor: "pointer" }}
      >
        <img src={logoGleyforGym} alt="Logo GleyforGym" />
      </button>

      <nav className="public-menu">
        {navLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            style={path === link.to ? { color: "var(--orange)" } : undefined}
          >
            {link.label}
          </Link>
        ))}
      </nav>

      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {cartCount > 0 && (
          <button
            className="btn-secondary"
            onClick={onCartClick}
            style={{ position: "relative" }}
          >
            Carrito ({cartCount})
          </button>
        )}
        <button className="btn-primary" onClick={irAcceso}>
          {isLoggedIn ? (rol === "ADMIN" ? "Admin" : rol === "ENTRENADOR" ? "Entrenador" : "Mi panel") : "Iniciar sesión"}
        </button>
      </div>
    </header>
  );
}
