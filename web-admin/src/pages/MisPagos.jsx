import React, { useEffect, useState } from "react";
import api from "../api/api";
import { descargarBlob } from "../utils/descargarArchivo";
import { useClienteActual } from "../hooks/useClienteActual";

function MisPagos() {
  const { cliente, error: errorCliente } = useClienteActual();
  const [pagos, setPagos] = useState([]);
  const [error, setError] = useState("");
  const [descargando, setDescargando] = useState(null);

  const descargarRecibo = async (idPago) => {
    setDescargando(idPago);
    try {
      const res = await api.get(`/pagos/${idPago}/recibo`, { responseType: "blob" });
      descargarBlob(res.data, `recibo-pago-${idPago}.pdf`);
    } catch (err) {
      console.error(err);
      setError("No se pudo descargar el recibo.");
    } finally {
      setDescargando(null);
    }
  };

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  useEffect(() => {
    if (!cliente) return;

    const cargarPagos = async () => {
      try {
        setError("");

        const pagosRes = await api.get(`/pagos/cliente/${cliente.id_cliente}`);

        const pagosOrdenados = pagosRes.data.sort(
          (a, b) => new Date(b.fecha_pago) - new Date(a.fecha_pago)
        );

        setPagos(pagosOrdenados);
      } catch (error) {
        console.error(error);
        setError("No se pudieron cargar tus pagos.");
      }
    };

    cargarPagos();
  }, [cliente]);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">MIS PAGOS</span>
          <h1>Historial de pagos</h1>
          <p>Aquí puedes revisar todos los pagos realizados en el gimnasio.</p>
        </div>
      </section>

      {(errorCliente || error) && <p className="error-message">{errorCliente || error}</p>}

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

              <div className="form-actions">
                <button
                  className="btn-secondary"
                  disabled={descargando === pago.id_pago}
                  onClick={() => descargarRecibo(pago.id_pago)}
                >
                  {descargando === pago.id_pago ? "Descargando..." : "Descargar recibo"}
                </button>
              </div>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}

export default MisPagos;