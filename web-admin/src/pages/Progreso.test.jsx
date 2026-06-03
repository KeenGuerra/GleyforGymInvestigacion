import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Progreso from "./Progreso";
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

const mockProgresos = [
  {
    id_progreso: 1,
    id_cliente: 1,
    peso: 80,
    porcentaje_grasa: 20,
    masa_grasa: 16,
    masa_magra: 64,
    medida_pecho: 100,
    medida_cintura: 85,
    medida_brazo_izquierdo: 35,
    medida_brazo_derecho: 35,
    medida_pierna_izquierda: 55,
    medida_pierna_derecha: 55,
    fecha_registro: "2026-06-01",
    observacion: "Inicial",
  },
];

describe("Progreso Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      return Promise.resolve({ data: mockProgresos });
    });
  });

  it("renders headers and loads progress history table", async () => {
    render(<Progreso />);
    expect(screen.getByText("Historial de progreso")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("80 kg")).toBeDefined();
      expect(screen.getByText("Juan Perez")).toBeDefined();
    });
  });

  it("filters progress history based on search term", async () => {
    render(<Progreso />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar por cliente...")).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText("Buscar por cliente...");
    fireEvent.change(searchInput, { target: { value: "Carlos" } });

    await waitFor(() => {
      expect(screen.queryByText("80 kg")).toBeNull();
    });
  });

  it("fails validation for incorrect input values", async () => {
    render(<Progreso />);

    // Open form
    fireEvent.click(screen.getByText("+ Registrar progreso"));

    await waitFor(() => {
      expect(screen.getByText("Juan Perez - DNI 12345678")).toBeDefined();
    });

    // 1. Missing client
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      expect(screen.getByText("Seleccione un cliente")).toBeDefined();
    });

    // Fill client
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });

    // 2. Empty weight
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      expect(screen.getByText("Peso inválido")).toBeDefined();
    });

    // Fill weight
    fireEvent.change(screen.getByLabelText("Peso (kg)"), { target: { value: "80" } });

    // 3. Out of bounds body fat
    fireEvent.change(screen.getByLabelText("% grasa corporal"), { target: { value: "150" } });
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      expect(screen.getByText("El porcentaje de grasa debe estar entre 0 y 100")).toBeDefined();
    });
  });

  it("calculates lean mass and fat mass dynamically", async () => {
    render(<Progreso />);
    fireEvent.click(screen.getByText("+ Registrar progreso"));

    const pesoInput = screen.getByLabelText("Peso (kg)");
    const grasaInput = screen.getByLabelText("% grasa corporal");
    const masaGrasaInput = screen.getByLabelText("Masa grasa");
    const masaMagraInput = screen.getByLabelText("Masa magra");

    fireEvent.change(pesoInput, { target: { value: "100" } });
    fireEvent.change(grasaInput, { target: { value: "15" } });

    expect(masaGrasaInput.value).toBe("15.00 kg");
    expect(masaMagraInput.value).toBe("85.00 kg");
  });

  it("submits the form successfully to create a new progress entry", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Progreso />);

    fireEvent.click(screen.getByText("+ Registrar progreso"));

    await waitFor(() => {
      expect(screen.getByText("Juan Perez - DNI 12345678")).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Peso (kg)"), { target: { value: "82" } });
    fireEvent.change(screen.getByLabelText("% grasa corporal"), { target: { value: "18" } });
    fireEvent.change(screen.getByLabelText("Pierna derecha (cm)"), { target: { value: "55.5" } });
    fireEvent.change(screen.getByLabelText("Fecha de registro"), { target: { value: "2026-06-02" } });
    fireEvent.change(screen.getByLabelText("Observación"), { target: { value: "Nueva" } });

    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/progreso/", {
        id_cliente: 1,
        peso: 82,
        porcentaje_grasa: 18,
        medida_pecho: null,
        medida_cintura: null,
        medida_brazo_izquierdo: null,
        medida_brazo_derecho: null,
        medida_pierna_izquierda: null,
        medida_pierna_derecha: 55.5,
        fecha_registro: "2026-06-02",
        observacion: "Nueva",
      });
    });
  });

  it("enters edit mode and updates progress entry via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Progreso />);

    await waitFor(() => {
      expect(screen.getByText("Editar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Editar"));

    // Check header changed
    expect(screen.getByRole("heading", { name: "Editar progreso" })).toBeDefined();

    // Modify weight
    fireEvent.change(screen.getByLabelText("Peso (kg)"), { target: { value: "85" } });

    fireEvent.click(screen.getByRole("button", { name: "Actualizar" }));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/progreso/1", {
        peso: 85,
        porcentaje_grasa: 20,
        medida_pecho: 100,
        medida_cintura: 85,
        medida_brazo_izquierdo: 35,
        medida_brazo_derecho: 35,
        medida_pierna_izquierda: 55,
        medida_pierna_derecha: 55,
        fecha_registro: "2026-06-01",
        observacion: "Inicial",
      });
    });
  });

  it("deletes a progress entry on confirmation", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Progreso />);

    await waitFor(() => {
      expect(screen.getByText("Eliminar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Eliminar"));

    expect(globalThis.confirm).toHaveBeenCalled();
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/progreso/1");
    });
  });

  it("does not delete if confirmation is cancelled", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));

    render(<Progreso />);

    await waitFor(() => {
      expect(screen.getByText("Eliminar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Eliminar"));

    expect(globalThis.confirm).toHaveBeenCalled();
    expect(api.delete).not.toHaveBeenCalled();
  });

  it("hides form when clicking Cancelar", async () => {
    render(<Progreso />);
    fireEvent.click(screen.getByText("+ Registrar progreso"));
    expect(screen.getByRole("heading", { name: "Registrar progreso" })).toBeDefined();

    fireEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("heading", { name: "Registrar progreso" })).toBeNull();
  });

  it("shows error message if loading fails", async () => {
    api.get.mockRejectedValue(new Error("Network Error"));
    render(<Progreso />);

    await waitFor(() => {
      expect(screen.getByText("Error al cargar progreso")).toBeDefined();
    });
  });
});
