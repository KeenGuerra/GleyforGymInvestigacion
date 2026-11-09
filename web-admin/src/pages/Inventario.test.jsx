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
const mockAlertasVencimiento = {
  vencidos: [{ id_lote: 2, nombre_producto: "Barritas", numero_lote: "L2", fecha_vencimiento: "2026-09-01", cantidad: 2, dias_restantes: -5 }],
  por_vencer: [{ id_lote: 1, nombre_producto: "Barras", numero_lote: "L1", fecha_vencimiento: "2026-10-01", cantidad: 3, dias_restantes: 7 }],
};

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

  it("switches to the alertas tab and shows stock, expired and about-to-expire alerts separately", async () => {
    render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Alertas"));

    await waitFor(() => {
      expect(screen.getByText("Stock bajo")).toBeDefined();
      expect(screen.getByText("Creatina")).toBeDefined();
      expect(screen.getAllByText("Vencidos").length).toBeGreaterThan(0);
      expect(screen.getByText("Barritas")).toBeDefined();
      expect(screen.getByText("Venció hace 5 día(s)")).toBeDefined();
      expect(screen.getByText("Próximos a vencer")).toBeDefined();
      expect(screen.getByText("Barras")).toBeDefined();
      expect(screen.getByText("Vence en 7 día(s)")).toBeDefined();
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
      if (url === "/inventario/alertas/vencimiento") return Promise.resolve({ data: { vencidos: [], por_vencer: [] } });
      return Promise.resolve({ data: [] });
    });

    render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());
    fireEvent.click(screen.getByText("Alertas"));

    await waitFor(() => {
      expect(screen.getByText("No hay alertas activas.")).toBeDefined();
    });
  });

  it("saves a physical inventory count and shows the calculated accuracy (F-16)", async () => {
    api.post.mockResolvedValue({
      data: {
        id_conteo: 1,
        fecha: "2026-11-01T10:00:00Z",
        observaciones: null,
        total_productos: 1,
        productos_correctos: 0,
        exactitud_pct: 0,
        detalles: [
          { id_detalle_conteo: 1, id_producto: 1, nombre_producto: "Proteína Whey", stock_sistema: 20, stock_fisico: 18, diferencia: 2 },
        ],
      },
    });

    const { container } = render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Conteo físico"));
    await waitFor(() => expect(screen.getByText("Conteo físico de inventario")).toBeDefined());

    const inputStockFisico = container.querySelector('.table input[type="number"]');
    expect(inputStockFisico.value).toBe("20");
    fireEvent.change(inputStockFisico, { target: { value: "18" } });

    fireEvent.click(screen.getByText("Guardar conteo"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/inventario/conteos", {
        detalles: [{ id_producto: 1, stock_fisico: 18 }],
      });
      expect(screen.getByText(/Resultado del conteo #1/)).toBeDefined();
      expect(screen.getByText("0%")).toBeDefined();
    });
  });

  it("falls back to the system stock (not 0) when the physical count input is cleared", async () => {
    api.post.mockResolvedValue({
      data: { id_conteo: 2, fecha: "2026-11-01T10:00:00Z", observaciones: null, total_productos: 1, productos_correctos: 1, exactitud_pct: 100, detalles: [] },
    });

    const { container } = render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Conteo físico"));
    await waitFor(() => expect(screen.getByText("Conteo físico de inventario")).toBeDefined());

    const inputStockFisico = container.querySelector('.table input[type="number"]');
    // El staff borra el campo para retipear (queda "" un momento) y guarda
    // antes de escribir el nuevo número -- no debe mandarse 0.
    fireEvent.change(inputStockFisico, { target: { value: "" } });

    fireEvent.click(screen.getByText("Guardar conteo"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/inventario/conteos", {
        detalles: [{ id_producto: 1, stock_fisico: 20 }],
      });
    });
  });

  it("shows an error when saving the physical count fails", async () => {
    api.post.mockRejectedValue({ response: { data: { detail: "Producto no encontrado" } } });

    render(<Inventario />);
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Conteo físico"));
    await waitFor(() => expect(screen.getByText("Guardar conteo")).toBeDefined());

    fireEvent.click(screen.getByText("Guardar conteo"));

    await waitFor(() => {
      expect(screen.getByText("Producto no encontrado")).toBeDefined();
    });
  });
});
