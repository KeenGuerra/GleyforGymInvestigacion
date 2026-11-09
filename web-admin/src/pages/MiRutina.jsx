import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import { useClienteActual } from "../hooks/useClienteActual";
import { descargarBlob } from "../utils/descargarArchivo";
import { formatearFecha as formatearFechaBase } from "../utils/formatearFecha";

function MiRutina() {
  const navigate = useNavigate();

  const { cliente, error: errorCliente } = useClienteActual();
  const [rutinas, setRutinas] = useState([]);
  const [error, setError] = useState("");
  const [descargandoId, setDescargandoId] = useState(null);

  const descargarPdf = async (id_rutina) => {
    try {
      setDescargandoId(id_rutina);
      setError("");
      const res = await api.get(`/rutinas/${id_rutina}/pdf`, { responseType: "blob" });
      descargarBlob(res.data, `rutina-${id_rutina}.pdf`);
    } catch (error) {
      console.error(error);
      setError("No se pudo descargar el PDF de la rutina");
    } finally {
      setDescargandoId(null);
    }
  };

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return formatearFechaBase(fecha);
  };

  useEffect(() => {
    if (!cliente) return;

    const cargarRutinas = async () => {
      try {
        setError("");

        const rutinasRes = await api.get(`/rutinas/cliente/${cliente.id_cliente}`);

        // El backend ya filtra lo pendiente/rechazado para un CLIENTE; este
        // filtro es una segunda capa de seguridad, no la única.
        const rutinasActivas = rutinasRes.data.filter(
          (rutina) =>
            rutina.estado !== "INACTIVA" &&
            (!rutina.estado_revision ||
              rutina.estado_revision === "aprobada" ||
              rutina.estado_revision === "aprobada_con_cambios")
        );

        setRutinas(rutinasActivas);
      } catch (error) {
        console.error(error);
        setError("No se pudieron cargar tus rutinas.");
      }
    };

    cargarRutinas();
  }, [cliente]);

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

      {(errorCliente || error) && <p className="error-message">{errorCliente || error}</p>}

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

              <div className="form-actions">
                <button
                  className="btn-primary"
                  onClick={() => navigate(`/rutinas/${rutina.id_rutina}/detalle`)}
                >
                  Ver detalle con videos
                </button>
                <button
                  className="btn-secondary"
                  disabled={descargandoId === rutina.id_rutina}
                  onClick={() => descargarPdf(rutina.id_rutina)}
                >
                  {descargandoId === rutina.id_rutina ? "Generando..." : "Descargar PDF"}
                </button>
              </div>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}

export default MiRutina;