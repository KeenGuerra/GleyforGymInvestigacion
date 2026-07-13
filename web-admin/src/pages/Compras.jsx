import React, { useEffect, useState } from "react";
import api from "../api/api";

function Compras() {
  const [compras, setCompras] = useState([]);
  const [proveedores, setProveedores] = useState([]);
  const [productos, setProductos] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [detalle, setDetalle] = useState([]);

  const formInicial = { id_proveedor: "", observaciones: "" };
  const [form, setForm] = useState(formInicial);

  const cargar = async () => {
    try {
      const [r1, r2, r3] = await Promise.all([
        api.get("/compras/"), api.get("/proveedores/"), api.get("/productos/")
      ]);
      setCompras(r1.data); setProveedores(r2.data); setProductos(r3.data);
    } catch (err) { setError("Error al cargar datos"); }
  };

  useEffect(() => { cargar(); }, []);

  const cambiar = (e) => { setForm({ ...form, [e.target.name]: e.target.value }); };

  const agregarDetalle = () => {
    setDetalle([...detalle, { id_producto: "", cantidad: 1, precio_unitario: 0 }]);
  };

  const actualizarDetalle = (index, campo, valor) => {
    const nuevo = [...detalle];
    nuevo[index] = { ...nuevo[index], [campo]: valor };
    setDetalle(nuevo);
  };

  const eliminarDetalle = (index) => {
    setDetalle(detalle.filter((_, i) => i !== index));
  };

  const subtotal = detalle.reduce((sum, d) => sum + (Number(d.cantidad) * Number(d.precio_unitario)), 0);
  const igv = subtotal * 0.18;
  const total = subtotal + igv;

  const limpiar = () => { setForm(formInicial); setDetalle([]); setError(""); setMostrarFormulario(false); };

  const validar = () => {
    if (!form.id_proveedor) return "Seleccione un proveedor";
    if (detalle.length === 0) return "Agregue al menos un producto";
    for (const d of detalle) {
      if (!d.id_producto) return "Seleccione un producto en cada detalle";
      if (Number(d.cantidad) <= 0) return "Cantidad inválida";
      if (Number(d.precio_unitario) < 0) return "Precio inválido";
    }
    return "";
  };

  const guardar = async (e) => {
    e.preventDefault(); setError("");
    const msg = validar(); if (msg) { setError(msg); return; }
    try {
      setCargando(true);
      await api.post("/compras/", {
        id_proveedor: Number(form.id_proveedor),
        detalles: detalle.map((d) => ({
          id_producto: Number(d.id_producto),
          cantidad: Number(d.cantidad),
          precio_unitario: Number(d.precio_unitario),
        })),
        observaciones: form.observaciones || null,
      });
      limpiar(); await cargar();
    } catch (err) { setError(err.response?.data?.detail || "Error al registrar compra"); }
    finally { setCargando(false); }
  };

  const confirmar = async (id) => {
    if (!globalThis.confirm("¿Confirmar compra? Se actualizará el inventario.")) return;
    try { await api.post(`/compras/${id}/confirmar`); await cargar(); }
    catch (err) { setError(err.response?.data?.detail || "Error al confirmar"); }
  };

  const anular = async (id) => {
    if (!globalThis.confirm("¿Anular esta compra?")) return;
    try { await api.post(`/compras/${id}/anular`); await cargar(); }
    catch (err) { setError(err.response?.data?.detail || "Error al anular"); }
  };

  const filtradas = compras.filter((c) => {
    const t = busqueda.toLowerCase();
    return (
      String(c.id_compra || "").includes(t) ||
      String(c.nombre_proveedor || "").toLowerCase().includes(t) ||
      String(c.estado || "").toLowerCase().includes(t)
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
          <h1>Compras</h1>
          <p>Registra compras de proveedores y actualiza inventario.</p>
        </div>
        <button className="btn-primary" onClick={() => { setMostrarFormulario(true); setForm(formInicial); setDetalle([]); setError(""); }}>
          + Nueva compra
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card"><span>Total</span><strong>{compras.length}</strong></div>
        <div className="stat-card"><span>Pendientes</span><strong>{compras.filter((c) => c.estado === "PENDIENTE").length}</strong></div>
        <div className="stat-card"><span>Confirmadas</span><strong>{compras.filter((c) => c.estado === "CONFIRMADA").length}</strong></div>
      </section>

      {error && <p className="error-message">{error}</p>}

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header"><div><h2>Nueva compra</h2></div></div>
          <div className="form-grid">
            <div className="form-field field-large">
              <label>Proveedor</label>
              <select name="id_proveedor" value={form.id_proveedor} onChange={cambiar}>
                <option value="">Seleccionar proveedor</option>
                {proveedores.filter((p) => p.estado === "ACTIVO").map((p) => (
                  <option key={p.id_proveedor} value={p.id_proveedor}>{p.razon_social}</option>
                ))}
              </select>
            </div>
            <div className="form-field field-large">
              <label>Observaciones</label>
              <textarea name="observaciones" value={form.observaciones} onChange={cambiar} />
            </div>
          </div>

          <h3 style={{ marginTop: "1rem" }}>Detalle de productos</h3>
          {detalle.map((d, i) => (
            <div key={i} className="form-grid" style={{ alignItems: "end", marginBottom: "0.5rem" }}>
              <div className="form-field">
                <label>Producto</label>
                <select value={d.id_producto} onChange={(e) => actualizarDetalle(i, "id_producto", e.target.value)}>
                  <option value="">Seleccionar</option>
                  {productos.filter((p) => p.estado === "ACTIVO").map((p) => (
                    <option key={p.id_producto} value={p.id_producto}>{p.nombre}</option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label>Cantidad</label>
                <input type="number" min="1" value={d.cantidad} onChange={(e) => actualizarDetalle(i, "cantidad", e.target.value)} />
              </div>
              <div className="form-field">
                <label>Precio unitario (S/)</label>
                <input type="number" step="0.01" min="0" value={d.precio_unitario} onChange={(e) => actualizarDetalle(i, "precio_unitario", e.target.value)} />
              </div>
              <div className="form-field">
                <label>Subtotal</label>
                <input readOnly value={`S/ ${(Number(d.cantidad) * Number(d.precio_unitario)).toFixed(2)}`} />
              </div>
              <button type="button" className="btn-danger" onClick={() => eliminarDetalle(i)}>X</button>
            </div>
          ))}

          <button type="button" className="btn-secondary" onClick={agregarDetalle} style={{ marginTop: "0.5rem" }}>+ Agregar producto</button>

          <div style={{ textAlign: "right", marginTop: "1rem", fontSize: "1.1rem" }}>
            <p>Subtotal: <strong>S/ {subtotal.toFixed(2)}</strong></p>
            <p>IGV (18%): <strong>S/ {igv.toFixed(2)}</strong></p>
            <p>Total: <strong>S/ {total.toFixed(2)}</strong></p>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={cargando}>{cargando ? "Guardando..." : "Registrar compra"}</button>
            <button type="button" className="btn-secondary" onClick={limpiar}>Cancelar</button>
          </div>
        </form>
      )}

      <section className="table-card">
        <div className="card-header">
          <div><h2>Historial de compras</h2></div>
          <input className="search-input" placeholder="Buscar..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
        </div>
        {filtradas.length === 0 ? <p className="empty-message">No hay compras registradas.</p> : (
          <div className="cards-grid">
            {filtradas.map((c) => (
              <div key={c.id_compra} className="card item-card">
                <div className="item-card-top">
                  <span className={badgeColor(c.estado)}>{c.estado}</span>
                  <span className="badge">#{c.id_compra}</span>
                </div>
                <h3>{c.nombre_proveedor || "Proveedor"}</h3>
                <div className="mini-stats-grid">
                  <div><strong>S/ {c.total?.toFixed(2)}</strong><span>Total</span></div>
                  <div><strong>{c.detalles?.length || 0}</strong><span>Productos</span></div>
                </div>
                <p className="item-description">Fecha: {new Date(c.fecha_compra).toLocaleDateString()}</p>
                {c.estado === "PENDIENTE" && (
                  <div className="item-actions">
                    <button className="btn-primary" onClick={() => confirmar(c.id_compra)}>Confirmar</button>
                    <button className="btn-danger" onClick={() => anular(c.id_compra)}>Anular</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Compras;
