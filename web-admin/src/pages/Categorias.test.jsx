import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Categorias from "./Categorias";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockCategorias = [
  { id_categoria: 1, nombre: "Suplementos", descripcion: "Proteínas y vitaminas", estado: "ACTIVO" },
];

describe("Categorias Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockCategorias });
  });

  it("renders headers and loads the categories list", async () => {
    render(<Categorias />);
    expect(screen.getByText("Lista de categorías")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Suplementos")).toBeDefined();
      expect(screen.getByText("Proteínas y vitaminas")).toBeDefined();
    });
  });

  it("filters categories based on search term", async () => {
    render(<Categorias />);
    await waitFor(() => expect(screen.getByText("Suplementos")).toBeDefined());

    fireEvent.change(screen.getByPlaceholderText("Buscar..."), { target: { value: "noexiste" } });

    await waitFor(() => {
      expect(screen.queryByText("Suplementos")).toBeNull();
    });
  });

  it("shows form and calls post on creating a category", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Categorias />);

    fireEvent.click(screen.getByText("+ Nueva categoría"));

    await waitFor(() => expect(screen.getByLabelText("Nombre")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Ropa" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/categorias/", {
        nombre: "Ropa",
        descripcion: null,
        estado: "ACTIVO",
      });
    });
  });

  it("validates the name field before submitting", async () => {
    render(<Categorias />);
    fireEvent.click(screen.getByText("+ Nueva categoría"));

    await waitFor(() => expect(screen.getByLabelText("Nombre")).toBeDefined());
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(screen.getByText("Ingrese el nombre de la categoría")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("enters edit mode and updates a category via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Categorias />);

    await waitFor(() => expect(screen.getByText("Editar")).toBeDefined());
    fireEvent.click(screen.getByText("Editar"));

    await waitFor(() => expect(screen.getByRole("heading", { name: "Editar categoría" })).toBeDefined());

    fireEvent.change(screen.getByLabelText("Estado"), { target: { value: "INACTIVO" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/categorias/1", {
        nombre: "Suplementos",
        descripcion: "Proteínas y vitaminas",
        estado: "INACTIVO",
      });
    });
  });

  it("deactivates a category on confirm", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Categorias />);
    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/categorias/1");
    });
  });

  it("does not deactivate when confirm is cancelled", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    render(<Categorias />);

    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    expect(api.delete).not.toHaveBeenCalled();
  });

  it("shows an empty message when there are no categories", async () => {
    api.get.mockResolvedValue({ data: [] });
    render(<Categorias />);

    await waitFor(() => {
      expect(screen.getByText("No hay categorías registradas.")).toBeDefined();
    });
  });

  it("shows the load error message instead of crashing when loading fails", async () => {
    api.get.mockRejectedValue(new Error("Network Error"));
    render(<Categorias />);

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/categorias/");
      expect(screen.getByText("Error al cargar categorías")).toBeDefined();
      expect(screen.getByText("No hay categorías registradas.")).toBeDefined();
    });
  });

  it("shows an error message when creation fails", async () => {
    api.post.mockRejectedValue({ response: { data: { detail: "Nombre duplicado" } } });
    render(<Categorias />);

    fireEvent.click(screen.getByText("+ Nueva categoría"));
    await waitFor(() => expect(screen.getByLabelText("Nombre")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Suplementos" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(screen.getByText("Nombre duplicado")).toBeDefined();
    });
  });
});
