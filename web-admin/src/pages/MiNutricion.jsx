import React, { useEffect, useState } from "react";
import api from "../api/api";

function MiNutricion() {
  const [cliente, setCliente] = useState(null);
  const [planes, setPlanes] = useState([]);
  const [error, setError] = useState("");

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const cargarNutricion = async () => {
    try {
      setError("");

      const idUsuario = localStorage.getItem("id_usuario");

      const clienteRes = await api.get(`/clientes/usuario/${idUsuario}`);
      const clienteData = clienteRes.data;

      setCliente(clienteData);

      const nutricionRes = await api.get(
        `/nutricion/cliente/${clienteData.id_cliente}`
      );

      const planesActivos = nutricionRes.data.filter(
        (plan) => plan.estado !== "INACTIVO"
      );

      setPlanes(planesActivos);
    } catch (error) {
      console.error(error);
      setError("No se pudo cargar tu plan nutricional.");
    }
  };

  useEffect(() => {
    cargarNutricion();
  }, []);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MI NUTRICIÓN</span>
          <h1>Mis planes nutricionales</h1>
          <p>
            {cliente
              ? `Hola ${cliente.nombres}, aquí puedes revisar tus planes alimenticios.`
              : "Aquí puedes revisar tus planes alimenticios."}
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      {planes.length === 0 ? (
        <section className="card empty-state">
          <h3>No tienes planes nutricionales activos</h3>
          <p>Cuando se genere un plan con IA, aparecerá aquí.</p>
        </section>
      ) : (
        <section className="list">
          {planes.map((plan) => {
            const comidas = plan.comidas || [];

            return (
              <article className="card item-card" key={plan.id_plan}>
                <div className="item-card-top">
                  <div>
                    <span className="badge">PLAN NUTRICIONAL</span>
                    <h3>{plan.objetivo || "Objetivo no definido"}</h3>
                    <p>
                      <strong>Fecha:</strong> {formatearFecha(plan.fecha_creacion)}
                    </p>
                    <p>
                      <strong>Generado por IA:</strong>{" "}
                      {plan.generada_por_ia ? "Sí" : "No"}
                    </p>
                  </div>

                  <div className="price-box">
                    <strong>{plan.calorias_diarias || 0}</strong>
                    <span>kcal/día</span>
                  </div>
                </div>

                <div className="mini-stats-grid">
                  <div>
                    <span>Proteínas</span>
                    <strong>{plan.proteinas || 0} g</strong>
                  </div>

                  <div>
                    <span>Carbohidratos</span>
                    <strong>{plan.carbohidratos || 0} g</strong>
                  </div>

                  <div>
                    <span>Grasas</span>
                    <strong>{plan.grasas || 0} g</strong>
                  </div>
                </div>

                <div className="card-header">
                  <div>
                    <h2>Comidas del plan</h2>
                    <p>Distribución de comidas recomendadas.</p>
                  </div>
                </div>

                {comidas.length === 0 ? (
                  <p className="empty-message">
                    Este plan todavía no tiene comidas registradas.
                  </p>
                ) : (
                  <div className="cards-grid">
                    {comidas.map((comida) => (
                      <div className="card item-card" key={comida.id_comida}>
                        <span className="badge">
                          {comida.tipo_comida || "Comida"}
                        </span>

                        <h3>{comida.descripcion || "Sin descripción"}</h3>

                        <p>
                          <strong>Calorías:</strong>{" "}
                          {comida.calorias_aprox || 0} kcal
                        </p>

                        <p>
                          <strong>Hora:</strong>{" "}
                          {comida.hora_recomendada || "No definida"}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </article>
            );
          })}
        </section>
      )}
    </div>
  );
}

export default MiNutricion;