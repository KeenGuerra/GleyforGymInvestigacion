import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Tienda from "./Tienda";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockProductos = [
  { id_producto: 1, nombre: "Proteína Whey", nombre_categoria: "Suplementos", precio_venta: 90, stock_actual: 10 },
  { id_producto: 2, nombre: "Creatina", nombre_categoria: "Suplementos", precio_venta: 50, stock_actual: 0 },
];

const mockPedidos = [
  { id_venta: 1, estado: "PENDIENTE", total: 90, metodo_pago: "EFECTIVO", detalles: [], fecha_venta: "2026-09-01T10:00:00Z" },
];

function renderTienda() {
  return render(
    <MemoryRouter>
      <Tienda />
    </MemoryRouter>
  );
}

describe("Tienda Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    api.get.mockImplementation((url) => {
      if (url === "/productos/disponibles") return Promise.resolve({ data: mockProductos });
      if (url === "/ventas/mis-pedidos") return Promise.resolve({ data: mockPedidos });
      return Promise.resolve({ data: [] });
    });
  });

  it("renders the public catalog without requiring login", async () => {
    renderTienda();
    await waitFor(() => {
      expect(screen.getByText("Proteína Whey")).toBeDefined();
      expect(screen.getByText("Creatina")).toBeDefined();
    });
    expect(screen.getAllByText(/Inicia sesión/).length).toBeGreaterThan(0);
  });

  it("filters products based on search term", async () => {
    renderTienda();
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.change(screen.getByPlaceholderText("Buscar producto..."), { target: { value: "noexiste" } });

    await waitFor(() => {
      expect(screen.getByText("No hay productos disponibles.")).toBeDefined();
    });
  });

  it("disables the add-to-cart button when a product has no stock", async () => {
    renderTienda();
    await waitFor(() => expect(screen.getByText("Creatina")).toBeDefined());

    const creatinaCard = screen.getByText("Creatina").closest(".item-card");
    expect(within(creatinaCard).getByText("Sin stock").closest("button")).toBeDisabled();
  });

  it("redirects a logged-out visitor to login when adding to cart", async () => {
    renderTienda();
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getAllByText("Inicia sesión o regístrate")[0]);

    await waitFor(() => {
      expect(screen.queryByText("Carrito está vacío")).toBeNull();
    });
  });

  it("adds a product to the cart and shows pedidos tab when logged in", async () => {
    localStorage.setItem("token", "fake-token");
    renderTienda();

    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());
    fireEvent.click(screen.getByText("+ Agregar"));

    fireEvent.click(screen.getAllByText("Carrito (1)")[1]);

    await waitFor(() => {
      expect(screen.getAllByText("S/ 90.00").length).toBeGreaterThan(0);
    });
  });

  it("shows Yape as the only payment method -- no dropdown, no other gateway", async () => {
    localStorage.setItem("token", "fake-token");

    renderTienda();
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("+ Agregar"));
    fireEvent.click(screen.getAllByText("Carrito (1)")[1]);

    await waitFor(() => expect(screen.getByText("Confirmar pedido")).toBeDefined());
    expect(screen.getByText("Yape (QR)")).toBeDefined();
    expect(screen.queryAllByRole("option").length).toBe(0);
  });

  it("checks out the cart with metodo_pago YAPE and lists the resulting order", async () => {
    localStorage.setItem("token", "fake-token");
    api.post.mockResolvedValue({ data: {} });

    renderTienda();
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("+ Agregar"));
    fireEvent.click(screen.getAllByText("Carrito (1)")[1]);

    await waitFor(() => expect(screen.getByText("Confirmar pedido")).toBeDefined());
    expect(
      screen.getByText("📍 Todas las compras se recogen en el gimnasio — no hacemos delivery.")
    ).toBeDefined();
    fireEvent.click(screen.getByText("Confirmar pedido"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ventas/solicitar", {
        metodo_pago: "YAPE",
        descuento: 0,
        observaciones: null,
        detalles: [{ id_producto: 1, cantidad: 1 }],
      });
    });

    await waitFor(() => {
      expect(screen.getByText("Mis pedidos (1)")).toBeDefined();
    });
  });

  it("shows an error when checkout fails", async () => {
    localStorage.setItem("token", "fake-token");
    api.post.mockRejectedValue({ response: { data: { detail: "Stock insuficiente" } } });

    renderTienda();
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("+ Agregar"));
    fireEvent.click(screen.getAllByText("Carrito (1)")[1]);

    await waitFor(() => expect(screen.getByText("Confirmar pedido")).toBeDefined());
    fireEvent.click(screen.getByText("Confirmar pedido"));

    await waitFor(() => {
      expect(screen.getByText("Stock insuficiente")).toBeDefined();
    });
  });

  it("shows a pickup reminder on a confirmed order instead of the pay button", async () => {
    localStorage.setItem("token", "fake-token");
    api.get.mockImplementation((url) => {
      if (url === "/productos/disponibles") return Promise.resolve({ data: mockProductos });
      if (url === "/ventas/mis-pedidos") {
        return Promise.resolve({
          data: [{ ...mockPedidos[0], estado: "CONFIRMADA" }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    renderTienda();
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Mis pedidos (1)"));

    await waitFor(() => {
      expect(
        screen.getByText("✔ Pago confirmado. Recógelo en el gimnasio — no hacemos delivery.")
      ).toBeDefined();
    });
    expect(screen.queryByText("Pagar con Yape")).toBeNull();
  });

  it("shows a delivered confirmation on an ENTREGADA order", async () => {
    localStorage.setItem("token", "fake-token");
    api.get.mockImplementation((url) => {
      if (url === "/productos/disponibles") return Promise.resolve({ data: mockProductos });
      if (url === "/ventas/mis-pedidos") {
        return Promise.resolve({
          data: [{ ...mockPedidos[0], estado: "ENTREGADA" }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    renderTienda();
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Mis pedidos (1)"));

    await waitFor(() => {
      expect(screen.getByText("✔ Entregado. ¡Gracias por tu compra!")).toBeDefined();
    });
    expect(screen.queryByText("Pagar con Yape")).toBeNull();
    expect(
      screen.queryByText("✔ Pago confirmado. Recógelo en el gimnasio — no hacemos delivery.")
    ).toBeNull();
  });

  it("shows the static Yape QR for a pending order, with no API call -- there is no gateway anymore", async () => {
    localStorage.setItem("token", "fake-token");

    renderTienda();
    await waitFor(() => expect(screen.getByText("Proteína Whey")).toBeDefined());

    fireEvent.click(screen.getByText("Mis pedidos (1)"));

    await waitFor(() => expect(screen.getByText("Pagar con Yape")).toBeDefined());
    fireEvent.click(screen.getByText("Pagar con Yape"));

    expect(screen.getByAltText("Código QR para pagar con Yape")).toBeDefined();
    expect(screen.getByText(/Escanea con Yape y paga/)).toBeDefined();
    expect(api.post).not.toHaveBeenCalledWith("/ventas/1/checkout");

    fireEvent.click(screen.getByText("Ocultar QR"));
    expect(screen.queryByAltText("Código QR para pagar con Yape")).toBeNull();
  });
});
