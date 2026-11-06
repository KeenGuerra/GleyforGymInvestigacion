import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Ventas from "./Ventas";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockProductosDisponibles = [
  { id_producto: 1, nombre: "Proteína Whey", precio_venta: 90, stock_actual: 10 },
];
const mockClientes = [{ id_cliente: 1, nombres: "Ana", apellidos: "López" }];
const mockResumen = { ventas_hoy: 2, ingresos_hoy: 180, ventas_mes: 20, ingresos_mes: 1800 };

const mockVentaPendiente = {
  id_venta: 1,
  nombre_cliente: "Ana López",
  estado: "PENDIENTE",
  total: 90,
  metodo_pago: "EFECTIVO",
  detalles: [{ id_detalle_venta: 1, nombre_producto: "Proteína Whey", cantidad: 1, subtotal: 90 }],
  fecha_venta: "2026-09-01T10:00:00Z",
};

function mockApiGet(ventas = [mockVentaPendiente]) {
  api.get.mockImplementation((url) => {
    if (url === "/ventas/") return Promise.resolve({ data: ventas });
    if (url === "/productos/disponibles") return Promise.resolve({ data: mockProductosDisponibles });
    if (url === "/clientes/") return Promise.resolve({ data: mockClientes });
    if (url === "/ventas/resumen") return Promise.resolve({ data: mockResumen });
    return Promise.resolve({ data: [] });
  });
}

describe("Ventas Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockApiGet();
  });

  it("renders the summary stats and sales history", async () => {
    render(<Ventas />);
    expect(screen.getByText("Historial de ventas")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Ana López")).toBeDefined();
      expect(screen.getByText("S/ 180.00")).toBeDefined();
    });
  });

  it("requests the first page with the expected pagination params", async () => {
    render(<Ventas />);
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/ventas/", { params: { skip: 0, limit: 20 } });
    });
  });

  it("filters sales based on search term", async () => {
    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Ana López")).toBeDefined());

    fireEvent.change(screen.getByPlaceholderText("Buscar..."), { target: { value: "noexiste" } });

    await waitFor(() => {
      expect(screen.getByText("No hay ventas registradas.")).toBeDefined();
    });
  });

  it("validates that at least one detail is required", async () => {
    render(<Ventas />);
    fireEvent.click(screen.getByText("+ Nueva venta"));

    await waitFor(() => expect(screen.getByText("Confirmar venta")).toBeDefined());
    fireEvent.click(screen.getByText("Confirmar venta"));

    await waitFor(() => {
      expect(screen.getByText("Agregue al menos un producto")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("registers a direct sale with one detail line", async () => {
    api.post.mockResolvedValue({ data: {} });
    const { container } = render(<Ventas />);

    fireEvent.click(screen.getByText("+ Nueva venta"));
    await waitFor(() => expect(screen.getByText("Confirmar venta")).toBeDefined());

    fireEvent.click(screen.getByText("+ Agregar producto"));

    const productoSelect = container.querySelectorAll(".form-grid select")[2];
    fireEvent.change(productoSelect, { target: { value: "1" } });

    const cantidadInput = container.querySelector('input[type="number"][min="1"]');
    fireEvent.change(cantidadInput, { target: { value: "2" } });

    fireEvent.click(screen.getByText("Confirmar venta"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ventas/", {
        id_cliente: null,
        metodo_pago: "EFECTIVO",
        descuento: 0,
        observaciones: null,
        detalles: [{ id_producto: 1, cantidad: 2 }],
      });
    });
  });

  it("rejects a quantity greater than the available stock", async () => {
    const { container } = render(<Ventas />);
    fireEvent.click(screen.getByText("+ Nueva venta"));
    await waitFor(() => expect(screen.getByText("Confirmar venta")).toBeDefined());

    fireEvent.click(screen.getByText("+ Agregar producto"));
    const productoSelect = container.querySelectorAll(".form-grid select")[2];
    fireEvent.change(productoSelect, { target: { value: "1" } });

    const cantidadInput = container.querySelector('input[type="number"][min="1"]');
    fireEvent.change(cantidadInput, { target: { value: "99" } });

    fireEvent.click(screen.getByText("Confirmar venta"));

    await waitFor(() => {
      expect(screen.getByText("Stock insuficiente: Proteína Whey")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("confirms a pending sale", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.post.mockResolvedValue({ data: {} });

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Confirmar")).toBeDefined());
    fireEvent.click(screen.getByText("Confirmar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ventas/1/confirmar");
    });
  });

  it("cancels a confirmed sale", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.post.mockResolvedValue({ data: {} });
    mockApiGet([{ ...mockVentaPendiente, estado: "CONFIRMADA" }]);

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Anular")).toBeDefined());
    fireEvent.click(screen.getByText("Anular"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ventas/1/anular");
    });
  });

  it("shows an error message when registering a sale fails", async () => {
    api.post.mockRejectedValue({ response: { data: { detail: "Producto inactivo" } } });
    const { container } = render(<Ventas />);

    fireEvent.click(screen.getByText("+ Nueva venta"));
    await waitFor(() => expect(screen.getByText("Confirmar venta")).toBeDefined());

    fireEvent.click(screen.getByText("+ Agregar producto"));
    const productoSelect = container.querySelectorAll(".form-grid select")[2];
    fireEvent.change(productoSelect, { target: { value: "1" } });

    fireEvent.click(screen.getByText("Confirmar venta"));

    await waitFor(() => {
      expect(screen.getByText("Producto inactivo")).toBeDefined();
    });
  });
});
