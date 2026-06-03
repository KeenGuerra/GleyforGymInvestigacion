import React, { useEffect, useState } from "react";
import api from "../api/api";
import { MSG_CLIENTE_NO_ENCONTRADO } from "../api/constants";

function Asistencias() {
  const [asistencias, setAsistencias] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [editandoId, setEditandoId] = useState(null);
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const hoy = new Date().toISOString().split("T")[0];

  const formInicial = {
    id_cliente: "",
    fecha: hoy,
    hora_entrada: "",
    hora_salida: "",
    observacion: "",
  };

  const [form, setForm] = useState(formInicial);

  const cargarDatos = async () => {
    try {
      setError("");

      const [resAsistencias, resClientes] = await Promise.all([
        api.get("/asistencias/"),
        api.get("/clientes/"),
      ]);

      setAsistencias(resAsistencias.data);
      setClientes(resClientes.data.filter((c) => c.estado === "ACTIVO"));
    } catch (error) {
      console.error(error);
      setError("Error al cargar asistencias");
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const obtenerNombreCliente = (id_cliente) => {
    const cliente = clientes.find((c) => c.id_cliente === id_cliente);
    if (!cliente) return MSG_CLIENTE_NO_ENCONTRADO;
    return `${cliente.nombres || ""} ${cliente.apellidos || ""}`.trim();
  };

  const limpiarFormulario = () => {
    setForm(formInicial);
    setEditandoId(null);
    setError("");
    setMostrarFormulario(false);
  };

  const validarFormulario = () => {
    if (!form.id_cliente) return "Seleccione un cliente";
    if (!form.fecha) return "Seleccione la fecha";
    if (!form.hora_entrada) return "Ingrese la hora de entrada";

    if (form.hora_salida && form.hora_salida < form.hora_entrada) {
      return "La hora de salida no puede ser menor que la hora de entrada";
    }

    return "";
  };

  const guardarAsistencia = async (e) => {
    e.preventDefault();
    setError("");

    const mensajeError = validarFormulario();
    if (mensajeError) {
      setError(mensajeError);
      return;
    }

    const data = {
      id_cliente: Number(form.id_cliente),
      fecha: form.fecha,
      hora_entrada: form.hora_entrada,
      hora_salida: form.hora_salida || null,
      observacion: form.observacion || null,
    };

    try {
      if (editandoId) {
        await api.put(`/asistencias/${editandoId}`, {
          fecha: data.fecha,
          hora_entrada: data.hora_entrada,
          hora_salida: data.hora_salida,
          observacion: data.observacion,
        });
      } else {
        await api.post("/asistencias/", data);
      }

      limpiarFormulario();
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al guardar asistencia");
    }
  };

  const editarAsistencia = (a) => {
    setEditandoId(a.id_asistencia);
    setMostrarFormulario(true);

    setForm({
      id_cliente: a.id_cliente || "",
      fecha: a.fecha || hoy,
      hora_entrada: a.hora_entrada || "",
      hora_salida: a.hora_salida || "",
      observacion: a.observacion || "",
    });

    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarAsistencia = async (id) => {
    const confirmar = globalThis.confirm("¿Seguro que deseas eliminar esta asistencia?");
    if (!confirmar) return;

    try {
      await api.delete(`/asistencias/${id}`);
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError("Error al eliminar asistencia");
    }
  };

  const asistenciasFiltradas = asistencias.filter((a) => {
    const nombre = obtenerNombreCliente(a.id_cliente).toLowerCase();
    const observacion = String(a.observacion || "").toLowerCase();
    const fecha = String(a.fecha || "").toLowerCase();
    const texto = busqueda.toLowerCase();

    return (
      nombre.includes(texto) ||
      observacion.includes(texto) ||
      fecha.includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">CONTROL DE INGRESO</span>
          <h1>Gestión de asistencias</h1>
          <p>Controla el ingreso, salida y observaciones de clientes activos.</p>
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
          + Registrar asistencia
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Total de registros</span>
          <strong>{asistencias.length}</strong>
        </div>

        <div className="stat-card">
          <span>Resultados filtrados</span>
          <strong>{asistenciasFiltradas.length}</strong>
        </div>

        <div className="stat-card">
          <span>Clientes activos</span>
          <strong>{clientes.length}</strong>
        </div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardarAsistencia} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editandoId ? "Editar asistencia" : "Registrar asistencia"}</h2>
              <p>
                {editandoId
                  ? "Actualiza los datos del registro seleccionado."
                  : "Registra la entrada diaria de un cliente activo."}
              </p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field field-large">
              <label htmlFor="id_cliente">Cliente</label>
              <select
                id="id_cliente"
                value={form.id_cliente}
                onChange={(e) => setForm({ ...form, id_cliente: e.target.value })}
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

            <div className="form-field">
              <label htmlFor="fecha">Fecha</label>
              <input
                id="fecha"
                type="date"
                value={form.fecha}
                onChange={(e) => setForm({ ...form, fecha: e.target.value })}
              />
            </div>

            <div className="form-field">
              <label htmlFor="hora_entrada">Hora entrada</label>
              <input
                id="hora_entrada"
                type="time"
                value={form.hora_entrada}
                onChange={(e) =>
                  setForm({ ...form, hora_entrada: e.target.value })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="hora_salida">Hora salida</label>
              <input
                id="hora_salida"
                type="time"
                value={form.hora_salida}
                onChange={(e) =>
                  setForm({ ...form, hora_salida: e.target.value })
                }
              />
            </div>

            <div className="form-field field-large">
              <label htmlFor="observacion">Observación</label>
              <input
                id="observacion"
                placeholder="Ejemplo: entrenamiento completo"
                value={form.observacion}
                onChange={(e) =>
                  setForm({ ...form, observacion: e.target.value })
                }
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {editandoId ? "Actualizar asistencia" : "Guardar asistencia"}
            </button>

            <button type="button" className="btn-secondary" onClick={limpiarFormulario}>
              Cancelar
            </button>
          </div>
        </form>
      )}

      {error && !mostrarFormulario && (
        <p className="error-message">{error}</p>
      )}

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Lista de asistencias</h2>
            <p>Consulta, edita o elimina registros de asistencia.</p>
          </div>

          <input
            className="search-input"
            type="text"
            placeholder="Buscar por cliente, fecha u observación..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Fecha</th>
                <th>Entrada</th>
                <th>Salida</th>
                <th>Observación</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {asistenciasFiltradas.length === 0 ? (
                <tr>
                  <td colSpan="7" className="empty-message">
                    No hay asistencias registradas
                  </td>
                </tr>
              ) : (
                asistenciasFiltradas.map((a) => (
                  <tr key={a.id_asistencia}>
                    <td>
                      <span className="badge">#{a.id_asistencia}</span>
                    </td>
                    <td>{obtenerNombreCliente(a.id_cliente)}</td>
                    <td>{formatearFecha(a.fecha)}</td>
                    <td>{a.hora_entrada || "-"}</td>
                    <td>{a.hora_salida || "-"}</td>
                    <td>
                      <span className="badge">
                        {a.observacion || "REGISTRADO"}
                      </span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="btn-secondary"
                          onClick={() => editarAsistencia(a)}
                        >
                          Editar
                        </button>

                        <button
                          className="btn-danger"
                          onClick={() => eliminarAsistencia(a.id_asistencia)}
                        >
                          Eliminar
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

export default Asistencias;