import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import api from "../api/api";
import { MSG_CLIENTE_NO_ENCONTRADO } from "../api/constants";
import { useToast } from "../hooks/useToast";
import ToastFeedback from "../components/ToastFeedback";

function DashboardAdmin() {
  const navigate = useNavigate();
  const { toast, mostrarError, cerrarToast } = useToast();

  const [clientes, setClientes] = useState([]);
  const [membresiasCliente, setMembresiasCliente] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [asistencias, setAsistencias] = useState([]);
  const [kpis, setKpis] = useState(null);
  const [productosMasVendidos, setProductosMasVendidos] = useState([]);

  const cargarDatos = useCallback(async () => {
    try {
      const hoyISO = new Date().toISOString().slice(0, 10);
      const primerDiaMes = new Date(new Date().getFullYear(), new Date().getMonth(), 1)
        .toISOString()
        .slice(0, 10);

      const [resClientes, resClienteMembresias, resPagos, resAsistencias, resKpis, resProductos] =
        await Promise.all([
          api.get("/clientes/"),
          api.get("/cliente-membresias/"),
          api.get("/pagos/"),
          api.get("/asistencias/"),
          api.get("/reportes/kpis"),
          api.get("/reportes/productos-mas-vendidos", { params: { desde: primerDiaMes, hasta: hoyISO } }),
        ]);

      setClientes(resClientes.data);
      setMembresiasCliente(resClienteMembresias.data);
      setPagos(resPagos.data);
      setAsistencias(resAsistencias.data);
      setKpis(Array.isArray(resKpis.data) ? null : resKpis.data);
      setProductosMasVendidos(resProductos.data);
    } catch (error) {
      console.error("Error al cargar dashboard:", error);
      mostrarError("No se pudo cargar el dashboard.");
    }
  }, [mostrarError]);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  const hoy = new Date().toISOString().slice(0, 10);

  const membresiasActivas = membresiasCliente.filter(
    (m) => m.estado === "ACTIVA"
  );

  const diasHasta = (fecha) => {
    if (!fecha) return null;
    const msPorDia = 1000 * 60 * 60 * 24;
    const hoyUtc = new Date(hoy).getTime();
    const fechaUtc = new Date(fecha.slice(0, 10)).getTime();
    return Math.round((fechaUtc - hoyUtc) / msPorDia);
  };

  const membresiasPorVencer = membresiasActivas
    .map((m) => ({ ...m, diasRestantes: diasHasta(m.fecha_fin) }))
    .filter((m) => m.diasRestantes !== null && m.diasRestantes >= 0 && m.diasRestantes <= 7)
    .sort((a, b) => a.diasRestantes - b.diasRestantes);

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

  const ultimosNDias = (n) => {
    const dias = [];
    for (let i = n - 1; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      dias.push(d.toISOString().slice(0, 10));
    }
    return dias;
  };

  const ingresosPorDia = ultimosNDias(7).map((fecha) => ({
    fecha: fecha.slice(5),
    monto: pagosValidos
      .filter((p) => (p.fecha_pago || "").slice(0, 10) === fecha)
      .reduce((total, p) => total + Number(p.monto || 0), 0),
  }));

  const asistenciasPorDia = ultimosNDias(7).map((fecha) => ({
    fecha: fecha.slice(5),
    cantidad: asistencias.filter((a) => (a.fecha || "").slice(0, 10) === fecha).length,
  }));

  // Qué tan sana está la base de socios de un vistazo -- más útil que
  // comparar clientes contra rutinas IA, dos cosas sin relación entre sí.
  const ESTADOS_MEMBRESIA = ["ACTIVA", "PAUSADA", "PENDIENTE", "TERMINADA", "CANCELADA"];
  const membresiasPorEstado = ESTADOS_MEMBRESIA.map((estado) => ({
    estado,
    cantidad: membresiasCliente.filter((m) => m.estado === estado).length,
  }));

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

      {kpis && (
        <section className="content-grid">
          <div className="table-card">
            <div className="card-header">
              <div>
                <h2>Membresías por estado</h2>
                <p>Cuántas activas, pausadas o por renovar tiene el gimnasio ahora.</p>
              </div>
            </div>

            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={membresiasPorEstado} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="estado" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="cantidad" name="Membresías" fill="#ff8a3d" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <aside className="side-column">
            <div className="card info-card">
              <h2>Recaudación del mes</h2>
              <strong style={{ fontSize: "28px" }}>
                S/ {Number(kpis.recaudacion_mes_actual || 0).toFixed(2)}
              </strong>
              <p>Pagos con estado PAGADO desde el día 1 del mes actual.</p>
            </div>

            <div className="card info-card">
              <h2>Progreso promedio</h2>
              <strong style={{ fontSize: "28px" }}>
                {kpis.progreso_promedio_grasa_30_dias != null
                  ? `${kpis.progreso_promedio_grasa_30_dias}% grasa`
                  : "Sin datos"}
              </strong>
              <p>Promedio de % de grasa registrado en los últimos 30 días.</p>
            </div>

            <div className="card info-card">
              <h2>Asistencias del mes</h2>
              <strong style={{ fontSize: "28px" }}>{kpis.asistencias_mes || 0}</strong>
              <p>{kpis.asistencias_hoy || 0} registradas hoy.</p>
            </div>
          </aside>
        </section>
      )}

      <section className="content-grid">
        <div className="table-card">
          <div className="card-header">
            <div>
              <h2>Ingresos de los últimos 7 días</h2>
              <p>Pagos de membresía registrados por día.</p>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={ingresosPorDia} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="fecha" />
              <YAxis allowDecimals={false} />
              <Tooltip formatter={(valor) => `S/ ${Number(valor).toFixed(2)}`} />
              <Line type="monotone" dataKey="monto" name="Ingresos (S/)" stroke="#ff8a3d" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="table-card">
          <div className="card-header">
            <div>
              <h2>Asistencias de los últimos 7 días</h2>
              <p>Cantidad de asistencias registradas por día.</p>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={asistenciasPorDia} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="fecha" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="cantidad" name="Asistencias" fill="#4dabf7" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="table-card">
          <div className="card-header">
            <div>
              <h2>Productos más vendidos</h2>
              <p>Este mes, por unidades vendidas.</p>
            </div>
          </div>

          {productosMasVendidos.length === 0 ? (
            <p className="empty-message">No hay ventas de productos registradas este mes.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={[...productosMasVendidos].sort((a, b) => b.cantidad_vendida - a.cantidad_vendida).slice(0, 5)}
                margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="producto" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="cantidad_vendida" name="Unidades vendidas" fill="#51cf66" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
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

          <div className="card info-card">
            <h2>Membresías por vencer</h2>
            <p>Activas que vencen en los próximos 7 días.</p>

            {membresiasPorVencer.length === 0 ? (
              <p className="empty-message">Sin membresías por vencer esta semana.</p>
            ) : (
              <div className="status-list">
                {membresiasPorVencer.map((m) => (
                  <span key={m.id_cliente_membresia}>
                    {obtenerNombreCliente(m.id_cliente)} —{" "}
                    {m.diasRestantes === 0 ? "vence hoy" : `${m.diasRestantes} día(s)`}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="card promo-card">
            <span className="badge">GLEYFORGYM</span>
            <h2>Gestión completa desde una sola plataforma</h2>
            <p>Administra GleyforGym con una experiencia moderna y ordenada.</p>
          </div>
        </aside>
      </section>

      <ToastFeedback toast={toast} onClose={cerrarToast} />
    </div>
  );
}

export default DashboardAdmin;