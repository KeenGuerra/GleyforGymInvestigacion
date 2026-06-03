import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Asistencias from "./Asistencias";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockClientes = [
  { id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO" },
];

const mockAsistencias = [
  {
    id_asistencia: 10,
    id_cliente: 1,
    fecha: "2026-06-01",
    hora_entrada: "08:00",
    hora_salida: "09:30",
    observacion: "Todo excelente",
  },
];

describe("Asistencias Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/asistencias/")) {
        return Promise.resolve({ data: mockAsistencias });
      }
      if (url.includes("/clientes/")) {
        return Promise.resolve({ data: mockClientes });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders headers and loads asistencias table list", async () => {
    render(<Asistencias />);
    expect(screen.getByText("Gestión de asistencias")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Total de registros")).toBeDefined();
      expect(screen.getByText("Todo excelente")).toBeDefined();
    });
  });

  it("allows search filtering on list", async () => {
    render(<Asistencias />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar por cliente, fecha u observación...")).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText("Buscar por cliente, fecha u observación...");
    fireEvent.change(searchInput, { target: { value: "Ninguna coincidencia" } });

    await waitFor(() => {
      expect(screen.queryByText("Todo excelente")).toBeNull();
    });
  });

  it("shows form and calls post on submitting new entry", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Asistencias />);

    await waitFor(() => {
      expect(screen.getByText("+ Registrar asistencia")).toBeDefined();
    });

    fireEvent.click(screen.getByText("+ Registrar asistencia"));

    await waitFor(() => {
      expect(screen.getByText("Registrar asistencia", { selector: "h2" })).toBeDefined();
    });

    // select client
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Hora entrada"), { target: { value: "08:00" } });
    fireEvent.change(screen.getByLabelText("Observación"), { target: { value: "Entrenamiento completado" } });

    fireEvent.click(screen.getByText("Guardar asistencia"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
  });

  it("enters edit mode, updates exit time and submits the form", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Asistencias />);

    await waitFor(() => {
      expect(screen.getByText("Editar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Editar"));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Editar asistencia" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Hora salida"), { target: { value: "11:00" } });
    fireEvent.click(screen.getByText("Actualizar asistencia"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalled();
    });
  });

  it("deletes an assistance on confirmation successfully", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Asistencias />);
    await waitFor(() => {
      expect(screen.getByText("Eliminar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Eliminar"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/asistencias/10");
    });
  });

  it("handles delete failure on confirmation", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockRejectedValue(new Error("Delete Error"));

    render(<Asistencias />);
    await waitFor(() => {
      expect(screen.getByText("Eliminar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Eliminar"));

    await waitFor(() => {
      expect(screen.getByText("Error al eliminar asistencia")).toBeDefined();
    });
  });

  it("does not delete if confirmation is cancelled", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    render(<Asistencias />);

    await waitFor(() => {
      expect(screen.getByText("Eliminar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Eliminar"));
    expect(api.delete).not.toHaveBeenCalled();
  });
});
