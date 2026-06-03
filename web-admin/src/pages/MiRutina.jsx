import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

function MiRutina() {
  const navigate = useNavigate();

  const [cliente, setCliente] = useState(null);
  const [rutinas, setRutinas] = useState([]);
  const [error, setError] = useState("");

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const cargarRutinas = async () => {
    try {
      setError("");

      const idUsuario = localStorage.getItem("id_usuario");

      const clienteRes = await api.get(`/clientes/usuario/${idUsuario}`);
      const clienteData = clienteRes.data;

      setCliente(clienteData);

      const rutinasRes = await api.get(
        `/rutinas/cliente/${clienteData.id_cliente}`
      );

      const rutinasActivas = rutinasRes.data.filter(
        (rutina) => rutina.estado !== "INACTIVA"
      );

      setRutinas(rutinasActivas);
    } catch (error) {
      console.error(error);
      setError("No se pudieron cargar tus rutinas.");
    }
  };

  useEffect(() => {
    cargarRutinas();
  }, []);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MI ENTRENAMIENTO</span>
          <h1>Mis rutinas</h1>
          <p>
            {cliente
              ? `Hola ${cliente.nombres}, aquí puedes revisar tus rutinas asignadas.`
              : "Aquí puedes revisar tus rutinas asignadas."}
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      {rutinas.length === 0 ? (
        <section className="card empty-state">
          <h3>No tienes rutinas activas</h3>
          <p>Cuando el entrenador o la IA genere una rutina, aparecerá aquí.</p>
        </section>
      ) : (
        <section className="cards-grid">
          {rutinas.map((rutina) => (
            <article className="card item-card" key={rutina.id_rutina}>
              <div className="item-card-top">
                <span className="badge">🏃 Rutina</span>
                <span className="badge">{rutina.estado || "ACTIVA"}</span>
              </div>

              <h3>{rutina.nombre || "Rutina sin nombre"}</h3>

              <div className="detail-list">
                <p><span>Objetivo</span><strong>{rutina.objetivo || "No definido"}</strong></p>
                <p><span>Nivel</span><strong>{rutina.nivel || "No definido"}</strong></p>
                <p><span>Días por semana</span><strong>{rutina.dias_semana || "-"}</strong></p>
                <p><span>Fecha</span><strong>{formatearFecha(rutina.fecha_creacion)}</strong></p>
                <p><span>Generada por IA</span><strong>{rutina.generada_por_ia ? "Sí" : "No"}</strong></p>
              </div>

              <button
                className="btn-primary"
                onClick={() => navigate(`/rutinas/${rutina.id_rutina}/detalle`)}
              >
                Ver detalle con videos
              </button>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}

export default MiRutina;