import React, { useCallback, useEffect, useState } from "react";
import api from "../api/api";
import { useToast } from "../hooks/useToast";
import ToastFeedback from "../components/ToastFeedback";

function DashboardRecepcionista() {
  const { toast, mostrarError, cerrarToast } = useToast();
  const [clientes, setClientes] = useState([]);
  const [asistenciasHoy, setAsistenciasHoy] = useState([]);
  const [pagosHoy, setPagosHoy] = useState([]);
  const [resumenVentas, setResumenVentas] = useState(null);

  const cargarDatos = useCallback(async () => {
    try {
      const hoy = new Date().toISOString().slice(0, 10);
      const [clientesRes, asistenciasRes, pagosRes, ventasRes] =
        await Promise.all([
          api.get("/clientes/"),
          api.get("/asistencias/"),
          api.get("/pagos/"),
          api.get("/ventas/resumen"),
        ]);

      setClientes(clientesRes.data.filter((c) => c.estado === "ACTIVO"));
      setAsistenciasHoy(
        asistenciasRes.data.filter((a) => a.fecha === hoy && a.estado !== "ANULADO")
      );
      setPagosHoy(pagosRes.data.filter((p) => p.fecha_pago === hoy));
      setResumenVentas(ventasRes.data);
    } catch (error) {
      console.error("Error cargando dashboard recepcionista:", error);
      mostrarError("No se pudo cargar el dashboard.");
    }
  }, [mostrarError]);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  const ingresosPagosHoy = pagosHoy
    .filter((p) => p.estado === "PAGADO")
    .reduce((total, p) => total + Number(p.monto || 0), 0);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">RECEPCIONISTA</span>
          <h1>Panel de recepción</h1>
          <p>Atención en mostrador: clientes, asistencias, membresías, pagos y ventas.</p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Clientes activos</span>
          <strong>{clientes.length}</strong>
        </div>

        <div className="stat-card">
          <span>Asistencias de hoy</span>
          <strong>{asistenciasHoy.length}</strong>
        </div>

        <div className="stat-card">
          <span>Pagos cobrados hoy</span>
          <strong>S/ {ingresosPagosHoy.toFixed(2)}</strong>
        </div>

        <div className="stat-card">
          <span>Ventas de hoy</span>
          <strong>{resumenVentas ? resumenVentas.ventas_hoy : 0}</strong>
        </div>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Asistencias de hoy</h2>
            <p>Clientes que ya marcaron asistencia en el día.</p>
          </div>
        </div>

        {asistenciasHoy.length === 0 ? (
          <p className="empty-message">Todavía no hay asistencias registradas hoy.</p>
        ) : (
          <div className="list">
            {asistenciasHoy.slice(0, 5).map((asistencia) => (
              <div className="list-item" key={asistencia.id_asistencia}>
                <div className="user-info">
                  <div>
                    <strong>Cliente #{asistencia.id_cliente}</strong>
                    <span>Entrada: {asistencia.hora_entrada}</span>
                  </div>
                </div>

                <span className="badge">
                  {asistencia.hora_salida ? "Salió" : "En gimnasio"}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      <ToastFeedback toast={toast} onClose={cerrarToast} />
    </div>
  );
}

export default DashboardRecepcionista;
