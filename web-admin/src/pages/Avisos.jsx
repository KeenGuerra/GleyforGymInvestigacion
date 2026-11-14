import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import api from "../api/api";
import { FaClock, FaUserTie, FaMusic, FaBullhorn } from "react-icons/fa";
import { formatearFecha } from "../utils/formatearFecha";

const CONFIG_TIPO = {
  HORARIO: { titulo: "Horario de atención", icono: FaClock, color: "var(--orange)", clase: "aviso-card-horario", badge: "Horario" },
  COACHES: { titulo: "Nuestros coaches", icono: FaUserTie, color: "#22c55e", clase: "aviso-card-coaches", badge: "Coaches" },
  BAILE: { titulo: "Clases de baile", icono: FaMusic, color: "#a855f7", clase: "aviso-card-baile", badge: "Baile" },
  COMUNICADO: { titulo: "Comunicados", icono: FaBullhorn, color: "var(--orange-text)", clase: "aviso-card-comunicado", badge: "Comunicado" },
  EVENTO: { titulo: "Próximos eventos", icono: FaBullhorn, color: "var(--orange-text)", clase: "aviso-card-comunicado", badge: "Evento" },
};

function Avisos() {
  const [avisos, setAvisos] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      try {
        const res = await api.get("/avisos/");
        const hoy = new Date().toISOString().slice(0, 10);
        setAvisos(
          res.data.filter(
            (a) =>
              a.estado === "ACTIVO" &&
              // Un EVENTO con fecha ya pasada no se muestra -- el backend ya
              // lo filtra para visitantes sin sesión, pero un usuario
              // logueado (cliente/staff) sí recibe todo, así que se repite
              // el filtro aquí para que esta página pública nunca muestre un
              // evento vencido a nadie.
              (a.tipo !== "EVENTO" || !a.fecha_evento || a.fecha_evento >= hoy)
          )
        );
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

  // Los próximos eventos se ven mejor ordenados por fecha (el más cercano
  // primero), no por orden de creación como el resto de tipos de aviso.
  if (grupos.EVENTO) {
    grupos.EVENTO = [...grupos.EVENTO].sort((a, b) =>
      (a.fecha_evento || "").localeCompare(b.fecha_evento || "")
    );
  }

  return (
    <div className="public-page">
      <Navbar />

      <section className="public-section tight-top">
        <div className="section-title">
          <span className="badge">Avisos</span>
          <h2>Horarios y novedades de GleyforGym</h2>
        </div>

        {error && <p className="error-message">{error}</p>}

        {avisos.length === 0 && !error ? (
          <p className="empty-message">No hay avisos publicados por el momento.</p>
        ) : (
          <div className="cards-grid wide">
            {Object.entries(grupos).map(([tipo, items]) => {
              const config = CONFIG_TIPO[tipo] || CONFIG_TIPO.COMUNICADO;
              const Icono = config.icono;

              return (
                <div className={`card item-card ${config.clase}`} key={tipo}>
                  <div className="item-card-top">
                    <Icono size={20} color={config.color} />
                    <span className="badge">{config.badge}</span>
                  </div>
                  <h3>{config.titulo}</h3>
                  <div className="aviso-items">
                    {items.map((aviso) => (
                      <div key={aviso.id_aviso}>
                        <strong>{aviso.titulo}</strong>
                        <p className="item-description">{aviso.contenido}</p>
                        {aviso.tipo === "EVENTO" && aviso.fecha_evento && (
                          <p className="item-description aviso-event-date">
                            {formatearFecha(aviso.fecha_evento)}
                          </p>
                        )}
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
