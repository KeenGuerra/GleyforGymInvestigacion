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

  it("shows a membership expiring soon in the alert card", async () => {
    const hoy = new Date();
    const enTresDias = new Date(hoy.getTime() + 3 * 24 * 60 * 60 * 1000)
      .toISOString()
      .slice(0, 10);

    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) {
        return Promise.resolve({ data: [{ id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO" }] });
      }
      if (url.includes("/cliente-membresias/")) {
        return Promise.resolve({
          data: [{ id_cliente_membresia: 1, id_cliente: 1, estado: "ACTIVA", fecha_fin: enTresDias }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<DashboardAdmin />);

    await waitFor(() => {
      expect(screen.getByText("Membresías por vencer")).toBeDefined();
      expect(screen.getByText(/Juan Perez — 3 día\(s\)/)).toBeDefined();
    });
  });

  it("shows the empty message when no membership is expiring soon", async () => {
    render(<DashboardAdmin />);

    await waitFor(() => {
      expect(screen.getByText("Sin membresías por vencer esta semana.")).toBeDefined();
    });
  });

  it("renders the KPI chart panel when /reportes/kpis returns data", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/reportes/kpis")) {
        return Promise.resolve({
          data: {
            clientes_activos: 12,
            recaudacion_mes_actual: 450.5,
            rutinas_generadas_ia: 7,
            progreso_promedio_grasa_30_dias: 18.4,
          },
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<DashboardAdmin />);

    await waitFor(() => {
      expect(screen.getByText("KPIs del gimnasio")).toBeDefined();
      expect(screen.getByText("S/ 450.50")).toBeDefined();
      expect(screen.getByText("18.4% grasa")).toBeDefined();
    });
  });

  it("shows a toast when loading the dashboard fails", async () => {
    api.get.mockRejectedValue(new Error("network error"));

    render(<DashboardAdmin />);

    await waitFor(() => {
      expect(screen.getByText("No se pudo cargar el dashboard.")).toBeDefined();
    });
  });
});
