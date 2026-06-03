import React, { useEffect, useState } from "react";
import api from "../api/api";

function DashboardCliente() {
  const [cliente, setCliente] = useState(null);
  const [rutinas, setRutinas] = useState([]);
  const [planes, setPlanes] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [progreso, setProgreso] = useState([]);

  const cargarDatos = async () => {
    try {
      const idUsuario = localStorage.getItem("id_usuario");

      const clienteRes = await api.get(`/clientes/usuario/${idUsuario}`);
      const clienteData = clienteRes.data;

      setCliente(clienteData);

      const idCliente = clienteData.id_cliente;

      const [rutinasRes, nutricionRes, pagosRes, progresoRes] =
        await Promise.all([
          api.get(`/rutinas/cliente/${idCliente}`),
          api.get(`/nutricion/cliente/${idCliente}`),
          api.get(`/pagos/cliente/${idCliente}`),
          api.get(`/progreso/cliente/${idCliente}`),
        ]);

      setRutinas(rutinasRes.data.filter((r) => r.estado !== "INACTIVA"));
      setPlanes(nutricionRes.data.filter((p) => p.estado !== "INACTIVO"));
      setPagos(pagosRes.data.filter((p) => p.estado !== "ANULADO"));
      setProgreso(progresoRes.data);
    } catch (error) {
      console.error("Error cargando dashboard cliente:", error);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">CLIENTE</span>
          <h1>Hola, {cliente ? cliente.nombres : "cliente"}</h1>
          <p>Este es el resumen de tu entrenamiento, nutrición y progreso.</p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Rutinas activas</span>
          <strong>{rutinas.length}</strong>
        </div>

        <div className="stat-card">
          <span>Planes activos</span>
          <strong>{planes.length}</strong>
        </div>

        <div className="stat-card">
          <span>Pagos registrados</span>
          <strong>{pagos.length}</strong>
        </div>

        <div className="stat-card">
          <span>Registros físicos</span>
          <strong>{progreso.length}</strong>
        </div>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Mi información</h2>
            <p>Datos principales usados para personalizar tus rutinas y planes.</p>
          </div>
        </div>

        {cliente ? (
          <div className="details-grid">
            <div>
              <span>Nombre</span>
              <strong>
                {cliente.nombres} {cliente.apellidos}
              </strong>
            </div>

            <div>
              <span>Objetivo</span>
              <strong>{cliente.objetivo || "No definido"}</strong>
            </div>

            <div>
              <span>Nivel</span>
              <strong>{cliente.nivel || "No definido"}</strong>
            </div>

            <div>
              <span>Peso</span>
              <strong>{cliente.peso || "-"} kg</strong>
            </div>

            <div>
              <span>Estatura</span>
              <strong>{cliente.estatura || "-"} m</strong>
            </div>

            <div>
              <span>Estado</span>
              <strong>
                <span className="badge">{cliente.estado || "ACTIVO"}</span>
              </strong>
            </div>
          </div>
        ) : (
          <p className="empty-message">Cargando información del cliente...</p>
        )}
      </section>
    </div>
  );
}

export default DashboardCliente;