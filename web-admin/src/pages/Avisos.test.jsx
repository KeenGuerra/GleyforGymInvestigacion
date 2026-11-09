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

  it("shows the event date for an EVENTO aviso", async () => {
    api.get.mockResolvedValue({
      data: [
        { id_aviso: 3, titulo: "Noche de retos", contenido: "Trae a un amigo", tipo: "EVENTO", fecha_evento: "2026-12-15", estado: "ACTIVO" },
      ],
    });

    render(
      <MemoryRouter>
        <Avisos />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Noche de retos")).toBeDefined();
      expect(screen.getByText(new Date("2026-12-15T00:00:00").toLocaleDateString("es-PE"))).toBeDefined();
    });
  });

  it("hides a past EVENTO and keeps a future one, sorted by closest date first", async () => {
    api.get.mockResolvedValue({
      data: [
        { id_aviso: 1, titulo: "Evento pasado", contenido: "Ya ocurrió", tipo: "EVENTO", fecha_evento: "2026-01-01", estado: "ACTIVO" },
        { id_aviso: 2, titulo: "Evento lejano", contenido: "En dos meses", tipo: "EVENTO", fecha_evento: "2027-01-15", estado: "ACTIVO" },
        { id_aviso: 3, titulo: "Evento cercano", contenido: "La próxima semana", tipo: "EVENTO", fecha_evento: "2026-11-15", estado: "ACTIVO" },
      ],
    });

    render(
      <MemoryRouter>
        <Avisos />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.queryByText("Evento pasado")).toBeNull();
      expect(screen.getByText("Evento cercano")).toBeDefined();
      expect(screen.getByText("Evento lejano")).toBeDefined();
    });

    const titulos = screen.getAllByText(/^Evento (cercano|lejano)$/).map((el) => el.textContent);
    expect(titulos).toEqual(["Evento cercano", "Evento lejano"]);
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
