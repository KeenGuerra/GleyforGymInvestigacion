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

vi.mock("../utils/descargarArchivo", () => ({
  descargarBlob: vi.fn(),
}));

const mockProductosDisponibles = [
  { id_producto: 1, nombre: "Proteína Whey", precio_venta: 90, stock_actual: 10 },
];
const mockClientes = [{ id_cliente: 1, nombres: "Ana", apellidos: "López", telefono: "987654321" }];
const mockResumen = { ventas_hoy: 2, ingresos_hoy: 180, ventas_mes: 20, ingresos_mes: 1800 };

const mockVentaPendiente = {
  id_venta: 1,
  id_cliente: 1,
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
    localStorage.clear();
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

  it("only offers EFECTIVO, YAPE and PLIN as payment methods -- the ones the gym actually uses at the counter", async () => {
    const { container } = render(<Ventas />);
    fireEvent.click(screen.getByText("+ Nueva venta"));
    await waitFor(() => expect(screen.getByText("Confirmar venta")).toBeDefined());

    const metodoPagoSelect = container.querySelector('select[name="metodo_pago"]');
    const opciones = Array.from(metodoPagoSelect.options).map((o) => o.value);
    expect(opciones).toEqual(["EFECTIVO", "YAPE", "PLIN"]);
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
    // El botón "Confirmar" se muestra para ADMIN/ENTRENADOR/RECEPCIONISTA --
    // con el pago único por QR de Yape, quien revisa que llegó el pago y
    // confirma es el personal de mostrador, no solo un ADMIN (ver el
    // comentario y el rol en Ventas.jsx y backend/app/routes/ventas.py).
    localStorage.setItem("rol", "ADMIN");
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.post.mockResolvedValue({ data: {} });

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Confirmar")).toBeDefined());
    fireEvent.click(screen.getByText("Confirmar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ventas/1/confirmar");
    });
  });

  it("also shows the Confirmar button for RECEPCIONISTA", async () => {
    localStorage.setItem("rol", "RECEPCIONISTA");

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Ana López")).toBeDefined());
    expect(screen.getByText("Confirmar")).toBeDefined();
  });

  it("does not show the Confirmar button for a non-staff role", async () => {
    localStorage.setItem("rol", "CLIENTE");

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Ana López")).toBeDefined());
    expect(screen.queryByText("Confirmar")).toBeNull();
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

  it("marks a confirmed sale as delivered", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.post.mockResolvedValue({ data: {} });
    mockApiGet([{ ...mockVentaPendiente, estado: "CONFIRMADA" }]);

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Marcar como entregado")).toBeDefined());
    fireEvent.click(screen.getByText("Marcar como entregado"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ventas/1/entregar");
    });
  });

  it("sends a WhatsApp confirmation to the client for a confirmed sale", async () => {
    const openSpy = vi.fn();
    vi.stubGlobal("open", openSpy);
    mockApiGet([{ ...mockVentaPendiente, estado: "CONFIRMADA" }]);

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Avisar por WhatsApp")).toBeDefined());
    fireEvent.click(screen.getByText("Avisar por WhatsApp"));

    expect(openSpy).toHaveBeenCalledTimes(1);
    const [url, target] = openSpy.mock.calls[0];
    expect(url).toContain("https://wa.me/51987654321?text=");
    const mensaje = decodeURIComponent(url.split("text=")[1]);
    expect(mensaje).toBe(
      "¡Hola Ana! 👋\n\n" +
      "Confirmamos tu pago de *S/ 90.00* por Yape ✅\n\n" +
      "Ya puedes pasar a recogerlo al gimnasio.\n\n" +
      "*GLEYFORGYM* 🏋️"
    );
    expect(target).toBe("_blank");

    vi.unstubAllGlobals();
  });

  it("blocks the WhatsApp confirmation when the client has no valid 9-digit phone", async () => {
    const openSpy = vi.fn();
    vi.stubGlobal("open", openSpy);
    api.get.mockImplementation((url) => {
      if (url === "/ventas/") return Promise.resolve({ data: [{ ...mockVentaPendiente, estado: "CONFIRMADA" }] });
      if (url === "/productos/disponibles") return Promise.resolve({ data: mockProductosDisponibles });
      if (url === "/clientes/") return Promise.resolve({ data: [{ ...mockClientes[0], telefono: null }] });
      if (url === "/ventas/resumen") return Promise.resolve({ data: mockResumen });
      return Promise.resolve({ data: [] });
    });

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Avisar por WhatsApp")).toBeDefined());
    fireEvent.click(screen.getByText("Avisar por WhatsApp"));

    expect(openSpy).not.toHaveBeenCalled();
    await waitFor(() => {
      expect(screen.getByText(/no tiene un teléfono válido de 9 dígitos/)).toBeDefined();
    });

    vi.unstubAllGlobals();
  });

  it("allows downloading the boleta and anular for an already delivered sale, but not marking it as delivered again", async () => {
    mockApiGet([{ ...mockVentaPendiente, estado: "ENTREGADA" }]);

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Descargar boleta")).toBeDefined());
    expect(screen.getByText("Anular")).toBeDefined();
    expect(screen.queryByText("Marcar como entregado")).toBeNull();
  });

  it("downloads the boleta for a confirmed sale", async () => {
    const { descargarBlob } = await import("../utils/descargarArchivo");
    const blobFalso = new Blob(["pdf"]);
    api.get.mockImplementation((url) => {
      if (url === "/ventas/") return Promise.resolve({ data: [{ ...mockVentaPendiente, estado: "CONFIRMADA" }] });
      if (url === "/productos/disponibles") return Promise.resolve({ data: mockProductosDisponibles });
      if (url === "/clientes/") return Promise.resolve({ data: mockClientes });
      if (url === "/ventas/resumen") return Promise.resolve({ data: mockResumen });
      if (url === "/ventas/1/boleta") return Promise.resolve({ data: blobFalso });
      return Promise.resolve({ data: [] });
    });

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Descargar boleta")).toBeDefined());
    fireEvent.click(screen.getByText("Descargar boleta"));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/ventas/1/boleta", { responseType: "blob" });
      expect(descargarBlob).toHaveBeenCalledWith(blobFalso, "boleta-venta-1.pdf");
    });
  });

  it("shows an error when downloading the boleta fails", async () => {
    api.get.mockImplementation((url) => {
      if (url === "/ventas/") return Promise.resolve({ data: [{ ...mockVentaPendiente, estado: "CONFIRMADA" }] });
      if (url === "/productos/disponibles") return Promise.resolve({ data: mockProductosDisponibles });
      if (url === "/clientes/") return Promise.resolve({ data: mockClientes });
      if (url === "/ventas/resumen") return Promise.resolve({ data: mockResumen });
      if (url === "/ventas/1/boleta") return Promise.reject(new Error("fail"));
      return Promise.resolve({ data: [] });
    });

    render(<Ventas />);
    await waitFor(() => expect(screen.getByText("Descargar boleta")).toBeDefined());
    fireEvent.click(screen.getByText("Descargar boleta"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo descargar la boleta")).toBeDefined();
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
