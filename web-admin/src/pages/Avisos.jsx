import React from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import { FaClock, FaUserTie, FaMusic, FaBullhorn, FaTiktok } from "react-icons/fa";

function Avisos() {
  const navigate = useNavigate();

  return (
    <div className="public-page">
      <Navbar />

      <section className="public-section" style={{ paddingTop: "2rem" }}>
        <div className="section-title">
          <span className="badge">Avisos</span>
          <h2>Horarios y novedades de GleyforGym</h2>
        </div>

        <div className="cards-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>

          {/* HORARIO DE ATENCIÓN */}
          <div className="card item-card" style={{ borderTop: "3px solid var(--orange)" }}>
            <div className="item-card-top">
              <FaClock size={20} color="var(--orange)" />
              <span className="badge">Horario</span>
            </div>
            <h3>Horario de atención</h3>
            <div style={{ marginTop: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                <span style={{ color: "#d4d4d8" }}>Lunes a Sábado</span>
                <strong style={{ color: "var(--orange)" }}>6:00 am – 10:00 pm</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
                <span style={{ color: "#d4d4d8" }}>Domingos</span>
                <strong style={{ color: "var(--orange)" }}>8:00 am – 12:00 pm</strong>
              </div>
            </div>
          </div>

          {/* COACHES */}
          <div className="card item-card" style={{ borderTop: "3px solid #22c55e" }}>
            <div className="item-card-top">
              <FaUserTie size={20} color="#22c55e" />
              <span className="badge badge-success">Coaches</span>
            </div>
            <h3>Nuestros coaches</h3>
            <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <strong style={{ color: "#fff" }}>Deyvi</strong>
                <p className="item-description" style={{ margin: 0 }}>Lun – Vie: 6:00 am – 12:00 pm | 3:00 pm – 9:00 pm</p>
              </div>
              <div>
                <strong style={{ color: "#fff" }}>Jhony</strong>
                <p className="item-description" style={{ margin: 0 }}>Lun – Sáb: 3:00 pm – 8:00 pm</p>
              </div>
              <div>
                <strong style={{ color: "#fff" }}>Alfrado</strong>
                <p className="item-description" style={{ margin: 0 }}>Dom: 8:00 am – 12:00 pm | Sáb: 3:00 pm – 9:00 pm</p>
              </div>
            </div>
          </div>

          {/* BAILE */}
          <div className="card item-card" style={{ borderTop: "3px solid #a855f7" }}>
            <div className="item-card-top">
              <FaMusic size={20} color="#a855f7" />
              <span className="badge" style={{ background: "rgba(168,85,247,0.15)", color: "#a855f7" }}>Baile</span>
            </div>
            <h3>Clases de baile</h3>
            <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <strong style={{ color: "#fff" }}>Katy Cambias Fit</strong>
                <p className="item-description" style={{ margin: 0 }}>Martes / Viernes: 7:00 pm – 8:00 pm</p>
              </div>
              <div>
                <strong style={{ color: "#fff" }}>Miguel Rodriguez – Zumba</strong>
                <p className="item-description" style={{ margin: 0 }}>Jueves: 7:00 pm – 8:00 pm</p>
              </div>
              <div>
                <strong style={{ color: "#fff" }}>Yanina Barreto – X-tream</strong>
                <p className="item-description" style={{ margin: 0 }}>Lun / Mié / Vie: 8:00 pm – 9:00 pm</p>
              </div>
            </div>
          </div>

          {/* COMUNICADO */}
          <div className="card item-card" style={{ borderTop: "3px solid #eab308" }}>
            <div className="item-card-top">
              <FaBullhorn size={20} color="#eab308" />
              <span className="badge" style={{ background: "rgba(234,179,8,0.15)", color: "#eab308" }}>Comunicado</span>
            </div>
            <h3>Próximos eventos</h3>
            <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <FaTiktok size={24} color="#00f2ea" />
                <div>
                  <strong style={{ color: "#fff" }}>Live en TikTok</strong>
                  <p className="item-description" style={{ margin: 0 }}>Jueves 7:00 pm – @gleyforgym</p>
                  <p className="item-description" style={{ margin: 0, color: "#eab308" }}>Sortearemos un premio</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <footer className="public-footer">
        <h3>Gleyfor<span>Gym</span></h3>
        <p>© 2026 Todos los derechos reservados</p>
      </footer>
    </div>
  );
}

export default Avisos;
