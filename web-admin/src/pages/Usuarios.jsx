import React, { useEffect, useState } from "react";
import api from "../api/api";

function Usuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const formInicial = {
    correo: "",
    password: "",
    rol: "ENTRENADOR",
    estado: "ACTIVO",
  };

  const [form, setForm] = useState(formInicial);

  const cargarUsuarios = async () => {
    try {
      const res = await api.get("/usuarios/");
      setUsuarios(res.data);
    } catch (error) {
      console.error("Error al cargar usuarios:", error);
      setError("Error al cargar usuarios");
    }
  };

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const cambiar = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const limpiarFormulario = () => {
    setEditandoId(null);
    setError("");
    setForm(formInicial);
    setMostrarFormulario(false);
  };

  const validarFormulario = () => {
    if (!form.correo.trim()) return "Ingrese el correo";

    if (!editandoId && !form.password.trim()) {
      return "Ingrese la contraseña";
    }

    if (!editandoId && form.password.length < 6) {
      return "La contraseña debe tener mínimo 6 caracteres";
    }

    return "";
  };

  const guardar = async (e) => {
    e.preventDefault();
    setError("");

    const mensajeError = validarFormulario();

    if (mensajeError) {
      setError(mensajeError);
      return;
    }

    try {
      if (editandoId) {
        await api.put(`/usuarios/${editandoId}`, {
          correo: form.correo,
          rol: form.rol,
          estado: form.estado,
        });
      } else {
        await api.post("/usuarios/", {
          correo: form.correo,
          password: form.password,
          rol: form.rol,
        });
      }

      limpiarFormulario();
      cargarUsuarios();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al guardar usuario");
    }
  };

  const editar = (usuario) => {
    setEditandoId(usuario.id_usuario);
    setMostrarFormulario(true);

    setForm({
      correo: usuario.correo || "",
      password: "",
      rol: usuario.rol || "ENTRENADOR",
      estado: usuario.estado || "ACTIVO",
    });

    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const desactivar = async (id) => {
    const confirmar = globalThis.confirm(
      "¿Seguro que deseas desactivar este usuario?"
    );

    if (!confirmar) return;

    try {
      await api.delete(`/usuarios/${id}`);
      cargarUsuarios();
    } catch (error) {
      console.error(error);
      setError("Error al desactivar usuario");
    }
  };

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const usuariosInternos = usuarios.filter((u) => u.rol !== "CLIENTE");

  const usuariosFiltrados = usuariosInternos.filter((u) => {
    const texto = busqueda.toLowerCase();

    return (
      String(u.correo || "").toLowerCase().includes(texto) ||
      String(u.rol || "").toLowerCase().includes(texto) ||
      String(u.estado || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">USUARIOS</span>
          <h1>Gestión de usuarios</h1>
          <p>
            Administra los usuarios internos del sistema: administradores y
            entrenadores.
          </p>
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
          + Crear usuario
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Usuarios internos</span>
          <strong>{usuariosInternos.length}</strong>
        </div>

        <div className="stat-card">
          <span>Administradores</span>
          <strong>{usuariosInternos.filter((u) => u.rol === "ADMIN").length}</strong>
        </div>

        <div className="stat-card">
          <span>Entrenadores</span>
          <strong>
            {usuariosInternos.filter((u) => u.rol === "ENTRENADOR").length}
          </strong>
        </div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editandoId ? "Editar usuario interno" : "Crear usuario interno"}</h2>
              <p>
                {editandoId
                  ? "Actualiza correo, rol o estado del usuario."
                  : "Registra un usuario interno para acceder al sistema."}
              </p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="correo">Correo electrónico</label>
              <input
                id="correo"
                type="email"
                name="correo"
                placeholder="Correo electrónico"
                value={form.correo}
                onChange={cambiar}
              />
            </div>

            {!editandoId && (
              <div className="form-field">
                <label htmlFor="password">Contraseña</label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  placeholder="Contraseña"
                  value={form.password}
                  onChange={cambiar}
                />
              </div>
            )}

            <div className="form-field">
              <label htmlFor="rol">Rol</label>
              <select id="rol" name="rol" value={form.rol} onChange={cambiar}>
                <option value="ENTRENADOR">ENTRENADOR</option>
                <option value="ADMIN">ADMIN</option>
              </select>
            </div>

            {editandoId && (
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
            <button type="submit" className="btn-primary">
              {editandoId ? "Actualizar usuario" : "Crear usuario"}
            </button>

            <button
              type="button"
              className="btn-secondary"
              onClick={limpiarFormulario}
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {error && !mostrarFormulario && <p className="error-message">{error}</p>}

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Lista de usuarios internos</h2>
            <p>Consulta, edita o desactiva usuarios internos.</p>
          </div>

          <input
            className="search-input"
            type="text"
            placeholder="Buscar por correo, rol o estado..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Correo</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Fecha creación</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {usuariosFiltrados.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-message">
                    No hay usuarios internos registrados
                  </td>
                </tr>
              ) : (
                usuariosFiltrados.map((u) => (
                  <tr key={u.id_usuario}>
                    <td>
                      <span className="badge">#{u.id_usuario}</span>
                    </td>

                    <td>{u.correo}</td>

                    <td>
                      <span className="badge">{u.rol}</span>
                    </td>

                    <td>
                      <span className="badge">{u.estado}</span>
                    </td>

                    <td>{formatearFecha(u.fecha_creacion)}</td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="btn-secondary"
                          onClick={() => editar(u)}
                        >
                          Editar
                        </button>

                        <button
                          onClick={() => desactivar(u.id_usuario)}
                          className="btn-danger"
                        >
                          Desactivar
                        </button>
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

export default Usuarios;