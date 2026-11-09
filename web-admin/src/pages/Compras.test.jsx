import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Compras from "./Compras";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockProveedores = [{ id_proveedor: 1, razon_social: "Nutrición SAC", estado: "ACTIVO" }];
const mockProductos = [{ id_producto: 1, nombre: "Proteína Whey", estado: "ACTIVO" }];

const mockCompraPendiente = {
  id_compra: 1,
  id_proveedor: 1,
  nombre_proveedor: "Nutrición SAC",
  estado: "PENDIENTE",
  total: 118,
  detalles: [{ id_producto: 1 }],
  fecha_compra: "2026-09-01T10:00:00Z",
};

function mockApiGet(compras = [mockCompraPendiente]) {
  api.get.mockImplementation((url) => {
    if (url === "/compras/") return Promise.resolve({ data: compras });
    if (url === "/proveedores/") return Promise.resolve({ data: mockProveedores });
    if (url === "/productos/") return Promise.resolve({ data: mockProductos });
    return Promise.resolve({ data: [] });
  });
}

describe("Compras Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockApiGet();
  });

  it("renders headers and loads the purchase history", async () => {
    render(<Compras />);
    expect(screen.getByText("Historial de compras")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Nutrición SAC")).toBeDefined();
      expect(screen.getByText("PENDIENTE")).toBeDefined();
    });
  });

  it("filters purchases based on search term", async () => {
    render(<Compras />);
    await waitFor(() => expect(screen.getByText("Nutrición SAC")).toBeDefined());

    fireEvent.change(screen.getByPlaceholderText("Buscar..."), { target: { value: "noexiste" } });

    await waitFor(() => {
      expect(screen.getByText("No hay compras registradas.")).toBeDefined();
    });
  });

  it("validates that a provider and at least one detail are required", async () => {
    render(<Compras />);
    fireEvent.click(screen.getByText("+ Nueva compra"));

    await waitFor(() => expect(screen.getByText("Registrar compra")).toBeDefined());
    fireEvent.click(screen.getByText("Registrar compra"));

    await waitFor(() => {
      expect(screen.getByText("Seleccione un proveedor")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("registers a purchase with one detail line", async () => {
    api.post.mockResolvedValue({ data: {} });
    const { container } = render(<Compras />);

    fireEvent.click(screen.getByText("+ Nueva compra"));
    await waitFor(() => expect(screen.getByText("Registrar compra")).toBeDefined());

    const proveedorSelect = container.querySelector('select[name="id_proveedor"]');
    fireEvent.change(proveedorSelect, { target: { value: "1" } });
    // Evita una condición de carrera: sin esto, los siguientes clics pueden
    // dispararse antes de que React procese este cambio (mismo fix que en
    // Nutricion.test.jsx/Rutinas.test.jsx, que sí llegó a fallar en CI).
    await waitFor(() => expect(proveedorSelect.value).toBe("1"));

    fireEvent.click(screen.getByText("+ Agregar producto"));

    const productoSelect = container.querySelectorAll(".form-grid select")[1];
    fireEvent.change(productoSelect, { target: { value: "1" } });

    const inputs = container.querySelectorAll('input[type="number"]');
    fireEvent.change(inputs[0], { target: { value: "10" } });
    fireEvent.change(inputs[1], { target: { value: "5" } });
    await waitFor(() => expect(inputs[1].value).toBe("5"));

    fireEvent.click(screen.getByText("Registrar compra"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/compras/", {
        id_proveedor: 1,
        detalles: [{ id_producto: 1, cantidad: 10, precio_unitario: 5 }],
        observaciones: null,
      });
    });
  });

  it("confirms a pending purchase", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.post.mockResolvedValue({ data: {} });

    render(<Compras />);
    await waitFor(() => expect(screen.getByText("Confirmar")).toBeDefined());
    fireEvent.click(screen.getByText("Confirmar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/compras/1/confirmar");
    });
  });

  it("cancels a pending purchase", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.post.mockResolvedValue({ data: {} });

    render(<Compras />);
    await waitFor(() => expect(screen.getByText("Anular")).toBeDefined());
    fireEvent.click(screen.getByText("Anular"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/compras/1/anular");
    });
  });

  it("does not show confirm/anular actions for a confirmed purchase", async () => {
    mockApiGet([{ ...mockCompraPendiente, estado: "CONFIRMADA" }]);
    render(<Compras />);

    await waitFor(() => expect(screen.getByText("CONFIRMADA")).toBeDefined());
    expect(screen.queryByText("Confirmar")).toBeNull();
    expect(screen.queryByText("Anular")).toBeNull();
  });

  it("shows an error message when confirming fails", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.post.mockRejectedValue({ response: { data: { detail: "Stock insuficiente" } } });

    render(<Compras />);
    await waitFor(() => expect(screen.getByText("Confirmar")).toBeDefined());
    fireEvent.click(screen.getByText("Confirmar"));

    await waitFor(() => {
      expect(screen.getByText("Stock insuficiente")).toBeDefined();
    });
  });
});
