import React, { useState } from "react";
import api from "../api/api";
import { exportarCsv } from "../utils/exportarCsv";

function primerDiaDelMes() {
  const hoy = new Date();
  return new Date(hoy.getFullYear(), hoy.getMonth(), 1).toISOString().slice(0, 10);
}

function Reportes() {
  const [desde, setDesde] = useState(primerDiaDelMes());
  const [hasta, setHasta] = useState(new Date().toISOString().slice(0, 10));
  const [ingresos, setIngresos] = useState(null);
  const [asistencias, setAsistencias] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const generarReporte = async () => {
    if (!desde || !hasta) {
      setError("Selecciona una fecha de inicio y de fin");
      return;
    }
    if (desde > hasta) {
      setError("La fecha de inicio no puede ser posterior a la fecha de fin");
      return;
    }

    try {
      setCargando(true);
      setError("");

      const [resIngresos, resAsistencias] = await Promise.all([
        api.get("/reportes/ingresos", { params: { desde, hasta } }),
        api.get("/reportes/asistencias", { params: { desde, hasta } }),
      ]);

      setIngresos(resIngresos.data);
      setAsistencias(resAsistencias.data);
    } catch (error) {
      console.error(error);
      setError("No se pudo generar el reporte");
    } finally {
      setCargando(false);
    }
  };

  const exportarIngresos = () => {
    exportarCsv(
      `ingresos-${desde}-a-${hasta}.csv`,
      [
        { etiqueta: "Fecha", valor: "fecha" },
        { etiqueta: "Monto (S/)", valor: "monto" },
      ],
      ingresos?.por_dia || []
    );
  };

  const exportarAsistencias = () => {
    exportarCsv(
      `asistencias-${desde}-a-${hasta}.csv`,
      [
        { etiqueta: "Fecha", valor: "fecha" },
        { etiqueta: "Cantidad", valor: "cantidad" },
      ],
      asistencias?.por_dia || []
    );
  };

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">REPORTES</span>
          <h1>Reportes operativos</h1>
          <p>Ingresos y asistencia consolidados por rango de fechas.</p>
        </div>
      </section>

      <section className="form-card">
        <div className="card-header">
          <h2>Seleccionar rango</h2>
        </div>

        {error && <p className="error-message">{error}</p>}

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="reporte_desde">Desde</label>
            <input
              id="reporte_desde"
              type="date"
              value={desde}
              onChange={(e) => setDesde(e.target.value)}
            />
          </div>

          <div className="form-field">
            <label htmlFor="reporte_hasta">Hasta</label>
            <input
              id="reporte_hasta"
              type="date"
              value={hasta}
              onChange={(e) => setHasta(e.target.value)}
            />
          </div>
        </div>

        <div className="form-actions">
          <button className="btn-primary" disabled={cargando} onClick={generarReporte}>
            {cargando ? "Generando..." : "Generar reporte"}
          </button>
        </div>
      </section>

      {ingresos && (
        <section className="table-card">
          <div className="table-header">
            <h2>Ingresos por día</h2>
            <button className="btn-secondary" onClick={exportarIngresos}>
              Exportar CSV
            </button>
          </div>

          <p>
            Total del período: <strong>S/ {Number(ingresos.total).toFixed(2)}</strong>
          </p>

          {ingresos.por_dia.length === 0 ? (
            <p className="empty-message">No hay ingresos registrados en este rango.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Monto</th>
                </tr>
              </thead>
              <tbody>
                {ingresos.por_dia.map((fila) => (
                  <tr key={fila.fecha}>
                    <td>{fila.fecha}</td>
                    <td>S/ {Number(fila.monto).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {asistencias && (
        <section className="table-card">
          <div className="table-header">
            <h2>Asistencias por día</h2>
            <button className="btn-secondary" onClick={exportarAsistencias}>
              Exportar CSV
            </button>
          </div>

          <p>
            Total del período: <strong>{asistencias.total}</strong>
          </p>

          {asistencias.por_dia.length === 0 ? (
            <p className="empty-message">No hay asistencias registradas en este rango.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Cantidad</th>
                </tr>
              </thead>
              <tbody>
                {asistencias.por_dia.map((fila) => (
                  <tr key={fila.fecha}>
                    <td>{fila.fecha}</td>
                    <td>{fila.cantidad}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </div>
  );
}

export default Reportes;
