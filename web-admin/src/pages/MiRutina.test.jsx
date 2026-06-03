import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MiRutina from "./MiRutina";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

describe("MiRutina Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    localStorage.setItem("id_usuario", "10");

    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1, nombres: "Juan" } });
      }
      if (url.includes("/rutinas/cliente/")) {
        return Promise.resolve({
          data: [
            {
              id_rutina: 15,
              nombre: "Hipertrofia de hombros",
              objetivo: "HIPERTROFIA",
              nivel: "AVANZADO",
              dias_semana: 4,
              fecha_creacion: "2026-06-01",
              generada_por_ia: false,
              estado: "ACTIVA",
            },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders active routines and navigates to details on button click", async () => {
    render(<MiRutina />);
    await waitFor(() => {
      expect(screen.getByText("Hola Juan, aquí puedes revisar tus rutinas asignadas.")).toBeDefined();
      expect(screen.getByText("Hipertrofia de hombros")).toBeDefined();
      expect(screen.getByText("Ver detalle con videos")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Ver detalle con videos"));
    expect(mockNavigate).toHaveBeenCalledWith("/rutinas/15/detalle");
  });
});
