import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

function DashboardComprador() {
  const navigate = useNavigate();
  const correo = localStorage.getItem("correo");
  const [pedidos, setPedidos] = useState([]);

  useEffect(() => {
    api
      .get("/ventas/mis-pedidos")
      .then((res) => setPedidos(res.data))
      .catch((error) => console.error("Error cargando pedidos:", error));
  }, []);

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">CUENTA DE COMPRAS</span>
          <h1>Hola, {correo || "cliente"}</h1>
          <p>
            Tu cuenta es solo para comprar en la tienda — no estás inscrito
            como socio del gimnasio todavía.
          </p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Pedidos realizados</span>
          <strong>{pedidos.length}</strong>
        </div>
      </section>

      <section className="quick-actions-grid">
        <button className="card quick-action" onClick={() => navigate("/tienda")}>
          <span>🛒</span>
          <strong>Ir a la tienda</strong>
        </button>
      </section>

      <section className="info-card card">
        <span className="badge">¿Quieres ser socio?</span>
        <h2>Accede a rutinas, plan nutricional y más</h2>
        <p>
          Completa tus datos de socio y elige un plan de membresía — tu
          cuenta actual seguirá funcionando igual, solo se le suman esas
          funciones.
        </p>
        <button className="btn-primary" onClick={() => navigate("/hazte-socio")}>
          Hazte socio ahora
        </button>
      </section>
    </div>
  );
}

export default DashboardComprador;
