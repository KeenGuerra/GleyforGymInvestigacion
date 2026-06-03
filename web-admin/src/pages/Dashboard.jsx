import React from "react";
import DashboardAdmin from "./DashboardAdmin";
import DashboardEntrenador from "./DashboardEntrenador";
import DashboardCliente from "./DashboardCliente";

function Dashboard() {
  const rol = localStorage.getItem("rol");

  if (rol === "ADMIN") return <DashboardAdmin />;
  if (rol === "ENTRENADOR") return <DashboardEntrenador />;
  if (rol === "CLIENTE") return <DashboardCliente />;

  return (
    <div className="page-container">
      <section className="card empty-state">
        <span className="badge">ERROR DE ACCESO</span>

        <h1>No se pudo identificar el rol</h1>

        <p>
          Tu sesión no tiene un rol válido. Vuelve a iniciar sesión para acceder
          correctamente al panel de GleyforGym.
        </p>

        <button className="btn-primary" onClick={() => (globalThis.location.href = "/login")}>
          Volver al login
        </button>
      </section>
    </div>
  );
}

export default Dashboard;