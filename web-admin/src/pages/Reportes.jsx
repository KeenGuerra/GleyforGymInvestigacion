import React, { useState } from "react";
import api from "../api/api";
import { exportarCsv } from "../utils/exportarCsv";
import { formatearFecha } from "../utils/formatearFecha";

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

  const [saldosPendientes, setSaldosPendientes] = useState(null);
  const [cargandoSaldos, setCargandoSaldos] = useState(false);
  const [mensajesSaldo, setMensajesSaldo] = useState({});

  const [corteTiempos, setCorteTiempos] = useState(() => {
    const fecha = new Date();
    fecha.setDate(fecha.getDate() - 30);
    return fecha.toISOString().slice(0, 10);
  });
  const [limpiandoTiempos, setLimpiandoTiempos] = useState(false);
  const [resultadoLimpieza, setResultadoLimpieza] = useState("");

  const generarReporte = async (rangoOverride) => {
    const rangoDesde = rangoOverride?.desde ?? desde;
    const rangoHasta = rangoOverride?.hasta ?? hasta;

    if (!rangoDesde || !rangoHasta) {
      setError("Selecciona una fecha de inicio y de fin");
      return;
    }
    if (rangoDesde > rangoHasta) {
      setError("La fecha de inicio no puede ser posterior a la fecha de fin");
      return;
    }

    try {
      setCargando(true);
      setError("");

      const [resIngresos, resAsistencias, resProductos, resMetodoPago] = await Promise.all([
        api.get("/reportes/ingresos", { params: { desde: rangoDesde, hasta: rangoHasta } }),
        api.get("/reportes/asistencias", { params: { desde: rangoDesde, hasta: rangoHasta } }),
        api.get("/reportes/productos-mas-vendidos", { params: { desde: rangoDesde, hasta: rangoHasta } }),
        api.get("/reportes/ventas-por-metodo-pago", { params: { desde: rangoDesde, hasta: rangoHasta } }),
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

  const aLlaveFecha = (fecha) => fecha.toISOString().slice(0, 10);

  const aplicarAtajo = (tipo) => {
    const hoy = new Date();
    let inicio;
    if (tipo === "hoy") {
      inicio = hoy;
    } else if (tipo === "semana") {
      // Lunes de esta semana (si hoy es domingo, retrocede 6 días).
      const diaSemana = hoy.getDay();
      const diasDesdeLunes = diaSemana === 0 ? 6 : diaSemana - 1;
      inicio = new Date(hoy);
      inicio.setDate(hoy.getDate() - diasDesdeLunes);
    } else {
      inicio = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
    }

    const nuevoRango = { desde: aLlaveFecha(inicio), hasta: aLlaveFecha(hoy) };
    setDesde(nuevoRango.desde);
    setHasta(nuevoRango.hasta);
    generarReporte(nuevoRango);
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

  const limpiarTiemposRespuesta = async () => {
    if (!corteTiempos) {
      setError("Selecciona una fecha de corte");
      return;
    }
    if (
      !globalThis.confirm(
        `Esto elimina para siempre los registros de tiempo de respuesta (F-04) anteriores al ${corteTiempos}. No se puede deshacer. ¿Continuar?`
      )
    ) {
      return;
    }

    try {
      setLimpiandoTiempos(true);
      setError("");
      setResultadoLimpieza("");
      const res = await api.delete("/reportes/sistema/tiempos-respuesta", {
        params: { antes_de: corteTiempos },
      });
      setResultadoLimpieza(`Se eliminaron ${res.data.eliminados} registros.`);
    } catch (err) {
      console.error(err);
      setError("No se pudo limpiar los registros de tiempo de respuesta");
    } finally {
      setLimpiandoTiempos(false);
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
    // *texto* = negrita en WhatsApp. La fecha se muestra en formato largo
    // ("14 de noviembre de 2026") en vez del ISO crudo ("2026-11-14"), que
    // se ve mejor en un chat. formatearFecha ya corrige el salto de día en
    // husos horarios negativos (ver web-admin/src/utils/formatearFecha.js).
    const fechaLegible = formatearFecha(fila.fecha_fin, {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
    return (
      `¡Hola ${primerNombre}! 👋\n\n` +
      `Tu membresía *${fila.nombre_membresia || ""}* vence el *${fechaLegible}* 📅\n\n` +
      "Renueva a tiempo y sigue entrenando sin interrupciones 💪\n\n" +
      "*GLEYFORGYM* 🏋️"
    );
  };

  const enviarWhatsApp = (fila, mensaje) => {
    const telefono = (fila.telefono_cliente || "").trim();
    if (!(telefono.length === 9 && /^\d+$/.test(telefono))) {
      setError(`${fila.nombre_cliente || "Este cliente"} no tiene un teléfono válido de 9 dígitos registrado.`);
      return;
    }
    const url = `https://wa.me/51${telefono}?text=${encodeURIComponent(mensaje)}`;
    globalThis.open(url, "_blank");
  };

  const enviarRecordatorioWhatsApp = (fila) => {
    enviarWhatsApp(fila, mensajes[fila.id_cliente_membresia] ?? mensajePredeterminado(fila));
  };

  const consultarSaldosPendientes = async () => {
    try {
      setCargandoSaldos(true);
      setError("");
      const res = await api.get("/reportes/saldos-pendientes");
      setSaldosPendientes(res.data);

      const mensajesIniciales = {};
      res.data.forEach((fila) => {
        mensajesIniciales[fila.id_cliente_membresia] = mensajePredeterminadoSaldo(fila);
      });
      setMensajesSaldo(mensajesIniciales);
    } catch (err) {
      console.error(err);
      setError("No se pudo consultar los saldos pendientes");
    } finally {
      setCargandoSaldos(false);
    }
  };

  const mensajePredeterminadoSaldo = (fila) => {
    const primerNombre = (fila.nombre_cliente || "").split(" ")[0] || "";
    return (
      `¡Hola ${primerNombre}! 👋\n\n` +
      `Tienes un saldo pendiente de *S/ ${Number(fila.saldo_pendiente).toFixed(2)}* por tu membresía *${fila.nombre_membresia || ""}* 💳\n\n` +
      "Puedes completar el pago cuando pases por el gimnasio.\n\n" +
      "*GLEYFORGYM* 🏋️"
    );
  };

  const enviarRecordatorioSaldoWhatsApp = (fila) => {
    enviarWhatsApp(fila, mensajesSaldo[fila.id_cliente_membresia] ?? mensajePredeterminadoSaldo(fila));
  };

  const exportarSaldosPendientes = () => {
    exportarCsv(
      "clientes-saldo-pendiente.csv",
      [
        { etiqueta: "Cliente", valor: "nombre_cliente" },
        { etiqueta: "Teléfono", valor: "telefono_cliente" },
        { etiqueta: "Membresía", valor: "nombre_membresia" },
        { etiqueta: "Pagado (S/)", valor: "monto_pagado" },
        { etiqueta: "Saldo pendiente (S/)", valor: "saldo_pendiente" },
      ],
      saldosPendientes || []
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
          <button className="btn-primary" disabled={cargando} onClick={() => generarReporte()}>
            {cargando ? "Generando..." : "Generar reporte"}
          </button>
          <button className="btn-secondary" disabled={cargando} onClick={() => aplicarAtajo("hoy")}>
            Hoy
          </button>
          <button className="btn-secondary" disabled={cargando} onClick={() => aplicarAtajo("semana")}>
            Esta semana
          </button>
          <button className="btn-secondary" disabled={cargando} onClick={() => aplicarAtajo("mes")}>
            Este mes
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
            Total de membresías del período: <strong>S/ {Number(ingresos.total).toFixed(2)}</strong>
          </p>
          {ventasPorMetodo && (
            <p>
              Ingresos totales del período (membresías + ventas de productos):{" "}
              <strong>
                S/ {(Number(ingresos.total) + Number(ventasPorMetodo.total || 0)).toFixed(2)}
              </strong>
            </p>
          )}

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
            <h2>Clientes con saldo pendiente</h2>
            <p>
              Membresías asignadas por el staff donde el cliente pagó solo una parte.
              Revisa quién debe y envíale un recordatorio por WhatsApp.
            </p>
          </div>
        </div>

        <div className="form-actions">
          <button className="btn-primary" disabled={cargandoSaldos} onClick={consultarSaldosPendientes}>
            {cargandoSaldos ? "Consultando..." : "Consultar saldos pendientes"}
          </button>
          {saldosPendientes && saldosPendientes.length > 0 && (
            <button className="btn-secondary" onClick={exportarSaldosPendientes}>
              Exportar CSV
            </button>
          )}
        </div>

        {saldosPendientes && (
          saldosPendientes.length === 0 ? (
            <p className="empty-message">No hay clientes con saldo pendiente.</p>
          ) : (
            <>
              <p>
                Total adeudado:{" "}
                <strong>
                  S/ {saldosPendientes.reduce((t, f) => t + Number(f.saldo_pendiente), 0).toFixed(2)}
                </strong>
              </p>
              <div className="cards-grid">
                {saldosPendientes.map((fila) => (
                  <article className="card item-card" key={fila.id_cliente_membresia}>
                    <div className="item-card-top">
                      <span className="badge badge-warning">
                        Falta S/ {Number(fila.saldo_pendiente).toFixed(2)}
                      </span>
                    </div>
                    <h3>{fila.nombre_cliente || `Cliente #${fila.id_cliente}`}</h3>
                    <p className="item-description">
                      {fila.nombre_membresia || "Membresía"} — pagó S/ {Number(fila.monto_pagado).toFixed(2)}{" "}
                      de S/ {Number(fila.precio_asignado || 0).toFixed(2)}
                    </p>
                    <p className="item-description">Teléfono: {fila.telefono_cliente || "no registrado"}</p>
                    <div className="form-field">
                      <label htmlFor={`mensaje-saldo-${fila.id_cliente_membresia}`}>Mensaje</label>
                      <textarea
                        id={`mensaje-saldo-${fila.id_cliente_membresia}`}
                        rows={3}
                        value={mensajesSaldo[fila.id_cliente_membresia] ?? mensajePredeterminadoSaldo(fila)}
                        onChange={(e) =>
                          setMensajesSaldo({ ...mensajesSaldo, [fila.id_cliente_membresia]: e.target.value })
                        }
                      />
                    </div>
                    <div className="item-actions">
                      <button className="btn-primary" onClick={() => enviarRecordatorioSaldoWhatsApp(fila)}>
                        Enviar recordatorio por WhatsApp
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            </>
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

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Mantenimiento: limpiar tiempos de respuesta (F-04)</h2>
            <p>
              Es el registro que más rápido crece de todo el sistema (una fila por cada
              petición al backend). Úsalo solo cuando ya no necesites los datos anteriores
              a una fecha -- normalmente, después de haber hecho la medición para la tesis.
              Esto elimina los registros para siempre, no los desactiva.
            </p>
          </div>
        </div>

        <div className="form-actions">
          <div className="form-field">
            <label htmlFor="corte-tiempos">Eliminar registros anteriores a</label>
            <input
              id="corte-tiempos"
              type="date"
              value={corteTiempos}
              onChange={(e) => setCorteTiempos(e.target.value)}
            />
          </div>

          <button className="btn-danger" disabled={limpiandoTiempos} onClick={limpiarTiemposRespuesta}>
            {limpiandoTiempos ? "Eliminando..." : "Eliminar registros antiguos"}
          </button>
        </div>

        {resultadoLimpieza && <p className="empty-message">{resultadoLimpieza}</p>}
      </section>
    </div>
  );
}

export default Reportes;
