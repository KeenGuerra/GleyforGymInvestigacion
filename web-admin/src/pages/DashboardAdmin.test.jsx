import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DashboardAdmin from "./DashboardAdmin";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

vi.mock("react-router-dom", () => ({
  useNavigate: () => vi.fn(),
}));

describe("DashboardAdmin Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) {
        return Promise.resolve({ data: [{ id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO" }] });
      }
      if (url.includes("/cliente-membresias/")) {
        return Promise.resolve({ data: [{ id_cliente_membresia: 1, id_cliente: 1, estado: "ACTIVA" }] });
      }
      if (url.includes("/pagos/")) {
        return Promise.resolve({ data: [{ id_pago: 1, monto: 100, estado: "COMPLETADO" }] });
      }
      if (url.includes("/asistencias/")) {
        return Promise.resolve({ data: [{ id_asistencia: 1, id_cliente: 1, fecha: "2026-06-01" }] });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders headers and admin stats cards", async () => {
    render(<DashboardAdmin />);
    expect(screen.getByText("Panel de control")).toBeDefined();
    await waitFor(() => {
      expect(screen.getAllByText(/Clientes registrados/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Membresías activas/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Ingresos registrados/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Asistencias de hoy/i).length).toBeGreaterThan(0);
    });
  });
});
