import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Inicio from "./pages/Inicio";
import Login from "./pages/Login";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

import Dashboard from "./pages/Dashboard";
import Clientes from "./pages/Clientes";
import Usuarios from "./pages/Usuarios";
import Membresias from "./pages/Membresias";
import ClienteMembresias from "./pages/ClienteMembresias";
import Pagos from "./pages/Pagos";
import Asistencias from "./pages/Asistencias";
import Progreso from "./pages/Progreso";
import Ejercicios from "./pages/Ejercicios";
import Comidas from "./pages/Comidas";
import Rutinas from "./pages/Rutinas";
import DetalleRutina from "./pages/DetalleRutina";
import Nutricion from "./pages/Nutricion";
import MiPerfil from "./pages/MiPerfil";
import MiRutina from "./pages/MiRutina";
import MiNutricion from "./pages/MiNutricion";
import MiProgreso from "./pages/MiProgreso";
import MiMembresia from "./pages/MiMembresia";
import MisPagos from "./pages/MisPagos";
import DetalleCliente from "./pages/DetalleCliente";
import Categorias from "./pages/Categorias";
import Productos from "./pages/Productos";
import Proveedores from "./pages/Proveedores";
import Compras from "./pages/Compras";
import Inventario from "./pages/Inventario";
import Ventas from "./pages/Ventas";
import Tienda from "./pages/Tienda";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* RUTAS PÚBLICAS */}
        <Route path="/" element={<Inicio />} />
        <Route path="/login" element={<Login />} />
        <Route path="/tienda" element={<Tienda />} />

        {/* RUTAS PRIVADAS CON LAYOUT */}
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />

          {/* ADMIN */}
          <Route
            path="/usuarios"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Usuarios />
              </ProtectedRoute>
            }
          />

          <Route
            path="/membresias"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Membresias />
              </ProtectedRoute>
            }
          />

          <Route
            path="/cliente-membresias"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <ClienteMembresias />
              </ProtectedRoute>
            }
          />

          <Route
            path="/pagos"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Pagos />
              </ProtectedRoute>
            }
          />

          <Route
            path="/comidas"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <Comidas />
              </ProtectedRoute>
            }
          />

          <Route
            path="/nutricion"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <Nutricion />
              </ProtectedRoute>
            }
          />

          {/* COMERCIO - ADMIN */}
          <Route
            path="/categorias"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Categorias />
              </ProtectedRoute>
            }
          />

          <Route
            path="/productos"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Productos />
              </ProtectedRoute>
            }
          />

          <Route
            path="/proveedores"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Proveedores />
              </ProtectedRoute>
            }
          />

          <Route
            path="/compras"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Compras />
              </ProtectedRoute>
            }
          />

          <Route
            path="/inventario"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Inventario />
              </ProtectedRoute>
            }
          />

          <Route
            path="/ventas"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Ventas />
              </ProtectedRoute>
            }
          />

          {/* ADMIN Y ENTRENADOR */}
          <Route
            path="/clientes"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <Clientes />
              </ProtectedRoute>
            }
          />

          <Route
            path="/clientes/:id/detalle"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <DetalleCliente />
              </ProtectedRoute>
            }
          />

          <Route
            path="/asistencias"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <Asistencias />
              </ProtectedRoute>
            }
          />

          <Route
            path="/progreso"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <Progreso />
              </ProtectedRoute>
            }
          />

          <Route
            path="/ejercicios"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <Ejercicios />
              </ProtectedRoute>
            }
          />

          <Route
            path="/rutinas"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <Rutinas />
              </ProtectedRoute>
            }
          />

          {/* RUTAS COMPARTIDAS */}
          <Route
            path="/rutinas/:id/detalle"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR", "CLIENTE"]}>
                <DetalleRutina />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-perfil"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
                <MiPerfil />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-rutina"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
                <MiRutina />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-nutricion"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
                <MiNutricion />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-progreso"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
                <MiProgreso />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-membresia"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
                <MiMembresia />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mis-pagos"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
                <MisPagos />
              </ProtectedRoute>
            }
          />
        </Route>

        {/* RUTA NO ENCONTRADA */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}