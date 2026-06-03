import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/api";

function DetalleCliente() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [detalle, setDetalle] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarDetalle = async () => {
      try {
        const res = await api.get(`/clientes/${id}/detalle`);
        setDetalle(res.data);
      } catch (error) {
        console.error("Error al cargar detalle:", error);
        setError("No se pudo cargar el detalle del cliente.");
      }
    };

    cargarDetalle();
  }, [id]);

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-PE");
  };

  if (error) return <p className="error-message">{error}</p>;
  if (!detalle) return <p className="empty-message">Cargando detalle...</p>;

  const { cliente, membresia_actual, ultimo_pago, ultimo_progreso } = detalle;

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div className="user-info">
          <div className="profile-avatar">
            {cliente.nombres?.[0]}
            {cliente.apellidos?.[0]}
          </div>

          <div>
            <span className="badge">DETALLE DEL CLIENTE</span>
            <h1>
              {cliente.nombres} {cliente.apellidos}
            </h1>
            <p>{cliente.correo}</p>
          </div>
        </div>

        <button className="btn-secondary" onClick={() => navigate("/clientes")}>
          Volver a clientes
        </button>
      </section>

      <section className="content-grid">
        <div className="table-card content-large">
          <div className="card-header">
            <div>
              <h2>Datos del cliente</h2>
              <p>Información personal y física registrada.</p>
            </div>
          </div>

          <div className="details-grid">
            <div><span>DNI</span><strong>{cliente.dni || "-"}</strong></div>
            <div><span>Teléfono</span><strong>{cliente.telefono || "-"}</strong></div>
            <div><span>Sexo</span><strong>{cliente.sexo || "-"}</strong></div>
            <div><span>Edad</span><strong>{cliente.edad || "-"}</strong></div>
            <div><span>Peso</span><strong>{cliente.peso || "-"} kg</strong></div>
            <div><span>Estatura</span><strong>{cliente.estatura || "-"} m</strong></div>
            <div><span>Objetivo</span><strong>{cliente.objetivo || "-"}</strong></div>
            <div><span>Nivel</span><strong>{cliente.nivel || "-"}</strong></div>
            <div><span>Fecha nacimiento</span><strong>{formatearFecha(cliente.fecha_nacimiento)}</strong></div>
            <div><span>Dirección</span><strong>{cliente.direccion || "-"}</strong></div>
            <div className="detail-full">
              <span>Restricciones</span>
              <strong>{cliente.restricciones_medicas || "-"}</strong>
            </div>
          </div>
        </div>

        <aside className="side-column">
          <div className="card info-card">
            <h2>Membresía actual</h2>

            {membresia_actual ? (
              <div className="detail-list">
                <p><span>Nombre</span><strong>{membresia_actual.nombre}</strong></p>
                <p><span>Estado</span><strong><span className="badge">{membresia_actual.estado}</span></strong></p>
                <p><span>Inicio</span><strong>{formatearFecha(membresia_actual.fecha_inicio)}</strong></p>
                <p><span>Fin</span><strong>{formatearFecha(membresia_actual.fecha_fin)}</strong></p>
                {membresia_actual.precio_asignado !== undefined && (
                  <p>
                    <span>Precio asignado</span>
                    <strong>S/ {Number(membresia_actual.precio_asignado || 0).toFixed(2)}</strong>
                  </p>
                )}
              </div>
            ) : (
              <p className="empty-message">No tiene membresía registrada.</p>
            )}
          </div>

          <div className="card info-card">
            <h2>Último pago</h2>

            {ultimo_pago ? (
              <div className="detail-list">
                <p><span>Monto</span><strong>S/ {Number(ultimo_pago.monto || 0).toFixed(2)}</strong></p>
                <p><span>Método</span><strong>{ultimo_pago.metodo_pago}</strong></p>
                <p><span>Fecha</span><strong>{formatearFecha(ultimo_pago.fecha_pago)}</strong></p>
                <p><span>Estado</span><strong><span className="badge">{ultimo_pago.estado}</span></strong></p>
                <p><span>Observación</span><strong>{ultimo_pago.observacion || "-"}</strong></p>
              </div>
            ) : (
              <p className="empty-message">No tiene pagos registrados.</p>
            )}
          </div>
        </aside>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Último progreso</h2>
            <p>Último registro físico del cliente.</p>
          </div>
        </div>

        {ultimo_progreso ? (
          <div className="details-grid">
            <div><span>Fecha</span><strong>{formatearFecha(ultimo_progreso.fecha_registro)}</strong></div>
            <div><span>Peso</span><strong>{ultimo_progreso.peso} kg</strong></div>
            <div><span>Grasa corporal</span><strong>{ultimo_progreso.porcentaje_grasa || "-"} %</strong></div>
            <div><span>Masa grasa</span><strong>{ultimo_progreso.masa_grasa || "-"} kg</strong></div>
            <div><span>Masa magra</span><strong>{ultimo_progreso.masa_magra || "-"} kg</strong></div>
            <div><span>Pecho</span><strong>{ultimo_progreso.medida_pecho || "-"} cm</strong></div>
            <div><span>Cintura</span><strong>{ultimo_progreso.medida_cintura || "-"} cm</strong></div>
            <div><span>Brazo izquierdo</span><strong>{ultimo_progreso.medida_brazo_izquierdo || "-"} cm</strong></div>
            <div><span>Brazo derecho</span><strong>{ultimo_progreso.medida_brazo_derecho || "-"} cm</strong></div>
            <div><span>Pierna izquierda</span><strong>{ultimo_progreso.medida_pierna_izquierda || "-"} cm</strong></div>
            <div><span>Pierna derecha</span><strong>{ultimo_progreso.medida_pierna_derecha || "-"} cm</strong></div>
            <div className="detail-full">
              <span>Observación</span>
              <strong>{ultimo_progreso.observacion || "-"}</strong>
            </div>
          </div>
        ) : (
          <p className="empty-message">No tiene progreso registrado.</p>
        )}
      </section>
    </div>
  );
}

export default DetalleCliente;