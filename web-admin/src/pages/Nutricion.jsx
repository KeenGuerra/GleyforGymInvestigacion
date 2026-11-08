import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import { MSG_CLIENTE_NO_ENCONTRADO } from "../api/constants";

function Nutricion() {
  const navigate = useNavigate();

  const [clientes, setClientes] = useState([]);
  const [planes, setPlanes] = useState([]);
  const [idClienteIA, setIdClienteIA] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [cargandoIA, setCargandoIA] = useState(false);

  const cargarDatos = async () => {
    try {
      setError("");

      const [resClientes, resPlanes] = await Promise.all([
        api.get("/clientes/"),
        api.get("/nutricion/"),
      ]);

      setClientes(resClientes.data.filter((c) => c.estado === "ACTIVO"));
      setPlanes(resPlanes.data);
    } catch (error) {
      console.error(error);
      setError("Error al cargar datos");
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const obtenerNombreCliente = (id) => {
    const c = clientes.find((c) => c.id_cliente === id);
    return c ? `${c.nombres} ${c.apellidos}` : MSG_CLIENTE_NO_ENCONTRADO;
  };

  const generarIA = async () => {
    setError("");

    if (!idClienteIA) {
      setError("Seleccione un cliente");
      return;
    }

    try {
      setCargandoIA(true);
      await api.post(`/ia/nutricion/generar/${idClienteIA}`);
      await cargarDatos();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al generar plan");
    } finally {
      setCargandoIA(false);
    }
  };

  const desactivarPlan = async (idPlan) => {
    const confirmar = globalThis.confirm(
      "¿Seguro que deseas desactivar este plan nutricional?"
    );
    if (!confirmar) return;

    try {
      await api.delete(`/nutricion/${idPlan}`);
      await cargarDatos();
    } catch (error) {
      console.error(error);
      setError("Error al desactivar plan");
    }
  };

  const activarPlan = async (idPlan) => {
    try {
      await api.put(`/nutricion/${idPlan}`, { estado: "ACTIVO" });
      await cargarDatos();
    } catch (error) {
      console.error(error);
      setError("Error al activar plan");
    }
  };

  const planesFiltrados = planes.filter((p) => {
    const cliente = obtenerNombreCliente(p.id_cliente).toLowerCase();
    const texto = busqueda.toLowerCase();

    return (
      cliente.includes(texto) ||
      String(p.objetivo || "").toLowerCase().includes(texto) ||
      String(p.estado || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">NUTRICIÓN IA</span>
          <h1>Planes nutricionales</h1>
          <p>
            Genera y administra planes nutricionales usando los datos del cliente y el catálogo de comidas.
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      <section className="form-card">
        <div className="card-header">
          <div>
            <h2>Generar plan nutricional</h2>
            <p>Selecciona un cliente activo para generar un plan con IA.</p>
          </div>
        </div>

        <div className="form-grid">
          <div className="form-field field-large">
            <label htmlFor="idClienteIA">Cliente</label>
            <select
              id="idClienteIA"
              value={idClienteIA}
              onChange={(e) => setIdClienteIA(e.target.value)}
            >
              <option value="">Seleccionar cliente</option>
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
            disabled={cargandoIA}
          >
            {cargandoIA ? "Generando..." : "Generar plan con IA"}
          </button>
        </div>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Planes generados</h2>
            <p>Consulta planes, revisa detalles o desactiva registros.</p>
          </div>

          <input
            className="search-input"
            type="text"
            placeholder="Buscar por cliente, objetivo o estado..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Objetivo</th>
                <th>Calorías</th>
                <th>Fecha</th>
                <th>IA</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {planesFiltrados.length === 0 ? (
                <tr>
                  <td colSpan="8" className="empty-message">
                    No hay planes nutricionales registrados
                  </td>
                </tr>
              ) : (
                planesFiltrados.map((p) => (
                  <tr key={p.id_plan}>
                    <td>
                      <span className="badge">#{p.id_plan}</span>
                    </td>
                    <td>{obtenerNombreCliente(p.id_cliente)}</td>
                    <td>{p.objetivo || "-"}</td>
                    <td>{p.calorias_diarias || 0} kcal</td>
                    <td>{formatearFecha(p.fecha_creacion)}</td>
                    <td>{p.generada_por_ia ? "Sí" : "No"}</td>
                    <td>
                      <span className="badge">{p.estado || "ACTIVO"}</span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="btn-secondary"
                          onClick={() => navigate(`/nutricion/${p.id_plan}/detalle`)}
                        >
                          Ver
                        </button>

                        {p.estado === "INACTIVO" ? (
                          <button
                            className="btn-secondary"
                            onClick={() => activarPlan(p.id_plan)}
                          >
                            Activar
                          </button>
                        ) : (
                          <button
                            className="btn-danger"
                            onClick={() => desactivarPlan(p.id_plan)}
                          >
                            Desactivar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default Nutricion;
