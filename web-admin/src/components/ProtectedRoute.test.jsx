import React from "react";
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";

describe("ProtectedRoute Component", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders children if authorized with correct role", () => {
    localStorage.setItem("token", "fake-token");
    localStorage.setItem("rol", "ADMIN");

    render(
      <MemoryRouter initialEntries={["/admin"]}>
        <Routes>
          <Route
            path="/admin"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <div>Contenido Protegido</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText("Contenido Protegido")).toBeDefined();
  });

  it("renders children if token is present and no rolesPermitidos is specified", () => {
    localStorage.setItem("token", "fake-token");
    localStorage.setItem("rol", "CLIENTE");

    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>Dashboard General</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText("Dashboard General")).toBeDefined();
  });

  it("redirects to /login if token is missing", () => {
    render(
      <MemoryRouter initialEntries={["/admin"]}>
        <Routes>
          <Route
            path="/admin"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <div>Contenido Protegido</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Página de Login</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText("Página de Login")).toBeDefined();
  });

  it("redirects to /dashboard if token is present but user role is unauthorized", () => {
    localStorage.setItem("token", "fake-token");
    localStorage.setItem("rol", "CLIENTE");

    render(
      <MemoryRouter initialEntries={["/admin"]}>
        <Routes>
          <Route
            path="/admin"
            element={
              <ProtectedRoute rolesPermitidos={["ADMIN"]}>
                <div>Contenido Protegido</div>
              </ProtectedRoute>
            }
          />
          <Route path="/dashboard" element={<div>Dashboard de Cliente</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText("Dashboard de Cliente")).toBeDefined();
  });
});
