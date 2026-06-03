import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ClienteMembresias from "./ClienteMembresias";
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
  { id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO", dni: "12345678" },
];

const mockMembresias = [
  { id_membresia: 5, nombre: "Plan Oro", duracion_dias: 90, precio: 150, estado: "ACTIVO" },
];

const mockAsignaciones = [
  {
    id_cliente_membresia: 12,
    id_cliente: 1,
    id_membresia: 5,
    fecha_inicio: "2026-06-01",
    fecha_fin: "2026-09-01",
    estado: "ACTIVA",
    precio_asignado: 150,
  },
];

describe("ClienteMembresias Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/cliente-membresias/")) {
        return Promise.resolve({ data: mockAsignaciones });
      }
      if (url.includes("/clientes/")) {
        return Promise.resolve({ data: mockClientes });
      }
      if (url.includes("/membresias/")) {
        return Promise.resolve({ data: mockMembresias });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders header and lists assigned memberships", async () => {
    render(<ClienteMembresias />);
    expect(screen.getByText("Asignar membresías")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText(/Juan Perez/)).toBeDefined();
      expect(screen.getByText(/Plan Oro/)).toBeDefined();
    });
  });

  it("fails validation for missing fields during assignment", async () => {
    render(<ClienteMembresias />);
    fireEvent.click(screen.getByText("+ Nueva asignación"));

    await waitFor(() => {
      expect(screen.getAllByText(/Juan Perez/i).length).toBeGreaterThan(1);
      expect(screen.getAllByText(/Plan Oro/i).length).toBeGreaterThan(1);
    });

    // 1. Missing client
    fireEvent.click(screen.getByRole("button", { name: "Asignar membresía" }));
    await waitFor(() => {
      expect(screen.getByText("Seleccione un cliente")).toBeDefined();
    });

    // Select client
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });

    // 2. Missing membership
    fireEvent.click(screen.getByRole("button", { name: "Asignar membresía" }));
    await waitFor(() => {
      expect(screen.getByText("Seleccione una membresía")).toBeDefined();
    });
  });

  it("calculates end date and submits a new assignment successfully", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<ClienteMembresias />);

    fireEvent.click(screen.getByText("+ Nueva asignación"));

    await waitFor(() => {
      expect(screen.getAllByText(/Juan Perez/i).length).toBeGreaterThan(1);
      expect(screen.getAllByText(/Plan Oro/i).length).toBeGreaterThan(1);
    });

    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Membresía"), { target: { value: "5" } });

    const fechaFinInput = screen.getByLabelText("Fecha fin");
    await waitFor(() => {
      expect(fechaFinInput.value).not.toBe("");
    });

    fireEvent.click(screen.getByRole("button", { name: "Asignar membresía" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
  });

  it("enters edit mode and updates assignment via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<ClienteMembresias />);

    await waitFor(() => {
      expect(screen.getByText("Editar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Editar"));

    // Title should change
    expect(screen.getByRole("heading", { name: "Editar asignación" })).toBeDefined();

    // Select a different status
    fireEvent.change(screen.getByLabelText("Estado"), { target: { value: "PAUSADA" } });

    fireEvent.click(screen.getByRole("button", { name: "Actualizar asignación" }));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/cliente-membresias/12", {
        id_membresia: 5,
        fecha_inicio: "2026-06-01",
        estado: "PAUSADA",
      });
    });
  });

  it("pauses and reactivates a membership on confirm", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.put.mockResolvedValue({ data: {} });
    render(<ClienteMembresias />);

    await waitFor(() => {
      expect(screen.getByText("Pausar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Pausar"));

    expect(globalThis.confirm).toHaveBeenCalled();
    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/cliente-membresias/12", {
        estado: "PAUSADA",
      });
    });
  });

  it("cancels assignment on confirm", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });
    render(<ClienteMembresias />);

    await waitFor(() => {
      expect(screen.getByText("Cancelar", { selector: "button" })).toBeDefined();
    });

    fireEvent.click(screen.getByText("Cancelar", { selector: "button" }));

    expect(globalThis.confirm).toHaveBeenCalled();
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/cliente-membresias/12");
    });
  });

  it("does not cancel or change state if confirmation is rejected", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    render(<ClienteMembresias />);

    await waitFor(() => {
      expect(screen.getByText("Pausar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Pausar"));
    expect(api.put).not.toHaveBeenCalled();
  });

  it("shows error if loading fails", async () => {
    api.get.mockRejectedValue(new Error("Loading Error"));
    render(<ClienteMembresias />);

    await waitFor(() => {
      expect(screen.getByText("Error al cargar datos")).toBeDefined();
    });
  });

  it("renders correct badge classes based on status and covers save errors", async () => {
    api.put.mockRejectedValue({
      response: { data: { detail: "Failed to update membership status" } }
    });
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));

    render(<ClienteMembresias />);
    await waitFor(() => {
      expect(screen.getByText("Pausar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Pausar"));

    await waitFor(() => {
      expect(screen.getByText("Error al cambiar estado de la membresía")).toBeDefined();
    });
  });

  it("renders other membership statuses like TERMINADA, CANCELADA, OTRO", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/cliente-membresias/")) {
        return Promise.resolve({
          data: [
            { id_cliente_membresia: 20, id_cliente: 1, id_membresia: 5, fecha_inicio: "2026-06-01", fecha_fin: "2026-09-01", estado: "TERMINADA" },
            { id_cliente_membresia: 21, id_cliente: 1, id_membresia: 5, fecha_inicio: "2026-06-01", fecha_fin: "2026-09-01", estado: "CANCELADA" },
            { id_cliente_membresia: 22, id_cliente: 1, id_membresia: 5, fecha_inicio: "2026-06-01", fecha_fin: "2026-09-01", estado: "OTRO_ESTADO" },
          ]
        });
      }
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/membresias/")) return Promise.resolve({ data: mockMembresias });
      return Promise.resolve({ data: [] });
    });

    render(<ClienteMembresias />);
    await waitFor(() => {
      expect(screen.getByText("TERMINADA")).toBeDefined();
      expect(screen.getByText("CANCELADA")).toBeDefined();
      expect(screen.getByText("OTRO_ESTADO")).toBeDefined();
    });
  });

  it("shows error if membership assignment creation fails", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "Cliente ya tiene membresía activa" } }
    });
    render(<ClienteMembresias />);
    fireEvent.click(screen.getByText("+ Nueva asignación"));

    await waitFor(() => {
      expect(screen.getByLabelText("Cliente")).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Membresía"), { target: { value: "5" } });

    fireEvent.click(screen.getByRole("button", { name: "Asignar membresía" }));

    await waitFor(() => {
      expect(screen.getByText("Cliente ya tiene membresía activa")).toBeDefined();
    });
  });
});
