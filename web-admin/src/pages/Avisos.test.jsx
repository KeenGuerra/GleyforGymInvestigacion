import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Avisos from "./Avisos";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("Avisos Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders avisos grouped by tipo from the API", async () => {
    api.get.mockResolvedValue({
      data: [
        { id_aviso: 1, titulo: "Lunes a Sábado", contenido: "6am - 10pm", tipo: "HORARIO", estado: "ACTIVO" },
        { id_aviso: 2, titulo: "Deyvi", contenido: "Lun-Vie", tipo: "COACHES", estado: "ACTIVO" },
      ],
    });

    render(
      <MemoryRouter>
        <Avisos />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Horario de atención")).toBeDefined();
      expect(screen.getByText("Nuestros coaches")).toBeDefined();
      expect(screen.getByText("Lunes a Sábado")).toBeDefined();
      expect(screen.getByText("Deyvi")).toBeDefined();
    });
  });

  it("shows an empty message when there are no avisos", async () => {
    api.get.mockResolvedValue({ data: [] });

    render(
      <MemoryRouter>
        <Avisos />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("No hay avisos publicados por el momento.")).toBeDefined();
    });
  });

  it("shows an error message when the API call fails", async () => {
    api.get.mockRejectedValue(new Error("network error"));

    render(
      <MemoryRouter>
        <Avisos />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("No se pudieron cargar los avisos.")).toBeDefined();
    });
  });
});
