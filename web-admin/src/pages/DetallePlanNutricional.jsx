import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/api";
import { descargarBlob } from "../utils/descargarArchivo";
import { formatearFecha as formatearFechaBase } from "../utils/formatearFecha";

function DetallePlanNutricional() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [plan, setPlan] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [descargando, setDescargando] = useState(false);
  const [errorDescarga, setErrorDescarga] = useState("");

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return formatearFechaBase(fecha);
  };

  const descargarPdf = async () => {
    try {
      setDescargando(true);
      setErrorDescarga("");
      const res = await api.get(`/nutricion/${id}/pdf`, { responseType: "blob" });
      descargarBlob(res.data, `plan-nutricional-${id}.pdf`);
    } catch (error) {
      console.error(error);
      setErrorDescarga("No se pudo descargar el PDF del plan");
    } finally {
      setDescargando(false);
    }
  };

  useEffect(() => {
    const cargarPlan = async () => {
      try {
        setError("");
        setCargando(true);

        const res = await api.get(`/nutricion/${id}`);
        setPlan(res.data);
      } catch (error) {
        console.error("Error al cargar plan nutricional:", error);
        setError("No se pudo cargar el detalle del plan nutricional.");
      } finally {
        setCargando(false);
      }
    };

    cargarPlan();
  }, [id]);

  if (cargando) return <p className="empty-message">Cargando plan nutricional...</p>;
  if (error) return <p className="error-message">{error}</p>;
  if (!plan) return <p className="empty-message">No se encontró el plan nutricional.</p>;

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">DETALLE DE PLAN NUTRICIONAL</span>
          <h1>{plan.objetivo || "Objetivo no definido"}</h1>
          <p>Generado el {formatearFecha(plan.fecha_creacion)}.</p>
        </div>

        <div style={{ display: "flex", gap: "12px" }}>
          <button className="btn-secondary" disabled={descargando} onClick={descargarPdf}>
            {descargando ? "Generando..." : "Descargar PDF"}
          </button>
          <button className="btn-secondary" onClick={() => navigate(-1)}>
            Volver
          </button>
        </div>
      </section>

      {errorDescarga && <p className="error-message">{errorDescarga}</p>}

      <section className="card meta-card">
        <span className="badge">{plan.estado || "ACTIVO"}</span>
        <span className="badge">{plan.generada_por_ia ? "IA" : "Manual"}</span>
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Macros</h2>
            <p>Objetivo calculado vs. lo que suman realmente las comidas asignadas.</p>
          </div>
        </div>

        <div className="mini-stats-grid">
          <div>
            <span>Calorías objetivo</span>
            <strong>{plan.calorias_diarias || 0} kcal</strong>
          </div>
          <div>
            <span>Proteínas objetivo</span>
            <strong>{plan.proteinas || 0} g</strong>
          </div>
          <div>
            <span>Carbohidratos objetivo</span>
            <strong>{plan.carbohidratos || 0} g</strong>
          </div>
          <div>
            <span>Grasas objetivo</span>
            <strong>{plan.grasas || 0} g</strong>
          </div>
        </div>

        <div className="mini-stats-grid">
          <div>
            <span>Calorías reales (comidas)</span>
            <strong>{plan.calorias_reales || 0} kcal</strong>
          </div>
          <div>
            <span>Proteínas reales</span>
            <strong>{plan.proteinas_reales || 0} g</strong>
          </div>
          <div>
            <span>Carbohidratos reales</span>
            <strong>{plan.carbohidratos_reales || 0} g</strong>
          </div>
          <div>
            <span>Grasas reales</span>
            <strong>{plan.grasas_reales || 0} g</strong>
          </div>
        </div>
      </section>

      {(!plan.comidas || plan.comidas.length === 0) ? (
        <section className="card empty-state">
          <h3>Este plan no tiene comidas</h3>
          <p>Cuando se agreguen comidas, aparecerán aquí.</p>
        </section>
      ) : (
        <section className="card">
          <div className="card-header">
            <div>
              <h2>Comidas</h2>
              <p>Alimentos incluidos en el plan.</p>
            </div>
          </div>

          <div className="list">
            {plan.comidas.map((comida) => (
              <div key={comida.id_comida} className="list-item">
                <div>
                  <strong>{comida.tipo_comida || "Comida"}</strong>
                  <span>{comida.descripcion || "Sin descripción"}</span>
                </div>

                <div className="tags-row">
                  <span className="badge">{comida.calorias_aprox || 0} kcal</span>
                  <span className="badge">{comida.hora_recomendada || "Sin hora"}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default DetallePlanNutricional;
