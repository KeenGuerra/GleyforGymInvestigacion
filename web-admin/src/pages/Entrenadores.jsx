import React, { useEffect, useState } from "react";
import api from "../api/api";

function Entrenadores() {
  const [entrenadores, setEntrenadores] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editando, setEditando] = useState(null);

  const formInicial = {
    dni: "",
    nombres: "",
    apellidos: "",
    telefono: "",
    especialidad: "",
    correo: "",
    password: "",
    estado: "ACTIVO",
  };

  const [form, setForm] = useState(formInicial);

  const cargar = async () => {
    try {
      setError("");
      const res = await api.get("/entrenadores/");
      setEntrenadores(res.data);
    } catch (err) {
      console.error(err);
      setError("Error al cargar entrenadores");
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
    if (!form.dni.trim()) return "Ingrese el DNI";
    if (!form.nombres.trim()) return "Ingrese los nombres";
    if (!form.apellidos.trim()) return "Ingrese los apellidos";

    if (!editando) {
      if (!form.correo.trim()) return "Ingrese el correo";
      if (!form.password.trim() || form.password.length < 6) {
        return "La contraseña debe tener mínimo 6 caracteres";
      }
    }

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

      if (editando) {
        await api.put(`/entrenadores/${editando.id_entrenador}`, {
          dni: form.dni,
          nombres: form.nombres,
          apellidos: form.apellidos,
          telefono: form.telefono || null,
          especialidad: form.especialidad || null,
          estado: form.estado,
        });
      } else {
        await api.post("/entrenadores/", {
          dni: form.dni,
          nombres: form.nombres,
          apellidos: form.apellidos,
          telefono: form.telefono || null,
          especialidad: form.especialidad || null,
          correo: form.correo,
          password: form.password,
        });
      }

      limpiar();
      await cargar();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Error al guardar entrenador");
    } finally {
      setCargando(false);
    }
  };

  const editar = (entrenador) => {
    setForm({
      dni: entrenador.dni || "",
      nombres: entrenador.nombres || "",
      apellidos: entrenador.apellidos || "",
      telefono: entrenador.telefono || "",
      especialidad: entrenador.especialidad || "",
      correo: "",
      password: "",
      estado: entrenador.estado || "ACTIVO",
    });
    setEditando(entrenador);
    setMostrarFormulario(true);
    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const desactivar = async (id) => {
    if (!globalThis.confirm("¿Seguro que deseas desactivar a este entrenador?")) return;

    try {
      await api.delete(`/entrenadores/${id}`);
      await cargar();
    } catch (err) {
      console.error(err);
      setError("Error al desactivar entrenador");
    }
  };

  const activar = async (id) => {
    try {
      await api.put(`/entrenadores/${id}`, { estado: "ACTIVO" });
      await cargar();
    } catch (err) {
      console.error(err);
      setError("Error al activar entrenador");
    }
  };

  const filtrados = entrenadores.filter((e) => {
    const texto = busqueda.toLowerCase();
    return (
      String(e.dni || "").toLowerCase().includes(texto) ||
      String(e.nombres || "").toLowerCase().includes(texto) ||
      String(e.apellidos || "").toLowerCase().includes(texto) ||
      String(e.especialidad || "").toLowerCase().includes(texto) ||
      String(e.estado || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">ADMINISTRACIÓN</span>
          <h1>Gestión de entrenadores</h1>
          <p>Registra y administra al personal deportivo del gimnasio.</p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            setMostrarFormulario(true);
            setForm(formInicial);
            setEditando(null);
            setError("");
          }}
        >
          + Registrar entrenador
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Total</span>
          <strong>{entrenadores.length}</strong>
        </div>
        <div className="stat-card">
          <span>Filtrados</span>
          <strong>{filtrados.length}</strong>
        </div>
        <div className="stat-card">
          <span>Activos</span>
          <strong>{entrenadores.filter((e) => e.estado === "ACTIVO").length}</strong>
        </div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editando ? "Editar entrenador" : "Registrar entrenador"}</h2>
              <p>
                {editando
                  ? "Modifica los datos del entrenador."
                  : "Crea el usuario y la ficha del nuevo entrenador."}
              </p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="dni">DNI</label>
              <input id="dni" name="dni" value={form.dni} onChange={cambiar} placeholder="DNI" />
            </div>

            <div className="form-field">
              <label htmlFor="nombres">Nombres</label>
              <input id="nombres" name="nombres" value={form.nombres} onChange={cambiar} placeholder="Nombres" />
            </div>

            <div className="form-field">
              <label htmlFor="apellidos">Apellidos</label>
              <input id="apellidos" name="apellidos" value={form.apellidos} onChange={cambiar} placeholder="Apellidos" />
            </div>

            <div className="form-field">
              <label htmlFor="telefono">Teléfono</label>
              <input id="telefono" name="telefono" value={form.telefono} onChange={cambiar} placeholder="Teléfono" />
            </div>

            <div className="form-field">
              <label htmlFor="especialidad">Especialidad</label>
              <input
                id="especialidad"
                name="especialidad"
                value={form.especialidad}
                onChange={cambiar}
                placeholder="Ej: Musculación, Funcional"
              />
            </div>

            {!editando && (
              <>
                <div className="form-field">
                  <label htmlFor="correo">Correo electrónico</label>
                  <input
                    id="correo"
                    type="email"
                    name="correo"
                    value={form.correo}
                    onChange={cambiar}
                    placeholder="Correo electrónico"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="password">Contraseña</label>
                  <input
                    id="password"
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={cambiar}
                    placeholder="Contraseña"
                  />
                </div>
              </>
            )}

            {editando && (
              <div className="form-field">
                <label htmlFor="estado">Estado</label>
                <select id="estado" name="estado" value={form.estado} onChange={cambiar}>
                  <option value="ACTIVO">ACTIVO</option>
                  <option value="INACTIVO">INACTIVO</option>
                </select>
              </div>
            )}
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={cargando}>
              {cargando ? "Guardando..." : editando ? "Actualizar entrenador" : "Registrar entrenador"}
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
            <h2>Lista de entrenadores</h2>
            <p>Consulta, edita o desactiva entrenadores.</p>
          </div>

          <input
            className="search-input"
            placeholder="Buscar por DNI, nombre o especialidad..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>DNI</th>
                <th>Nombres</th>
                <th>Apellidos</th>
                <th>Teléfono</th>
                <th>Especialidad</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {filtrados.length === 0 ? (
                <tr>
                  <td colSpan="8" className="empty-message">
                    No hay entrenadores registrados
                  </td>
                </tr>
              ) : (
                filtrados.map((e) => (
                  <tr key={e.id_entrenador}>
                    <td>
                      <span className="badge">#{e.id_entrenador}</span>
                    </td>
                    <td>{e.dni}</td>
                    <td>{e.nombres}</td>
                    <td>{e.apellidos}</td>
                    <td>{e.telefono || "-"}</td>
                    <td>{e.especialidad || "-"}</td>
                    <td>
                      <span className="badge">{e.estado}</span>
                    </td>
                    <td>
                      <div className="table-actions">
                        <button className="btn-secondary" onClick={() => editar(e)}>
                          Editar
                        </button>
                        {e.estado === "INACTIVO" ? (
                          <button className="btn-secondary" onClick={() => activar(e.id_entrenador)}>
                            Activar
                          </button>
                        ) : (
                          <button className="btn-danger" onClick={() => desactivar(e.id_entrenador)}>
                            Desactivar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default Entrenadores;
