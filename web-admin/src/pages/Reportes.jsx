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
  const [productosMasVendidos, setProductosMasVendidos] = useState(null);
  const [ventasPorMetodo, setVentasPorMetodo] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [exportandoTesis, setExportandoTesis] = useState("");

  const [diasVencimiento, setDiasVencimiento] = useState(7);
  const [membresiasPorVencer, setMembresiasPorVencer] = useState(null);
  const [cargandoVencimiento, setCargandoVencimiento] = useState(false);
  const [mensajes, setMensajes] = useState({});

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

      const [resIngresos, resAsistencias, resProductos, resMetodoPago] = await Promise.all([
        api.get("/reportes/ingresos", { params: { desde, hasta } }),
        api.get("/reportes/asistencias", { params: { desde, hasta } }),
        api.get("/reportes/productos-mas-vendidos", { params: { desde, hasta } }),
        api.get("/reportes/ventas-por-metodo-pago", { params: { desde, hasta } }),
      ]);

      setIngresos(resIngresos.data);
      setAsistencias(resAsistencias.data);
      setProductosMasVendidos(resProductos.data);
      setVentasPorMetodo(resMetodoPago.data);
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

  const exportarF04Tiempos = async () => {
    try {
      setExportandoTesis("F-04");
      setError("");
      const res = await api.get("/reportes/sistema/tiempos-respuesta", { params: { desde, hasta } });
      exportarCsv(
        `F-04-tiempos-respuesta-${desde}-a-${hasta}.csv`,
        [
          { etiqueta: "Módulo", valor: "modulo" },
          { etiqueta: "Tiempo promedio (ms)", valor: "tiempo_promedio_ms" },
          { etiqueta: "N° de operaciones", valor: "n_operaciones" },
        ],
        res.data
      );
    } catch (err) {
      console.error(err);
      setError("No se pudo exportar F-04");
    } finally {
      setExportandoTesis("");
    }
  };

  const exportarF05Registros = async () => {
    try {
      setExportandoTesis("F-05");
      setError("");
      const res = await api.get("/reportes/sistema/registros-recientes", { params: { desde, hasta } });
      exportarCsv(
        `F-05-registros-recientes-${desde}-a-${hasta}.csv`,
        [
          { etiqueta: "Entidad", valor: "entidad" },
          { etiqueta: "ID", valor: "id_entidad" },
          { etiqueta: "Acción", valor: "accion" },
          { etiqueta: "Detalle", valor: "detalle" },
          { etiqueta: "Fecha", valor: "fecha" },
        ],
        res.data
      );
    } catch (err) {
      console.error(err);
      setError("No se pudo exportar F-05");
    } finally {
      setExportandoTesis("");
    }
  };

  const exportarF12Duplicidad = async () => {
    try {
      setExportandoTesis("F-12");
      setError("");
      const res = await api.get("/reportes/sistema/duplicidad", { params: { desde, hasta } });
      exportarCsv(
        `F-12-duplicidad-${desde}-a-${hasta}.csv`,
        [
          { etiqueta: "Tipo de hallazgo", valor: "tipo_hallazgo" },
          { etiqueta: "Entidad", valor: "entidad" },
          { etiqueta: "ID", valor: "id_entidad" },
          { etiqueta: "Detalle", valor: "detalle" },
        ],
        res.data
      );
    } catch (err) {
      console.error(err);
      setError("No se pudo exportar F-12");
    } finally {
      setExportandoTesis("");
    }
  };

  const exportarF15Progreso = async () => {
    try {
      setExportandoTesis("F-15");
      setError("");
      const res = await api.get("/reportes/progreso-fisico", { params: { desde, hasta } });
      exportarCsv(
        `F-15-seguimiento-progreso-${desde}-a-${hasta}.csv`,
        [
          { etiqueta: "Código cliente", valor: "codigo_cliente" },
          { etiqueta: "¿Tiene seguimiento?", valor: (fila) => (fila.tiene_seguimiento ? "Sí" : "No") },
        ],
        res.data.detalle || []
      );
    } catch (err) {
      console.error(err);
      setError("No se pudo exportar F-15");
    } finally {
      setExportandoTesis("");
    }
  };

  const exportarProductosMasVendidos = () => {
    exportarCsv(
      `productos-mas-vendidos-${desde}-a-${hasta}.csv`,
      [
        { etiqueta: "Producto", valor: "producto" },
        { etiqueta: "Cantidad vendida", valor: "cantidad_vendida" },
        { etiqueta: "Ingresos (S/)", valor: "ingresos" },
      ],
      productosMasVendidos || []
    );
  };

  const exportarVentasPorMetodo = () => {
    exportarCsv(
      `ventas-por-metodo-pago-${desde}-a-${hasta}.csv`,
      [
        { etiqueta: "Método de pago", valor: "metodo_pago" },
        { etiqueta: "Monto (S/)", valor: "monto" },
        { etiqueta: "Cantidad de ventas", valor: "cantidad" },
      ],
      ventasPorMetodo?.por_metodo || []
    );
  };

  const consultarMembresiasPorVencer = async () => {
    try {
      setCargandoVencimiento(true);
      setError("");
      const res = await api.get("/reportes/membresias-por-vencer", { params: { dias: diasVencimiento } });
      setMembresiasPorVencer(res.data);

      const mensajesIniciales = {};
      res.data.forEach((fila) => {
        mensajesIniciales[fila.id_cliente_membresia] = mensajePredeterminado(fila);
      });
      setMensajes(mensajesIniciales);
    } catch (err) {
      console.error(err);
      setError("No se pudo consultar las membresías por vencer");
    } finally {
      setCargandoVencimiento(false);
    }
  };

  const mensajePredeterminado = (fila) => {
    const primerNombre = (fila.nombre_cliente || "").split(" ")[0] || "";
    return (
      `Hola ${primerNombre}, tu membresía "${fila.nombre_membresia || ""}" vence el ${fila.fecha_fin}. ` +
      "Recuerda renovarla para seguir entrenando sin interrupciones. — GLEYFORGYM"
    );
  };

  const enviarRecordatorioWhatsApp = (fila) => {
    const telefono = (fila.telefono_cliente || "").trim();
    if (!(telefono.length === 9 && /^\d+$/.test(telefono))) {
      setError(`${fila.nombre_cliente || "Este cliente"} no tiene un teléfono válido de 9 dígitos registrado.`);
      return;
    }
    const mensaje = mensajes[fila.id_cliente_membresia] ?? mensajePredeterminado(fila);
    const url = `https://wa.me/51${telefono}?text=${encodeURIComponent(mensaje)}`;
    globalThis.open(url, "_blank");
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

      {productosMasVendidos && (
        <section className="table-card">
          <div className="table-header">
            <h2>Productos más vendidos</h2>
            <button className="btn-secondary" onClick={exportarProductosMasVendidos}>
              Exportar CSV
            </button>
          </div>

          {productosMasVendidos.length === 0 ? (
            <p className="empty-message">No hay ventas de productos registradas en este rango.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Cantidad vendida</th>
                  <th>Ingresos</th>
                </tr>
              </thead>
              <tbody>
                {productosMasVendidos.map((fila) => (
                  <tr key={fila.producto}>
                    <td>{fila.producto}</td>
                    <td>{fila.cantidad_vendida}</td>
                    <td>S/ {Number(fila.ingresos).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {ventasPorMetodo && (
        <section className="table-card">
          <div className="table-header">
            <h2>Ventas por método de pago</h2>
            <button className="btn-secondary" onClick={exportarVentasPorMetodo}>
              Exportar CSV
            </button>
          </div>

          <p>
            Total del período: <strong>S/ {Number(ventasPorMetodo.total || 0).toFixed(2)}</strong>
          </p>

          {(ventasPorMetodo.por_metodo || []).length === 0 ? (
            <p className="empty-message">No hay ventas de productos registradas en este rango.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Método de pago</th>
                  <th>Monto</th>
                  <th>N° de ventas</th>
                </tr>
              </thead>
              <tbody>
                {(ventasPorMetodo.por_metodo || []).map((fila) => (
                  <tr key={fila.metodo_pago}>
                    <td>{fila.metodo_pago}</td>
                    <td>S/ {Number(fila.monto).toFixed(2)}</td>
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
            <h2>Membresías por vencer</h2>
            <p>Consulta a quién le vence pronto la membresía y envíale un recordatorio por WhatsApp.</p>
          </div>
        </div>

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="dias_vencimiento">Días hacia adelante</label>
            <input
              id="dias_vencimiento"
              type="number"
              min="1"
              value={diasVencimiento}
              onChange={(e) => setDiasVencimiento(Number(e.target.value))}
            />
          </div>
        </div>

        <div className="form-actions">
          <button className="btn-primary" disabled={cargandoVencimiento} onClick={consultarMembresiasPorVencer}>
            {cargandoVencimiento ? "Consultando..." : "Consultar"}
          </button>
        </div>

        {membresiasPorVencer && (
          membresiasPorVencer.length === 0 ? (
            <p className="empty-message">No hay membresías por vencer en ese rango de días.</p>
          ) : (
            <div className="cards-grid">
              {membresiasPorVencer.map((fila) => (
                <article className="card item-card" key={fila.id_cliente_membresia}>
                  <div className="item-card-top">
                    <span className="badge badge-warning">{fila.dias_restantes} día(s)</span>
                  </div>
                  <h3>{fila.nombre_cliente || `Cliente #${fila.id_cliente}`}</h3>
                  <p className="item-description">
                    {fila.nombre_membresia || "Membresía"} — vence el {fila.fecha_fin}
                  </p>
                  <p className="item-description">Teléfono: {fila.telefono_cliente || "no registrado"}</p>
                  <div className="form-field">
                    <label htmlFor={`mensaje-${fila.id_cliente_membresia}`}>Mensaje</label>
                    <textarea
                      id={`mensaje-${fila.id_cliente_membresia}`}
                      rows={3}
                      value={mensajes[fila.id_cliente_membresia] ?? mensajePredeterminado(fila)}
                      onChange={(e) =>
                        setMensajes({ ...mensajes, [fila.id_cliente_membresia]: e.target.value })
                      }
                    />
                  </div>
                  <div className="item-actions">
                    <button className="btn-primary" onClick={() => enviarRecordatorioWhatsApp(fila)}>
                      Enviar recordatorio por WhatsApp
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )
        )}
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Exportaciones para tesis</h2>
            <p>Clientes anonimizados (código C-00X), sin nombres ni DNI.</p>
          </div>
        </div>

        <div className="form-actions">
          <button className="btn-secondary" disabled={exportandoTesis === "F-04"} onClick={exportarF04Tiempos}>
            {exportandoTesis === "F-04" ? "Exportando..." : "F-04: tiempo de respuesta"}
          </button>
          <button className="btn-secondary" disabled={exportandoTesis === "F-05"} onClick={exportarF05Registros}>
            {exportandoTesis === "F-05" ? "Exportando..." : "F-05: registros recientes"}
          </button>
          <button className="btn-secondary" disabled={exportandoTesis === "F-07"} onClick={exportarF07Kcal}>
            {exportandoTesis === "F-07" ? "Exportando..." : "F-07: kcal plan vs. objetivo"}
          </button>
          <button className="btn-secondary" disabled={exportandoTesis === "F-08"} onClick={exportarF08Decisiones}>
            {exportandoTesis === "F-08" ? "Exportando..." : "F-08: decisiones de revisión"}
          </button>
          <button className="btn-secondary" disabled={exportandoTesis === "F-09"} onClick={exportarF09Restricciones}>
            {exportandoTesis === "F-09" ? "Exportando..." : "F-09: verificación de restricciones"}
          </button>
          <button className="btn-secondary" disabled={exportandoTesis === "F-12"} onClick={exportarF12Duplicidad}>
            {exportandoTesis === "F-12" ? "Exportando..." : "F-12: duplicidad de registros"}
          </button>
          <button className="btn-secondary" disabled={exportandoTesis === "F-15"} onClick={exportarF15Progreso}>
            {exportandoTesis === "F-15" ? "Exportando..." : "F-15: seguimiento de progreso"}
          </button>
        </div>
      </section>
    </div>
  );
}

export default Reportes;
