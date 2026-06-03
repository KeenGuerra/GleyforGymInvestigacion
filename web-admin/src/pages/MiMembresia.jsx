import React, { useEffect, useState } from "react";
import api from "../api/api";

function MiMembresia() {
  const [membresias, setMembresias] = useState([]);
  const [error, setError] = useState("");

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const calcularDiasRestantes = (fechaFin) => {
    if (!fechaFin) return 0;

    const hoy = new Date();
    const fin = new Date(fechaFin);

    hoy.setHours(0, 0, 0, 0);
    fin.setHours(0, 0, 0, 0);

    const diferencia = fin - hoy;

    return Math.max(Math.ceil(diferencia / (1000 * 60 * 60 * 24)), 0);
  };

  const obtenerPrecio = (item) => {
    return Number(item.precio_asignado ?? item.plan?.precio ?? 0).toFixed(2);
  };

  const obtenerTextoEstado = (estado) => {
    if (estado === "TERMINADA") return "Membresía terminada";
    if (estado === "CANCELADA") return "Membresía cancelada";
    if (estado === "PAUSADA") return "Membresía pausada";
    return "Días restantes";
  };

  const cargarMembresia = async () => {
    try {
      setError("");

      const idUsuario = localStorage.getItem("id_usuario");

      const clienteRes = await api.get(`/clientes/usuario/${idUsuario}`);
      const idCliente = clienteRes.data.id_cliente;

      const [clienteMembresiasRes, planesRes] = await Promise.all([
        api.get(`/cliente-membresias/cliente/${idCliente}`),
        api.get("/membresias/"),
      ]);

      const planes = planesRes.data;

      const datosCompletos = clienteMembresiasRes.data.map((item) => {
        const plan = planes.find((p) => p.id_membresia === item.id_membresia);

        return {
          ...item,
          plan: plan || null,
        };
      });

      setMembresias(datosCompletos);
    } catch (error) {
      console.error(error);
      setError("No se pudo cargar tu membresía.");
    }
  };

  useEffect(() => {
    cargarMembresia();
  }, []);

  const membresiaActiva =
    membresias.find((m) => m.estado === "ACTIVA") ||
    membresias.find((m) => m.estado === "PAUSADA");

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MI MEMBRESÍA</span>
          <h1>Estado de mi membresía</h1>
          <p>
            Consulta tu plan actual, fechas de vigencia y estado de tu membresía.
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      {membresias.length === 0 ? (
        <section className="card empty-state">
          <h3>No tienes membresías registradas</h3>
          <p>Cuando se te asigne una membresía, aparecerá aquí.</p>
        </section>
      ) : (
        <>
          {membresiaActiva && (
            <section className="card promo-card">
              <span className="badge">
                {membresiaActiva.estado === "PAUSADA"
                  ? "PLAN PAUSADO"
                  : "PLAN ACTIVO"}
              </span>

              <h2>{membresiaActiva.plan?.nombre || "Membresía activa"}</h2>

              <p>
                {membresiaActiva.plan?.descripcion ||
                  "Plan asignado actualmente."}
              </p>

              <div className="price-box">
                <strong>S/ {obtenerPrecio(membresiaActiva)}</strong>
                <span>{membresiaActiva.plan?.duracion_dias || "-"} días</span>
              </div>
            </section>
          )}

          <section className="cards-grid">
            {membresias.map((item) => {
              const diasRestantes =
                item.estado === "TERMINADA" || item.estado === "CANCELADA"
                  ? 0
                  : calcularDiasRestantes(item.fecha_fin);

              return (
                <article
                  className="card item-card"
                  key={item.id_cliente_membresia}
                >
                  <div className="item-card-top">
                    <span className="badge">{item.estado || "SIN ESTADO"}</span>
                  </div>

                  <h3>{item.plan?.nombre || `Plan #${item.id_membresia}`}</h3>
                  <p>{item.plan?.descripcion || "Sin descripción"}</p>

                  <div className="mini-stats-grid">
                    <div>
                      <span>Precio asignado</span>
                      <strong>S/ {obtenerPrecio(item)}</strong>
                    </div>

                    <div>
                      <span>Duración</span>
                      <strong>{item.plan?.duracion_dias || "-"} días</strong>
                    </div>

                    <div>
                      <span>Inicio</span>
                      <strong>{formatearFecha(item.fecha_inicio)}</strong>
                    </div>

                    <div>
                      <span>Fin</span>
                      <strong>{formatearFecha(item.fecha_fin)}</strong>
                    </div>
                  </div>

                  <div className="progress-block">
                    <div className="progress-info">
                      <span>
                        {obtenerTextoEstado(item.estado)}
                      </span>

                      <strong>{diasRestantes} días</strong>
                    </div>

                    <div className="progress-bar">
                      <div
                        style={{
                          width: `${Math.min(
                            100,
                            (diasRestantes /
                              Number(item.plan?.duracion_dias || 1)) *
                              100
                          )}%`,
                        }}
                      ></div>
                    </div>
                  </div>
                </article>
              );
            })}
          </section>
        </>
      )}
    </div>
  );
}

export default MiMembresia;