import React from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";

function NotFound() {
  return (
    <div className="public-page">
      <Navbar />

      <div className="page-container" style={{ textAlign: "center", paddingBlock: "60px" }}>
        <span className="badge">404</span>
        <h1>Página no encontrada</h1>
        <p>La dirección a la que intentas entrar no existe o fue movida.</p>
        <Link to="/" className="btn-primary" style={{ display: "inline-block", marginTop: "16px" }}>
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}

export default NotFound;
