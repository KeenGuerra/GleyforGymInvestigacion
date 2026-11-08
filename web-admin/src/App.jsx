import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Inicio from "./pages/Inicio";
import Login from "./pages/Login";
import Registro from "./pages/Registro";
import ResetPassword from "./pages/ResetPassword";
import VerificarCorreo from "./pages/VerificarCorreo";
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
import DetallePlanNutricional from "./pages/DetallePlanNutricional";
import RevisionIA from "./pages/RevisionIA";
import MiPerfil from "./pages/MiPerfil";
import MiRutina from "./pages/MiRutina";
import MiNutricion from "./pages/MiNutricion";
import MiProgreso from "./pages/MiProgreso";
import MiMembresia from "./pages/MiMembresia";
import HazteSocio from "./pages/HazteSocio";
import MisPagos from "./pages/MisPagos";
import DetalleCliente from "./pages/DetalleCliente";
import Categorias from "./pages/Categorias";
import Productos from "./pages/Productos";
import Proveedores from "./pages/Proveedores";
import Compras from "./pages/Compras";
import Inventario from "./pages/Inventario";
import Ventas from "./pages/Ventas";
import Tienda from "./pages/Tienda";
import Avisos from "./pages/Avisos";
import GestionAvisos from "./pages/GestionAvisos";
import Entrenadores from "./pages/Entrenadores";
import Auditoria from "./pages/Auditoria";
import Reportes from "./pages/Reportes";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* RUTAS PÚBLICAS */}
        <Route path="/" element={<Inicio />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/verificar-correo" element={<VerificarCorreo />} />
        <Route path="/tienda" element={<Tienda />} />
        <Route path="/avisos" element={<Avisos />} />

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
            path="/gestion-avisos"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <GestionAvisos />
              </ProtectedRoute>
            }
          />

          <Route
            path="/entrenadores"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Entrenadores />
              </ProtectedRoute>
            }
          />

          <Route
            path="/auditoria"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <Auditoria />
              </ProtectedRoute>
            }
          />

          <Route
            path="/reportes"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <Reportes />
              </ProtectedRoute>
            }
          />

          <Route
            path="/cliente-membresias"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "RECEPCIONISTA"]}>
                <ClienteMembresias />
              </ProtectedRoute>
            }
          />

          <Route
            path="/pagos"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "RECEPCIONISTA"]}>
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

          <Route
            path="/nutricion/:id/detalle"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <DetallePlanNutricional />
              </ProtectedRoute>
            }
          />

          <Route
            path="/revision-ia"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR"]}>
                <RevisionIA />
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
              <ProtectedRoute rolesPermitidos={["ADMIN", "RECEPCIONISTA"]}>
                <Ventas />
              </ProtectedRoute>
            }
          />

          {/* ADMIN Y ENTRENADOR */}
          <Route
            path="/clientes"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR", "RECEPCIONISTA"]}>
                <Clientes />
              </ProtectedRoute>
            }
          />

          <Route
            path="/clientes/:id/detalle"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR", "RECEPCIONISTA"]}>
                <DetalleCliente />
              </ProtectedRoute>
            }
          />

          <Route
            path="/asistencias"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN", "ENTRENADOR", "RECEPCIONISTA"]}>
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
              <ProtectedRoute rolesPermitidos={["CLIENTE"]} requiereCliente>
                <MiPerfil />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-rutina"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]} requiereCliente>
                <MiRutina />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-nutricion"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]} requiereCliente>
                <MiNutricion />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-progreso"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]} requiereCliente>
                <MiProgreso />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mi-membresia"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]} requiereCliente>
                <MiMembresia />
              </ProtectedRoute>
            }
          />

          <Route
            path="/hazte-socio"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
                <HazteSocio />
              </ProtectedRoute>
            }
          />

          <Route
            path="/mis-pagos"
            element={
              <ProtectedRoute rolesPermitidos={["CLIENTE"]} requiereCliente>
                <MisPagos />
              </ProtectedRoute>
            }
          />
        </Route>

        {/* RUTA NO ENCONTRADA */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}