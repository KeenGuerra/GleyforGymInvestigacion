import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
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
});
