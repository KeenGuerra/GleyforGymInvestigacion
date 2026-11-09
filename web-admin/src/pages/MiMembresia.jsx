import React, { useEffect, useState } from "react";
import api from "../api/api";
import { useClienteActual } from "../hooks/useClienteActual";
import CheckoutModal from "../components/CheckoutModal";
import { formatearFecha as formatearFechaBase } from "../utils/formatearFecha";

function MiMembresia() {
  const { cliente, error: errorCliente } = useClienteActual();
  const [membresias, setMembresias] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [planes, setPlanes] = useState([]);
  const [error, setError] = useState("");
  const [comprandoId, setComprandoId] = useState(null);
  const [pagandoId, setPagandoId] = useState(null);
  const [checkoutInfo, setCheckoutInfo] = useState(null);

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return formatearFechaBase(fecha);
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
    if (!cliente) return;

    try {
      setError("");

      const [clienteMembresiasRes, planesRes, pagosRes] = await Promise.all([
        api.get(`/cliente-membresias/cliente/${cliente.id_cliente}`),
        api.get("/membresias/"),
        api.get(`/pagos/cliente/${cliente.id_cliente}`),
      ]);

      const planesData = planesRes.data;

      const datosCompletos = clienteMembresiasRes.data.map((item) => {
        const plan = planesData.find((p) => p.id_membresia === item.id_membresia);

        return {
          ...item,
          plan: plan || null,
        };
      });

      setMembresias(datosCompletos);
      setPlanes(planesData);
      setPagos(pagosRes.data);
    } catch (error) {
      console.error(error);
      setError("No se pudo cargar tu membresía.");
    }
  };

  useEffect(() => {
    cargarMembresia();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cliente]);

  const membresiaActiva =
    membresias.find((m) => m.estado === "ACTIVA") ||
    membresias.find((m) => m.estado === "PAUSADA");

  const membresiaPendiente = membresias.find((m) => m.estado === "PENDIENTE");
  const pagoPendiente = membresiaPendiente
    ? pagos.find(
        (p) => p.estado === "PENDIENTE" && p.id_cliente_membresia === membresiaPendiente.id_cliente_membresia
      )
    : null;
  const puedeComprar = !membresiaActiva && !membresiaPendiente;
  const planesDisponibles = planes.filter((p) => p.estado === "ACTIVO");

  const comprarPlan = async (id_membresia) => {
    try {
      setComprandoId(id_membresia);
      setError("");
      await api.post("/cliente-membresias/comprar", { id_membresia });
      await cargarMembresia();
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo iniciar la compra de la membresía.");
    } finally {
      setComprandoId(null);
    }
  };

  const pagarPendiente = async (id_pago) => {
    try {
      setPagandoId(id_pago);
      setError("");
      const res = await api.post(`/pagos/${id_pago}/checkout`);
      setCheckoutInfo(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo iniciar el pago.");
    } finally {
      setPagandoId(null);
    }
  };

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

      {(errorCliente || error) && <p className="error-message">{errorCliente || error}</p>}

      {membresiaPendiente && pagoPendiente && (
        <section className="card promo-card" style={{ display: "flex", flexDirection: "column" }}>
          <span className="badge">PAGO PENDIENTE</span>
          <h2>{membresiaPendiente.plan?.nombre || `Plan #${membresiaPendiente.id_membresia}`}</h2>
          <p>Completa el pago para activar tu membresía.</p>
          <div className="price-box">
            <strong>S/ {obtenerPrecio(membresiaPendiente)}</strong>
          </div>
          <button
            className="btn-primary"
            style={{ marginTop: "16px", width: "100%" }}
            disabled={pagandoId === pagoPendiente.id_pago}
            onClick={() => pagarPendiente(pagoPendiente.id_pago)}
          >
            {pagandoId === pagoPendiente.id_pago ? "Generando pago..." : "Completar pago"}
          </button>
        </section>
      )}

      {puedeComprar && (
        <section>
          <h3>Elige un plan</h3>
          {planesDisponibles.length === 0 ? (
            <p className="empty-message">No hay planes disponibles por ahora.</p>
          ) : (
            <section className="cards-grid">
              {planesDisponibles.map((p) => (
                <article
                  className="card item-card"
                  key={p.id_membresia}
                  style={{ display: "flex", flexDirection: "column" }}
                >
                  <div className="item-card-top">
                    <span className="badge">{p.duracion_dias} días</span>
                  </div>

                  <h3>{p.nombre}</h3>
                  <p className="item-description">{p.descripcion || "Sin descripción"}</p>

                  {p.beneficios && <p className="item-description">{p.beneficios}</p>}

                  <div className="price-box">
                    <strong>S/ {Number(p.precio).toFixed(2)}</strong>
                    <span>{p.duracion_dias} días</span>
                  </div>

                  <button
                    className="btn-primary"
                    style={{ marginTop: "16px", width: "100%" }}
                    disabled={comprandoId === p.id_membresia}
                    onClick={() => comprarPlan(p.id_membresia)}
                  >
                    {comprandoId === p.id_membresia ? "Procesando..." : "Comprar"}
                  </button>
                </article>
              ))}
            </section>
          )}
        </section>
      )}

      {membresias.length === 0 ? null : (
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
                      <strong>
                        {item.estado === "PENDIENTE" ? "Por confirmar" : formatearFecha(item.fecha_inicio)}
                      </strong>
                    </div>

                    <div>
                      <span>Fin</span>
                      <strong>
                        {item.estado === "PENDIENTE" ? "Por confirmar" : formatearFecha(item.fecha_fin)}
                      </strong>
                    </div>
                  </div>

                  {item.estado === "PENDIENTE" ? (
                    <p className="item-description">
                      Esperando confirmación de pago. Las fechas se calculan recién cuando se confirme.
                    </p>
                  ) : (
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
                  )}
                </article>
              );
            })}
          </section>
        </>
      )}

      <CheckoutModal info={checkoutInfo} onClose={() => setCheckoutInfo(null)} />
    </div>
  );
}

export default MiMembresia;