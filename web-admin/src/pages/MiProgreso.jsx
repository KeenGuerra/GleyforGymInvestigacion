import React, { useEffect, useState } from "react";
import { formatearFecha as formatearFechaBase } from "../utils/formatearFecha";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import api from "../api/api";
import { useClienteActual } from "../hooks/useClienteActual";

function MiProgreso() {
  const { cliente, error: errorCliente } = useClienteActual();
  const [progresos, setProgresos] = useState([]);
  const [error, setError] = useState("");

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return formatearFechaBase(fecha);
  };

  const calcularIMC = (peso, estatura) => {
    const p = Number(peso);
    const e = Number(estatura);

    if (!p || !e) return null;

    return (p / (e * e)).toFixed(2);
  };

  const cargarProgreso = async (idCliente) => {
    try {
      setError("");

      const progresoRes = await api.get(`/progreso/cliente/${idCliente}`);

      setProgresos(progresoRes.data);
    } catch (error) {
      console.error(error);
      setError("No se pudo cargar tu progreso.");
    }
  };

  useEffect(() => {
    if (errorCliente) {
      setError("No se pudo cargar tu progreso.");
    }
  }, [errorCliente]);

  useEffect(() => {
    if (!cliente) return;
    cargarProgreso(cliente.id_cliente);
  }, [cliente]);

  const ultimoProgreso = progresos.length > 0 ? progresos[0] : null;
  // El peso del último registro es la fuente real una vez que hay progresos
  // -- cliente.peso es solo el dato inicial de cuando se dio de alta, y ya
  // no se sincroniza automáticamente (el registro ahora lo hace el staff
  // desde "Progreso", no el propio cliente).
  const pesoActual = ultimoProgreso?.peso ?? cliente?.peso;
  const imcActual = calcularIMC(pesoActual, cliente?.estatura);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MI PROGRESO</span>
          <h1>Mi progreso físico</h1>
          <p>
            Tu entrenador registra tu peso, medidas y composición corporal
            durante tus evaluaciones en el gimnasio. Acércate al staff cuando
            quieras que lo actualicen.
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      <section className="stats-grid">
        <div className="stat-card">
          <span>Peso</span>
          <strong>{pesoActual || "-"} kg</strong>
        </div>
        <div className="stat-card">
          <span>Estatura</span>
          <strong>{cliente?.estatura || "-"} m</strong>
        </div>
        <div className="stat-card">
          <span>IMC</span>
          <strong>{imcActual || "-"}</strong>
        </div>
        <div className="stat-card">
          <span>Registros</span>
          <strong>{progresos.length}</strong>
        </div>
      </section>

      {ultimoProgreso && (
        <section className="table-card">
          <div className="card-header">
            <div>
              <h2>Último registro</h2>
              <p>{formatearFecha(ultimoProgreso.fecha_registro)}</p>
            </div>
          </div>

          <div className="stats-grid">
            <div className="stat-card highlight">
              <span>Peso</span>
              <strong>{ultimoProgreso.peso} kg</strong>
            </div>
            <div className="stat-card highlight">
              <span>% Grasa</span>
              <strong>{ultimoProgreso.porcentaje_grasa || "-"}%</strong>
            </div>
            <div className="stat-card highlight">
              <span>Masa grasa</span>
              <strong>{ultimoProgreso.masa_grasa || "-"} kg</strong>
            </div>
            <div className="stat-card highlight">
              <span>Masa magra</span>
              <strong>{ultimoProgreso.masa_magra || "-"} kg</strong>
            </div>
          </div>

          <div className="detail-list" style={{ marginTop: "20px" }}>
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
            <p className="detail-full">
              <span>Observación</span>
              <strong>{ultimoProgreso.observacion || "Sin observación"}</strong>
            </p>
          </div>
        </section>
      )}

      {progresos.length > 1 && (
        <section className="table-card">
          <div className="card-header">
            <div>
              <h2>Evolución de tu progreso</h2>
              <p>Peso y % de grasa corporal a lo largo del tiempo.</p>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <LineChart
              data={[...progresos]
                .slice()
                .reverse()
                .map((p) => ({
                  fecha: formatearFecha(p.fecha_registro),
                  peso: p.peso,
                  grasa: p.porcentaje_grasa,
                }))}
              margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="fecha" />
              <YAxis yAxisId="peso" />
              <YAxis yAxisId="grasa" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="peso" type="monotone" dataKey="peso" name="Peso (kg)" stroke="#ff8a3d" strokeWidth={2} />
              <Line yAxisId="grasa" type="monotone" dataKey="grasa" name="% Grasa" stroke="#4dabf7" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </section>
      )}

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
            <p>
              Cuando el staff registre tu primera evaluación, aparecerá
              aquí.
            </p>
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
