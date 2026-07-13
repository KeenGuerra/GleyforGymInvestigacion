import React, { useEffect, useState } from "react";
import api from "../api/api";

function Ventas() {
  const [ventas, setVentas] = useState([]);
  const [productos, setProductos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [procesando, setProcesando] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [detalle, setDetalle] = useState([]);
  const [resumen, setResumen] = useState({});

  const formInicial = { id_cliente: "", metodo_pago: "EFECTIVO", descuento: 0, observaciones: "" };
  const [form, setForm] = useState(formInicial);

  const cargar = async () => {
    try {
      const [r1, r2, r3, r4] = await Promise.all([
        api.get("/ventas/"), api.get("/productos/disponibles"),
        api.get("/clientes/"), api.get("/ventas/resumen"),
      ]);
      setVentas(r1.data); setProductos(r2.data); setClientes(r3.data); setResumen(r4.data);
    } catch (err) { setError("Error al cargar datos"); }
  };

  useEffect(() => { cargar(); }, []);

  const cambiar = (e) => { setForm({ ...form, [e.target.name]: e.target.value }); };

  const agregarDetalle = () => {
    setDetalle([...detalle, { id_producto: "", cantidad: 1 }]);
  };

  const actualizarDetalle = (index, campo, valor) => {
    const nuevo = [...detalle];
    nuevo[index] = { ...nuevo[index], [campo]: valor };
    setDetalle(nuevo);
  };

  const eliminarDetalle = (index) => {
    setDetalle(detalle.filter((_, i) => i !== index));
  };

  const getProducto = (id) => productos.find((p) => p.id_producto === Number(id));

  const subtotal = detalle.reduce((sum, d) => {
    const prod = getProducto(d.id_producto);
    return sum + (prod ? Number(d.cantidad) * prod.precio_venta : 0);
  }, 0);

  const descuento = Number(form.descuento) || 0;
  const total = Math.max(0, subtotal - descuento);

  const limpiar = () => { setForm(formInicial); setDetalle([]); setError(""); setMostrarFormulario(false); };

  const validar = () => {
    if (detalle.length === 0) return "Agregue al menos un producto";
    for (const d of detalle) {
      if (!d.id_producto) return "Seleccione un producto en cada detalle";
      if (Number(d.cantidad) <= 0) return "Cantidad inválida";
      const prod = getProducto(d.id_producto);
      if (prod && Number(d.cantidad) > (prod.stock_actual || 0)) return `Stock insuficiente: ${prod.nombre}`;
    }
    return "";
  };

  const guardar = async (e) => {
    e.preventDefault(); setError("");
    const msg = validar(); if (msg) { setError(msg); return; }
    try {
      setCargando(true);
      await api.post("/ventas/", {
        id_cliente: form.id_cliente ? Number(form.id_cliente) : null,
        metodo_pago: form.metodo_pago,
        descuento: descuento,
        observaciones: form.observaciones || null,
        detalles: detalle.map((d) => ({
          id_producto: Number(d.id_producto),
          cantidad: Number(d.cantidad),
        })),
      });
      limpiar(); await cargar();
    } catch (err) { setError(err.response?.data?.detail || "Error al registrar venta"); }
    finally { setCargando(false); }
  };

  const anular = async (id) => {
    if (!globalThis.confirm("¿Anular esta venta? Se revertirá el inventario.")) return;
    try { setProcesando(id); await api.post(`/ventas/${id}/anular`); await cargar(); }
    catch (err) { setError(err.response?.data?.detail || "Error al anular"); }
    finally { setProcesando(null); }
  };

  const confirmar = async (id) => {
    if (!globalThis.confirm("¿Confirmar esta venta? Se descontará el inventario.")) return;
    try { setProcesando(id); await api.post(`/ventas/${id}/confirmar`); await cargar(); }
    catch (err) { setError(err.response?.data?.detail || "Error al confirmar"); }
    finally { setProcesando(null); }
  };

  const filtradas = ventas.filter((v) => {
    const t = busqueda.toLowerCase();
    return (
      String(v.id_venta || "").includes(t) ||
      String(v.nombre_cliente || "").toLowerCase().includes(t) ||
      String(v.metodo_pago || "").toLowerCase().includes(t) ||
      String(v.estado || "").toLowerCase().includes(t)
    );
  });

  const badgeColor = (estado) => {
    if (estado === "CONFIRMADA") return "badge badge-success";
    if (estado === "ANULADA") return "badge badge-danger";
    return "badge";
  };

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">COMERCIO</span>
          <h1>Ventas</h1>
          <p>Registra ventas de productos, valida stock y genera reportes.</p>
        </div>
        <button className="btn-primary" onClick={() => { setMostrarFormulario(true); setForm(formInicial); setDetalle([]); setError(""); }}>
          + Nueva venta
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card"><span>Ventas hoy</span><strong>{resumen.ventas_hoy || 0}</strong></div>
        <div className="stat-card"><span>Ingresos hoy</span><strong>S/ {resumen.ingresos_hoy?.toFixed(2) || "0.00"}</strong></div>
        <div className="stat-card"><span>Ventas mes</span><strong>{resumen.ventas_mes || 0}</strong></div>
        <div className="stat-card"><span>Ingresos mes</span><strong>S/ {resumen.ingresos_mes?.toFixed(2) || "0.00"}</strong></div>
      </section>

      {error && <p className="error-message">{error}</p>}

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header"><div><h2>Nueva venta</h2></div></div>
          <div className="form-grid">
            <div className="form-field">
              <label>Cliente (opcional)</label>
              <select name="id_cliente" value={form.id_cliente} onChange={cambiar}>
                <option value="">Sin cliente</option>
                {clientes.map((c) => (
                  <option key={c.id_cliente} value={c.id_cliente}>{c.nombres} {c.apellidos}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Método de pago</label>
              <select name="metodo_pago" value={form.metodo_pago} onChange={cambiar}>
                <option value="EFECTIVO">EFECTIVO</option>
                <option value="YAPE">YAPE</option>
                <option value="PLIN">PLIN</option>
                <option value="TRANSFERENCIA">TRANSFERENCIA</option>
                <option value="TARJETA">TARJETA</option>
              </select>
            </div>
            <div className="form-field">
              <label>Descuento (S/)</label>
              <input name="descuento" type="number" step="0.01" min="0" value={form.descuento} onChange={cambiar} />
            </div>
            <div className="form-field">
              <label>Observaciones</label>
              <input name="observaciones" value={form.observaciones} onChange={cambiar} />
            </div>
          </div>

          <h3 style={{ marginTop: "1rem" }}>Detalle de productos</h3>
          {detalle.map((d, i) => {
            const prod = getProducto(d.id_producto);
            const sub = prod ? Number(d.cantidad) * prod.precio_venta : 0;
            return (
              <div key={i} className="form-grid" style={{ alignItems: "end", marginBottom: "0.5rem" }}>
                <div className="form-field">
                  <label>Producto</label>
                  <select value={d.id_producto} onChange={(e) => actualizarDetalle(i, "id_producto", e.target.value)}>
                    <option value="">Seleccionar</option>
                    {productos.map((p) => (
                      <option key={p.id_producto} value={p.id_producto}>{p.nombre} (S/{p.precio_venta} | Stock: {p.stock_actual})</option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label>Cantidad</label>
                  <input type="number" min="1" value={d.cantidad} onChange={(e) => actualizarDetalle(i, "cantidad", e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Subtotal</label>
                  <input readOnly value={`S/ ${sub.toFixed(2)}`} />
                </div>
                <button type="button" className="btn-danger" onClick={() => eliminarDetalle(i)}>X</button>
              </div>
            );
          })}

          <button type="button" className="btn-secondary" onClick={agregarDetalle} style={{ marginTop: "0.5rem" }}>+ Agregar producto</button>

          <div style={{ textAlign: "right", marginTop: "1rem", fontSize: "1.1rem" }}>
            <p>Subtotal: <strong>S/ {subtotal.toFixed(2)}</strong></p>
            <p>Descuento: <strong>S/ {descuento.toFixed(2)}</strong></p>
            <p>Total: <strong>S/ {total.toFixed(2)}</strong></p>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={cargando}>{cargando ? "Procesando..." : "Confirmar venta"}</button>
            <button type="button" className="btn-secondary" onClick={limpiar}>Cancelar</button>
          </div>
        </form>
      )}

      <section className="table-card">
        <div className="card-header">
          <div><h2>Historial de ventas</h2></div>
          <input className="search-input" placeholder="Buscar..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
        </div>
        {filtradas.length === 0 ? <p className="empty-message">No hay ventas registradas.</p> : (
          <div className="cards-grid">
            {filtradas.map((v) => (
              <div key={v.id_venta} className="card item-card">
                <div className="item-card-top">
                  <span className={badgeColor(v.estado)}>{v.estado}</span>
                  <span className="badge">#{v.id_venta}</span>
                </div>
                <h3>{v.nombre_cliente || "Venta general"}</h3>
                <div className="mini-stats-grid">
                  <div><strong>S/ {v.total?.toFixed(2)}</strong><span>Total</span></div>
                  <div><strong>{v.metodo_pago}</strong><span>Método</span></div>
                  <div><strong>{v.detalles?.length || 0}</strong><span>Productos</span></div>
                </div>
                <p className="item-description">{new Date(v.fecha_venta).toLocaleString()}</p>
                {v.detalles && v.detalles.length > 0 && (
                  <div style={{ margin: "0.5rem 0" }}>
                    {v.detalles.map((d) => (
                      <p key={d.id_detalle_venta} className="item-description">
                        {d.nombre_producto} x{d.cantidad} — S/ {d.subtotal?.toFixed(2)}
                      </p>
                    ))}
                  </div>
                )}
                <div className="item-actions">
                  {v.estado === "PENDIENTE" && (
                    <button className="btn-primary" disabled={procesando === v.id_venta} onClick={() => confirmar(v.id_venta)}>
                      {procesando === v.id_venta ? "Confirmando..." : "Confirmar"}
                    </button>
                  )}
                  {v.estado === "CONFIRMADA" && (
                    <button className="btn-danger" disabled={procesando === v.id_venta} onClick={() => anular(v.id_venta)}>
                      {procesando === v.id_venta ? "Anulando..." : "Anular"}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Ventas;
