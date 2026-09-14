import React, { useEffect, useState } from "react";
import api from "../api/api";

const TIPOS = ["HORARIO", "COACHES", "BAILE", "COMUNICADO", "EVENTO"];

function GestionAvisos() {
  const [avisos, setAvisos] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editandoId, setEditandoId] = useState(null);

  const formInicial = {
    titulo: "",
    contenido: "",
    tipo: "COMUNICADO",
    fecha_evento: "",
    estado: "ACTIVO",
  };

  const [form, setForm] = useState(formInicial);

  const cargarAvisos = async () => {
    try {
      setError("");
      const res = await api.get("/avisos/");
      setAvisos(res.data);
    } catch (error) {
      console.error(error);
      setError("Error al cargar avisos");
    }
  };

  useEffect(() => {
    cargarAvisos();
  }, []);

  const cambiar = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const limpiar = () => {
    setForm(formInicial);
    setEditandoId(null);
    setError("");
    setMostrarFormulario(false);
  };

  const validar = () => {
    if (!form.titulo.trim()) return "Ingrese el título del aviso";
    if (!form.contenido.trim()) return "Ingrese el contenido del aviso";
    return "";
  };

  const guardar = async (e) => {
    e.preventDefault();
    setError("");

    const mensaje = validar();
    if (mensaje) {
      setError(mensaje);
      return;
    }

    const data = {
      titulo: form.titulo,
      contenido: form.contenido,
      tipo: form.tipo,
      fecha_evento: form.fecha_evento || null,
      estado: form.estado,
    };

    try {
      if (editandoId) {
        await api.put(`/avisos/${editandoId}`, data);
      } else {
        await api.post("/avisos/", data);
      }
      limpiar();
      await cargarAvisos();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al guardar el aviso");
    }
  };

  const editar = (aviso) => {
    setEditandoId(aviso.id_aviso);
    setMostrarFormulario(true);
    setForm({
      titulo: aviso.titulo || "",
      contenido: aviso.contenido || "",
      tipo: aviso.tipo || "COMUNICADO",
      fecha_evento: aviso.fecha_evento || "",
      estado: aviso.estado || "ACTIVO",
    });
    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const desactivar = async (id) => {
    if (!globalThis.confirm("¿Seguro que deseas desactivar este aviso?")) return;

    try {
      await api.delete(`/avisos/${id}`);
      await cargarAvisos();
    } catch (error) {
      console.error(error);
      setError("Error al desactivar el aviso");
    }
  };

  const avisosFiltrados = avisos.filter((a) => {
    const texto = busqueda.toLowerCase();
    return (
      String(a.titulo || "").toLowerCase().includes(texto) ||
      String(a.tipo || "").toLowerCase().includes(texto) ||
      String(a.estado || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">AVISOS</span>
          <h1>Gestión de avisos</h1>
          <p>Edita los horarios, coaches, clases y comunicados que ven tus clientes en la página pública.</p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            setMostrarFormulario(true);
            setEditandoId(null);
            setForm(formInicial);
            setError("");
          }}
        >
          + Nuevo aviso
        </button>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editandoId ? "Editar aviso" : "Nuevo aviso"}</h2>
              <p>Este contenido se muestra en la página pública "/avisos".</p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="titulo">Título</label>
              <input
                id="titulo"
                name="titulo"
                placeholder="Ej: Deyvi, o Lunes a Sábado"
                value={form.titulo}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="tipo">Tipo</label>
              <select id="tipo" name="tipo" value={form.tipo} onChange={cambiar}>
                {TIPOS.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            {form.tipo === "EVENTO" && (
              <div className="form-field">
                <label htmlFor="fecha_evento">Fecha del evento</label>
                <input
                  id="fecha_evento"
                  name="fecha_evento"
                  type="date"
                  value={form.fecha_evento}
                  onChange={cambiar}
                />
              </div>
            )}

            <div className="form-field">
              <label htmlFor="estado">Estado</label>
              <select id="estado" name="estado" value={form.estado} onChange={cambiar}>
                <option value="ACTIVO">ACTIVO</option>
                <option value="INACTIVO">INACTIVO</option>
              </select>
            </div>

            <div className="form-field field-large">
              <label htmlFor="contenido">Contenido</label>
              <textarea
                id="contenido"
                name="contenido"
                placeholder="Ej: Lun – Vie: 6:00 am – 12:00 pm | 3:00 pm – 9:00 pm"
                value={form.contenido}
                onChange={cambiar}
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {editandoId ? "Actualizar aviso" : "Guardar aviso"}
            </button>
            <button type="button" className="btn-secondary" onClick={limpiar}>
              Cancelar
            </button>
          </div>
        </form>
      )}

      {error && !mostrarFormulario && <p className="error-message">{error}</p>}

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Lista de avisos</h2>
            <p>Consulta, edita o desactiva los avisos publicados.</p>
          </div>

          <input
            className="search-input"
            placeholder="Buscar por título, tipo o estado..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        {avisosFiltrados.length === 0 ? (
          <p className="empty-message">No hay avisos registrados.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Título</th>
                  <th>Tipo</th>
                  <th>Contenido</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {avisosFiltrados.map((a) => (
                  <tr key={a.id_aviso}>
                    <td>{a.titulo}</td>
                    <td><span className="badge">{a.tipo}</span></td>
                    <td>{a.contenido}</td>
                    <td><span className="badge">{a.estado}</span></td>
                    <td>
                      <div className="table-actions">
                        <button className="btn-secondary" onClick={() => editar(a)}>
                          Editar
                        </button>
                        <button className="btn-danger" onClick={() => desactivar(a.id_aviso)}>
                          Desactivar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default GestionAvisos;
