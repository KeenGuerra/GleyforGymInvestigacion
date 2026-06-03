import React, { useEffect, useState } from "react";
import api from "../api/api";

function MiPerfil() {
  const [cliente, setCliente] = useState(null);
  const [editando, setEditando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const correo = localStorage.getItem("correo");

  const [form, setForm] = useState({
    telefono: "",
    direccion: "",
    edad: "",
    peso: "",
    estatura: "",
    objetivo: "",
    nivel: "",
    restricciones_medicas: "",
  });

  const cargarPerfil = async () => {
    try {
      const idUsuario = localStorage.getItem("id_usuario");
      const res = await api.get(`/clientes/usuario/${idUsuario}`);

      setCliente(res.data);

      setForm({
        telefono: res.data.telefono || "",
        direccion: res.data.direccion || "",
        edad: res.data.edad || "",
        peso: res.data.peso || "",
        estatura: res.data.estatura || "",
        objetivo: res.data.objetivo || "",
        nivel: res.data.nivel || "",
        restricciones_medicas: res.data.restricciones_medicas || "",
      });
    } catch (error) {
      console.error("Error cargando perfil:", error);
    }
  };

  useEffect(() => {
    cargarPerfil();
  }, []);

  const formatearFecha = (fecha) => {
    if (!fecha) return "No registrada";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const actualizarPerfil = async (e) => {
    e.preventDefault();
    setMensaje("");

    try {
      await api.put(`/clientes/${cliente.id_cliente}`, {
        telefono: form.telefono,
        direccion: form.direccion,
        edad: form.edad ? Number(form.edad) : null,
        peso: form.peso ? Number(form.peso) : null,
        estatura: form.estatura ? Number(form.estatura) : null,
        objetivo: form.objetivo || null,
        nivel: form.nivel || null,
        restricciones_medicas: form.restricciones_medicas || null,
      });

      setMensaje("Perfil actualizado correctamente ✔");
      setEditando(false);
      cargarPerfil();
    } catch (error) {
      console.error("Error actualizando perfil:", error);
      setMensaje("No se pudo actualizar el perfil ❌");
    }
  };

  if (!cliente) {
    return <p className="empty-message">Cargando perfil...</p>;
  }

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div className="user-info">
          <div className="profile-avatar">
            {cliente.nombres?.charAt(0)}
            {cliente.apellidos?.charAt(0)}
          </div>

          <div>
            <span className="badge">MI PERFIL</span>
            <h1>
              {cliente.nombres} {cliente.apellidos}
            </h1>
            <p>{correo}</p>
          </div>
        </div>

        <button
          className={editando ? "btn-secondary" : "btn-primary"}
          onClick={() => setEditando(!editando)}
        >
          {editando ? "Cancelar" : "Editar perfil"}
        </button>
      </section>

      {mensaje && <p className="error-message">{mensaje}</p>}

      {editando ? (
        <section className="form-card">
          <div className="card-header">
            <div>
              <h2>Editar mi información</h2>
              <p>Actualiza tus datos físicos y deportivos.</p>
            </div>
          </div>

          <form onSubmit={actualizarPerfil}>
            <div className="form-grid">
              <div className="form-field">
                <label htmlFor="telefono">Teléfono</label>
                <input
                  id="telefono"
                  value={form.telefono}
                  onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="direccion">Dirección</label>
                <input
                  id="direccion"
                  value={form.direccion}
                  onChange={(e) => setForm({ ...form, direccion: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="edad">Edad</label>
                <input
                  id="edad"
                  type="number"
                  value={form.edad}
                  onChange={(e) => setForm({ ...form, edad: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="peso">Peso (kg)</label>
                <input
                  id="peso"
                  type="number"
                  step="0.01"
                  value={form.peso}
                  onChange={(e) => setForm({ ...form, peso: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="estatura">Estatura (m)</label>
                <input
                  id="estatura"
                  type="number"
                  step="0.01"
                  value={form.estatura}
                  onChange={(e) => setForm({ ...form, estatura: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="objetivo">Objetivo</label>
                <select
                  id="objetivo"
                  value={form.objetivo}
                  onChange={(e) => setForm({ ...form, objetivo: e.target.value })}
                >
                  <option value="">Seleccionar</option>
                  <option value="Bajar de peso">Bajar de peso</option>
                  <option value="Ganar masa muscular">Ganar masa muscular</option>
                  <option value="Mantener condición física">
                    Mantener condición física
                  </option>
                  <option value="Mejorar resistencia">Mejorar resistencia</option>
                </select>
              </div>

              <div className="form-field">
                <label htmlFor="nivel">Nivel</label>
                <select
                  id="nivel"
                  value={form.nivel}
                  onChange={(e) => setForm({ ...form, nivel: e.target.value })}
                >
                  <option value="">Seleccionar</option>
                  <option value="Principiante">Principiante</option>
                  <option value="Intermedio">Intermedio</option>
                  <option value="Avanzado">Avanzado</option>
                </select>
              </div>

              <div className="form-field field-large">
                <label htmlFor="restricciones_medicas">Restricciones médicas</label>
                <textarea
                  id="restricciones_medicas"
                  rows="3"
                  value={form.restricciones_medicas}
                  onChange={(e) =>
                    setForm({ ...form, restricciones_medicas: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">
                Guardar cambios
              </button>

              <button
                type="button"
                className="btn-secondary"
                onClick={() => setEditando(false)}
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>
      ) : (
        <>
          <section className="content-grid">
            <div className="table-card">
              <div className="card-header">
                <div>
                  <h2>Datos personales</h2>
                  <p>Información principal del cliente.</p>
                </div>
              </div>

              <div className="detail-list">
                <p><span>DNI</span><strong>{cliente.dni || "No registrado"}</strong></p>
                <p><span>Teléfono</span><strong>{cliente.telefono || "No registrado"}</strong></p>
                <p><span>Sexo</span><strong>{cliente.sexo || "No registrado"}</strong></p>
                <p><span>Edad</span><strong>{cliente.edad || "No registrado"}</strong></p>
                <p><span>Dirección</span><strong>{cliente.direccion || "No registrado"}</strong></p>
              </div>
            </div>

            <div className="table-card">
              <div className="card-header">
                <div>
                  <h2>Datos deportivos</h2>
                  <p>Datos usados para rutinas y nutrición.</p>
                </div>
              </div>

              <div className="detail-list">
                <p><span>Objetivo</span><strong>{cliente.objetivo || "No definido"}</strong></p>
                <p><span>Nivel</span><strong>{cliente.nivel || "No definido"}</strong></p>
                <p><span>Peso</span><strong>{cliente.peso || "-"} kg</strong></p>
                <p><span>Estatura</span><strong>{cliente.estatura || "-"} m</strong></p>
                <p><span>Restricciones</span><strong>{cliente.restricciones_medicas || "Ninguna"}</strong></p>
              </div>
            </div>
          </section>

          <section className="table-card">
            <div className="card-header">
              <div>
                <h2>Estado de cuenta</h2>
                <p>Resumen del estado actual del perfil.</p>
              </div>
            </div>

            <div className="details-grid">
              <div>
                <span>Estado</span>
                <strong>
                  <span className="badge">{cliente.estado || "ACTIVO"}</span>
                </strong>
              </div>

              <div>
                <span>Fecha de registro</span>
                <strong>{formatearFecha(cliente.fecha_registro)}</strong>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default MiPerfil;