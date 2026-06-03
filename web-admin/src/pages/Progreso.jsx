import React, { useEffect, useState } from "react";
import api from "../api/api";
import { MSG_CLIENTE_NO_ENCONTRADO } from "../api/constants";

function Progreso() {
  const [progresos, setProgresos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [editandoId, setEditandoId] = useState(null);
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const hoy = new Date().toISOString().split("T")[0];

  const formInicial = {
    id_cliente: "",
    peso: "",
    porcentaje_grasa: "",
    medida_pecho: "",
    medida_cintura: "",
    medida_brazo_izquierdo: "",
    medida_brazo_derecho: "",
    medida_pierna_izquierda: "",
    medida_pierna_derecha: "",
    fecha_registro: hoy,
    observacion: "",
  };

  const [form, setForm] = useState(formInicial);

  const cargarDatos = async () => {
    try {
      setError("");

      const [resProgreso, resClientes] = await Promise.all([
        api.get("/progreso/"),
        api.get("/clientes/"),
      ]);

      setProgresos(resProgreso.data);
      setClientes(resClientes.data.filter((c) => c.estado === "ACTIVO"));
    } catch (error) {
      console.error(error);
      setError("Error al cargar progreso");
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

  const calcularMasaGrasa = () => {
    const peso = Number(form.peso);
    const grasa = Number(form.porcentaje_grasa);
    if (!peso || !grasa) return "-";
    return (peso * (grasa / 100)).toFixed(2);
  };

  const calcularMasaMagra = () => {
    const peso = Number(form.peso);
    const grasa = Number(form.porcentaje_grasa);
    if (!peso || !grasa) return "-";
    const masaGrasa = peso * (grasa / 100);
    return (peso - masaGrasa).toFixed(2);
  };

  const validarFormulario = () => {
    if (!form.id_cliente) return "Seleccione un cliente";
    if (!form.peso || Number(form.peso) <= 0) return "Peso inválido";

    if (
      form.porcentaje_grasa &&
      (Number(form.porcentaje_grasa) < 0 ||
        Number(form.porcentaje_grasa) > 100)
    ) {
      return "El porcentaje de grasa debe estar entre 0 y 100";
    }

    if (!form.fecha_registro) return "Seleccione fecha";

    return "";
  };

  const limpiarFormulario = () => {
    setForm(formInicial);
    setEditandoId(null);
    setError("");
    setMostrarFormulario(false);
  };

  const convertirNumeroONull = (valor) => {
    return valor !== "" && valor !== null && valor !== undefined
      ? Number(valor)
      : null;
  };

  const guardarProgreso = async (e) => {
    e.preventDefault();
    setError("");

    const msg = validarFormulario();

    if (msg) {
      setError(msg);
      return;
    }

    const data = {
      id_cliente: Number(form.id_cliente),
      peso: Number(form.peso),
      porcentaje_grasa: convertirNumeroONull(form.porcentaje_grasa),
      medida_pecho: convertirNumeroONull(form.medida_pecho),
      medida_cintura: convertirNumeroONull(form.medida_cintura),
      medida_brazo_izquierdo: convertirNumeroONull(
        form.medida_brazo_izquierdo
      ),
      medida_brazo_derecho: convertirNumeroONull(form.medida_brazo_derecho),
      medida_pierna_izquierda: convertirNumeroONull(
        form.medida_pierna_izquierda
      ),
      medida_pierna_derecha: convertirNumeroONull(form.medida_pierna_derecha),
      fecha_registro: form.fecha_registro,
      observacion: form.observacion || null,
    };

    try {
      if (editandoId) {
        await api.put(`/progreso/${editandoId}`, {
          peso: data.peso,
          porcentaje_grasa: data.porcentaje_grasa,
          medida_pecho: data.medida_pecho,
          medida_cintura: data.medida_cintura,
          medida_brazo_izquierdo: data.medida_brazo_izquierdo,
          medida_brazo_derecho: data.medida_brazo_derecho,
          medida_pierna_izquierda: data.medida_pierna_izquierda,
          medida_pierna_derecha: data.medida_pierna_derecha,
          fecha_registro: data.fecha_registro,
          observacion: data.observacion,
        });
      } else {
        await api.post("/progreso/", data);
      }

      limpiarFormulario();
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al guardar progreso");
    }
  };

  const editarProgreso = (p) => {
    setEditandoId(p.id_progreso);
    setMostrarFormulario(true);

    setForm({
      id_cliente: p.id_cliente || "",
      peso: p.peso || "",
      porcentaje_grasa: p.porcentaje_grasa || "",
      medida_pecho: p.medida_pecho || "",
      medida_cintura: p.medida_cintura || "",
      medida_brazo_izquierdo: p.medida_brazo_izquierdo || "",
      medida_brazo_derecho: p.medida_brazo_derecho || "",
      medida_pierna_izquierda: p.medida_pierna_izquierda || "",
      medida_pierna_derecha: p.medida_pierna_derecha || "",
      fecha_registro: p.fecha_registro || hoy,
      observacion: p.observacion || "",
    });

    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarProgreso = async (id) => {
    const confirmar = globalThis.confirm(
      "¿Seguro que deseas eliminar este registro?"
    );
    if (!confirmar) return;

    try {
      await api.delete(`/progreso/${id}`);
      cargarDatos();
    } catch (error) {
      console.error(error);
      setError("Error al eliminar progreso");
    }
  };

  const progresosFiltrados = progresos.filter((p) => {
    const nombre = obtenerNombreCliente(p.id_cliente).toLowerCase();
    const texto = busqueda.toLowerCase();

    return nombre.includes(texto);
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">PROGRESO FÍSICO</span>
          <h1>Seguimiento físico</h1>
          <p>Registra y consulta el progreso corporal de los clientes.</p>
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
          + Registrar progreso
        </button>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardarProgreso} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editandoId ? "Editar progreso" : "Registrar progreso"}</h2>
              <p>Completa peso, medidas corporales y observación del cliente.</p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field field-large">
              <label htmlFor="id_cliente">Cliente</label>
              <select
                id="id_cliente"
                value={form.id_cliente}
                onChange={(e) =>
                  setForm({ ...form, id_cliente: e.target.value })
                }
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
              <label htmlFor="porcentaje_grasa">% grasa corporal</label>
              <input
                id="porcentaje_grasa"
                type="number"
                step="0.01"
                value={form.porcentaje_grasa}
                onChange={(e) =>
                  setForm({ ...form, porcentaje_grasa: e.target.value })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="masa_grasa">Masa grasa</label>
              <input id="masa_grasa" type="text" value={`${calcularMasaGrasa()} kg`} disabled />
            </div>

            <div className="form-field">
              <label htmlFor="masa_magra">Masa magra</label>
              <input id="masa_magra" type="text" value={`${calcularMasaMagra()} kg`} disabled />
            </div>

            <div className="form-field">
              <label htmlFor="medida_pecho">Pecho (cm)</label>
              <input
                id="medida_pecho"
                type="number"
                step="0.01"
                value={form.medida_pecho}
                onChange={(e) =>
                  setForm({ ...form, medida_pecho: e.target.value })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="medida_cintura">Cintura (cm)</label>
              <input
                id="medida_cintura"
                type="number"
                step="0.01"
                value={form.medida_cintura}
                onChange={(e) =>
                  setForm({ ...form, medida_cintura: e.target.value })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="medida_brazo_izquierdo">Brazo izquierdo (cm)</label>
              <input
                id="medida_brazo_izquierdo"
                type="number"
                step="0.01"
                value={form.medida_brazo_izquierdo}
                onChange={(e) =>
                  setForm({
                    ...form,
                    medida_brazo_izquierdo: e.target.value,
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="medida_brazo_derecho">Brazo derecho (cm)</label>
              <input
                id="medida_brazo_derecho"
                type="number"
                step="0.01"
                value={form.medida_brazo_derecho}
                onChange={(e) =>
                  setForm({
                    ...form,
                    medida_brazo_derecho: e.target.value,
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="medida_pierna_izquierda">Pierna izquierda (cm)</label>
              <input
                id="medida_pierna_izquierda"
                type="number"
                step="0.01"
                value={form.medida_pierna_izquierda}
                onChange={(e) =>
                  setForm({
                    ...form,
                    medida_pierna_izquierda: e.target.value,
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="medida_pierna_derecha">Pierna derecha (cm)</label>
              <input
                id="medida_pierna_derecha"
                type="number"
                step="0.01"
                value={form.medida_pierna_derecha}
                onChange={(e) =>
                  setForm({
                    ...form,
                    medida_pierna_derecha: e.target.value,
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="fecha_registro">Fecha de registro</label>
              <input
                id="fecha_registro"
                type="date"
                value={form.fecha_registro}
                onChange={(e) =>
                  setForm({ ...form, fecha_registro: e.target.value })
                }
              />
            </div>

            <div className="form-field field-large">
              <label htmlFor="observacion">Observación</label>
              <textarea
                id="observacion"
                placeholder="Observación"
                value={form.observacion}
                onChange={(e) =>
                  setForm({ ...form, observacion: e.target.value })
                }
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {editandoId ? "Actualizar" : "Guardar"}
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
            <h2>Historial de progreso</h2>
            <p>Consulta, edita o elimina registros físicos.</p>
          </div>

          <input
            className="search-input"
            type="text"
            placeholder="Buscar por cliente..."
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
                <th>Peso</th>
                <th>% Grasa</th>
                <th>Masa grasa</th>
                <th>Masa magra</th>
                <th>Brazos</th>
                <th>Piernas</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {progresosFiltrados.length === 0 ? (
                <tr>
                  <td colSpan="10" className="empty-message">
                    No hay registros
                  </td>
                </tr>
              ) : (
                progresosFiltrados.map((p) => (
                  <tr key={p.id_progreso}>
                    <td>
                      <span className="badge">#{p.id_progreso}</span>
                    </td>
                    <td>{obtenerNombreCliente(p.id_cliente)}</td>
                    <td>{p.peso} kg</td>
                    <td>{p.porcentaje_grasa || "-"}%</td>
                    <td>{p.masa_grasa || "-"} kg</td>
                    <td>{p.masa_magra || "-"} kg</td>
                    <td>
                      I: {p.medida_brazo_izquierdo || "-"} cm / D:{" "}
                      {p.medida_brazo_derecho || "-"} cm
                    </td>
                    <td>
                      I: {p.medida_pierna_izquierda || "-"} cm / D:{" "}
                      {p.medida_pierna_derecha || "-"} cm
                    </td>
                    <td>{formatearFecha(p.fecha_registro)}</td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="btn-secondary"
                          onClick={() => editarProgreso(p)}
                        >
                          Editar
                        </button>

                        <button
                          className="btn-danger"
                          onClick={() => eliminarProgreso(p.id_progreso)}
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

export default Progreso;