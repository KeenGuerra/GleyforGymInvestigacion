import React, { useEffect, useState } from "react";
import api from "../api/api";

const CART_KEY = "carrito_tienda";

function Tienda() {
  const [productos, setProductos] = useState([]);
  const [pedidos, setPedidos] = useState([]);
  const [carrito, setCarrito] = useState(() => {
    try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
    catch { return []; }
  });
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  const [tab, setTab] = useState("tienda");
  const [metodoPago, setMetodoPago] = useState("EFECTIVO");
  const [observaciones, setObservaciones] = useState("");
  const [procesando, setProcesando] = useState(false);

  useEffect(() => {
    localStorage.setItem(CART_KEY, JSON.stringify(carrito));
  }, [carrito]);

  const cargar = async () => {
    try {
      setError("");
      const [rProd, rPed] = await Promise.all([
        api.get("/productos/disponibles"),
        api.get("/ventas/mis-pedidos"),
      ]);
      setProductos(rProd.data);
      setPedidos(rPed.data);
    } catch (err) {
      setError("Error al cargar datos");
    }
  };

  useEffect(() => { cargar(); }, []);

  const agregarAlCarrito = (producto) => {
    if ((producto.stock_actual || 0) <= 0) {
      setError("Producto sin stock");
      return;
    }
    setCarrito((prev) => {
      const existente = prev.find((c) => c.id_producto === producto.id_producto);
      if (existente) {
        if (existente.cantidad >= producto.stock_actual) {
          setError(`Stock insuficiente: ${producto.nombre} (disponible: ${producto.stock_actual})`);
          return prev;
        }
        return prev.map((c) =>
          c.id_producto === producto.id_producto
            ? { ...c, cantidad: c.cantidad + 1 }
            : c
        );
      }
      return [...prev, {
        id_producto: producto.id_producto,
        nombre: producto.nombre,
        precio_venta: producto.precio_venta,
        stock_actual: producto.stock_actual,
        unidad_medida: producto.unidad_medida,
        nombre_categoria: producto.nombre_categoria,
        cantidad: 1,
      }];
    });
    setError("");
  };

  const actualizarCantidad = (id_producto, nuevaCantidad) => {
    const cantidad = Math.max(1, Number(nuevaCantidad) || 1);
    setCarrito((prev) =>
      prev.map((c) => {
        if (c.id_producto !== id_producto) return c;
        if (cantidad > c.stock_actual) {
          setError(`Stock insuficiente: ${c.nombre} (disponible: ${c.stock_actual})`);
          return c;
        }
        return { ...c, cantidad };
      })
    );
  };

  const eliminarDelCarrito = (id_producto) => {
    setCarrito((prev) => prev.filter((c) => c.id_producto !== id_producto));
  };

  const subtotal = carrito.reduce((sum, c) => sum + c.cantidad * c.precio_venta, 0);
  const total = Math.max(0, subtotal);

  const checkout = async () => {
    if (carrito.length === 0) { setError("El carrito está vacío"); return; }
    try {
      setProcesando(true);
      setError("");
      await api.post("/ventas/solicitar", {
        metodo_pago: metodoPago,
        descuento: 0,
        observaciones: observaciones || null,
        detalles: carrito.map((c) => ({
          id_producto: c.id_producto,
          cantidad: c.cantidad,
        })),
      });
      setCarrito([]);
      setObservaciones("");
      setTab("pedidos");
      await cargar();
    } catch (err) {
      setError(err.response?.data?.detail || "Error al realizar el pedido");
    } finally {
      setProcesando(false);
    }
  };

  const filtrados = productos.filter((p) => {
    const t = busqueda.toLowerCase();
    return (
      String(p.nombre || "").toLowerCase().includes(t) ||
      String(p.nombre_categoria || "").toLowerCase().includes(t)
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
          <span className="badge">TIENDA</span>
          <h1>Mi Tienda</h1>
          <p>Explora productos, agrega al carrito y realiza tu pedido.</p>
        </div>
        {carrito.length > 0 && (
          <button className="btn-primary" onClick={() => setTab("carrito")}>
            Carrito ({carrito.length})
          </button>
        )}
      </section>

      <section className="stats-grid">
        <div className="stat-card"><span>Productos</span><strong>{productos.length}</strong></div>
        <div className="stat-card"><span>En carrito</span><strong>{carrito.reduce((s, c) => s + c.cantidad, 0)}</strong></div>
        <div className="stat-card"><span>Total carrito</span><strong>S/ {total.toFixed(2)}</strong></div>
        <div className="stat-card"><span>Mis pedidos</span><strong>{pedidos.length}</strong></div>
      </section>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        {["tienda", "carrito", "pedidos"].map((t) => (
          <button key={t} className={tab === t ? "btn-primary" : "btn-secondary"} onClick={() => setTab(t)}>
            {t === "tienda" ? "Tienda" : t === "carrito" ? `Carrito (${carrito.length})` : "Mis pedidos"}
          </button>
        ))}
      </div>

      {error && <p className="error-message">{error}</p>}

      {tab === "tienda" && (
        <section className="table-card">
          <div className="card-header">
            <div><h2>Productos disponibles</h2></div>
            <input className="search-input" placeholder="Buscar producto..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
          </div>
          {filtrados.length === 0 ? (
            <p className="empty-message">No hay productos disponibles.</p>
          ) : (
            <div className="cards-grid">
              {filtrados.map((p) => (
                <div key={p.id_producto} className="card item-card">
                  <div className="item-card-top">
                    <span className="badge">{p.nombre_categoria || "PRODUCTO"}</span>
                    <span className="badge badge-success">S/ {Number(p.precio_venta).toFixed(2)}</span>
                  </div>
                  <h3>{p.nombre}</h3>
                  {p.descripcion && <p className="item-description">{p.descripcion}</p>}
                  <div className="mini-stats-grid">
                    <div><strong>{p.stock_actual || 0}</strong><span>Stock</span></div>
                    <div><strong>{p.unidad_medida}</strong><span>Unidad</span></div>
                  </div>
                  <button
                    className="btn-primary"
                    disabled={(p.stock_actual || 0) <= 0}
                    onClick={() => agregarAlCarrito(p)}
                  >
                    {(p.stock_actual || 0) <= 0 ? "Sin stock" : "+ Agregar al carrito"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {tab === "carrito" && (
        <section className="table-card">
          <div className="card-header">
            <div><h2>Mi carrito</h2></div>
          </div>
          {carrito.length === 0 ? (
            <p className="empty-message">Tu carrito está vacío.</p>
          ) : (
            <>
              <div className="cards-grid">
                {carrito.map((c) => (
                  <div key={c.id_producto} className="card item-card">
                    <div className="item-card-top">
                      <span className="badge">{c.nombre_categoria || "PRODUCTO"}</span>
                      <span className="badge badge-success">S/ {(c.cantidad * c.precio_venta).toFixed(2)}</span>
                    </div>
                    <h3>{c.nombre}</h3>
                    <div className="mini-stats-grid">
                      <div>
                        <strong>S/ {c.precio_venta.toFixed(2)}</strong>
                        <span>Precio unit.</span>
                      </div>
                      <div>
                        <input
                          type="number"
                          min="1"
                          max={c.stock_actual}
                          value={c.cantidad}
                          onChange={(e) => actualizarCantidad(c.id_producto, e.target.value)}
                          style={{ width: "60px", padding: "0.3rem", borderRadius: "6px", border: "1px solid #444", background: "#1a1a2e", color: "#fff", textAlign: "center" }}
                        />
                        <span>Cant.</span>
                      </div>
                    </div>
                    <button className="btn-danger" onClick={() => eliminarDelCarrito(c.id_producto)}>
                      Eliminar
                    </button>
                  </div>
                ))}
              </div>

              <div className="form-card" style={{ marginTop: "1rem" }}>
                <div className="card-header"><div><h2>Finalizar pedido</h2></div></div>
                <div className="form-grid">
                  <div className="form-field">
                    <label>Método de pago</label>
                    <select value={metodoPago} onChange={(e) => setMetodoPago(e.target.value)}>
                      <option value="EFECTIVO">Efectivo</option>
                      <option value="YAPE">Yape</option>
                      <option value="PLIN">Plin</option>
                      <option value="TRANSFERENCIA">Transferencia</option>
                      <option value="TARJETA">Tarjeta</option>
                    </select>
                  </div>
                  <div className="form-field field-large">
                    <label>Observaciones</label>
                    <input
                      value={observaciones}
                      onChange={(e) => setObservaciones(e.target.value)}
                      placeholder="Nota opcional para tu pedido"
                    />
                  </div>
                </div>
                <div style={{ textAlign: "right", marginTop: "1rem", fontSize: "1.1rem" }}>
                  <p>Subtotal: <strong>S/ {subtotal.toFixed(2)}</strong></p>
                  <p><strong>Total: S/ {total.toFixed(2)}</strong></p>
                </div>
                <div className="form-actions">
                  <button className="btn-primary" disabled={procesando} onClick={checkout}>
                    {procesando ? "Procesando..." : "Confirmar pedido"}
                  </button>
                  <button className="btn-secondary" onClick={() => setCarrito([])}>Vaciar carrito</button>
                </div>
              </div>
            </>
          )}
        </section>
      )}

      {tab === "pedidos" && (
        <section className="table-card">
          <div className="card-header">
            <div><h2>Mis pedidos</h2></div>
          </div>
          {pedidos.length === 0 ? (
            <p className="empty-message">No tienes pedidos registrados.</p>
          ) : (
            <div className="cards-grid">
              {pedidos.map((v) => (
                <div key={v.id_venta} className="card item-card">
                  <div className="item-card-top">
                    <span className={badgeColor(v.estado)}>{v.estado}</span>
                    <span className="badge">#{v.id_venta}</span>
                  </div>
                  <div className="mini-stats-grid">
                    <div><strong>S/ {v.total?.toFixed(2)}</strong><span>Total</span></div>
                    <div><strong>{v.metodo_pago}</strong><span>Método</span></div>
                    <div><strong>{v.detalles?.length || 0}</strong><span>Productos</span></div>
                  </div>
                  <p className="item-description">{new Date(v.fecha_venta).toLocaleString()}</p>
                  {v.detalles && v.detalles.length > 0 && (
                    <div style={{ marginTop: "0.5rem" }}>
                      {v.detalles.map((d) => (
                        <p key={d.id_detalle_venta} className="item-description">
                          {d.nombre_producto} x{d.cantidad} — S/ {d.subtotal?.toFixed(2)}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default Tienda;
