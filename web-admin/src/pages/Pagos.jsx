import React, { useEffect, useState } from "react";
import api from "../api/api";
import { MSG_CLIENTE_NO_ENCONTRADO } from "../api/constants";

function Pagos() {
  const [pagos, setPagos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [asignaciones, setAsignaciones] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [editandoId, setEditandoId] = useState(null);
  const [error, setError] = useState("");

  const hoy = new Date().toISOString().split("T")[0];

  const formInicial = {
    id_cliente: "",
    id_cliente_membresia: "",
    monto: "",
    metodo_pago: "",
    fecha_pago: hoy,
    estado: "PAGADO",
    observacion: "",
  };

  const [form, setForm] = useState(formInicial);

  const cargarDatos = async () => {
    try {
      setError("");

      const [resPagos, resClientes, resAsignaciones] = await Promise.all([
        api.get("/pagos/"),
        api.get("/clientes/"),
        api.get("/cliente-membresias/"),
      ]);

      setPagos(resPagos.data);
      setClientes(resClientes.data.filter((c) => c.estado === "ACTIVO"));
      setAsignaciones(resAsignaciones.data);
    } catch (error) {
      console.error(error);
      setError("Error al cargar los datos de pagos");
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

  const asignacionesCliente = asignaciones.filter(
    (a) => a.id_cliente === Number(form.id_cliente) && a.estado === "ACTIVA"
  );

  const validarFormulario = () => {
    if (!form.id_cliente) return "Seleccione un cliente";
    if (!form.monto || Number(form.monto) <= 0)
      return "El monto debe ser mayor a 0";
    if (!form.metodo_pago) return "Seleccione un método de pago";
    if (!form.fecha_pago) return "Seleccione la fecha de pago";
    return "";
  };

  const limpiarFormulario = () => {
    setForm(formInicial);
    setEditandoId(null);
    setError("");
  };

  const guardarPago = async (e) => {
    e.preventDefault();
    setError("");

    const mensajeError = validarFormulario();

    if (mensajeError) {
      setError(mensajeError);
      return;
    }

    const data = {
      id_cliente: Number(form.id_cliente),
      id_cliente_membresia: form.id_cliente_membresia
        ? Number(form.id_cliente_membresia)
        : null,
      monto: Number(form.monto),
      metodo_pago: form.metodo_pago,
      fecha_pago: form.fecha_pago,
      estado: form.estado,
      observacion: form.observacion || null,
    };

    try {
      if (editandoId) {
        await api.put(`/pagos/${editandoId}`, {
          id_cliente_membresia: data.id_cliente_membresia,
          monto: data.monto,
          metodo_pago: data.metodo_pago,
          fecha_pago: data.fecha_pago,
          estado: data.estado,
          observacion: data.observacion,
        });
      } else {
        await api.post("/pagos/", data);
      }

      limpiarFormulario();
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al guardar el pago");
    }
  };

  const editarPago = (pago) => {
    setEditandoId(pago.id_pago);

    setForm({
      id_cliente: pago.id_cliente || "",
      id_cliente_membresia: pago.id_cliente_membresia || "",
      monto: pago.monto || "",
      metodo_pago: pago.metodo_pago || "",
      fecha_pago: pago.fecha_pago || hoy,
      estado: pago.estado || "PAGADO",
      observacion: pago.observacion || "",
    });

    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const anularPago = async (id_pago) => {
    if (!globalThis.confirm("¿Seguro que deseas anular este pago?")) return;

    try {
      await api.delete(`/pagos/${id_pago}`);
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError("Error al anular el pago");
    }
  };

  const pagosFiltrados = pagos.filter((pago) => {
    const texto = busqueda.toLowerCase();
    return (
      obtenerNombreCliente(pago.id_cliente).toLowerCase().includes(texto) ||
      String(pago.metodo_pago || "").toLowerCase().includes(texto) ||
      String(pago.estado || "").toLowerCase().includes(texto)
    );
  });

  const total = pagosFiltrados
    .filter((p) => p.estado !== "ANULADO")
    .reduce((t, p) => t + Number(p.monto || 0), 0);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">PAGOS</span>
          <h1>Gestión de pagos</h1>
          <p>Registra y controla los pagos del gimnasio.</p>
        </div>
      </section>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Total pagos</span>
          <h2>{pagos.length}</h2>
        </div>

        <div className="stat-card highlight">
          <span>Ingresos</span>
          <h2>S/ {total.toFixed(2)}</h2>
        </div>

        <div className="stat-card">
          <span>Filtrados</span>
          <h2>{pagosFiltrados.length}</h2>
        </div>
      </div>

      <form onSubmit={guardarPago} className="form-card">
        <div className="card-header">
          <h2>{editandoId ? "Editar pago" : "Nuevo pago"}</h2>
        </div>

        {error && <p className="error-message">{error}</p>}

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="id_cliente">Cliente</label>
            <select
              id="id_cliente"
              value={form.id_cliente}
              onChange={(e) =>
                setForm({
                  ...form,
                  id_cliente: e.target.value,
                  id_cliente_membresia: "",
                })
              }
            >
              <option value="">Seleccione cliente</option>
              {clientes.map((c) => (
                <option key={c.id_cliente} value={c.id_cliente}>
                  {c.nombres} {c.apellidos}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="id_cliente_membresia">Membresía</label>
            <select
              id="id_cliente_membresia"
              value={form.id_cliente_membresia}
              onChange={(e) =>
                setForm({ ...form, id_cliente_membresia: e.target.value })
              }
            >
              <option value="">Seleccione membresía</option>
              {asignacionesCliente.map((a) => (
                <option key={a.id_cliente_membresia} value={a.id_cliente_membresia}>
                  #{a.id_cliente_membresia}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="monto">Monto (S/)</label>
            <input
              id="monto"
              type="number"
              placeholder="Monto"
              value={form.monto}
              onChange={(e) => setForm({ ...form, monto: e.target.value })}
            />
          </div>

          <div className="form-field">
            <label htmlFor="metodo_pago">Método de pago</label>
            <select
              id="metodo_pago"
              value={form.metodo_pago}
              onChange={(e) =>
                setForm({ ...form, metodo_pago: e.target.value })
              }
            >
              <option value="">Seleccione método</option>
              <option>YAPE</option>
              <option>PLIN</option>
              <option>EFECTIVO</option>
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="fecha_pago">Fecha de pago</label>
            <input
              id="fecha_pago"
              type="date"
              value={form.fecha_pago}
              onChange={(e) =>
                setForm({ ...form, fecha_pago: e.target.value })
              }
            />
          </div>
        </div>

        <div className="form-actions">
          <button className="btn-primary">
            {editandoId ? "Actualizar" : "Guardar"}
          </button>
        </div>
      </form>

      <section className="table-card">
        <div className="table-header">
          <h2>Lista de pagos</h2>

          <input
            className="search-input"
            placeholder="Buscar..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Cliente</th>
              <th>Monto</th>
              <th>Método</th>
              <th>Fecha</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {pagosFiltrados.map((p) => (
              <tr key={p.id_pago}>
                <td>#{p.id_pago}</td>
                <td>{obtenerNombreCliente(p.id_cliente)}</td>
                <td>S/ {Number(p.monto).toFixed(2)}</td>
                <td>{p.metodo_pago}</td>
                <td>{formatearFecha(p.fecha_pago)}</td>
                <td>
                  <span className="badge">{p.estado}</span>
                </td>
                <td className="table-actions">
                  <button onClick={() => editarPago(p)}>Editar</button>
                  <button
                    className="btn-danger"
                    onClick={() => anularPago(p.id_pago)}
                  >
                    Anular
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default Pagos;