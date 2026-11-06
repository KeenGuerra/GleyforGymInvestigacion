import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Productos from "./Productos";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockCategorias = [{ id_categoria: 1, nombre: "Suplementos", estado: "ACTIVO" }];

const mockProductos = [
  {
    id_producto: 1,
    nombre: "Proteína Whey",
    nombre_categoria: "Suplementos",
    descripcion: "1kg sabor vainilla",
    precio_compra: 60,
    precio_venta: 90,
    stock_actual: 15,
    unidad_medida: "UNIDAD",
    estado: "ACTIVO",
  },
];

function getField(container, name) {
  return container.querySelector(`[name="${name}"]`);
}

describe("Productos Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url === "/categorias/") return Promise.resolve({ data: mockCategorias });
      return Promise.resolve({ data: mockProductos });
    });
  });

  it("renders headers and loads the products list", async () => {
    render(<Productos />);
    expect(screen.getByText("Lista de productos")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Proteína Whey")).toBeDefined();
      expect(screen.getByText("S/90")).toBeDefined();
    });
  });

  it("requests the first page with the expected pagination params", async () => {
    render(<Productos />);
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/productos/", { params: { skip: 0, limit: 20 } });
    });
  });

  it("filters products based on search term", async () => {
    render(<Productos />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.change(screen.getByPlaceholderText("Buscar..."), { target: { value: "noexiste" } });

    await waitFor(() => {
      expect(screen.getByText("No hay productos registrados.")).toBeDefined();
    });
  });

  it("shows form and calls post with form data on creating a product", async () => {
    api.post.mockResolvedValue({ data: {} });
    const { container } = render(<Productos />);

    fireEvent.click(screen.getByText("+ Nuevo producto"));
    await waitFor(() => expect(getField(container, "nombre")).not.toBeNull());

    fireEvent.change(getField(container, "nombre"), { target: { value: "Creatina" } });
    fireEvent.change(getField(container, "precio_venta"), { target: { value: "50" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        "/productos/",
        expect.any(FormData),
        { headers: { "Content-Type": "multipart/form-data" } }
      );
    });

    const formData = api.post.mock.calls[0][1];
    expect(formData.get("nombre")).toBe("Creatina");
    expect(formData.get("precio_venta")).toBe("50");
  });

  it("validates required fields before submitting", async () => {
    render(<Productos />);
    fireEvent.click(screen.getByText("+ Nuevo producto"));

    await waitFor(() => expect(screen.getByText("Guardar")).toBeDefined());
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(screen.getByText("Ingrese el nombre del producto")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("enters edit mode and updates a product via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Productos />);

    await waitFor(() => expect(screen.getByText("Editar")).toBeDefined());
    fireEvent.click(screen.getByText("Editar"));

    await waitFor(() => expect(screen.getByRole("heading", { name: "Editar producto" })).toBeDefined());
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith(
        "/productos/1",
        expect.any(FormData),
        { headers: { "Content-Type": "multipart/form-data" } }
      );
    });
  });

  it("deactivates a product on confirm", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Productos />);
    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/productos/1");
    });
  });

  it("navigates between pages", async () => {
    render(<Productos />);
    await waitFor(() => expect(screen.getByText("Página 1")).toBeDefined());

    expect(screen.getByText("Anterior").closest("button")).toBeDisabled();
    expect(screen.getByText("Siguiente").closest("button")).toBeDisabled();
  });

  it("shows an error message when creation fails", async () => {
    api.post.mockRejectedValue({ response: { data: { detail: "Nombre duplicado" } } });
    const { container } = render(<Productos />);

    fireEvent.click(screen.getByText("+ Nuevo producto"));
    await waitFor(() => expect(getField(container, "nombre")).not.toBeNull());

    fireEvent.change(getField(container, "nombre"), { target: { value: "Creatina" } });
    fireEvent.change(getField(container, "precio_venta"), { target: { value: "50" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(screen.getByText("Nombre duplicado")).toBeDefined();
    });
  });
});
