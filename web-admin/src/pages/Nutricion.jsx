import React, { useEffect, useState } from "react";
import api from "../api/api";

function Nutricion() {
  const [clientes, setClientes] = useState([]);
  const [idCliente, setIdCliente] = useState("");
  const [planes, setPlanes] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const cargarClientes = async () => {
    try {
      setError("");
      const res = await api.get("/clientes/");
      setClientes(res.data.filter((c) => c.estado === "ACTIVO"));
    } catch (error) {
      console.error(error);
      setError("Error al cargar clientes");
    }
  };

  const cargarPlanes = async (id) => {
    if (!id) {
      setPlanes([]);
      return;
    }

    try {
      setError("");
      const res = await api.get(`/nutricion/cliente/${id}`);
      setPlanes(res.data);
    } catch (error) {
      console.error(error);
      setError("Error al cargar planes nutricionales");
    }
  };

  useEffect(() => {
    cargarClientes();
  }, []);

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const cambiarCliente = async (e) => {
    const id = e.target.value;
    setIdCliente(id);
    await cargarPlanes(id);
  };

  const generarIA = async () => {
    if (!idCliente) {
      setError("Selecciona un cliente primero");
      return;
    }

    try {
      setError("");
      setCargando(true);
      await api.post(`/ia/nutricion/generar/${idCliente}`);
      await cargarPlanes(idCliente);
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al generar plan");
    } finally {
      setCargando(false);
    }
  };

  const desactivarPlan = async (idPlan) => {
    const confirmar = globalThis.confirm(
      "¿Seguro que deseas desactivar este plan nutricional?"
    );

    if (!confirmar) return;

    try {
      await api.delete(`/nutricion/${idPlan}`);
      await cargarPlanes(idCliente);
    } catch (error) {
      console.error(error);
      setError("Error al desactivar plan");
    }
  };

  const planesActivos = planes.filter((p) => p.estado !== "INACTIVO");

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">NUTRICIÓN IA</span>
          <h1>Planes nutricionales</h1>
          <p>
            Genera planes nutricionales personalizados según los datos del
            cliente y el catálogo de comidas.
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      <section className="form-card">
        <div className="card-header">
          <div>
            <h2>Generar plan nutricional</h2>
            <p>Selecciona un cliente activo para crear o revisar su plan.</p>
          </div>
        </div>

        <div className="form-grid">
          <div className="form-field field-large">
            <label htmlFor="cliente_nutricion">Cliente</label>
            <select id="cliente_nutricion" value={idCliente} onChange={cambiarCliente}>
              <option value="">Seleccione un cliente</option>
              {clientes.map((c) => (
                <option key={c.id_cliente} value={c.id_cliente}>
                  {c.nombres} {c.apellidos} - {c.objetivo || "Sin objetivo"}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-actions">
          <button
            className="btn-primary"
            onClick={generarIA}
            disabled={cargando || !idCliente}
          >
            {cargando ? "Generando..." : "Generar plan con IA"}
          </button>
        </div>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Planes del cliente</h2>
            <p>Consulta planes activos y comidas recomendadas.</p>
          </div>
        </div>

        {!idCliente && (
          <p className="empty-message">
            Selecciona un cliente para ver sus planes nutricionales.
          </p>
        )}

        {idCliente && planesActivos.length === 0 && (
          <p className="empty-message">
            Este cliente aún no tiene planes nutricionales activos.
          </p>
        )}

        {planesActivos.length > 0 && (
          <div className="cards-grid">
            {planesActivos.map((plan) => (
              <article key={plan.id_plan} className="card item-card">
                <div className="item-card-top">
                  <span className="badge">Plan #{plan.id_plan}</span>
                  <span className="badge">{plan.estado || "ACTIVO"}</span>
                </div>

                <h3>{plan.objetivo || "Objetivo no definido"}</h3>

                <div className="mini-stats-grid">
                  <div>
                    <span>Calorías</span>
                    <strong>{plan.calorias_diarias || 0} kcal</strong>
                  </div>

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

                <div className="detail-list">
                  <p>
                    <span>Generado por IA</span>
                    <strong>{plan.generada_por_ia ? "Sí" : "No"}</strong>
                  </p>

                  <p>
                    <span>Fecha</span>
                    <strong>{formatearFecha(plan.fecha_creacion)}</strong>
                  </p>
                </div>

                <div className="card-header">
                  <div>
                    <h2>Comidas</h2>
                    <p>Alimentos incluidos en el plan.</p>
                  </div>
                </div>

                {plan.comidas && plan.comidas.length > 0 ? (
                  <div className="list">
                    {plan.comidas.map((comida) => (
                      <div key={comida.id_comida} className="list-item">
                        <div>
                          <strong>{comida.tipo_comida || "Comida"}</strong>
                          <span>{comida.descripcion || "Sin descripción"}</span>
                        </div>

                        <div className="tags-row">
                          <span className="badge">
                            {comida.calorias_aprox || 0} kcal
                          </span>
                          <span className="badge">
                            {comida.hora_recomendada || "Sin hora"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty-message">
                    No hay comidas registradas en este plan.
                  </p>
                )}

                <div className="form-actions">
                  <button
                    className="btn-danger"
                    onClick={() => desactivarPlan(plan.id_plan)}
                  >
                    Desactivar plan
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Nutricion;