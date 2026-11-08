import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Nutricion from "./Nutricion";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockClientes = [
  { id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO", objetivo: "Ganar masa" },
];

const mockPlanes = [
  {
    id_plan: 10,
    id_cliente: 1,
    estado: "ACTIVO",
    objetivo: "Dieta Hiperproteica",
    calorias_diarias: 2500,
    generada_por_ia: true,
    fecha_creacion: "2026-06-01",
  },
];

function renderNutricion() {
  return render(
    <MemoryRouter>
      <Nutricion />
    </MemoryRouter>
  );
}

describe("Nutricion Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/nutricion/")) return Promise.resolve({ data: mockPlanes });
      return Promise.resolve({ data: [] });
    });
  });

  it("renders the header and lists generated plans", async () => {
    renderNutricion();
    expect(screen.getByText("Planes nutricionales")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Dieta Hiperproteica")).toBeDefined();
      expect(screen.getByText("Juan Perez")).toBeDefined();
      expect(screen.getByText("2500 kcal")).toBeDefined();
    });
  });

  it("filters plans based on search term", async () => {
    renderNutricion();
    await waitFor(() => expect(screen.getByText("Dieta Hiperproteica")).toBeDefined());

    fireEvent.change(
      screen.getByPlaceholderText("Buscar por cliente, objetivo o estado..."),
      { target: { value: "noexiste" } }
    );

    await waitFor(() => {
      expect(screen.queryByText("Dieta Hiperproteica")).toBeNull();
      expect(screen.getByText("No hay planes nutricionales registrados")).toBeDefined();
    });
  });

  it("requires a client before generating a plan with IA", async () => {
    renderNutricion();
    await waitFor(() => expect(screen.getByText("Generar plan con IA")).toBeDefined());

    fireEvent.click(screen.getByText("Generar plan con IA"));

    await waitFor(() => {
      expect(screen.getByText("Seleccione un cliente")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("generates a plan with IA for the selected client", async () => {
    api.post.mockResolvedValue({ data: { id_plan: 11 } });
    renderNutricion();

    await waitFor(() => expect(screen.getByText("Generar plan con IA")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.click(screen.getByText("Generar plan con IA"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ia/nutricion/generar/1");
    });
  });

  it("shows an error when IA generation fails", async () => {
    api.post.mockRejectedValue({ response: { data: { detail: "Límite de tokens IA excedido" } } });
    renderNutricion();

    await waitFor(() => expect(screen.getByText("Generar plan con IA")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.click(screen.getByText("Generar plan con IA"));

    await waitFor(() => {
      expect(screen.getByText("Límite de tokens IA excedido")).toBeDefined();
    });
  });

  it("shows an error when loading data fails", async () => {
    api.get.mockRejectedValue(new Error("Network Error"));
    renderNutricion();

    await waitFor(() => {
      expect(screen.getByText("Error al cargar datos")).toBeDefined();
    });
  });

  it("navigates to the plan detail when clicking Ver", async () => {
    renderNutricion();
    await waitFor(() => expect(screen.getByText("Dieta Hiperproteica")).toBeDefined());

    fireEvent.click(screen.getByText("Ver"));

    expect(mockNavigate).toHaveBeenCalledWith("/nutricion/10/detalle");
  });

  it("deactivates a plan on confirm", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });
    renderNutricion();

    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    expect(globalThis.confirm).toHaveBeenCalled();
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/nutricion/10");
    });
  });

  it("does not deactivate a plan if the user cancels the confirmation", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    renderNutricion();

    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    expect(globalThis.confirm).toHaveBeenCalled();
    expect(api.delete).not.toHaveBeenCalled();
  });

  it("shows an error when deactivating a plan fails", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockRejectedValue(new Error("Delete Error"));
    renderNutricion();

    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(screen.getByText("Error al desactivar plan")).toBeDefined();
    });
  });
});
