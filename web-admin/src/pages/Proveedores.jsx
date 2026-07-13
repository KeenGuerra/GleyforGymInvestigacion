import React, { useEffect, useState } from "react";
import api from "../api/api";

function Proveedores() {
  const [proveedores, setProveedores] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editando, setEditando] = useState(null);

  const formInicial = { razon_social: "", ruc: "", telefono: "", correo: "", direccion: "", contacto: "", estado: "ACTIVO" };
  const [form, setForm] = useState(formInicial);

  const cargar = async () => {
    try { setError(""); const res = await api.get("/proveedores/"); setProveedores(res.data); }
    catch (err) { setError("Error al cargar proveedores"); }
  };

  useEffect(() => { cargar(); }, []);

  const cambiar = (e) => { setForm({ ...form, [e.target.name]: e.target.value }); };
  const limpiar = () => { setForm(formInicial); setError(""); setMostrarFormulario(false); setEditando(null); };

  const validar = () => {
    if (!form.razon_social.trim()) return "Ingrese la razón social";
    return "";
  };

  const guardar = async (e) => {
    e.preventDefault(); setError("");
    const msg = validar(); if (msg) { setError(msg); return; }
    try {
      setCargando(true);
      const data = { razon_social: form.razon_social, ruc: form.ruc || null, telefono: form.telefono || null, correo: form.correo || null, direccion: form.direccion || null, contacto: form.contacto || null, estado: form.estado };
      if (editando) { await api.put(`/proveedores/${editando.id_proveedor}`, data); }
      else { await api.post("/proveedores/", data); }
      limpiar(); await cargar();
    } catch (err) { setError(err.response?.data?.detail || "Error al guardar"); }
    finally { setCargando(false); }
  };

  const editar = (p) => {
    setForm({ razon_social: p.razon_social, ruc: p.ruc || "", telefono: p.telefono || "", correo: p.correo || "", direccion: p.direccion || "", contacto: p.contacto || "", estado: p.estado });
    setEditando(p); setMostrarFormulario(true);
  };

  const desactivar = async (id) => {
    if (!globalThis.confirm("¿Desactivar proveedor?")) return;
    try { await api.delete(`/proveedores/${id}`); await cargar(); } catch (err) { setError("Error al desactivar"); }
  };

  const filtrados = proveedores.filter((p) => {
    const t = busqueda.toLowerCase();
    return String(p.razon_social || "").toLowerCase().includes(t) || String(p.ruc || "").includes(t) || String(p.estado || "").toLowerCase().includes(t);
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">COMERCIO</span>
          <h1>Proveedores</h1>
          <p>Gestiona los proveedores de productos y suplementos.</p>
        </div>
        <button className="btn-primary" onClick={() => { setMostrarFormulario(true); setForm(formInicial); setEditando(null); }}>
          + Nuevo proveedor
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card"><span>Total</span><strong>{proveedores.length}</strong></div>
        <div className="stat-card"><span>Filtrados</span><strong>{filtrados.length}</strong></div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header"><div><h2>{editando ? "Editar proveedor" : "Nuevo proveedor"}</h2></div></div>
          {error && <p className="error-message">{error}</p>}
          <div className="form-grid">
            <div className="form-field field-large"><label>Razón social</label><input name="razon_social" value={form.razon_social} onChange={cambiar} /></div>
            <div className="form-field"><label>RUC</label><input name="ruc" value={form.ruc} onChange={cambiar} /></div>
            <div className="form-field"><label>Teléfono</label><input name="telefono" value={form.telefono} onChange={cambiar} /></div>
            <div className="form-field"><label>Correo</label><input name="correo" type="email" value={form.correo} onChange={cambiar} /></div>
            <div className="form-field"><label>Contacto</label><input name="contacto" value={form.contacto} onChange={cambiar} /></div>
            <div className="form-field"><label>Estado</label><select name="estado" value={form.estado} onChange={cambiar}><option>ACTIVO</option><option>INACTIVO</option></select></div>
            <div className="form-field field-large"><label>Dirección</label><input name="direccion" value={form.direccion} onChange={cambiar} /></div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={cargando}>{cargando ? "Guardando..." : "Guardar"}</button>
            <button type="button" className="btn-secondary" onClick={limpiar}>Cancelar</button>
          </div>
        </form>
      )}

      <section className="table-card">
        <div className="card-header">
          <div><h2>Lista de proveedores</h2></div>
          <input className="search-input" placeholder="Buscar..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
        </div>
        {filtrados.length === 0 ? <p className="empty-message">No hay proveedores.</p> : (
          <div className="cards-grid">
            {filtrados.map((p) => (
              <div key={p.id_proveedor} className="card item-card">
                <div className="item-card-top"><span className="badge">{p.estado}</span></div>
                <h3>{p.razon_social}</h3>
                {p.ruc && <p className="item-description">RUC: {p.ruc}</p>}
                {p.telefono && <p className="item-description">Tel: {p.telefono}</p>}
                {p.correo && <p className="item-description">Email: {p.correo}</p>}
                {p.contacto && <p className="item-description">Contacto: {p.contacto}</p>}
                <div className="item-actions">
                  <button className="btn-secondary" onClick={() => editar(p)}>Editar</button>
                  <button className="btn-danger" onClick={() => desactivar(p.id_proveedor)}>Desactivar</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Proveedores;
