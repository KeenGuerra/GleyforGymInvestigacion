import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/api";

function DetalleRutina() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [rutina, setRutina] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarRutina = async () => {
      try {
        setError("");
        setCargando(true);

        const res = await api.get(`/rutinas/${id}/detalle`);
        setRutina(res.data);
      } catch (error) {
        console.error("Error al cargar rutina:", error);
        setError("No se pudo cargar el detalle de la rutina.");
      } finally {
        setCargando(false);
      }
    };

    cargarRutina();
  }, [id]);

  if (cargando) return <p className="empty-message">Cargando rutina...</p>;
  if (error) return <p className="error-message">{error}</p>;
  if (!rutina) return <p className="empty-message">No se encontró la rutina.</p>;

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">DETALLE DE RUTINA</span>
          <h1>{rutina.nombre || "Rutina sin nombre"}</h1>
          <p>{rutina.descripcion || "Sin descripción registrada."}</p>
        </div>

        <button className="btn-secondary" onClick={() => navigate(-1)}>
          Volver
        </button>
      </section>

      <section className="card meta-card">
        <span className="badge">{rutina.objetivo || "-"}</span>
        <span className="badge">{rutina.nivel || "-"}</span>
        <span className="badge">{rutina.dias_semana || "-"} días</span>
        <span className="badge">{rutina.estado || "ACTIVA"}</span>
        <span className="badge">{rutina.generada_por_ia ? "IA" : "Manual"}</span>
      </section>

      {rutina.ejercicios?.length === 0 ? (
        <section className="card empty-state">
          <h3>Esta rutina no tiene ejercicios</h3>
          <p>Cuando se agreguen ejercicios, aparecerán aquí.</p>
        </section>
      ) : (
        <section className="cards-grid">
          {rutina.ejercicios.map((ejercicio) => (
            <div className="card item-card" key={ejercicio.id_rutina_ejercicio}>
              <div className="video-box">
                {ejercicio.video_url ? (
                  <video src={ejercicio.video_url} controls>
                    <track kind="captions" src="" srcLang="es" label="Español" default />
                  </video>
                ) : (
                  <div className="empty-video">Sin video</div>
                )}
              </div>

              <h3>{ejercicio.nombre || "Ejercicio sin nombre"}</h3>
              <p>{ejercicio.grupo_muscular || "Grupo no definido"}</p>

              <div className="tags-row">
                <span className="badge">{ejercicio.dia_semana || "Sin día"}</span>
                <span className="badge">{ejercicio.series || "-"} series</span>
                <span className="badge">{ejercicio.repeticiones || "-"} reps</span>
                <span className="badge">
                  {ejercicio.descanso_segundos || "-"}s descanso
                </span>
              </div>

              {ejercicio.descripcion && (
                <p className="item-description">
                  <strong>Descripción:</strong> {ejercicio.descripcion}
                </p>
              )}

              {ejercicio.instrucciones && (
                <p className="item-description">
                  <strong>Instrucciones:</strong> {ejercicio.instrucciones}
                </p>
              )}
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

export default DetalleRutina;