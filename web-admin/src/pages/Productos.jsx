import React, { useEffect, useState } from "react";
import api from "../api/api";

function Productos() {
  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editando, setEditando] = useState(null);

  const formInicial = {
    id_categoria: "",
    nombre: "",
    descripcion: "",
    precio_compra: "",
    precio_venta: "",
    unidad_medida: "UNIDAD",
    stock_minimo: "",
    controla_lote: false,
    controla_vencimiento: false,
    estado: "ACTIVO",
  };

  const [form, setForm] = useState(formInicial);

  const cargar = async () => {
    try {
      setError("");
      const [resProd, resCat] = await Promise.all([
        api.get("/productos/"),
        api.get("/categorias/"),
      ]);
      setProductos(resProd.data);
      setCategorias(resCat.data);
    } catch (err) {
      console.error(err);
      setError("Error al cargar productos");
    }
  };

  useEffect(() => { cargar(); }, []);

  const cambiar = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const limpiar = () => { setForm(formInicial); setError(""); setMostrarFormulario(false); setEditando(null); };

  const validar = () => {
    if (!form.nombre.trim()) return "Ingrese el nombre del producto";
    if (!form.precio_venta || Number(form.precio_venta) < 0) return "Precio de venta inválido";
    return "";
  };

  const guardar = async (e) => {
    e.preventDefault();
    setError("");
    const msg = validar();
    if (msg) { setError(msg); return; }

    try {
      setCargando(true);
      const data = {
        id_categoria: form.id_categoria ? Number(form.id_categoria) : null,
        nombre: form.nombre,
        descripcion: form.descripcion || null,
        precio_compra: Number(form.precio_compra) || 0,
        precio_venta: Number(form.precio_venta) || 0,
        unidad_medida: form.unidad_medida,
        stock_minimo: Number(form.stock_minimo) || 0,
        controla_lote: form.controla_lote,
        controla_vencimiento: form.controla_vencimiento,
        estado: form.estado,
      };

      if (editando) {
        await api.put(`/productos/${editando.id_producto}`, data);
      } else {
        await api.post("/productos/", data);
      }
      limpiar();
      await cargar();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Error al guardar producto");
    } finally {
      setCargando(false);
    }
  };

  const editar = (p) => {
    setForm({
      id_categoria: p.id_categoria || "",
      nombre: p.nombre,
      descripcion: p.descripcion || "",
      precio_compra: p.precio_compra || "",
      precio_venta: p.precio_venta || "",
      unidad_medida: p.unidad_medida || "UNIDAD",
      stock_minimo: p.stock_minimo || "",
      controla_lote: p.controla_lote || false,
      controla_vencimiento: p.controla_vencimiento || false,
      estado: p.estado,
    });
    setEditando(p);
    setMostrarFormulario(true);
  };

  const desactivar = async (id) => {
    if (!globalThis.confirm("¿Seguro que deseas desactivar este producto?")) return;
    try { await api.delete(`/productos/${id}`); await cargar(); } catch (err) { setError("Error al desactivar"); }
  };

  const filtrados = productos.filter((p) => {
    const t = busqueda.toLowerCase();
    return (
      String(p.nombre || "").toLowerCase().includes(t) ||
      String(p.nombre_categoria || "").toLowerCase().includes(t) ||
      String(p.estado || "").toLowerCase().includes(t)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">COMERCIO</span>
          <h1>Productos y suplementos</h1>
          <p>Registra productos, precios, stock mínimo y control de lotes.</p>
        </div>
        <button className="btn-primary" onClick={() => { setMostrarFormulario(true); setForm(formInicial); setEditando(null); }}>
          + Nuevo producto
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card"><span>Total</span><strong>{productos.length}</strong></div>
        <div className="stat-card"><span>Filtrados</span><strong>{filtrados.length}</strong></div>
        <div className="stat-card"><span>Activos</span><strong>{productos.filter((p) => p.estado === "ACTIVO").length}</strong></div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header"><div><h2>{editando ? "Editar producto" : "Nuevo producto"}</h2></div></div>
          {error && <p className="error-message">{error}</p>}
          <div className="form-grid">
            <div className="form-field field-large">
              <label>Nombre</label>
              <input name="nombre" value={form.nombre} onChange={cambiar} placeholder="Nombre del producto" />
            </div>
            <div className="form-field">
              <label>Categoría</label>
              <select name="id_categoria" value={form.id_categoria} onChange={cambiar}>
                <option value="">Sin categoría</option>
                {categorias.filter((c) => c.estado === "ACTIVO").map((c) => (
                  <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Precio compra (S/)</label>
              <input name="precio_compra" type="number" step="0.01" value={form.precio_compra} onChange={cambiar} />
            </div>
            <div className="form-field">
              <label>Precio venta (S/)</label>
              <input name="precio_venta" type="number" step="0.01" value={form.precio_venta} onChange={cambiar} />
            </div>
            <div className="form-field">
              <label>Unidad</label>
              <select name="unidad_medida" value={form.unidad_medida} onChange={cambiar}>
                <option>UNIDAD</option>
                <option>KILOGRAMO</option>
                <option>GRAMO</option>
                <option>LITRO</option>
                <option>MILILITRO</option>
                <option>CAJA</option>
                <option>PAQUETE</option>
              </select>
            </div>
            <div className="form-field">
              <label>Stock mínimo</label>
              <input name="stock_minimo" type="number" value={form.stock_minimo} onChange={cambiar} />
            </div>
            <div className="form-field">
              <label>Estado</label>
              <select name="estado" value={form.estado} onChange={cambiar}>
                <option value="ACTIVO">ACTIVO</option>
                <option value="INACTIVO">INACTIVO</option>
              </select>
            </div>
            <div className="form-field">
              <label><input type="checkbox" name="controla_lote" checked={form.controla_lote} onChange={cambiar} /> Controla lote</label>
            </div>
            <div className="form-field">
              <label><input type="checkbox" name="controla_vencimiento" checked={form.controla_vencimiento} onChange={cambiar} /> Controla vencimiento</label>
            </div>
            <div className="form-field field-large">
              <label>Descripción</label>
              <textarea name="descripcion" value={form.descripcion} onChange={cambiar} />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={cargando}>{cargando ? "Guardando..." : "Guardar"}</button>
            <button type="button" className="btn-secondary" onClick={limpiar}>Cancelar</button>
          </div>
        </form>
      )}

      <section className="table-card">
        <div className="card-header">
          <div><h2>Lista de productos</h2></div>
          <input className="search-input" placeholder="Buscar..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
        </div>
        {filtrados.length === 0 ? (
          <p className="empty-message">No hay productos registrados.</p>
        ) : (
          <div className="cards-grid">
            {filtrados.map((p) => (
              <div key={p.id_producto} className="card item-card">
                <div className="item-card-top">
                  <span className="badge">{p.nombre_categoria || "SIN CAT."}</span>
                  <span className="badge">{p.estado}</span>
                </div>
                <h3>{p.nombre}</h3>
                <div className="mini-stats-grid">
                  <div><strong>S/{p.precio_venta}</strong><span>Venta</span></div>
                  <div><strong>S/{p.precio_compra}</strong><span>Compra</span></div>
                  <div><strong>{p.stock_actual || 0}</strong><span>Stock</span></div>
                  <div><strong>{p.unidad_medida}</strong><span>Unidad</span></div>
                </div>
                {p.descripcion && <p className="item-description">{p.descripcion}</p>}
                <div className="item-actions">
                  <button className="btn-secondary" onClick={() => editar(p)}>Editar</button>
                  <button className="btn-danger" onClick={() => desactivar(p.id_producto)}>Desactivar</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Productos;
