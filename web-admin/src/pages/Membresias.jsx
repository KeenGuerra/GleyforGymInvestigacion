import React, { useEffect, useState } from "react";
import api from "../api/api";

function Membresias() {
  const [membresias, setMembresias] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [editando, setEditando] = useState(null);
  const [error, setError] = useState("");

  const formInicial = {
    nombre: "",
    descripcion: "",
    beneficios: "",
    precio: "",
    duracion_dias: "",
    estado: "ACTIVO",
  };

  const [form, setForm] = useState(formInicial);

  const cargarMembresias = async () => {
    try {
      setError("");
      const res = await api.get("/membresias/");
      setMembresias(res.data);
    } catch (error) {
      console.error(error);
      setError("Error cargando membresías");
    }
  };

  useEffect(() => {
    cargarMembresias();
  }, []);

  const limpiarFormulario = () => {
    setForm(formInicial);
    setEditando(null);
    setMostrarFormulario(false);
    setError("");
  };

  const validar = () => {
    if (!form.nombre.trim()) return "Ingrese el nombre del plan";
    if (!form.precio || Number(form.precio) <= 0) return "Precio inválido";
    if (!form.duracion_dias || Number(form.duracion_dias) <= 0)
      return "Duración inválida";
    return "";
  };

  const guardarMembresia = async (e) => {
    e.preventDefault();
    setError("");

    const err = validar();
    if (err) {
      setError(err);
      return;
    }

    const datos = {
      nombre: form.nombre,
      descripcion: form.descripcion || null,
      beneficios: form.beneficios || null,
      precio: Number(form.precio),
      duracion_dias: Number(form.duracion_dias),
      estado: form.estado,
    };

    try {
      if (editando) {
        await api.put(`/membresias/${editando.id_membresia}`, datos);
      } else {
        await api.post("/membresias/", datos);
      }

      limpiarFormulario();
      cargarMembresias();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al guardar");
    }
  };

  const editarMembresia = (m) => {
    setEditando(m);

    setForm({
      nombre: m.nombre || "",
      descripcion: m.descripcion || "",
      beneficios: m.beneficios || "",
      precio: m.precio || "",
      duracion_dias: m.duracion_dias || "",
      estado: m.estado || "ACTIVO",
    });

    setMostrarFormulario(true);
    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const desactivarMembresia = async (id) => {
    const confirmar = globalThis.confirm(
      "¿Seguro que deseas desactivar esta membresía?"
    );

    if (!confirmar) return;

    try {
      await api.delete(`/membresias/${id}`);
      cargarMembresias();
    } catch (error) {
      console.error(error);
      setError("No se pudo desactivar la membresía");
    }
  };

  const membresiasFiltradas = membresias.filter((m) =>
    `${m.nombre} ${m.descripcion} ${m.beneficios} ${m.estado}`
      .toLowerCase()
      .includes(busqueda.toLowerCase())
  );

  const activas = membresias.filter((m) => m.estado === "ACTIVO").length;

  const ingresosProyectados = membresias.reduce(
    (total, m) => total + Number(m.precio || 0),
    0
  );

  const planMasCaro =
    membresias.length > 0
      ? membresias.reduce((max, m) =>
          Number(m.precio) > Number(max.precio) ? m : max,
          membresias[0]
        )
      : null;

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MÓDULO ADMINISTRATIVO</span>
          <h1>Planes de membresía</h1>
          <p>Administra precios, duración, beneficios y estado de los planes.</p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            limpiarFormulario();
            setMostrarFormulario(true);
          }}
        >
          + Crear plan
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Activas</span>
          <strong>{activas}</strong>
        </div>

        <div className="stat-card">
          <span>Total planes</span>
          <strong>{membresias.length}</strong>
        </div>

        <div className="stat-card">
          <span>Ingresos base</span>
          <strong>S/ {ingresosProyectados.toFixed(2)}</strong>
        </div>

        <div className="stat-card">
          <span>Plan más caro</span>
          <strong>{planMasCaro?.nombre || "-"}</strong>
        </div>
      </section>

      {mostrarFormulario && (
        <section className="form-card">
          <div className="card-header">
            <div>
              <h2>{editando ? "Editar plan" : "Nuevo plan"}</h2>
              <p>Completa los datos del plan de membresía.</p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <form onSubmit={guardarMembresia}>
            <div className="form-grid">
              <div className="form-field">
                <label htmlFor="nombre">Nombre</label>
                <input
                  id="nombre"
                  type="text"
                  placeholder="Nombre del plan"
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="precio">Precio</label>
                <input
                  id="precio"
                  type="number"
                  placeholder="Precio"
                  value={form.precio}
                  onChange={(e) => setForm({ ...form, precio: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="duracion_dias">Duración</label>
                <input
                  id="duracion_dias"
                  type="number"
                  placeholder="Duración en días"
                  value={form.duracion_dias}
                  onChange={(e) =>
                    setForm({ ...form, duracion_dias: e.target.value })
                  }
                />
              </div>

              <div className="form-field">
                <label htmlFor="estado">Estado</label>
                <select
                  id="estado"
                  value={form.estado}
                  onChange={(e) => setForm({ ...form, estado: e.target.value })}
                >
                  <option value="ACTIVO">ACTIVO</option>
                  <option value="INACTIVO">INACTIVO</option>
                </select>
              </div>

              <div className="form-field field-large">
                <label htmlFor="descripcion">Descripción</label>
                <textarea
                  id="descripcion"
                  placeholder="Descripción general del plan"
                  value={form.descripcion}
                  onChange={(e) =>
                    setForm({ ...form, descripcion: e.target.value })
                  }
                />
              </div>

              <div className="form-field field-large">
                <label htmlFor="beneficios">Beneficios</label>
                <textarea
                  id="beneficios"
                  placeholder={`Escribe un beneficio por línea:\nAcceso al gimnasio\nRutinas personalizadas\nSeguimiento de progreso`}
                  value={form.beneficios}
                  onChange={(e) =>
                    setForm({ ...form, beneficios: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="form-actions">
              <button className="btn-primary" type="submit">
                {editando ? "Actualizar" : "Guardar"}
              </button>

              <button
                className="btn-secondary"
                type="button"
                onClick={limpiarFormulario}
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>
      )}

      {error && !mostrarFormulario && <p className="error-message">{error}</p>}

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Planes registrados</h2>
            <p>Consulta, edita o desactiva los planes disponibles.</p>
          </div>

          <input
            className="search-input"
            type="text"
            placeholder="Buscar por nombre, descripción, beneficios o estado..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        {membresiasFiltradas.length === 0 ? (
          <p className="empty-message">No hay planes registrados.</p>
        ) : (
          <div className="cards-grid">
            {membresiasFiltradas.map((plan) => (
              <article className="card item-card" key={plan.id_membresia}>
                <div className="item-card-top">
                  <span className="badge">PLAN</span>
                  <span className="badge">{plan.estado}</span>
                </div>

                <h3>{plan.nombre}</h3>

                <h2>
                  S/ {Number(plan.precio).toFixed(2)}
                  <span> / {plan.duracion_dias} días</span>
                </h2>

                <p>{plan.descripcion || "Sin descripción"}</p>

                {plan.beneficios && (
                  <ul>
                    {plan.beneficios.split("\n").map((beneficio) => (
                      <li key={beneficio}>{beneficio}</li>
                    ))}
                  </ul>
                )}

                <div className="form-actions">
                  <button
                    className="btn-primary"
                    onClick={() => editarMembresia(plan)}
                  >
                    Editar
                  </button>

                  <button
                    onClick={() => desactivarMembresia(plan.id_membresia)}
                    className="btn-danger"
                  >
                    Desactivar
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Membresias;