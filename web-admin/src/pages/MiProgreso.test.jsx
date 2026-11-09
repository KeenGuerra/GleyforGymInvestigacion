import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import MiProgreso from "./MiProgreso";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
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
              masa_grasa: 16,
              masa_magra: 64,
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
    expect(screen.getByText("Mi progreso físico")).toBeDefined();
    await waitFor(() => {
      expect(screen.getAllByText(/Peso/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/IMC/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Inicio/i).length).toBeGreaterThan(0);
    });
  });

  it("does not offer self-registration -- the client can only view, the staff registers it", async () => {
    render(<MiProgreso />);
    await waitFor(() => {
      expect(screen.getAllByText(/Peso/i).length).toBeGreaterThan(0);
    });

    expect(screen.queryByText("+ Nuevo registro")).toBeNull();
    expect(screen.queryByText("Guardar progreso")).toBeNull();
    expect(
      screen.getByText(/Tu entrenador registra tu peso, medidas y composición corporal/)
    ).toBeDefined();
  });

  it("shows the latest record's headline body-composition stats", async () => {
    render(<MiProgreso />);
    await waitFor(() => {
      expect(screen.getByText("Último registro")).toBeDefined();
    });

    expect(screen.getByText("20%")).toBeDefined();
    expect(screen.getByText("16 kg")).toBeDefined();
    expect(screen.getByText("64 kg")).toBeDefined();
  });

  it("shows the evolution chart when there is more than one record", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1, nombres: "Juan", peso: 80, estatura: 1.75 } });
      }
      if (url.includes("/progreso/cliente/")) {
        return Promise.resolve({
          data: [
            { id_progreso: 2, peso: 78, porcentaje_grasa: 18, fecha_registro: "2026-07-01", observacion: "Mes 2" },
            { id_progreso: 1, peso: 80, porcentaje_grasa: 20, fecha_registro: "2026-06-01", observacion: "Inicio" },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<MiProgreso />);
    await waitFor(() => {
      expect(screen.getByText("Evolución de tu progreso")).toBeDefined();
    });
  });

  it("shows an empty state pointing to the staff when there are no records yet", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1, nombres: "Juan", peso: 80, estatura: 1.75 } });
      }
      return Promise.resolve({ data: [] });
    });

    render(<MiProgreso />);
    await waitFor(() => {
      expect(screen.getByText("No tienes registros todavía")).toBeDefined();
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
