import React, { useEffect, useState } from "react";
import api from "../api/api";

function MisPagos() {
  const [pagos, setPagos] = useState([]);
  const [error, setError] = useState("");

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  const cargarPagos = async () => {
    try {
      setError("");

      const idUsuario = localStorage.getItem("id_usuario");

      const clienteRes = await api.get(`/clientes/usuario/${idUsuario}`);
      const idCliente = clienteRes.data.id_cliente;

      const pagosRes = await api.get(`/pagos/cliente/${idCliente}`);

      const pagosOrdenados = pagosRes.data.sort(
        (a, b) => new Date(b.fecha_pago) - new Date(a.fecha_pago)
      );

      setPagos(pagosOrdenados);
    } catch (error) {
      console.error(error);
      setError("No se pudieron cargar tus pagos.");
    }
  };

  useEffect(() => {
    cargarPagos();
  }, []);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MIS PAGOS</span>
          <h1>Historial de pagos</h1>
          <p>Aquí puedes revisar todos los pagos realizados en el gimnasio.</p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      {pagos.length === 0 ? (
        <section className="card empty-state">
          <h3>No tienes pagos registrados</h3>
          <p>Cuando realices un pago, aparecerá aquí.</p>
        </section>
      ) : (
        <section className="cards-grid">
          {pagos.map((pago) => (
            <article className="card item-card" key={pago.id_pago}>
              <div className="item-card-top">
                <span className="badge">💰 Pago</span>
                <span className="badge">{pago.estado || "PAGADO"}</span>
              </div>

              <h2>S/ {Number(pago.monto || 0).toFixed(2)}</h2>

              <div className="detail-list">
                <p>
                  <span>Método</span>
                  <strong>{pago.metodo_pago || "-"}</strong>
                </p>

                <p>
                  <span>Fecha</span>
                  <strong>{formatearFecha(pago.fecha_pago)}</strong>
                </p>

                <p>
                  <span>Estado</span>
                  <strong>{pago.estado || "PAGADO"}</strong>
                </p>

                <p>
                  <span>Observación</span>
                  <strong>{pago.observacion || "Sin observaciones"}</strong>
                </p>
              </div>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}

export default MisPagos;