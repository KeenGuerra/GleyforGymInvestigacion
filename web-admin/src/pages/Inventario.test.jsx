import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Inventario from "./Inventario";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockInventario = [
  { id_inventario: 1, id_producto: 1, nombre_producto: "Proteína Whey", stock_actual: 20, stock_minimo: 5, unidad_medida: "UNIDAD", ultimo_costo: 60 },
];
const mockMovimientos = [
  { id_movimiento: 1, nombre_producto: "Proteína Whey", tipo_movimiento: "ENTRADA_COMPRA", cantidad: 10, costo_unitario: 60, fecha_movimiento: "2026-09-01T10:00:00Z" },
];
const mockAlertasStock = [{ id_inventario: 2, nombre_producto: "Creatina", stock_actual: 1, stock_minimo: 5 }];
const mockAlertasVencimiento = [{ id_lote: 1, nombre_producto: "Barras", numero_lote: "L1", fecha_vencimiento: "2026-10-01", cantidad: 3 }];

function mockApiGet() {
  api.get.mockImplementation((url) => {
    if (url === "/inventario/") return Promise.resolve({ data: mockInventario });
    if (url === "/inventario/movimientos/") return Promise.resolve({ data: mockMovimientos });
    if (url === "/inventario/alertas/stock") return Promise.resolve({ data: mockAlertasStock });
    if (url === "/inventario/alertas/vencimiento") return Promise.resolve({ data: mockAlertasVencimiento });
    return Promise.resolve({ data: [] });
  });
}

describe("Inventario Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockApiGet();
  });

  it("renders stock cards on the inventario tab by default", async () => {
    render(<Inventario />);
    expect(screen.getByText("Stock actual")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Proteína Whey")).toBeDefined();
    });
  });

  it("filters inventory by product name", async () => {
    render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.change(screen.getByPlaceholderText("Buscar..."), { target: { value: "noexiste" } });

    await waitFor(() => {
      expect(screen.getByText("Sin datos de inventario.")).toBeDefined();
    });
  });

  it("switches to the movimientos tab", async () => {
    render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Movimientos"));

    await waitFor(() => {
      expect(screen.getByText("Movimientos de stock")).toBeDefined();
      expect(screen.getByText("ENTRADA_COMPRA")).toBeDefined();
    });
  });

  it("switches to the alertas tab and shows both alert types", async () => {
    render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Alertas"));

    await waitFor(() => {
      expect(screen.getByText("Stock bajo")).toBeDefined();
      expect(screen.getByText("Creatina")).toBeDefined();
      expect(screen.getByText("Próximos a vencer")).toBeDefined();
      expect(screen.getByText("Barras")).toBeDefined();
    });
  });

  it("applies a manual stock adjustment", async () => {
    api.post.mockResolvedValue({ data: {} });
    const { container } = render(<Inventario />);

    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());
    fireEvent.click(screen.getByText("+ Ajuste manual"));

    await waitFor(() => expect(screen.getByText("Ajuste de inventario")).toBeDefined());

    const productoSelect = container.querySelector(".form-card select");
    fireEvent.change(productoSelect, { target: { value: "1" } });

    const cantidadInput = container.querySelector('.form-card input[type="number"]');
    fireEvent.change(cantidadInput, { target: { value: "5" } });

    fireEvent.click(screen.getByText("Aplicar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/inventario/ajustes", {
        id_producto: 1,
        cantidad: 5,
        descripcion: null,
      });
    });
  });

  it("requires a product before applying an adjustment", async () => {
    render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("+ Ajuste manual"));
    await waitFor(() => expect(screen.getByText("Aplicar")).toBeDefined());

    fireEvent.click(screen.getByText("Aplicar"));

    await waitFor(() => {
      expect(screen.getByText("Seleccione un producto")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("shows an empty message when there are no active alerts", async () => {
    api.get.mockImplementation((url) => {
      if (url === "/inventario/") return Promise.resolve({ data: mockInventario });
      if (url === "/inventario/movimientos/") return Promise.resolve({ data: [] });
      if (url === "/inventario/alertas/stock") return Promise.resolve({ data: [] });
      if (url === "/inventario/alertas/vencimiento") return Promise.resolve({ data: [] });
      return Promise.resolve({ data: [] });
    });

    render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());
    fireEvent.click(screen.getByText("Alertas"));

    await waitFor(() => {
      expect(screen.getByText("No hay alertas activas.")).toBeDefined();
    });
  });
});
