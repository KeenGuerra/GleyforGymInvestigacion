import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import { MSG_CLIENTE_NO_ENCONTRADO } from "../api/constants";

function Rutinas() {
  const navigate = useNavigate();

  const [clientes, setClientes] = useState([]);
  const [rutinas, setRutinas] = useState([]);
  const [idClienteIA, setIdClienteIA] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [cargandoIA, setCargandoIA] = useState(false);

  const cargarDatos = async () => {
    try {
      setError("");

      const [resClientes, resRutinas] = await Promise.all([
        api.get("/clientes/"),
        api.get("/rutinas/"),
      ]);

      setClientes(resClientes.data.filter((c) => c.estado === "ACTIVO"));
      setRutinas(resRutinas.data);
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

  const generarRutinaIA = async () => {
    setError("");

    if (!idClienteIA) {
      setError("Seleccione un cliente");
      return;
    }

    try {
      setCargandoIA(true);

      const res = await api.post(`/ia/rutina/generar/${idClienteIA}`);

      await cargarDatos();

      if (res.data?.id_rutina) {
        navigate(`/rutinas/${res.data.id_rutina}/detalle`);
      }
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al generar rutina IA");
    } finally {
      setCargandoIA(false);
    }
  };

  const desactivarRutina = async (id) => {
    const confirmar = globalThis.confirm("¿Seguro que deseas desactivar esta rutina?");
    if (!confirmar) return;

    try {
      await api.delete(`/rutinas/${id}`);
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError("Error al desactivar rutina");
    }
  };

  const rutinasFiltradas = rutinas.filter((r) => {
    const cliente = obtenerNombreCliente(r.id_cliente).toLowerCase();
    const texto = busqueda.toLowerCase();

    return (
      cliente.includes(texto) ||
      String(r.nombre || "").toLowerCase().includes(texto) ||
      String(r.objetivo || "").toLowerCase().includes(texto) ||
      String(r.nivel || "").toLowerCase().includes(texto) ||
      String(r.estado || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">RUTINAS IA</span>
          <h1>Rutinas personalizadas</h1>
          <p>
            Genera y administra rutinas usando los datos del cliente y el catálogo de ejercicios.
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      <section className="form-card">
        <div className="card-header">
          <div>
            <h2>Generar rutina automática</h2>
            <p>Selecciona un cliente activo para generar una rutina con IA.</p>
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
                  {c.nombres} {c.apellidos} - {c.objetivo || "Sin objetivo"} -{" "}
                  {c.nivel || "Sin nivel"}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-actions">
          <button
            className="btn-primary"
            onClick={generarRutinaIA}
            disabled={cargandoIA}
          >
            {cargandoIA ? "Generando..." : "Generar rutina IA"}
          </button>
        </div>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Rutinas generadas</h2>
            <p>Consulta rutinas, revisa detalles o desactiva registros.</p>
          </div>

          <input
            className="search-input"
            type="text"
            placeholder="Buscar por cliente, rutina, objetivo, nivel o estado..."
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
                <th>Nombre</th>
                <th>Objetivo</th>
                <th>Nivel</th>
                <th>Fecha</th>
                <th>IA</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {rutinasFiltradas.length === 0 ? (
                <tr>
                  <td colSpan="9" className="empty-message">
                    No hay rutinas registradas
                  </td>
                </tr>
              ) : (
                rutinasFiltradas.map((r) => (
                  <tr key={r.id_rutina}>
                    <td>
                      <span className="badge">#{r.id_rutina}</span>
                    </td>
                    <td>{obtenerNombreCliente(r.id_cliente)}</td>
                    <td>{r.nombre || "-"}</td>
                    <td>{r.objetivo || "-"}</td>
                    <td>{r.nivel || "-"}</td>
                    <td>{formatearFecha(r.fecha_creacion)}</td>
                    <td>{r.generada_por_ia ? "Sí" : "No"}</td>
                    <td>
                      <span className="badge">{r.estado || "ACTIVA"}</span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="btn-secondary"
                          onClick={() =>
                            navigate(`/rutinas/${r.id_rutina}/detalle`)
                          }
                        >
                          Ver
                        </button>

                        <button
                          className="btn-danger"
                          onClick={() => desactivarRutina(r.id_rutina)}
                        >
                          Desactivar
                        </button>
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

export default Rutinas;