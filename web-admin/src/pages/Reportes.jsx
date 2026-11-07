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
  const [exportandoTesis, setExportandoTesis] = useState("");

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

  const exportarF07Kcal = async () => {
    try {
      setExportandoTesis("F-07");
      setError("");
      const res = await api.get("/reportes/ia/kcal");
      exportarCsv(
        "F-07-kcal-plan-vs-objetivo.csv",
        [
          { etiqueta: "Código cliente", valor: "codigo_cliente" },
          { etiqueta: "Kcal plan", valor: "kcal_plan" },
          { etiqueta: "Kcal objetivo", valor: "kcal_objetivo" },
          { etiqueta: "Desviación %", valor: "desviacion_pct" },
        ],
        res.data
      );
    } catch (err) {
      console.error(err);
      setError("No se pudo exportar F-07");
    } finally {
      setExportandoTesis("");
    }
  };

  const exportarF08Decisiones = async () => {
    try {
      setExportandoTesis("F-08");
      setError("");
      const res = await api.get("/reportes/ia/decisiones");
      exportarCsv(
        "F-08-decisiones-revision.csv",
        [
          { etiqueta: "Código cliente", valor: "codigo_cliente" },
          { etiqueta: "Código rutina", valor: "codigo_rutina" },
          { etiqueta: "Decisión", valor: "decision" },
          { etiqueta: "Cambios realizados", valor: "cambios_realizados" },
          { etiqueta: "Fecha", valor: "fecha" },
        ],
        res.data
      );
    } catch (err) {
      console.error(err);
      setError("No se pudo exportar F-08");
    } finally {
      setExportandoTesis("");
    }
  };

  const exportarF09Restricciones = async () => {
    try {
      setExportandoTesis("F-09");
      setError("");
      const res = await api.get("/reportes/ia/restricciones");
      exportarCsv(
        "F-09-verificacion-restricciones.csv",
        [
          { etiqueta: "Código cliente", valor: "codigo_cliente" },
          { etiqueta: "Tipo", valor: "tipo" },
          { etiqueta: "Objetivo", valor: "objetivo" },
          { etiqueta: "Restricciones registradas", valor: "restricciones_registradas" },
          { etiqueta: "¿Viola restricción?", valor: (fila) => (fila.viola_restriccion ? "Sí" : "No") },
        ],
        res.data
      );
    } catch (err) {
      console.error(err);
      setError("No se pudo exportar F-09");
    } finally {
      setExportandoTesis("");
    }
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

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Exportaciones para tesis</h2>
            <p>Clientes anonimizados (código C-00X), sin nombres ni DNI.</p>
          </div>
        </div>

        <div className="form-actions">
          <button className="btn-secondary" disabled={exportandoTesis === "F-07"} onClick={exportarF07Kcal}>
            {exportandoTesis === "F-07" ? "Exportando..." : "F-07: kcal plan vs. objetivo"}
          </button>
          <button className="btn-secondary" disabled={exportandoTesis === "F-08"} onClick={exportarF08Decisiones}>
            {exportandoTesis === "F-08" ? "Exportando..." : "F-08: decisiones de revisión"}
          </button>
          <button className="btn-secondary" disabled={exportandoTesis === "F-09"} onClick={exportarF09Restricciones}>
            {exportandoTesis === "F-09" ? "Exportando..." : "F-09: verificación de restricciones"}
          </button>
        </div>
      </section>
    </div>
  );
}

export default Reportes;
