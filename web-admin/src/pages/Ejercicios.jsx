import React, { useEffect, useRef, useState } from "react";
import api from "../api/api";
import { OBJETIVOS, NIVELES, GRUPOS_MUSCULARES, RESTRICCIONES_MEDICAS, codigosATexto, textoACodigos } from "../constants/opciones";

function Ejercicios() {
  const [ejercicios, setEjercicios] = useState([]);
  const [video, setVideo] = useState(null);
  const [imagenRef, setImagenRef] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editandoId, setEditandoId] = useState(null);

  const fileRef = useRef(null);
  const fileRefImagen = useRef(null);

  const formInicial = {
    nombre: "",
    grupo_muscular: "",
    nivel: "",
    objetivo: "",
    descripcion: "",
    instrucciones: "",
    estado: "ACTIVO",
    restricciones: "",
  };

  const [form, setForm] = useState(formInicial);

  const alternarRestriccion = (codigo) => {
    const actuales = textoACodigos(form.restricciones);
    const nuevas = actuales.includes(codigo)
      ? actuales.filter((c) => c !== codigo)
      : [...actuales, codigo];
    setForm({ ...form, restricciones: codigosATexto(nuevas) });
  };

  const cargar = async () => {
    try {
      setError("");
      const res = await api.get("/ejercicios/");
      setEjercicios(res.data);
    } catch (error) {
      console.error("Error al cargar ejercicios:", error);
      setError("No se pudieron cargar los ejercicios");
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const cambiar = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const limpiarFormulario = () => {
    setForm(formInicial);
    setVideo(null);
    setImagenRef(null);
    setError("");
    setMostrarFormulario(false);
    setEditandoId(null);

    if (fileRef.current) fileRef.current.value = "";
    if (fileRefImagen.current) fileRefImagen.current.value = "";
  };

  const iniciarEdicion = (ejercicio) => {
    setForm({
      nombre: ejercicio.nombre || "",
      grupo_muscular: ejercicio.grupo_muscular || "",
      nivel: ejercicio.nivel || "",
      objetivo: ejercicio.objetivo || "",
      descripcion: ejercicio.descripcion || "",
      instrucciones: ejercicio.instrucciones || "",
      estado: ejercicio.estado || "ACTIVO",
      restricciones: ejercicio.restricciones || "",
    });
    setVideo(null);
    setImagenRef(null);
    setEditandoId(ejercicio.id_ejercicio);
    setError("");
    setMostrarFormulario(true);
  };

  const validar = () => {
    if (!form.nombre.trim()) return "Ingrese el nombre del ejercicio";
    if (!form.grupo_muscular.trim()) return "Ingrese el grupo muscular";
    if (!form.nivel) return "Seleccione el nivel";
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

    try {
      setCargando(true);

      if (editandoId) {
        await api.put(`/ejercicios/${editandoId}`, {
          nombre: form.nombre,
          grupo_muscular: form.grupo_muscular,
          nivel: form.nivel,
          objetivo: form.objetivo || null,
          descripcion: form.descripcion || null,
          instrucciones: form.instrucciones || null,
          estado: form.estado,
          restricciones: form.restricciones || null,
        });
      } else {
        const data = new FormData();

        Object.entries(form).forEach(([key, value]) => {
          data.append(key, value || "");
        });

        if (video) data.append("video", video);
        if (imagenRef) data.append("imagen", imagenRef);

        await api.post("/ejercicios/", data, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }

      limpiarFormulario();
      await cargar();
    } catch (error) {
      console.error("Error al guardar ejercicio:", error);
      setError(error.response?.data?.detail || "Error al guardar el ejercicio");
    } finally {
      setCargando(false);
    }
  };

  const desactivar = async (id) => {
    const confirmar = globalThis.confirm(
      "¿Seguro que deseas desactivar este ejercicio?"
    );
    if (!confirmar) return;

    try {
      await api.delete(`/ejercicios/${id}`);
      await cargar();
    } catch (error) {
      console.error("Error al desactivar ejercicio:", error);
      setError("No se pudo desactivar el ejercicio");
    }
  };

  const activar = async (id) => {
    try {
      await api.put(`/ejercicios/${id}`, { estado: "ACTIVO" });
      await cargar();
    } catch (error) {
      console.error("Error al activar ejercicio:", error);
      setError("No se pudo activar el ejercicio");
    }
  };

  const ejerciciosFiltrados = ejercicios.filter((e) => {
    const texto = busqueda.toLowerCase();

    return (
      String(e.nombre || "").toLowerCase().includes(texto) ||
      String(e.grupo_muscular || "").toLowerCase().includes(texto) ||
      String(e.nivel || "").toLowerCase().includes(texto) ||
      String(e.objetivo || "").toLowerCase().includes(texto) ||
      String(e.estado || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">RUTINAS IA</span>
          <h1>Gestión de ejercicios</h1>
          <p>Registra ejercicios con videos para que la IA genere rutinas más completas.</p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            setMostrarFormulario(true);
            setForm(formInicial);
            setEditandoId(null);
            setError("");
          }}
        >
          + Registrar ejercicio
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Total ejercicios</span>
          <strong>{ejercicios.length}</strong>
        </div>

        <div className="stat-card">
          <span>Filtrados</span>
          <strong>{ejerciciosFiltrados.length}</strong>
        </div>

        <div className="stat-card">
          <span>Activos</span>
          <strong>{ejercicios.filter((e) => e.estado === "ACTIVO").length}</strong>
        </div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editandoId ? "Editar ejercicio" : "Registrar ejercicio"}</h2>
              <p>
                {editandoId
                  ? "Actualiza los datos de este ejercicio del catálogo."
                  : "Agrega nombre, grupo muscular, nivel, objetivo y video."}
              </p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="nombre">Nombre</label>
              <input id="nombre" name="nombre" value={form.nombre} onChange={cambiar} />
            </div>

            <div className="form-field">
              <label htmlFor="grupo_muscular">Grupo muscular</label>
              <select id="grupo_muscular" name="grupo_muscular" value={form.grupo_muscular} onChange={cambiar}>
                <option value="">Seleccionar</option>
                {GRUPOS_MUSCULARES.map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="nivel">Nivel</label>
              <select id="nivel" name="nivel" value={form.nivel} onChange={cambiar}>
                <option value="">Seleccionar</option>
                {NIVELES.map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="objetivo">Objetivo</label>
              <select id="objetivo" name="objetivo" value={form.objetivo} onChange={cambiar}>
                <option value="">Seleccionar</option>
                {OBJETIVOS.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="estado">Estado</label>
              <select id="estado" name="estado" value={form.estado} onChange={cambiar}>
                <option>ACTIVO</option>
                <option>INACTIVO</option>
              </select>
            </div>

            {editandoId ? (
              <div className="form-field field-large">
                <p className="muted-text" style={{ margin: 0 }}>
                  El video y la imagen no se pueden cambiar desde aquí. Para reemplazarlos,
                  desactiva este ejercicio y registra uno nuevo con los archivos actualizados.
                </p>
              </div>
            ) : (
              <>
                <div className="form-field">
                  <label htmlFor="video">Video</label>
                  <input
                    id="video"
                    ref={fileRef}
                    type="file"
                    accept="video/*"
                    onChange={(e) => setVideo(e.target.files[0] || null)}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="imagen">Imagen de referencia (para el PDF de la rutina)</label>
                  <input
                    id="imagen"
                    ref={fileRefImagen}
                    type="file"
                    accept="image/*"
                    onChange={(e) => setImagenRef(e.target.files[0] || null)}
                  />
                </div>
              </>
            )}

            <div className="form-field field-large">
              <label htmlFor="descripcion">Descripción</label>
              <textarea id="descripcion" name="descripcion" value={form.descripcion} onChange={cambiar} />
            </div>

            <div className="form-field field-large">
              <label htmlFor="instrucciones">Instrucciones</label>
              <textarea id="instrucciones" name="instrucciones" value={form.instrucciones} onChange={cambiar} />
            </div>

            <div className="form-field field-large">
              <label>Restricciones físicas que agrava (para excluirlo si el cliente las tiene)</label>
              <div className="checkbox-group">
                {RESTRICCIONES_MEDICAS.map((r) => (
                  <label key={r.value} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={textoACodigos(form.restricciones).includes(r.value)}
                      onChange={() => alternarRestriccion(r.value)}
                    />
                    {r.label}
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={cargando}>
              {cargando ? "Guardando..." : editandoId ? "Guardar cambios" : "Guardar ejercicio"}
            </button>

            <button type="button" className="btn-secondary" onClick={limpiarFormulario}>
              Cancelar
            </button>
          </div>
        </form>
      )}

      {error && !mostrarFormulario && <p className="error-message">{error}</p>}

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Lista de ejercicios</h2>
            <p>Consulta los ejercicios registrados.</p>
          </div>

          <input
            className="search-input"
            placeholder="Buscar..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        {ejerciciosFiltrados.length === 0 ? (
          <p className="empty-message">No hay ejercicios registrados.</p>
        ) : (
          <div className="cards-grid">
            {ejerciciosFiltrados.map((e) => (
              <div key={e.id_ejercicio} className="card item-card">
                <div className="video-box">
                  {e.video_url ? (
                    <video src={e.video_url} controls>
                      <track kind="captions" src="" srcLang="es" label="Español" default />
                    </video>
                  ) : (
                    <div className="empty-video">Sin video</div>
                  )}
                </div>

                {e.imagen_referencial_url && (
                  <div className="image-preview">
                    <img src={e.imagen_referencial_url} alt={`Referencia de ${e.nombre}`} />
                  </div>
                )}

                <div className="tags-row">
                  <span className="badge">{e.nivel || "SIN NIVEL"}</span>
                  <span className="badge">{e.estado || "ACTIVO"}</span>
                </div>

                <h3>{e.nombre}</h3>

                <div className="tags-row">
                  <span className="badge">{e.grupo_muscular}</span>
                  <span className="badge">{e.objetivo}</span>
                </div>

                {e.descripcion && (
                  <p className="item-description">
                    <strong>Descripción:</strong> {e.descripcion}
                  </p>
                )}

                {e.instrucciones && (
                  <p className="item-description">
                    <strong>Instrucciones:</strong> {e.instrucciones}
                  </p>
                )}

                <div className="card-actions">
                  <button className="btn-secondary" onClick={() => iniciarEdicion(e)}>
                    Editar
                  </button>

                  {e.estado === "INACTIVO" ? (
                    <button
                      className="btn-secondary"
                      onClick={() => activar(e.id_ejercicio)}
                    >
                      Activar
                    </button>
                  ) : (
                    <button
                      className="btn-danger"
                      onClick={() => desactivar(e.id_ejercicio)}
                    >
                      Desactivar
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

export default Ejercicios;