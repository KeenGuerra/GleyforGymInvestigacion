import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import MiMembresia from "./MiMembresia";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe("MiMembresia Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    localStorage.setItem("id_usuario", "10");

    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1 } });
      }
      if (url.includes("/cliente-membresias/cliente/")) {
        return Promise.resolve({
          data: [
            {
              id_cliente_membresia: 1,
              id_membresia: 5,
              precio_asignado: 120,
              fecha_inicio: "2026-06-01",
              fecha_fin: "2026-09-01",
              estado: "ACTIVA",
            },
          ],
        });
      }
      if (url.includes("/membresias/")) {
        return Promise.resolve({
          data: [
            {
              id_membresia: 5,
              nombre: "Plan Fuerza Semestral",
              estado: "ACTIVO",
            },
          ],
        });
      }
      if (url.includes("/pagos/cliente/")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders active membership info card", async () => {
    render(<MiMembresia />);
    await waitFor(() => {
      expect(screen.getAllByText(/Plan Fuerza Semestral/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/120\.00/i).length).toBeGreaterThan(0);
      expect(screen.getByText("Días restantes")).toBeDefined();
      expect(screen.getByText("ACTIVA")).toBeDefined();
    });
  });

  it("shows no 'comprar' option while a membership is already active", async () => {
    render(<MiMembresia />);
    await waitFor(() => {
      expect(screen.getAllByText(/Plan Fuerza Semestral/i).length).toBeGreaterThan(0);
    });
    expect(screen.queryByText("Elige un plan")).toBeNull();
  });

  it("offers available plans and lets the client buy one when there is no active membership", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1 } });
      }
      if (url.includes("/cliente-membresias/cliente/")) {
        return Promise.resolve({ data: [] });
      }
      if (url.includes("/membresias/")) {
        return Promise.resolve({
          data: [{
            id_membresia: 7, nombre: "Plan Mensual", precio: 100, duracion_dias: 30, estado: "ACTIVO",
            beneficios: "Pesas, Cardio, Sauna",
          }],
        });
      }
      if (url.includes("/pagos/cliente/")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({ data: [] });
    });
    api.post.mockResolvedValue({ data: { id_pago: 9, id_cliente_membresia: 2, estado: "PENDIENTE" } });

    render(<MiMembresia />);
    await waitFor(() => {
      expect(screen.getByText("Plan Mensual")).toBeDefined();
      expect(screen.getByText("Pesas, Cardio, Sauna")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Comprar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/cliente-membresias/comprar", { id_membresia: 7 });
    });
  });

  it("shows a 'completar pago' button that opens the checkout modal when a payment is pending", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1 } });
      }
      if (url.includes("/cliente-membresias/cliente/")) {
        return Promise.resolve({
          data: [
            {
              id_cliente_membresia: 2,
              id_membresia: 7,
              precio_asignado: 100,
              fecha_inicio: "2026-06-01",
              fecha_fin: "2026-06-01",
              estado: "PENDIENTE",
            },
          ],
        });
      }
      if (url.includes("/membresias/")) {
        return Promise.resolve({
          data: [{ id_membresia: 7, nombre: "Plan Mensual", precio: 100, duracion_dias: 30, estado: "ACTIVO" }],
        });
      }
      if (url.includes("/pagos/cliente/")) {
        return Promise.resolve({
          data: [{ id_pago: 9, id_cliente_membresia: 2, estado: "PENDIENTE", monto: 100 }],
        });
      }
      return Promise.resolve({ data: [] });
    });
    api.post.mockResolvedValue({
      data: { id_pago: 9, url_checkout: "https://pago.simulado/9", qr_yape: null },
    });

    render(<MiMembresia />);
    await waitFor(() => {
      expect(screen.getByText("Completar pago")).toBeDefined();
    });

    // El historial de abajo también lista la membresía PENDIENTE (misma
    // compra, por si el Pago asociado llegara a faltar) pero no debe mostrar
    // fechas/días restantes falsos -- fecha_inicio/fecha_fin son solo un
    // placeholder ("hoy") hasta que el webhook confirme el pago.
    expect(screen.getAllByText("Por confirmar").length).toBe(2);
    expect(screen.queryByText("Días restantes")).toBeNull();

    fireEvent.click(screen.getByText("Completar pago"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/pagos/9/checkout");
      expect(screen.getByText("Pagar con PagoEfectivo")).toBeDefined();
    });
  });
});
