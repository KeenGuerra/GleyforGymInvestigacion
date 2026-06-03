import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import { MSG_CLIENTE_NO_ENCONTRADO } from "../api/constants";

function DashboardAdmin() {
  const navigate = useNavigate();

  const [clientes, setClientes] = useState([]);
  const [membresiasCliente, setMembresiasCliente] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [asistencias, setAsistencias] = useState([]);

  const cargarDatos = async () => {
    try {
      const [resClientes, resClienteMembresias, resPagos, resAsistencias] =
        await Promise.all([
          api.get("/clientes/"),
          api.get("/cliente-membresias/"),
          api.get("/pagos/"),
          api.get("/asistencias/"),
        ]);

      setClientes(resClientes.data);
      setMembresiasCliente(resClienteMembresias.data);
      setPagos(resPagos.data);
      setAsistencias(resAsistencias.data);
    } catch (error) {
      console.error("Error al cargar dashboard:", error);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const hoy = new Date().toISOString().slice(0, 10);

  const membresiasActivas = membresiasCliente.filter(
    (m) => m.estado === "ACTIVA"
  );

  const pagosValidos = pagos.filter((p) => p.estado !== "ANULADO");

  const ingresosTotales = pagosValidos.reduce(
    (total, pago) => total + Number(pago.monto || 0),
    0
  );

  const asistenciasHoy = asistencias.filter((a) => {
    if (!a.fecha) return false;
    return a.fecha.slice(0, 10) === hoy;
  });

  const obtenerNombreCliente = (id_cliente) => {
    const cliente = clientes.find((c) => c.id_cliente === id_cliente);
    if (!cliente) return MSG_CLIENTE_NO_ENCONTRADO;
    return `${cliente.nombres || ""} ${cliente.apellidos || ""}`.trim();
  };

  const iniciales = (nombre) => {
    if (!nombre) return "??";
    return nombre
      .split(" ")
      .map((n) => n[0])
      .join("")
      .substring(0, 2)
      .toUpperCase();
  };

  const actividadReciente = [
    ...asistencias.slice(0, 4).map((a) => ({
      id: `a-${a.id_asistencia}`,
      cliente: obtenerNombreCliente(a.id_cliente),
      accion: "Asistencia registrada",
      estado: a.observacion || "REGISTRADO",
      fecha: a.fecha || "-",
    })),
    ...pagosValidos.slice(0, 4).map((p) => ({
      id: `p-${p.id_pago}`,
      cliente: obtenerNombreCliente(p.id_cliente),
      accion: "Pago registrado",
      estado: p.estado || "PAGADO",
      fecha: p.fecha_pago || "-",
    })),
  ].slice(0, 6);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">ADMINISTRADOR</span>
          <h1>Panel de control</h1>
          <p>
            Gestiona clientes, pagos, membresías, asistencias, rutinas y planes
            nutricionales de GLEYFORGYM.
          </p>
        </div>

        <button className="btn-primary" onClick={() => navigate("/clientes")}>
          Ver clientes
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Clientes registrados</span>
          <strong>{clientes.length}</strong>
        </div>

        <div className="stat-card">
          <span>Membresías activas</span>
          <strong>{membresiasActivas.length}</strong>
        </div>

        <div className="stat-card">
          <span>Ingresos registrados</span>
          <strong>S/ {ingresosTotales.toFixed(2)}</strong>
        </div>

        <div className="stat-card">
          <span>Asistencias de hoy</span>
          <strong>{asistenciasHoy.length}</strong>
        </div>
      </section>

      <section className="quick-actions-grid">
        <button className="card quick-action" onClick={() => navigate("/cliente-membresias")}>
          <span>🎫</span>
          <strong>Asignar membresía</strong>
        </button>

        <button className="card quick-action" onClick={() => navigate("/pagos")}>
          <span>💰</span>
          <strong>Registrar pago</strong>
        </button>

        <button className="card quick-action" onClick={() => navigate("/asistencias")}>
          <span>✅</span>
          <strong>Registrar asistencia</strong>
        </button>

        <button className="card quick-action" onClick={() => navigate("/rutinas")}>
          <span>🏃</span>
          <strong>Generar rutina IA</strong>
        </button>
      </section>

      <section className="content-grid">
        <div className="table-card">
          <div className="card-header">
            <div>
              <h2>Actividad reciente</h2>
              <p>Últimos pagos y asistencias registradas.</p>
            </div>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Cliente</th>
                  <th>Acción</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                </tr>
              </thead>

              <tbody>
                {actividadReciente.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="empty-message">
                      No hay actividad reciente
                    </td>
                  </tr>
                ) : (
                  actividadReciente.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <div className="user-info">
                          <div className="profile-avatar">
                            {iniciales(item.cliente)}
                          </div>
                          <span>{item.cliente}</span>
                        </div>
                      </td>

                      <td>{item.accion}</td>

                      <td>
                        <span className="badge">{item.estado}</span>
                      </td>

                      <td>{item.fecha}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="side-column">
          <div className="card info-card">
            <h2>Estado del sistema</h2>
            <p>
              Plataforma conectada con clientes, membresías, pagos, asistencias,
              progreso, rutinas IA y nutrición IA.
            </p>

            <div className="status-list">
              <span>Backend FastAPI activo</span>
              <span>Base de datos PostgreSQL</span>
              <span>Panel administrativo</span>
              <span>Módulos de IA conectados</span>
            </div>
          </div>

          <div className="card info-card">
            <h2>Resumen rápido</h2>

            <div className="summary-item">
              <span>👥</span>
              <div>
                <strong>{clientes.length} clientes</strong>
                <p>Clientes registrados</p>
              </div>
            </div>

            <div className="summary-item">
              <span>🏅</span>
              <div>
                <strong>{membresiasActivas.length} activas</strong>
                <p>Membresías vigentes</p>
              </div>
            </div>

            <div className="summary-item">
              <span>💵</span>
              <div>
                <strong>S/ {ingresosTotales.toFixed(2)}</strong>
                <p>Ingresos registrados</p>
              </div>
            </div>
          </div>

          <div className="card promo-card">
            <span className="badge">GLEYFORGYM SaaS</span>
            <h2>Gestión completa desde una sola plataforma</h2>
            <p>Administra tu gimnasio con una experiencia moderna y ordenada.</p>
          </div>
        </aside>
      </section>
    </div>
  );
}

export default DashboardAdmin;