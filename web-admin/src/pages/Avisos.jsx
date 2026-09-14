import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import api from "../api/api";
import { FaClock, FaUserTie, FaMusic, FaBullhorn } from "react-icons/fa";

const CONFIG_TIPO = {
  HORARIO: { titulo: "Horario de atención", icono: FaClock, color: "var(--orange)", badge: "Horario" },
  COACHES: { titulo: "Nuestros coaches", icono: FaUserTie, color: "#22c55e", badge: "Coaches" },
  BAILE: { titulo: "Clases de baile", icono: FaMusic, color: "#a855f7", badge: "Baile" },
  COMUNICADO: { titulo: "Comunicados", icono: FaBullhorn, color: "#eab308", badge: "Comunicado" },
  EVENTO: { titulo: "Próximos eventos", icono: FaBullhorn, color: "#eab308", badge: "Evento" },
};

function Avisos() {
  const [avisos, setAvisos] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      try {
        const res = await api.get("/avisos/");
        setAvisos(res.data.filter((a) => a.estado === "ACTIVO"));
      } catch (err) {
        console.error("Error al cargar avisos:", err);
        setError("No se pudieron cargar los avisos.");
      }
    };
    cargar();
  }, []);

  const grupos = avisos.reduce((acc, aviso) => {
    const tipo = aviso.tipo || "COMUNICADO";
    if (!acc[tipo]) acc[tipo] = [];
    acc[tipo].push(aviso);
    return acc;
  }, {});

  return (
    <div className="public-page">
      <Navbar />

      <section className="public-section" style={{ paddingTop: "2rem" }}>
        <div className="section-title">
          <span className="badge">Avisos</span>
          <h2>Horarios y novedades de GleyforGym</h2>
        </div>

        {error && <p className="error-message">{error}</p>}

        {avisos.length === 0 && !error ? (
          <p className="empty-message">No hay avisos publicados por el momento.</p>
        ) : (
          <div className="cards-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>
            {Object.entries(grupos).map(([tipo, items]) => {
              const config = CONFIG_TIPO[tipo] || CONFIG_TIPO.COMUNICADO;
              const Icono = config.icono;

              return (
                <div className="card item-card" style={{ borderTop: `3px solid ${config.color}` }} key={tipo}>
                  <div className="item-card-top">
                    <Icono size={20} color={config.color} />
                    <span className="badge">{config.badge}</span>
                  </div>
                  <h3>{config.titulo}</h3>
                  <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "12px" }}>
                    {items.map((aviso) => (
                      <div key={aviso.id_aviso}>
                        <strong style={{ color: "#fff" }}>{aviso.titulo}</strong>
                        <p className="item-description" style={{ margin: 0 }}>{aviso.contenido}</p>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      <footer className="public-footer">
        <h3>Gleyfor<span>Gym</span></h3>
        <p>© 2026 Todos los derechos reservados</p>
      </footer>
    </div>
  );
}

export default Avisos;
