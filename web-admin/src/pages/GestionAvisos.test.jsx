import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import GestionAvisos from "./GestionAvisos";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockAvisos = [
  { id_aviso: 1, titulo: "Deyvi", contenido: "Lun-Vie", tipo: "COACHES", estado: "ACTIVO" },
];

describe("GestionAvisos Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockAvisos });
  });

  it("renders the avisos list", async () => {
    render(<GestionAvisos />);
    expect(screen.getByText("Gestión de avisos")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Deyvi")).toBeDefined();
    });
  });

  it("shows the event date for EVENTO avisos and a dash for the rest", async () => {
    api.get.mockResolvedValue({
      data: [
        ...mockAvisos,
        { id_aviso: 2, titulo: "Noche de retos", contenido: "Trae a un amigo", tipo: "EVENTO", fecha_evento: "2026-12-15", estado: "ACTIVO" },
      ],
    });
    render(<GestionAvisos />);

    await waitFor(() => {
      expect(screen.getByText("Noche de retos")).toBeDefined();
    });

    const filaEvento = screen.getByText("Noche de retos").closest("tr");
    expect(within(filaEvento).getByText(new Date("2026-12-15").toLocaleDateString("es-PE"))).toBeDefined();

    const filaSinFecha = screen.getByText("Deyvi").closest("tr");
    expect(within(filaSinFecha).getByText("—")).toBeDefined();
  });

  it("marks a past EVENTO as 'Pasado' but not a future one", async () => {
    api.get.mockResolvedValue({
      data: [
        { id_aviso: 3, titulo: "Evento pasado", contenido: "Ya ocurrió", tipo: "EVENTO", fecha_evento: "2026-01-01", estado: "ACTIVO" },
        { id_aviso: 4, titulo: "Evento futuro", contenido: "Próximamente", tipo: "EVENTO", fecha_evento: "2026-12-15", estado: "ACTIVO" },
      ],
    });
    render(<GestionAvisos />);

    await waitFor(() => {
      expect(screen.getByText("Evento pasado")).toBeDefined();
    });

    const filaPasado = screen.getByText("Evento pasado").closest("tr");
    expect(within(filaPasado).getByText("Pasado")).toBeDefined();

    const filaFuturo = screen.getByText("Evento futuro").closest("tr");
    expect(within(filaFuturo).queryByText("Pasado")).toBeNull();
  });

  it("creates a new aviso", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<GestionAvisos />);

    fireEvent.click(screen.getByText("+ Nuevo aviso"));
    await waitFor(() => expect(screen.getByLabelText("Título")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Título"), { target: { value: "Nuevo horario" } });
    fireEvent.change(screen.getByLabelText("Contenido"), { target: { value: "9am - 6pm" } });
    fireEvent.click(screen.getByText("Guardar aviso"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/avisos/", expect.objectContaining({
        titulo: "Nuevo horario",
        contenido: "9am - 6pm",
      }));
    });
  });

  it("shows validation error when title is missing", async () => {
    render(<GestionAvisos />);
    fireEvent.click(screen.getByText("+ Nuevo aviso"));
    await waitFor(() => expect(screen.getByText("Guardar aviso")).toBeDefined());

    fireEvent.click(screen.getByText("Guardar aviso"));

    await waitFor(() => {
      expect(screen.getByText("Ingrese el título del aviso")).toBeDefined();
    });
  });

  it("deactivates an aviso after confirmation", async () => {
    globalThis.confirm = vi.fn(() => true);
    api.delete.mockResolvedValue({ data: {} });

    render(<GestionAvisos />);
    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());

    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/avisos/1");
    });
  });

  it("shows an Activar button instead of Desactivar for an INACTIVO aviso, and reactivates it", async () => {
    api.get.mockResolvedValue({ data: [{ ...mockAvisos[0], estado: "INACTIVO" }] });
    api.put.mockResolvedValue({ data: {} });

    render(<GestionAvisos />);
    await waitFor(() => expect(screen.getByText("Activar")).toBeDefined());
    expect(screen.queryByText("Desactivar")).toBeNull();

    fireEvent.click(screen.getByText("Activar"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/avisos/1", { estado: "ACTIVO" });
    });
  });
});
