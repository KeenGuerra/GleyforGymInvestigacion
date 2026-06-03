import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import MiMembresia from "./MiMembresia";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
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
            },
          ],
        });
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
});
