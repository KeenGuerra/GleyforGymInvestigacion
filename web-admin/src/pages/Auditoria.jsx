import React, { useCallback, useEffect, useState } from "react";
import api from "../api/api";

const ENTIDADES = ["Usuario", "Pago", "ClienteMembresia", "Compra", "Venta", "Aviso"];

function Auditoria() {
  const [registros, setRegistros] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [entidad, setEntidad] = useState("");
  const [error, setError] = useState("");

  const cargar = useCallback(async (filtroEntidad = entidad) => {
    try {
      setError("");
      const res = await api.get("/auditoria/", {
        params: filtroEntidad ? { entidad: filtroEntidad } : {},
      });
      setRegistros(res.data);
    } catch (err) {
      console.error(err);
      setError("Error al cargar el historial de auditoría");
    }
  }, [entidad]);

  useEffect(() => {
    cargar(entidad);
  }, [entidad, cargar]);

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleString("es-PE");
  };

  const registrosFiltrados = registros.filter((r) => {
    const texto = busqueda.toLowerCase();
    return (
      String(r.correo_usuario || "").toLowerCase().includes(texto) ||
      String(r.accion || "").toLowerCase().includes(texto) ||
      String(r.entidad || "").toLowerCase().includes(texto) ||
      String(r.detalle || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">ADMINISTRACIÓN</span>
          <h1>Auditoría del sistema</h1>
          <p>Historial de operaciones críticas: usuarios, pagos, membresías, compras y ventas.</p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Registros mostrados</span>
          <strong>{registrosFiltrados.length}</strong>
        </div>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Historial de operaciones</h2>
            <p>Las 200 operaciones críticas más recientes, de más nueva a más antigua.</p>
          </div>

          <div className="table-header-actions">
            <select
              aria-label="Filtrar por entidad"
              value={entidad}
              onChange={(e) => setEntidad(e.target.value)}
            >
              <option value="">Todas las entidades</option>
              {ENTIDADES.map((ent) => (
                <option key={ent} value={ent}>{ent}</option>
              ))}
            </select>

            <input
              className="search-input"
              placeholder="Buscar por usuario, acción o detalle..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>
        </div>

        {error && <p className="error-message">{error}</p>}

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Usuario</th>
                <th>Acción</th>
                <th>Entidad</th>
                <th>ID entidad</th>
                <th>Detalle</th>
              </tr>
            </thead>

            <tbody>
              {registrosFiltrados.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-message">
                    No hay registros de auditoría para este filtro
                  </td>
                </tr>
              ) : (
                registrosFiltrados.map((r) => (
                  <tr key={r.id_registro}>
                    <td>{formatearFecha(r.fecha)}</td>
                    <td>{r.correo_usuario || "Sistema"}</td>
                    <td>
                      <span className="badge">{r.accion}</span>
                    </td>
                    <td>{r.entidad}</td>
                    <td>{r.id_entidad ?? "-"}</td>
                    <td>{r.detalle || "-"}</td>
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

export default Auditoria;
