import React, { useEffect, useState } from "react";
import api from "../api/api";

function Categorias() {
  const [categorias, setCategorias] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editando, setEditando] = useState(null);

  const formInicial = {
    nombre: "",
    descripcion: "",
    estado: "ACTIVO",
  };

  const [form, setForm] = useState(formInicial);

  const cargar = async () => {
    try {
      setError("");
      const res = await api.get("/categorias/");
      setCategorias(res.data);
    } catch (err) {
      console.error(err);
      setError("Error al cargar categorías");
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const cambiar = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const limpiar = () => {
    setForm(formInicial);
    setError("");
    setMostrarFormulario(false);
    setEditando(null);
  };

  const validar = () => {
    if (!form.nombre.trim()) return "Ingrese el nombre de la categoría";
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
        nombre: form.nombre,
        descripcion: form.descripcion || null,
        estado: form.estado,
      };

      if (editando) {
        await api.put(`/categorias/${editando.id_categoria}`, data);
      } else {
        await api.post("/categorias/", data);
      }

      limpiar();
      await cargar();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Error al guardar categoría");
    } finally {
      setCargando(false);
    }
  };

  const editar = (cat) => {
    setForm({
      nombre: cat.nombre,
      descripcion: cat.descripcion || "",
      estado: cat.estado,
    });
    setEditando(cat);
    setMostrarFormulario(true);
  };

  const desactivar = async (id) => {
    if (!globalThis.confirm("¿Seguro que deseas desactivar esta categoría?")) return;
    try {
      await api.delete(`/categorias/${id}`);
      await cargar();
    } catch (err) {
      console.error(err);
      setError("Error al desactivar categoría");
    }
  };

  const filtradas = categorias.filter((c) => {
    const t = busqueda.toLowerCase();
    return (
      String(c.nombre || "").toLowerCase().includes(t) ||
      String(c.descripcion || "").toLowerCase().includes(t) ||
      String(c.estado || "").toLowerCase().includes(t)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">COMERCIO</span>
          <h1>Categorías de productos</h1>
          <p>Administra las categorías para clasificar productos y suplementos.</p>
        </div>
        <button className="btn-primary" onClick={() => { setMostrarFormulario(true); setForm(formInicial); setEditando(null); setError(""); }}>
          + Nueva categoría
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card"><span>Total</span><strong>{categorias.length}</strong></div>
        <div className="stat-card"><span>Filtradas</span><strong>{filtradas.length}</strong></div>
        <div className="stat-card"><span>Activas</span><strong>{categorias.filter((c) => c.estado === "ACTIVO").length}</strong></div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editando ? "Editar categoría" : "Nueva categoría"}</h2>
              <p>{editando ? "Modifica los datos de la categoría." : "Registra una nueva categoría para productos."}</p>
            </div>
          </div>
          {error && <p className="error-message">{error}</p>}
          <div className="form-grid">
            <div className="form-field field-large">
              <label htmlFor="nombre">Nombre</label>
              <input id="nombre" name="nombre" value={form.nombre} onChange={cambiar} placeholder="Ej: Suplementos" />
            </div>
            <div className="form-field">
              <label htmlFor="estado">Estado</label>
              <select id="estado" name="estado" value={form.estado} onChange={cambiar}>
                <option value="ACTIVO">ACTIVO</option>
                <option value="INACTIVO">INACTIVO</option>
              </select>
            </div>
            <div className="form-field field-large">
              <label htmlFor="descripcion">Descripción</label>
              <textarea id="descripcion" name="descripcion" value={form.descripcion} onChange={cambiar} placeholder="Descripción de la categoría" />
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
          <div><h2>Lista de categorías</h2></div>
          <input className="search-input" placeholder="Buscar..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
        </div>
        {filtradas.length === 0 ? (
          <p className="empty-message">No hay categorías registradas.</p>
        ) : (
          <div className="cards-grid">
            {filtradas.map((c) => (
              <div key={c.id_categoria} className="card item-card">
                <div className="item-card-top">
                  <span className="badge">{c.estado}</span>
                </div>
                <h3>{c.nombre}</h3>
                {c.descripcion && <p className="item-description">{c.descripcion}</p>}
                <div className="item-actions">
                  <button className="btn-secondary" onClick={() => editar(c)}>Editar</button>
                  <button className="btn-danger" onClick={() => desactivar(c.id_categoria)}>Desactivar</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Categorias;
