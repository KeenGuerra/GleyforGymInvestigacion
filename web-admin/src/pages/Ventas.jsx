import React, { useCallback, useEffect, useState } from "react";
import api from "../api/api";
import { descargarBlob } from "../utils/descargarArchivo";
import { useConfirmacion } from "../hooks/useConfirmacion";
import ConfirmModal from "../components/ConfirmModal";

const VENTAS_POR_PAGINA = 20;

function Ventas() {
  const { pregunta, confirmarAccion, responderConfirmacion } = useConfirmacion();
  const rol = localStorage.getItem("rol");
  const [ventas, setVentas] = useState([]);
  const [productos, setProductos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [procesando, setProcesando] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("TODAS");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [detalle, setDetalle] = useState([]);
  const [resumen, setResumen] = useState({});
  const [pagina, setPagina] = useState(0);
  const [haySiguiente, setHaySiguiente] = useState(false);

  const formInicial = { id_cliente: "", metodo_pago: "EFECTIVO", descuento: 0, observaciones: "" };
  const [form, setForm] = useState(formInicial);
  const [codigoEscaneado, setCodigoEscaneado] = useState("");
  const [escaneando, setEscaneando] = useState(false);

  const cargar = useCallback(async (paginaActual = pagina) => {
    try {
      const [r1, r2, r3, r4] = await Promise.all([
        api.get("/ventas/", { params: { skip: paginaActual * VENTAS_POR_PAGINA, limit: VENTAS_POR_PAGINA } }),
        api.get("/productos/disponibles"),
        api.get("/clientes/"), api.get("/ventas/resumen"),
      ]);
      setVentas(r1.data); setHaySiguiente(r1.data.length === VENTAS_POR_PAGINA);
      setProductos(r2.data); setClientes(r3.data); setResumen(r4.data);
    } catch { setError("Error al cargar datos"); }
  }, [pagina]);

  useEffect(() => { cargar(pagina); }, [pagina, cargar]);

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

  // Un lector de código de barras USB/Bluetooth "escribe" el código como si
  // fuera un teclado y termina con Enter -- por eso esto es un input normal
  // con un onKeyDown, no una integración especial con ningún hardware.
  const agregarPorCodigo = async () => {
    const codigo = codigoEscaneado.trim();
    if (!codigo) return;

    try {
      setEscaneando(true);
      setError("");
      const res = await api.get(`/productos/por-codigo/${encodeURIComponent(codigo)}`);
      const producto = res.data;

      setDetalle((prev) => {
        const existente = prev.find((d) => Number(d.id_producto) === producto.id_producto);
        if (existente) {
          return prev.map((d) =>
            Number(d.id_producto) === producto.id_producto
              ? { ...d, cantidad: Number(d.cantidad) + 1 }
              : d
          );
        }
        return [...prev, { id_producto: String(producto.id_producto), cantidad: 1 }];
      });
      setCodigoEscaneado("");
    } catch (err) {
      setError(
        err.response?.status === 404
          ? `No hay ningún producto con el código ${codigo}`
          : "Error al buscar el código de barras"
      );
    } finally {
      setEscaneando(false);
    }
  };

  const manejarTeclaEscaneo = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      agregarPorCodigo();
    }
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
    if (!(await confirmarAccion("¿Anular esta venta? Se revertirá el inventario."))) return;
    try { setProcesando(id); await api.post(`/ventas/${id}/anular`); await cargar(); }
    catch (err) { setError(err.response?.data?.detail || "Error al anular"); }
    finally { setProcesando(null); }
  };

  const confirmar = async (id) => {
    if (!(await confirmarAccion("¿Confirmar esta venta? Se descontará el inventario."))) return;
    try { setProcesando(id); await api.post(`/ventas/${id}/confirmar`); await cargar(); }
    catch (err) { setError(err.response?.data?.detail || "Error al confirmar"); }
    finally { setProcesando(null); }
  };

  const enviarConfirmacionWhatsApp = (venta) => {
    const cliente = clientes.find((c) => c.id_cliente === venta.id_cliente);
    const telefono = (cliente?.telefono || "").trim();
    if (!(telefono.length === 9 && /^\d+$/.test(telefono))) {
      setError(`${venta.nombre_cliente || "Este cliente"} no tiene un teléfono válido de 9 dígitos registrado.`);
      return;
    }
    const primerNombre = (venta.nombre_cliente || "").split(" ")[0] || "";
    const mensaje =
      `¡Hola ${primerNombre}! 👋\n\n` +
      `Confirmamos tu pago de *S/ ${Number(venta.total || 0).toFixed(2)}* por Yape ✅\n\n` +
      "Ya puedes pasar a recogerlo al gimnasio.\n\n" +
      "*GLEYFORGYM* 🏋️";
    const url = `https://wa.me/51${telefono}?text=${encodeURIComponent(mensaje)}`;
    globalThis.open(url, "_blank");
  };

  const entregar = async (id) => {
    if (!(await confirmarAccion("¿Marcar esta venta como entregada? El cliente ya pasó a recogerla."))) return;
    try { setProcesando(id); await api.post(`/ventas/${id}/entregar`); await cargar(); }
    catch (err) { setError(err.response?.data?.detail || "Error al marcar como entregada"); }
    finally { setProcesando(null); }
  };

  const descargarBoleta = async (id) => {
    try {
      const res = await api.get(`/ventas/${id}/boleta`, { responseType: "blob" });
      descargarBlob(res.data, `boleta-venta-${id}.pdf`);
    } catch {
      setError("No se pudo descargar la boleta");
    }
  };

  const filtradasPorBusqueda = ventas.filter((v) => {
    const t = busqueda.toLowerCase();
    return (
      String(v.id_venta || "").includes(t) ||
      String(v.nombre_cliente || "").toLowerCase().includes(t) ||
      String(v.metodo_pago || "").toLowerCase().includes(t) ||
      String(v.estado || "").toLowerCase().includes(t)
    );
  });

  // Agrupar por estado para que el staff vea primero lo que necesita accion
  // (pendientes de confirmar) en vez de una sola grilla con todo mezclado.
  const conteoPorEstado = filtradasPorBusqueda.reduce((acc, v) => {
    acc[v.estado] = (acc[v.estado] || 0) + 1;
    return acc;
  }, {});
  const ESTADOS_VENTA = ["PENDIENTE", "CONFIRMADA", "ENTREGADA", "ANULADA"];

  const filtradas =
    filtroEstado === "TODAS"
      ? filtradasPorBusqueda
      : filtradasPorBusqueda.filter((v) => v.estado === filtroEstado);

  const badgeColor = (estado) => {
    if (estado === "ENTREGADA") return "badge badge-success";
    if (estado === "CONFIRMADA") return "badge badge-warning";
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
              {/* Solo los 3 métodos que el gimnasio realmente usa en el
                  mostrador -- el mismo criterio que ya tenía Pagos.jsx. */}
              <select name="metodo_pago" value={form.metodo_pago} onChange={cambiar}>
                <option value="EFECTIVO">EFECTIVO</option>
                <option value="YAPE">YAPE</option>
                <option value="PLIN">PLIN</option>
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

          <h3 className="detail-heading">Detalle de productos</h3>

          <div className="form-field field-large">
            <label>Escanear código de barras</label>
            <input
              value={codigoEscaneado}
              onChange={(e) => setCodigoEscaneado(e.target.value)}
              onKeyDown={manejarTeclaEscaneo}
              disabled={escaneando}
              placeholder="Apunta el lector aquí y escanea, o escribe el código y presiona Enter"
              autoComplete="off"
            />
          </div>

          {detalle.map((d, i) => {
            const prod = getProducto(d.id_producto);
            const sub = prod ? Number(d.cantidad) * prod.precio_venta : 0;
            return (
              <div key={i} className="form-grid detail-row">
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

          <button type="button" className="btn-secondary spaced-top-sm" onClick={agregarDetalle}>+ Agregar producto</button>

          <div className="totals-box">
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

        <div className="estado-filtros">
          {ESTADOS_VENTA.map((estado) => (
            <button
              key={estado}
              type="button"
              className={filtroEstado === estado ? "active" : ""}
              onClick={() => setFiltroEstado(estado)}
            >
              {estado}
              <span className="count">{conteoPorEstado[estado] || 0}</span>
            </button>
          ))}
          <button
            type="button"
            className={filtroEstado === "TODAS" ? "active" : ""}
            onClick={() => setFiltroEstado("TODAS")}
          >
            Todas
            <span className="count">{filtradasPorBusqueda.length}</span>
          </button>
        </div>

        {(pagina > 0 || haySiguiente) && (
          <p className="item-description">
            El filtro y los conteos son solo de esta página (las {VENTAS_POR_PAGINA} ventas más recientes
            cargadas); cambia de página para revisar el resto del historial.
          </p>
        )}

        {filtradas.length === 0 ? <p className="empty-message">No hay ventas con ese filtro.</p> : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Cliente</th>
                  <th>Total</th>
                  <th>Método</th>
                  <th>Productos</th>
                  <th>Fecha</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtradas.map((v) => (
                  <tr key={v.id_venta}>
                    <td><span className="badge">#{v.id_venta}</span></td>
                    <td>{v.nombre_cliente || "Venta general"}</td>
                    <td>S/ {v.total?.toFixed(2)}</td>
                    <td>{v.metodo_pago}</td>
                    <td>{v.detalles?.length || 0}</td>
                    <td>{new Date(v.fecha_venta).toLocaleString()}</td>
                    <td><span className={badgeColor(v.estado)}>{v.estado}</span></td>
                    <td>
                      <div className="table-actions">
                        {v.estado === "PENDIENTE" && ["ADMIN", "ENTRENADOR", "RECEPCIONISTA"].includes(rol) && (
                          <button className="btn-primary" disabled={procesando === v.id_venta} onClick={() => confirmar(v.id_venta)}>
                            {procesando === v.id_venta ? "Confirmando..." : "Confirmar"}
                          </button>
                        )}
                        {(v.estado === "CONFIRMADA" || v.estado === "ENTREGADA") && (
                          <>
                            {v.estado === "CONFIRMADA" && (
                              <>
                                <button className="btn-primary" disabled={procesando === v.id_venta} onClick={() => entregar(v.id_venta)}>
                                  {procesando === v.id_venta ? "Marcando..." : "Marcar como entregado"}
                                </button>
                                <button className="btn-secondary" onClick={() => enviarConfirmacionWhatsApp(v)}>
                                  Avisar por WhatsApp
                                </button>
                              </>
                            )}
                            <button className="btn-secondary" onClick={() => descargarBoleta(v.id_venta)}>
                              Descargar boleta
                            </button>
                            <button className="btn-danger" disabled={procesando === v.id_venta} onClick={() => anular(v.id_venta)}>
                              {procesando === v.id_venta ? "Anulando..." : "Anular"}
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="card-actions">
          <button
            className="btn-secondary"
            disabled={pagina === 0}
            onClick={() => setPagina((p) => Math.max(0, p - 1))}
          >
            Anterior
          </button>
          <span>Página {pagina + 1}</span>
          <button
            className="btn-secondary"
            disabled={!haySiguiente}
            onClick={() => setPagina((p) => p + 1)}
          >
            Siguiente
          </button>
        </div>
      </section>

      <ConfirmModal pregunta={pregunta} onResponder={responderConfirmacion} />
    </div>
  );
}

export default Ventas;
