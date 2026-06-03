import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DashboardCliente from "./DashboardCliente";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("DashboardCliente Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    localStorage.setItem("id_usuario", "10");

    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({
          data: {
            id_cliente: 1,
            nombres: "Juan",
            apellidos: "Perez",
            objetivo: "PERDIDA_PESO",
            nivel: "PRINCIPIANTE",
            peso: 80,
            estatura: 1.75,
            estado: "ACTIVO",
          },
        });
      }
      if (url.includes("/rutinas/cliente/")) {
        return Promise.resolve({ data: [{ id_rutina: 1, estado: "ACTIVA" }] });
      }
      if (url.includes("/nutricion/cliente/")) {
        return Promise.resolve({ data: [{ id_plan_nutricional: 1, estado: "ACTIVO" }] });
      }
      if (url.includes("/pagos/cliente/")) {
        return Promise.resolve({ data: [{ id_pago: 1, estado: "COMPLETADO" }] });
      }
      if (url.includes("/progreso/cliente/")) {
        return Promise.resolve({ data: [{ id_progreso: 1 }] });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders headers and loads client overview and profile stats", async () => {
    render(<DashboardCliente />);
    await waitFor(() => {
      expect(screen.getByText("Hola, Juan")).toBeDefined();
      expect(screen.getByText("Rutinas activas")).toBeDefined();
      expect(screen.getByText("Planes activos")).toBeDefined();
      expect(screen.getByText("Pagos registrados")).toBeDefined();
      expect(screen.getByText("Registros físicos")).toBeDefined();
      expect(screen.getByText("PERDIDA_PESO")).toBeDefined();
      expect(screen.getByText("PRINCIPIANTE")).toBeDefined();
    });
  });
});
