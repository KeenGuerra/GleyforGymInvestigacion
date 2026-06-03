import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Comidas from "./Comidas";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockComidas = [
  {
    id_comida_catalogo: 1,
    nombre: "Ensalada César",
    tipo_comida: "ALMUERZO",
    calorias: 350,
    proteinas: 25,
    carbohidratos: 10,
    grasas: 20,
    objetivo: "PERDIDA_PESO",
    estado: "ACTIVO",
  },
];

describe("Comidas Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockComidas });
  });

  it("renders header and lists meals", async () => {
    render(<Comidas />);
    expect(screen.getByText("Lista de comidas")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Ensalada César")).toBeDefined();
    });
  });

  it("filters meals list based on search term", async () => {
    render(<Comidas />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar por nombre, tipo, objetivo o estado...")).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText("Buscar por nombre, tipo, objetivo o estado...");
    fireEvent.change(searchInput, { target: { value: "Pollo" } });

    await waitFor(() => {
      expect(screen.queryByText("Ensalada César")).toBeNull();
    });
  });

  it("shows form and calls post on submitting a new meal", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Comidas />);

    await waitFor(() => {
      expect(screen.getByText("+ Registrar comida")).toBeDefined();
    });

    fireEvent.click(screen.getByText("+ Registrar comida"));

    await waitFor(() => {
      expect(screen.getByText("Registrar comida", { selector: "h2" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Pollo a la plancha" } });
    fireEvent.change(screen.getByLabelText("Tipo de comida"), { target: { value: "ALMUERZO" } });
    fireEvent.change(screen.getByLabelText("Calorías"), { target: { value: "400" } });

    fireEvent.click(screen.getByText("Guardar comida"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
  });
});
