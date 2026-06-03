import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import MisPagos from "./MisPagos";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockPagos = [
  {
    id_pago: 101,
    monto: 150,
    metodo_pago: "YAPE",
    fecha_pago: "2026-06-01",
    estado: "COMPLETADO",
    observacion: "Pago puntual",
  },
];

describe("MisPagos Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    localStorage.setItem("id_usuario", "10");

    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1 } });
      }
      if (url.includes("/pagos/cliente/")) {
        return Promise.resolve({ data: mockPagos });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders active user payment history list card", async () => {
    render(<MisPagos />);
    expect(screen.getByText("Historial de pagos")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("S/ 150.00")).toBeDefined();
      expect(screen.getByText("YAPE")).toBeDefined();
      expect(screen.getByText("Pago puntual")).toBeDefined();
    });
  });
});
