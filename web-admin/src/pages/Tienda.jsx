import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

const CART_KEY = "carrito_tienda";

function Tienda() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const isLoggedIn = !!token;

  const [productos, setProductos] = useState([]);
  const [pedidos, setPedidos] = useState([]);
  const [carrito, setCarrito] = useState(() => {
    try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
    catch { return []; }
  });
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
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
      const resProd = await api.get("/productos/disponibles");
      setProductos(resProd.data);
      if (isLoggedIn) {
        try {
          const resPed = await api.get("/ventas/mis-pedidos");
          setPedidos(resPed.data);
        } catch { setPedidos([]); }
      }
    } catch {
      setError("Error al cargar productos");
    }
  };

  useEffect(() => { cargar(); }, [isLoggedIn]);

  const agregarAlCarrito = (producto) => {
    if (!isLoggedIn) { navigate("/login"); return; }
    if ((producto.stock_actual || 0) <= 0) { setError("Producto sin stock"); return; }
    setCarrito((prev) => {
      const existente = prev.find((c) => c.id_producto === producto.id_producto);
      if (existente) {
        if (existente.cantidad >= producto.stock_actual) {
          setError(`Stock insuficiente: ${producto.nombre} (disponible: ${producto.stock_actual})`);
          return prev;
        }
        return prev.map((c) =>
          c.id_producto === producto.id_producto ? { ...c, cantidad: c.cantidad + 1 } : c
        );
      }
      return [...prev, {
        id_producto: producto.id_producto, nombre: producto.nombre,
        precio_venta: producto.precio_venta, stock_actual: producto.stock_actual,
        unidad_medida: producto.unidad_medida, nombre_categoria: producto.nombre_categoria, cantidad: 1,
      }];
    });
    setError("");
  };

  const actualizarCantidad = (id_producto, nuevaCantidad) => {
    const cantidad = Math.max(1, Number(nuevaCantidad) || 1);
    setCarrito((prev) => prev.map((c) => {
      if (c.id_producto !== id_producto) return c;
      if (cantidad > c.stock_actual) { setError(`Stock insuficiente: ${c.nombre}`); return c; }
      return { ...c, cantidad };
    }));
  };

  const eliminarDelCarrito = (id_producto) => {
    setCarrito((prev) => prev.filter((c) => c.id_producto !== id_producto));
  };

  const subtotal = carrito.reduce((sum, c) => sum + c.cantidad * c.precio_venta, 0);
  const total = Math.max(0, subtotal);

  const checkout = async () => {
    if (!isLoggedIn) { navigate("/login"); return; }
    if (carrito.length === 0) { setError("El carrito está vacío"); return; }
    try {
      setProcesando(true); setError("");
      await api.post("/ventas/solicitar", {
        metodo_pago: metodoPago, descuento: 0,
        observaciones: observaciones || null,
        detalles: carrito.map((c) => ({ id_producto: c.id_producto, cantidad: c.cantidad })),
      });
      setCarrito([]); setObservaciones(""); setTab("pedidos"); await cargar();
    } catch (err) {
      setError(err.response?.data?.detail || "Error al realizar el pedido");
    } finally { setProcesando(false); }
  };

  const filtrados = productos.filter((p) => {
    const t = busqueda.toLowerCase();
    return String(p.nombre || "").toLowerCase().includes(t) ||
      String(p.nombre_categoria || "").toLowerCase().includes(t);
  });

  const badgeColor = (estado) => {
    if (estado === "CONFIRMADA") return "badge badge-success";
    if (estado === "ANULADA") return "badge badge-danger";
    return "badge";
  };

  const totalCarrito = carrito.reduce((s, c) => s + c.cantidad, 0);

  return (
    <div className="public-page">
      <header className="public-navbar">
        <button
          className="public-brand"
          onClick={() => navigate("/")}
          style={{ background: "none", border: "none", cursor: "pointer", color: "#fff" }}
        >
          Gleyfor<span>Gym</span>
        </button>

        <nav className="public-menu">
          <a href="/" style={{ color: "#d4d4d8" }}>Inicio</a>
        </nav>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {isLoggedIn && carrito.length > 0 && (
            <button
              className="btn-primary"
              onClick={() => setTab("carrito")}
              style={{ position: "relative", padding: "8px 16px", fontSize: "13px" }}
            >
              Carrito ({totalCarrito})
            </button>
          )}
          <button className="btn-primary" onClick={() => navigate(isLoggedIn ? "/dashboard" : "/login")}>
            {isLoggedIn ? "Mi panel" : "Iniciar sesión"}
          </button>
        </div>
      </header>

      <section className="public-section" id="tienda" style={{ minHeight: "calc(100vh - 76px)" }}>
        <div className="section-title" style={{ textAlign: "center" }}>
          <span className="badge">Tienda</span>
          <h2>Productos y suplementos</h2>
        </div>

        <div style={{ maxWidth: "480px", margin: "0 auto 2rem" }}>
          <input
            className="search-input"
            placeholder="Buscar producto..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            style={{ width: "100%", padding: "12px 16px", fontSize: "15px", borderRadius: "12px", border: "1px solid var(--border)", background: "var(--surface)", color: "#fff" }}
          />
        </div>

        {error && <p className="error-message" style={{ textAlign: "center" }}>{error}</p>}

        {isLoggedIn && (
          <div style={{ display: "flex", gap: "0.5rem", justifyContent: "center", marginBottom: "2rem" }}>
            <button className={tab === "tienda" ? "btn-primary" : "btn-secondary"} onClick={() => setTab("tienda")}>Tienda</button>
            <button className={tab === "carrito" ? "btn-primary" : "btn-secondary"} onClick={() => setTab("carrito")}>Carrito ({totalCarrito})</button>
            <button className={tab === "pedidos" ? "btn-primary" : "btn-secondary"} onClick={() => setTab("pedidos")}>Mis pedidos ({pedidos.length})</button>
          </div>
        )}

        {!isLoggedIn && (
          <p style={{ textAlign: "center", color: "#a1a1aa", marginBottom: "2rem", fontSize: "15px" }}>
            <a href="/login" style={{ color: "var(--orange)", textDecoration: "none", fontWeight: 600 }}>Inicia sesión</a> para agregar productos al carrito.
          </p>
        )}

        {/* TAB: TIENDA */}
        {tab === "tienda" && (
          <div className="cards-grid">
            {filtrados.length === 0 ? (
              <p className="empty-message" style={{ gridColumn: "1 / -1", textAlign: "center" }}>No hay productos disponibles.</p>
            ) : (
              filtrados.map((p) => (
                <div key={p.id_producto} className="card item-card product-card">
                  <div className="product-image">
                    {p.imagen_url ? (
                      <img src={p.imagen_url} alt={p.nombre} />
                    ) : (
                      <div className="product-image-placeholder">
                        <span>{p.nombre.charAt(0)}</span>
                      </div>
                    )}
                  </div>
                  <div className="product-info">
                    <div className="item-card-top">
                      <span className="badge">{p.nombre_categoria || "PRODUCTO"}</span>
                      <span className="badge badge-success">S/ {Number(p.precio_venta).toFixed(2)}</span>
                    </div>
                    <h3>{p.nombre}</h3>
                    {p.descripcion && <p className="item-description">{p.descripcion}</p>}
                    <button
                      className="btn-primary"
                      disabled={(p.stock_actual || 0) <= 0}
                      onClick={() => agregarAlCarrito(p)}
                    >
                      {(p.stock_actual || 0) <= 0 ? "Sin stock" : isLoggedIn ? "+ Agregar" : "Iniciar sesión para comprar"}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* TAB: CARRITO */}
        {isLoggedIn && tab === "carrito" && (
          <div style={{ maxWidth: "700px", margin: "0 auto" }}>
            {carrito.length === 0 ? (
              <p className="empty-message" style={{ textAlign: "center" }}>Tu carrito está vacío.</p>
            ) : (
              <>
                {carrito.map((c) => (
                  <div key={c.id_producto} className="card item-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", padding: "16px 20px" }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={{ margin: 0, fontSize: "16px" }}>{c.nombre}</h3>
                      <p className="item-description" style={{ margin: 0 }}>S/ {c.precio_venta.toFixed(2)} c/u</p>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <input
                        type="number" min="1" max={c.stock_actual} value={c.cantidad}
                        onChange={(e) => actualizarCantidad(c.id_producto, e.target.value)}
                        style={{ width: "50px", padding: "6px", borderRadius: "8px", border: "1px solid #444", background: "#1a1a2e", color: "#fff", textAlign: "center" }}
                      />
                      <strong style={{ minWidth: "70px", textAlign: "right" }}>S/ {(c.cantidad * c.precio_venta).toFixed(2)}</strong>
                      <button className="btn-danger" onClick={() => eliminarDelCarrito(c.id_producto)} style={{ padding: "6px 12px", fontSize: "13px" }}>X</button>
                    </div>
                  </div>
                ))}

                <div className="card" style={{ padding: "24px", marginTop: "1rem" }}>
                  <div className="form-grid" style={{ marginBottom: "1rem" }}>
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
                      <input value={observaciones} onChange={(e) => setObservaciones(e.target.value)} placeholder="Nota opcional" />
                    </div>
                  </div>
                  <div style={{ textAlign: "right", marginBottom: "1rem", fontSize: "1.1rem" }}>
                    <p>Subtotal: <strong>S/ {subtotal.toFixed(2)}</strong></p>
                    <p><strong>Total: S/ {total.toFixed(2)}</strong></p>
                  </div>
                  <div className="form-actions" style={{ justifyContent: "flex-end" }}>
                    <button className="btn-secondary" onClick={() => setCarrito([])}>Vaciar</button>
                    <button className="btn-primary" disabled={procesando} onClick={checkout}>
                      {procesando ? "Procesando..." : "Confirmar pedido"}
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB: PEDIDOS */}
        {isLoggedIn && tab === "pedidos" && (
          <div style={{ maxWidth: "700px", margin: "0 auto" }}>
            {pedidos.length === 0 ? (
              <p className="empty-message" style={{ textAlign: "center" }}>No tienes pedidos registrados.</p>
            ) : (
              <div className="cards-grid" style={{ gridTemplateColumns: "1fr" }}>
                {pedidos.map((v) => (
                  <div key={v.id_venta} className="card item-card" style={{ padding: "20px" }}>
                    <div className="item-card-top">
                      <span className={badgeColor(v.estado)}>{v.estado}</span>
                      <span className="badge">#{v.id_venta}</span>
                    </div>
                    <div className="mini-stats-grid" style={{ marginTop: "0.5rem" }}>
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
          </div>
        )}
      </section>

      <footer className="public-footer">
        <h3>Gleyfor<span>Gym</span></h3>
        <p>© 2026 Todos los derechos reservados</p>
      </footer>
    </div>
  );
}

export default Tienda;
