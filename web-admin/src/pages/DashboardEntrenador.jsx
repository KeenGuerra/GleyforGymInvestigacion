import React, { useEffect, useState } from "react";
import api from "../api/api";

function DashboardEntrenador() {
  const [clientes, setClientes] = useState([]);
  const [rutinas, setRutinas] = useState([]);
  const [progreso, setProgreso] = useState([]);
  const [asistencias, setAsistencias] = useState([]);

  const cargarDatos = async () => {
    try {
      const [clientesRes, rutinasRes, progresoRes, asistenciasRes] =
        await Promise.all([
          api.get("/clientes/"),
          api.get("/rutinas/"),
          api.get("/progreso/"),
          api.get("/asistencias/"),
        ]);

      setClientes(clientesRes.data.filter((c) => c.estado === "ACTIVO"));
      setRutinas(rutinasRes.data.filter((r) => r.estado !== "INACTIVA"));
      setProgreso(progresoRes.data);
      setAsistencias(asistenciasRes.data);
    } catch (error) {
      console.error("Error cargando dashboard entrenador:", error);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">ENTRENADOR</span>
          <h1>Panel del entrenador</h1>
          <p>Seguimiento deportivo de clientes, rutinas, asistencias y progreso.</p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Clientes activos</span>
          <strong>{clientes.length}</strong>
        </div>

        <div className="stat-card">
          <span>Rutinas activas</span>
          <strong>{rutinas.length}</strong>
        </div>

        <div className="stat-card">
          <span>Registros físicos</span>
          <strong>{progreso.length}</strong>
        </div>

        <div className="stat-card">
          <span>Asistencias registradas</span>
          <strong>{asistencias.length}</strong>
        </div>
      </section>

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Clientes recientes</h2>
            <p>Vista rápida de los últimos clientes activos registrados.</p>
          </div>
        </div>

        {clientes.length === 0 ? (
          <p className="empty-message">
            No hay clientes activos registrados.
          </p>
        ) : (
          <div className="list">
            {clientes.slice(0, 5).map((cliente) => (
              <div className="list-item" key={cliente.id_cliente}>
                <div className="user-info">
                  <div className="profile-avatar">
                    {`${cliente.nombres} ${cliente.apellidos}`
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .substring(0, 2)
                      .toUpperCase()}
                  </div>

                  <div>
                    <strong>
                      {cliente.nombres} {cliente.apellidos}
                    </strong>
                    <span>
                      Objetivo: {cliente.objetivo || "No definido"}
                    </span>
                  </div>
                </div>

                <span className="badge">
                  {cliente.nivel || "Sin nivel"}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default DashboardEntrenador;