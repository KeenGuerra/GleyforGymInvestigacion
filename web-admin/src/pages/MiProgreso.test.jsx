import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MiProgreso from "./MiProgreso";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
  },
}));

describe("MiProgreso Page Component", () => {
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
            peso: 80,
            estatura: 1.75,
          },
        });
      }
      if (url.includes("/progreso/cliente/")) {
        return Promise.resolve({
          data: [
            {
              id_progreso: 1,
              peso: 80,
              porcentaje_grasa: 20,
              fecha_registro: "2026-06-01",
              observacion: "Inicio",
            },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders progress headers, stats and historical table", async () => {
    render(<MiProgreso />);
    expect(screen.getByText("Actualizar progreso")).toBeDefined();
    await waitFor(() => {
      expect(screen.getAllByText(/Peso/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/IMC/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Inicio/i).length).toBeGreaterThan(0);
    });
  });

  it("shows form and calls post/put on saving new progress entry", async () => {
    api.post.mockResolvedValue({ data: {} });
    api.put.mockResolvedValue({ data: {} });
    render(<MiProgreso />);

    await waitFor(() => {
      expect(screen.getByText("+ Nuevo registro")).toBeDefined();
    });

    fireEvent.click(screen.getByText("+ Nuevo registro"));

    await waitFor(() => {
      expect(screen.getByText("Nuevo registro", { selector: "h2" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText(/Peso actual/i), { target: { value: "85" } });
    fireEvent.change(screen.getByLabelText(/Observación/i), { target: { value: "Aumento fuerza" } });

    fireEvent.click(screen.getByText("Guardar progreso", { selector: "button" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
      expect(api.put).toHaveBeenCalled();
    });
  });

  it("triggers change on right leg measurement, registration date and handles save error", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "Failed to save progress" } }
    });
    render(<MiProgreso />);

    await waitFor(() => {
      expect(screen.getByText("+ Nuevo registro")).toBeDefined();
    });

    fireEvent.click(screen.getByText("+ Nuevo registro"));

    await waitFor(() => {
      expect(screen.getByLabelText(/Pierna derecha/i)).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText(/Peso actual/i), { target: { value: "85" } });
    fireEvent.change(screen.getByLabelText(/Pierna derecha/i), { target: { value: "56.5" } });
    fireEvent.change(screen.getByLabelText(/Fecha de registro/i), { target: { value: "2026-06-02" } });

    fireEvent.click(screen.getByText("Guardar progreso", { selector: "button" }));

    await waitFor(() => {
      expect(screen.getByText("Failed to save progress")).toBeDefined();
    });
  });

  it("handles client progress load failure", async () => {
    api.get.mockRejectedValue(new Error("Load Error"));
    render(<MiProgreso />);

    await waitFor(() => {
      expect(screen.getByText("No se pudo cargar tu progreso.")).toBeDefined();
    });
  });
});
