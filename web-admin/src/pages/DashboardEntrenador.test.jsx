import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DashboardEntrenador from "./DashboardEntrenador";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("DashboardEntrenador Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) {
        return Promise.resolve({ data: [{ id_cliente: 1, nombres: "Juan", apellidos: "Perez", objetivo: "HIPERTROFIA", nivel: "AVANZADO", estado: "ACTIVO" }] });
      }
      if (url.includes("/rutinas/")) {
        return Promise.resolve({ data: [{ id_rutina: 1, estado: "ACTIVA" }] });
      }
      if (url.includes("/progreso/")) {
        return Promise.resolve({ data: [{ id_progreso: 1 }] });
      }
      if (url.includes("/asistencias/")) {
        return Promise.resolve({ data: [{ id_asistencia: 1 }] });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders headers and trainer statistics and recent clients list", async () => {
    render(<DashboardEntrenador />);
    expect(screen.getByText("Panel del entrenador")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Clientes activos")).toBeDefined();
      expect(screen.getByText("Rutinas activas")).toBeDefined();
      expect(screen.getByText("Registros físicos")).toBeDefined();
      expect(screen.getByText("Asistencias registradas")).toBeDefined();
      expect(screen.getByText("Juan Perez")).toBeDefined();
      expect(screen.getByText("Objetivo: HIPERTROFIA")).toBeDefined();
      expect(screen.getByText("AVANZADO")).toBeDefined();
    });
  });
});
