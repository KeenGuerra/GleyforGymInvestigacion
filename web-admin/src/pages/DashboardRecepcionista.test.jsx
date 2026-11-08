import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DashboardRecepcionista from "./DashboardRecepcionista";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const hoy = new Date().toISOString().slice(0, 10);

describe("DashboardRecepcionista Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) {
        return Promise.resolve({ data: [{ id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO" }] });
      }
      if (url.includes("/asistencias/")) {
        return Promise.resolve({
          data: [{ id_asistencia: 1, id_cliente: 1, fecha: hoy, hora_entrada: "08:00", hora_salida: null, estado: "ACTIVO" }],
        });
      }
      if (url.includes("/pagos/")) {
        return Promise.resolve({ data: [{ id_pago: 1, fecha_pago: hoy, monto: 50, estado: "PAGADO" }] });
      }
      if (url.includes("/ventas/resumen")) {
        return Promise.resolve({ data: { ventas_hoy: 3, ingresos_hoy: 120 } });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders the header, front-desk stats and today's attendance list", async () => {
    render(<DashboardRecepcionista />);
    expect(screen.getByText("Panel de recepción")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Clientes activos")).toBeDefined();
      expect(screen.getAllByText("Asistencias de hoy").length).toBeGreaterThan(0);
      expect(screen.getByText((_, el) => el.tagName === "STRONG" && el.textContent === "S/ 50.00")).toBeDefined();
      expect(screen.getByText("3")).toBeDefined();
      expect(screen.getByText("Cliente #1")).toBeDefined();
      expect(screen.getByText("En gimnasio")).toBeDefined();
    });
  });

  it("shows a toast when loading the dashboard fails", async () => {
    api.get.mockRejectedValue(new Error("network error"));

    render(<DashboardRecepcionista />);

    await waitFor(() => {
      expect(screen.getByText("No se pudo cargar el dashboard.")).toBeDefined();
    });
  });
});
