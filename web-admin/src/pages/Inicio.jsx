import { useNavigate } from "react-router-dom";
import React, { useEffect, useState } from "react";
import api from "../api/api";

import logoGleyforGym from "../assets/logo-gleyforgym.jpeg";
import gymHero from "../assets/gym-hero.jpeg";
import { FaFacebookF, FaInstagram, FaWhatsapp, FaTiktok} from "react-icons/fa";

function Inicio() {
  const navigate = useNavigate();

  const token = localStorage.getItem("token");
  const rol = localStorage.getItem("rol");

  const [planes, setPlanes] = useState([]);
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState("");

  const irAcceso = () => {
    navigate(token ? "/dashboard" : "/login");
  };

  const cargarPlanes = async () => {
    try {
      setError("");
      const res = await api.get("/membresias/");
      const activos = res.data.filter((p) => p.estado === "ACTIVO");
      setPlanes(activos);
    } catch (error) {
      console.error(error);
      setError("No se pudieron cargar los planes.");
    }
  };

  const cargarProductos = async () => {
    try {
      const res = await api.get("/productos/disponibles");
      setProductos(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    cargarPlanes();
    cargarProductos();
  }, []);

  const obtenerBeneficios = (plan) => {
    if (!plan.beneficios) return [];

    return plan.beneficios
      .split("\n")
      .map((beneficio) => beneficio.trim())
      .filter((beneficio) => beneficio.length > 0);
  };

  return (
    <div className="public-page">
      <header className="public-navbar">
        <button
          className="public-brand-logo"
          onClick={() => navigate("/")}
          style={{ background: "none", border: "none", padding: 0, cursor: "pointer" }}
        >
          <img src={logoGleyforGym} alt="Logo GleyforGym" />
        </button>

        <nav className="public-menu">
          <a href="#inicio">Inicio</a>
          <a href="#beneficios">Beneficios</a>
          <a href="#tienda">Tienda</a>
          <a href="#planes">Planes</a>
          <a href="#contacto">Contacto</a>
        </nav>

        <button className="btn-primary" onClick={irAcceso}>
          {token ? `Ir al panel ${rol}` : "Iniciar sesión"}
        </button>
      </header>

      <section className="public-hero-full" id="inicio">
  <img src={gymHero} alt="Gimnasio GleyforGym" className="public-hero-bg" />

  <div className="public-hero-layer"></div>

  <div className="public-hero-full-content">
    <span className="badge">Sistema inteligente para gimnasios</span>

    <h1>
      GleyforGym: tu gimnasio inteligente en Chupaca
    </h1>

    <p>
      Gestiona clientes, pagos, asistencias, rutinas con inteligencia artificial
      y planes nutricionales personalizados desde una plataforma moderna.
    </p>

    <div className="form-actions">
      <button className="btn-primary" onClick={irAcceso}>
        {token ? "Ir a mi panel" : "Comenzar ahora"}
      </button>

      <a className="btn-secondary public-link-btn" href="#planes">
        Ver planes
      </a>
    </div>
  </div>
</section>

      <section className="public-section" id="beneficios">
        <div className="section-title">
          <span className="badge">Nuestras ventajas</span>
          <h2>Todo lo que necesita un gimnasio moderno</h2>
        </div>

        <div className="cards-grid">
          <div className="card item-card">
            <span className="badge">01</span>
            <h3>Gestión de clientes</h3>
            <p>
              Controla socios, membresías, pagos, asistencia y progreso físico
              desde un panel administrativo ordenado.
            </p>
          </div>

          <div className="card item-card">
            <span className="badge">02</span>
            <h3>Control de pagos</h3>
            <p>
              Registra pagos, consulta historial y mantén organizadas las
              membresías activas.
            </p>
          </div>

          <div className="card item-card">
            <span className="badge">03</span>
            <h3>Rutinas IA</h3>
            <p>
              Genera rutinas personalizadas usando información real registrada
              en el sistema.
            </p>
          </div>

          <div className="card item-card">
            <span className="badge">04</span>
            <h3>Dashboard de control</h3>
            <p>
              Visualiza métricas importantes y accede a módulos según el rol:
              administrador, entrenador o cliente.
            </p>
          </div>
        </div>
      </section>

      {productos.length > 0 && (
        <section className="public-section" id="tienda">
          <div className="section-title">
            <span className="badge">Tienda</span>
            <h2>Productos y suplementos</h2>
          </div>

          <div className="cards-grid">
            {productos.slice(0, 8).map((prod) => (
              <div key={prod.id_producto} className="card item-card">
                <div className="item-card-top">
                  <span className="badge">{prod.nombre_categoria || "PRODUCTO"}</span>
                  <span className="badge badge-success">S/ {Number(prod.precio_venta).toFixed(2)}</span>
                </div>

                <h3>{prod.nombre}</h3>

                {prod.descripcion && (
                  <p className="item-description">{prod.descripcion}</p>
                )}

                <div className="mini-stats-grid">
                  <div>
                    <strong>{prod.stock_actual || 0}</strong>
                    <span>Disponible</span>
                  </div>
                  <div>
                    <strong>{prod.unidad_medida || "UNIDAD"}</strong>
                    <span>Unidad</span>
                  </div>
                </div>

                <button className="btn-primary" onClick={irAcceso}>
                  {token ? "Ver en panel" : "Consultar precio"}
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="public-section" id="planes">
        <div className="section-title">
          <span className="badge">Planes disponibles</span>
          <h2>Membresías de GleyforGym</h2>
        </div>

        {error && <p className="error-message">{error}</p>}

        <div className="cards-grid">
          {planes.map((plan, index) => {
            const beneficios = obtenerBeneficios(plan);

            return (
              <div
                key={plan.id_membresia}
                className="card item-card plan-card"
              >
                {index === 1 && <span className="badge">POPULAR</span>}

                <span className="badge">
                  {index + 1 < 10 ? `0${index + 1}` : index + 1}
                </span>

                <h3>{plan.nombre}</h3>

                <h2>
                  S/ {Number(plan.precio).toFixed(0)}
                  <span>/mes</span>
                </h2>

                <p>{plan.descripcion || "Sin descripción"}</p>

                {beneficios.length > 0 && (
                  <ul>
                    {beneficios.map((beneficio) => (
                      <li key={beneficio}>{beneficio}</li>
                    ))}
                  </ul>
                )}

                <button className="btn-primary" onClick={irAcceso}>
                  {token ? "Ir a mi panel" : "Empezar ahora"}
                </button>
              </div>
            );
          })}
        </div>
      </section>

      <section className="public-section" id="contacto">
        <div className="content-grid">
          <div className="card info-card">
            <span className="badge">Contacto</span>
            <h2>¿Listo para entrenar mejor?</h2>

            <p>
              <strong>Dirección:</strong> Chupaca, Perú
            </p>
            <p>
              <strong>Teléfono:</strong> +51 902321009
            </p>
            <p>
              <strong>Email:</strong> gleyfor3@gmail.com
            </p>

            <div className="social-links">
              <a
                href="https://www.facebook.com/p/Gleyfor-GYM-61579024964992/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Facebook"
              >
                <FaFacebookF />
              </a>

              <a
                href="https://www.instagram.com/gleyforgym/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Instagram"
              >
                <FaInstagram />
              </a>

              <a
                href="https://www.tiktok.com/@gleyforgym"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="TikTok"
              >
                <FaTiktok />
              </a>

              <a
                href="https://wa.me/51902321009"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="WhatsApp"
              >
                <FaWhatsapp />
              </a>
            </div>

            <button className="btn-primary" onClick={irAcceso}>
              {token ? "Ir a mi panel" : "Unirme ahora"}
            </button>
          </div>

          <div className="card map-card">
            <iframe
              title="Mapa gimnasio"
              src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d243.85664196895084!2d-75.28908014431451!3d-12.06371950223546!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses!2spe!4v1777926809952!5m2!1ses!2spe"
              width="100%"
              height="350"
              style={{ border: 0 }}
            ></iframe>
          </div>
        </div>
      </section>

      <footer className="public-footer">
        <h3>
          Gleyfor<span>Gym</span>
        </h3>
        <p>© 2026 Todos los derechos reservados</p>
      </footer>
    </div>
  );
}

export default Inicio;