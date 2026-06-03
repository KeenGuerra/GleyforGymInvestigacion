import React, { useEffect, useState } from "react";
import api from "../api/api";

function MiProgreso() {
  const [cliente, setCliente] = useState(null);
  const [progresos, setProgresos] = useState([]);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const hoy = new Date().toISOString().split("T")[0];

  const [form, setForm] = useState({
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
  });

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const calcularIMC = (peso, estatura) => {
    const p = Number(peso);
    const e = Number(estatura);

    if (!p || !e) return null;

    return (p / (e * e)).toFixed(2);
  };

  const calcularMasaGrasa = () => {
    const peso = Number(form.peso);
    const grasa = Number(form.porcentaje_grasa);

    if (!peso || !grasa) return null;

    return (peso * (grasa / 100)).toFixed(2);
  };

  const calcularMasaMagra = () => {
    const peso = Number(form.peso);
    const grasa = Number(form.porcentaje_grasa);

    if (!peso || !grasa) return null;

    const masaGrasa = peso * (grasa / 100);
    return (peso - masaGrasa).toFixed(2);
  };

  const numeroONull = (valor) => {
    return valor !== "" && valor !== null && valor !== undefined
      ? Number(valor)
      : null;
  };

  const cargarProgreso = async () => {
    try {
      setError("");

      const idUsuario = localStorage.getItem("id_usuario");

      const clienteRes = await api.get(`/clientes/usuario/${idUsuario}`);
      const clienteData = clienteRes.data;

      setCliente(clienteData);

      setForm((prev) => ({
        ...prev,
        peso: clienteData.peso || "",
      }));

      const progresoRes = await api.get(
        `/progreso/cliente/${clienteData.id_cliente}`
      );

      setProgresos(progresoRes.data);
    } catch (error) {
      console.error(error);
      setError("No se pudo cargar tu progreso.");
    }
  };

  useEffect(() => {
    cargarProgreso();
  }, []);

  const registrarProgreso = async (e) => {
    e.preventDefault();
    setMensaje("");
    setError("");

    if (!cliente) return;

    if (Number(form.peso) <= 0) {
      setError("El peso debe ser mayor a 0.");
      return;
    }

    if (
      form.porcentaje_grasa &&
      (Number(form.porcentaje_grasa) < 0 ||
        Number(form.porcentaje_grasa) > 100)
    ) {
      setError("El porcentaje de grasa debe estar entre 0 y 100.");
      return;
    }

    try {
      await api.post("/progreso/", {
        id_cliente: cliente.id_cliente,
        peso: Number(form.peso),
        porcentaje_grasa: numeroONull(form.porcentaje_grasa),
        medida_pecho: numeroONull(form.medida_pecho),
        medida_cintura: numeroONull(form.medida_cintura),
        medida_brazo_izquierdo: numeroONull(form.medida_brazo_izquierdo),
        medida_brazo_derecho: numeroONull(form.medida_brazo_derecho),
        medida_pierna_izquierda: numeroONull(form.medida_pierna_izquierda),
        medida_pierna_derecha: numeroONull(form.medida_pierna_derecha),
        fecha_registro: form.fecha_registro,
        observacion: form.observacion || null,
      });

      await api.put(`/clientes/${cliente.id_cliente}`, {
        peso: Number(form.peso),
      });

      setMensaje("Progreso registrado correctamente ✔");
      setMostrarFormulario(false);

      setForm({
        peso: form.peso,
        porcentaje_grasa: "",
        medida_pecho: "",
        medida_cintura: "",
        medida_brazo_izquierdo: "",
        medida_brazo_derecho: "",
        medida_pierna_izquierda: "",
        medida_pierna_derecha: "",
        fecha_registro: hoy,
        observacion: "",
      });

      cargarProgreso();
    } catch (error) {
      console.error("Error registrando progreso:", error);
      setError(
        error.response?.data?.detail || "No se pudo registrar el progreso."
      );
    }
  };

  const cancelarFormulario = () => {
    setMostrarFormulario(false);
    setError("");
    setMensaje("");

    setForm((prev) => ({
      ...prev,
      porcentaje_grasa: "",
      medida_pecho: "",
      medida_cintura: "",
      medida_brazo_izquierdo: "",
      medida_brazo_derecho: "",
      medida_pierna_izquierda: "",
      medida_pierna_derecha: "",
      fecha_registro: hoy,
      observacion: "",
    }));
  };

  const ultimoProgreso = progresos.length > 0 ? progresos[0] : null;
  const imcActual = calcularIMC(form.peso, cliente?.estatura);
  const masaGrasa = calcularMasaGrasa();
  const masaMagra = calcularMasaMagra();

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MI PROGRESO</span>
          <h1>Actualizar progreso</h1>
          <p>
            Registra tu peso, porcentaje de grasa y medidas para llevar un
            seguimiento real de tu evolución física.
          </p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            setMostrarFormulario(true);
            setMensaje("");
            setError("");
          }}
        >
          + Nuevo registro
        </button>
      </section>

      {mensaje && <p className="error-message">{mensaje}</p>}
      {error && <p className="error-message">{error}</p>}

      <section className="content-grid">
        {mostrarFormulario && (
          <form onSubmit={registrarProgreso} className="form-card">
            <div className="card-header">
              <div>
                <h2>Nuevo registro</h2>
                <p>Completa tus medidas actuales.</p>
              </div>
            </div>

            <div className="form-grid">
              <div className="form-field">
                <label htmlFor="peso">Peso actual (kg)</label>
                <input
                  id="peso"
                  type="number"
                  step="0.01"
                  value={form.peso}
                  onChange={(e) => setForm({ ...form, peso: e.target.value })}
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="porcentaje_grasa">Grasa corporal (%)</label>
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
                  required
                />
              </div>

              <div className="form-field field-large">
                <label htmlFor="observacion">Observación</label>
                <textarea
                  id="observacion"
                  rows="3"
                  placeholder="Ejemplo: Me siento con más energía..."
                  value={form.observacion}
                  onChange={(e) =>
                    setForm({ ...form, observacion: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="mini-stats-grid">
              <div>
                <span>IMC estimado</span>
                <strong>{imcActual || "--"}</strong>
              </div>

              <div>
                <span>Masa grasa</span>
                <strong>{masaGrasa ? `${masaGrasa} kg` : "--"}</strong>
              </div>

              <div>
                <span>Masa magra</span>
                <strong>{masaMagra ? `${masaMagra} kg` : "--"}</strong>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">
                Guardar progreso
              </button>

              <button
                type="button"
                className="btn-secondary"
                onClick={cancelarFormulario}
              >
                Cancelar
              </button>
            </div>
          </form>
        )}

        <aside className="side-column">
          <div className="card info-card">
            <h2>Resumen actual</h2>

            <div className="details-grid single-column">
              <div>
                <span>Peso</span>
                <strong>{form.peso || "-"} kg</strong>
              </div>
              <div>
                <span>Estatura</span>
                <strong>{cliente?.estatura || "-"} m</strong>
              </div>
              <div>
                <span>IMC</span>
                <strong>{imcActual || "-"}</strong>
              </div>
              <div>
                <span>Registros</span>
                <strong>{progresos.length}</strong>
              </div>
            </div>
          </div>

          {ultimoProgreso && (
            <div className="card info-card">
              <h2>Último registro</h2>

              <div className="detail-list">
                <p>
                  <span>Fecha</span>
                  <strong>{formatearFecha(ultimoProgreso.fecha_registro)}</strong>
                </p>
                <p>
                  <span>Peso</span>
                  <strong>{ultimoProgreso.peso} kg</strong>
                </p>
                <p>
                  <span>% Grasa</span>
                  <strong>{ultimoProgreso.porcentaje_grasa || "-"}%</strong>
                </p>
                <p>
                  <span>Masa grasa</span>
                  <strong>{ultimoProgreso.masa_grasa || "-"} kg</strong>
                </p>
                <p>
                  <span>Masa magra</span>
                  <strong>{ultimoProgreso.masa_magra || "-"} kg</strong>
                </p>
                <p>
                  <span>Brazo izq.</span>
                  <strong>{ultimoProgreso.medida_brazo_izquierdo || "-"} cm</strong>
                </p>
                <p>
                  <span>Brazo der.</span>
                  <strong>{ultimoProgreso.medida_brazo_derecho || "-"} cm</strong>
                </p>
                <p>
                  <span>Pierna izq.</span>
                  <strong>{ultimoProgreso.medida_pierna_izquierda || "-"} cm</strong>
                </p>
                <p>
                  <span>Pierna der.</span>
                  <strong>{ultimoProgreso.medida_pierna_derecha || "-"} cm</strong>
                </p>
                <p>
                  <span>Observación</span>
                  <strong>{ultimoProgreso.observacion || "Sin observación"}</strong>
                </p>
              </div>
            </div>
          )}
        </aside>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Historial de progreso</h2>
            <p>Listado de todos tus registros físicos.</p>
          </div>
        </div>

        {progresos.length === 0 ? (
          <section className="card empty-state">
            <h3>No tienes registros todavía</h3>
            <p>Cuando registres tu primer progreso, aparecerá aquí.</p>
          </section>
        ) : (
          <div className="list">
            {progresos.map((item) => (
              <div className="list-item" key={item.id_progreso}>
                <div>
                  <strong>{formatearFecha(item.fecha_registro)}</strong>
                  <span>{item.observacion || "Sin observación"}</span>
                </div>

                <div className="tags-row">
                  <span className="badge">Peso: {item.peso || "-"} kg</span>
                  <span className="badge">
                    % Grasa: {item.porcentaje_grasa || "-"}%
                  </span>
                  <span className="badge">
                    Masa grasa: {item.masa_grasa || "-"} kg
                  </span>
                  <span className="badge">
                    Masa magra: {item.masa_magra || "-"} kg
                  </span>
                  <span className="badge">
                    Cintura: {item.medida_cintura || "-"} cm
                  </span>
                  <span className="badge">
                    Brazo I: {item.medida_brazo_izquierdo || "-"} cm
                  </span>
                  <span className="badge">
                    Brazo D: {item.medida_brazo_derecho || "-"} cm
                  </span>
                  <span className="badge">
                    Pierna I: {item.medida_pierna_izquierda || "-"} cm
                  </span>
                  <span className="badge">
                    Pierna D: {item.medida_pierna_derecha || "-"} cm
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default MiProgreso;