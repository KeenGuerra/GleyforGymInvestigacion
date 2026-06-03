import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Nutricion from "./Nutricion";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockClientes = [
  { id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO", objetivo: "Ganar masa" },
];

const mockPlanes = [
  {
    id_plan: 10,
    estado: "ACTIVO",
    objetivo: "Dieta Hiperproteica",
    calorias_diarias: 2500,
    proteinas: 150,
    carbohidratos: 200,
    grasas: 70,
    generada_por_ia: true,
    fecha_creacion: "2026-06-01",
    comidas: [
      {
        id_comida: 5,
        tipo_comida: "Desayuno",
        descripcion: "Avena con plátano",
        calorias_aprox: 400,
        hora_recomendada: "08:00 AM",
      },
    ],
  },
];

describe("Nutricion Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/nutricion/cliente/")) return Promise.resolve({ data: mockPlanes });
      return Promise.resolve({ data: [] });
    });
  });

  it("has an accessible label associated with the client select", async () => {
    render(<Nutricion />);
    const selectElement = document.getElementById("cliente_nutricion");
    expect(selectElement).toBeDefined();
    expect(selectElement?.tagName).toBe("SELECT");
  });

  it("shows the client select with the correct label", async () => {
    render(<Nutricion />);
    const label = screen.getByText("Cliente");
    expect(label).toBeDefined();
  });

  it("loads planes when a client is selected", async () => {
    render(<Nutricion />);
    await waitFor(() => {
      expect(screen.getByText("Juan Perez - Ganar masa")).toBeDefined();
    });

    const select = screen.getByLabelText("Cliente");
    fireEvent.change(select, { target: { value: "1" } });

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/nutricion/cliente/1");
      expect(screen.getByText("Plan #10")).toBeDefined();
      expect(screen.getByText("Dieta Hiperproteica")).toBeDefined();
      expect(screen.getByText("2500 kcal")).toBeDefined();
      expect(screen.getByText("Avena con plátano")).toBeDefined();
    });
  });

  it("calls API to generate plan with IA on click", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Nutricion />);

    await waitFor(() => {
      expect(screen.getByText("Juan Perez - Ganar masa")).toBeDefined();
    });

    const select = screen.getByLabelText("Cliente");
    fireEvent.change(select, { target: { value: "1" } });

    const btn = screen.getByText("Generar plan con IA");
    fireEvent.click(btn);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ia/nutricion/generar/1");
    });
  });

  it("shows error if API generation fails", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "Límite de tokens IA excedido" } },
    });
    render(<Nutricion />);

    await waitFor(() => {
      expect(screen.getByText("Juan Perez - Ganar masa")).toBeDefined();
    });

    const select = screen.getByLabelText("Cliente");
    fireEvent.change(select, { target: { value: "1" } });

    const btn = screen.getByText("Generar plan con IA");
    fireEvent.click(btn);

    await waitFor(() => {
      expect(screen.getByText("Límite de tokens IA excedido")).toBeDefined();
    });
  });

  it("shows error if client loading fails", async () => {
    api.get.mockRejectedValue(new Error("Network Error"));
    render(<Nutricion />);

    await waitFor(() => {
      expect(screen.getByText("Error al cargar clientes")).toBeDefined();
    });
  });

  it("handles plan deactivation with confirmation", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Nutricion />);

    await waitFor(() => {
      expect(screen.getByText("Juan Perez - Ganar masa")).toBeDefined();
    });

    const select = screen.getByLabelText("Cliente");
    fireEvent.change(select, { target: { value: "1" } });

    await waitFor(() => {
      expect(screen.getByText("Desactivar plan")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar plan"));

    expect(globalThis.confirm).toHaveBeenCalled();
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/nutricion/10");
    });
  });

  it("does not deactivate plan if user cancels confirmation", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));

    render(<Nutricion />);

    await waitFor(() => {
      expect(screen.getByText("Juan Perez - Ganar masa")).toBeDefined();
    });

    const select = screen.getByLabelText("Cliente");
    fireEvent.change(select, { target: { value: "1" } });

    await waitFor(() => {
      expect(screen.getByText("Desactivar plan")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar plan"));

    expect(globalThis.confirm).toHaveBeenCalled();
    expect(api.delete).not.toHaveBeenCalled();
  });

  it("shows error if plan deactivation fails", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockRejectedValue(new Error("Delete Error"));

    render(<Nutricion />);
    await waitFor(() => {
      expect(screen.getByText("Juan Perez - Ganar masa")).toBeDefined();
    });

    const select = screen.getByLabelText("Cliente");
    fireEvent.change(select, { target: { value: "1" } });

    await waitFor(() => {
      expect(screen.getByText("Desactivar plan")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar plan"));

    await waitFor(() => {
      expect(screen.getByText("Error al desactivar plan")).toBeDefined();
    });
  });

  it("displays empty message when plan has no meals", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/nutricion/cliente/")) {
        return Promise.resolve({
          data: [{ ...mockPlanes[0], comidas: [] }]
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Nutricion />);
    await waitFor(() => {
      expect(screen.getByText("Juan Perez - Ganar masa")).toBeDefined();
    });

    const select = screen.getByLabelText("Cliente");
    fireEvent.change(select, { target: { value: "1" } });

    await waitFor(() => {
      expect(screen.getByText("No hay comidas registradas en este plan.")).toBeDefined();
    });
  });

  it("displays empty message when client has no active plans", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/nutricion/cliente/")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Nutricion />);
    await waitFor(() => {
      expect(screen.getByText("Juan Perez - Ganar masa")).toBeDefined();
    });

    const select = screen.getByLabelText("Cliente");
    fireEvent.change(select, { target: { value: "1" } });

    await waitFor(() => {
      expect(screen.getByText("Este cliente aún no tiene planes nutricionales activos.")).toBeDefined();
    });
  });
});
