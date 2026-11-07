import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import PropTypes from "prop-types";

export default function ProtectedRoute({ children, rolesPermitidos, requiereCliente }) {
  const location = useLocation();

  const token = localStorage.getItem("token");
  const rol = localStorage.getItem("rol");

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (rolesPermitidos && !rolesPermitidos.includes(rol)) {
    return <Navigate to="/dashboard" replace />;
  }

  // Páginas de socio (Mi perfil, Mi rutina, etc.): un comprador sin
  // membresía (cuenta de autoregistro público, ver POST /usuarios/registro)
  // no tiene perfil de Cliente y no debe poder llegar aquí ni escribiendo
  // la URL a mano, porque esas páginas asumen que sí existe.
  if (requiereCliente && localStorage.getItem("tiene_cliente") === "false") {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
  rolesPermitidos: PropTypes.arrayOf(PropTypes.string),
  requiereCliente: PropTypes.bool,
};