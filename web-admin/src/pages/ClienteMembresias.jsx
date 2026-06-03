import React, { useEffect, useState } from "react";
import api from "../api/api";
import { MSG_CLIENTE_NO_ENCONTRADO } from "../api/constants";

function ClienteMembresias() {
  const [asignaciones, setAsignaciones] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [membresias, setMembresias] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const hoy = new Date().toISOString().split("T")[0];

  const formInicial = {
    id_cliente: "",
    id_membresia: "",
    fecha_inicio: hoy,
    fecha_fin: "",
    estado: "ACTIVA",
  };

  const [form, setForm] = useState(formInicial);

  const cargarDatos = async () => {
    try {
      setError("");

      const [resAsignaciones, resClientes, resMembresias] = await Promise.all([
        api.get("/cliente-membresias/"),
        api.get("/clientes/"),
        api.get("/membresias/"),
      ]);

      setAsignaciones(resAsignaciones.data);
      setClientes(resClientes.data.filter((c) => c.estado === "ACTIVO"));
      setMembresias(resMembresias.data.filter((m) => m.estado === "ACTIVO"));
    } catch (error) {
      console.error(error);
      setError("Error al cargar datos");
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const calcularFechaFin = (idMembresia, fechaInicio) => {
    const membresia = membresias.find(
      (m) => m.id_membresia === Number(idMembresia)
    );

    if (!membresia || !fechaInicio) return "";

    const fecha = new Date(fechaInicio);
    fecha.setDate(fecha.getDate() + Number(membresia.duracion_dias || 0));

    return fecha.toISOString().split("T")[0];
  };

  const cambiar = (e) => {
    const { name, value } = e.target;

    const nuevoForm = {
      ...form,
      [name]: value,
    };

    if (name === "id_membresia" || name === "fecha_inicio") {
      nuevoForm.fecha_fin = calcularFechaFin(
        name === "id_membresia" ? value : nuevoForm.id_membresia,
        name === "fecha_inicio" ? value : nuevoForm.fecha_inicio
      );
    }

    setForm(nuevoForm);
  };

  const limpiarFormulario = () => {
    setEditandoId(null);
    setError("");
    setForm(formInicial);
    setMostrarFormulario(false);
  };

  const validarFormulario = () => {
    if (!form.id_cliente) return "Seleccione un cliente";
    if (!form.id_membresia) return "Seleccione una membresía";
    if (!form.fecha_inicio) return "Seleccione la fecha de inicio";
    if (!form.fecha_fin) return "La fecha fin se calcula al seleccionar el plan";

    if (form.fecha_fin < form.fecha_inicio) {
      return "La fecha de fin no puede ser menor que la fecha de inicio";
    }

    return "";
  };

  const guardar = async (e) => {
    e.preventDefault();
    setError("");

    const mensaje = validarFormulario();

    if (mensaje) {
      setError(mensaje);
      return;
    }

    const data = {
      id_cliente: Number(form.id_cliente),
      id_membresia: Number(form.id_membresia),
      fecha_inicio: form.fecha_inicio,
      fecha_fin: form.fecha_fin,
      estado: form.estado,
    };

    try {
      if (editandoId) {
        await api.put(`/cliente-membresias/${editandoId}`, {
          id_membresia: data.id_membresia,
          fecha_inicio: data.fecha_inicio,
          estado: data.estado,
        });
      } else {
        await api.post("/cliente-membresias/", data);
      }

      limpiarFormulario();
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al guardar asignación");
    }
  };

  const editar = (item) => {
    setEditandoId(item.id_cliente_membresia);
    setMostrarFormulario(true);

    setForm({
      id_cliente: item.id_cliente || "",
      id_membresia: item.id_membresia || "",
      fecha_inicio: item.fecha_inicio || hoy,
      fecha_fin: item.fecha_fin || "",
      estado: item.estado || "ACTIVA",
    });

    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const cancelarAsignacion = async (id) => {
    const confirmar = globalThis.confirm(
      "¿Seguro que deseas cancelar esta membresía?"
    );

    if (!confirmar) return;

    try {
      await api.delete(`/cliente-membresias/${id}`);
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError("Error al cancelar asignación");
    }
  };

  const pausarOReactivar = async (item) => {
    const nuevoEstado = item.estado === "PAUSADA" ? "ACTIVA" : "PAUSADA";

    const confirmar = globalThis.confirm(
      `¿Seguro que deseas ${
        nuevoEstado === "PAUSADA" ? "pausar" : "reactivar"
      } esta membresía?`
    );

    if (!confirmar) return;

    try {
      await api.put(`/cliente-membresias/${item.id_cliente_membresia}`, {
        estado: nuevoEstado,
      });

      cargarDatos();
    } catch (error) {
      console.error(error);
      setError("Error al cambiar estado de la membresía");
    }
  };

  const obtenerCliente = (id_cliente) => {
    const cliente = clientes.find((c) => c.id_cliente === id_cliente);
    if (!cliente) return MSG_CLIENTE_NO_ENCONTRADO;
    return `${cliente.nombres} ${cliente.apellidos} - DNI ${cliente.dni}`;
  };

  const obtenerMembresia = (asignacion) => {
    const membresia = membresias.find(
      (m) => m.id_membresia === asignacion.id_membresia
    );

    const nombre = membresia
      ? membresia.nombre
      : `Plan #${asignacion.id_membresia}`;

    const precio = asignacion.precio_asignado ?? membresia?.precio ?? 0;

    return `${nombre} - S/ ${Number(precio).toFixed(2)}`;
  };

  const claseEstado = (estado) => {
    switch (estado) {
      case "ACTIVA":
        return "badge success";
      case "PAUSADA":
        return "badge warning";
      case "TERMINADA":
        return "badge neutral";
      case "CANCELADA":
        return "badge danger";
      default:
        return "badge";
    }
  };

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MEMBRESÍAS</span>
          <h1>Asignar membresías</h1>
          <p>Asigna planes activos a los clientes registrados del gimnasio.</p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            setMostrarFormulario(true);
            setEditandoId(null);
            setForm({
              ...formInicial,
              fecha_fin: "",
            });
            setError("");
          }}
        >
          + Nueva asignación
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Asignaciones</span>
          <strong>{asignaciones.length}</strong>
        </div>

        <div className="stat-card">
          <span>Activas</span>
          <strong>
            {asignaciones.filter((a) => a.estado === "ACTIVA").length}
          </strong>
        </div>

        <div className="stat-card">
          <span>Pausadas</span>
          <strong>
            {asignaciones.filter((a) => a.estado === "PAUSADA").length}
          </strong>
        </div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editandoId ? "Editar asignación" : "Nueva asignación"}</h2>
              <p>
                {editandoId
                  ? "Actualiza el plan, fecha de inicio o estado de la membresía."
                  : "Selecciona cliente y plan. La fecha fin se calcula automáticamente."}
              </p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field field-large">
              <label htmlFor="id_cliente">Cliente</label>
              <select
                id="id_cliente"
                name="id_cliente"
                value={form.id_cliente}
                onChange={cambiar}
                disabled={!!editandoId}
              >
                <option value="">Seleccione cliente</option>
                {clientes.map((c) => (
                  <option key={c.id_cliente} value={c.id_cliente}>
                    {c.nombres} {c.apellidos} - DNI {c.dni}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field field-large">
              <label htmlFor="id_membresia">Membresía</label>
              <select
                id="id_membresia"
                name="id_membresia"
                value={form.id_membresia}
                onChange={cambiar}
              >
                <option value="">Seleccione membresía</option>
                {membresias.map((m) => (
                  <option key={m.id_membresia} value={m.id_membresia}>
                    {m.nombre} - {m.duracion_dias} días - S/{" "}
                    {Number(m.precio || 0).toFixed(2)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="fecha_inicio">Fecha inicio</label>
              <input
                id="fecha_inicio"
                type="date"
                name="fecha_inicio"
                value={form.fecha_inicio}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="fecha_fin">Fecha fin</label>
              <input
                id="fecha_fin"
                type="date"
                name="fecha_fin"
                value={form.fecha_fin}
                readOnly
              />
            </div>

            <div className="form-field">
              <label htmlFor="estado">Estado</label>
              <select id="estado" name="estado" value={form.estado} onChange={cambiar}>
                <option value="ACTIVA">ACTIVA</option>
                <option value="PAUSADA">PAUSADA</option>
                <option value="TERMINADA">TERMINADA</option>
                <option value="CANCELADA">CANCELADA</option>
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {editandoId ? "Actualizar asignación" : "Asignar membresía"}
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
            <h2>Membresías asignadas</h2>
            <p>Listado de planes asignados a clientes activos.</p>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Membresía</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {asignaciones.length === 0 ? (
                <tr>
                  <td colSpan="7" className="empty-message">
                    No hay membresías asignadas
                  </td>
                </tr>
              ) : (
                asignaciones.map((a) => (
                  <tr key={a.id_cliente_membresia}>
                    <td>
                      <span className="badge">#{a.id_cliente_membresia}</span>
                    </td>

                    <td>{obtenerCliente(a.id_cliente)}</td>

                    <td>{obtenerMembresia(a)}</td>

                    <td>{formatearFecha(a.fecha_inicio)}</td>

                    <td>{formatearFecha(a.fecha_fin)}</td>

                    <td>
                      <span className={claseEstado(a.estado)}>{a.estado}</span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="btn-secondary"
                          onClick={() => editar(a)}
                        >
                          Editar
                        </button>

                        {a.estado !== "TERMINADA" &&
                          a.estado !== "CANCELADA" && (
                            <button
                              className="btn-secondary"
                              onClick={() => pausarOReactivar(a)}
                            >
                              {a.estado === "PAUSADA" ? "Reactivar" : "Pausar"}
                            </button>
                          )}

                        <button
                          className="btn-danger"
                          onClick={() =>
                            cancelarAsignacion(a.id_cliente_membresia)
                          }
                        >
                          Cancelar
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

export default ClienteMembresias;