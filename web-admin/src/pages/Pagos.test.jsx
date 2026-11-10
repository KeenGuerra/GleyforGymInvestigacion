import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Pagos from "./Pagos";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockPagos = [
  {
    id_pago: 1,
    id_cliente: 1,
    id_cliente_membresia: 10,
    monto: 100,
    metodo_pago: "EFECTIVO",
    fecha_pago: "2026-06-01",
    estado: "PAGADO",
  },
];

const mockClientes = [
  { id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO" },
];

const mockAsignaciones = [
  {
    id_cliente_membresia: 10,
    id_cliente: 1,
    estado: "ACTIVA",
    nombre_membresia: "Plan Oro",
    fecha_fin: "2026-12-01",
  },
];

describe("Pagos Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/cliente-membresias/")) return Promise.resolve({ data: mockAsignaciones });
      return Promise.resolve({ data: mockPagos });
    });
  });

  it("renders headers, payment form and payments list", async () => {
    render(<Pagos />);
    expect(screen.getByText("Gestión de pagos")).toBeDefined();
    expect(screen.getByText("Lista de pagos")).toBeDefined();
    await waitFor(() => {
      expect(screen.getAllByText("Juan Perez").length).toBeGreaterThan(0);
    });
  });

  it("shows the plan name in the Membresía dropdown, not just its internal id", async () => {
    render(<Pagos />);

    fireEvent.change(await screen.findByLabelText("Cliente"), { target: { value: "1" } });

    await waitFor(() => {
      expect(
        screen.getByRole("option", { name: "Plan Oro (ACTIVA, vence 1/12/2026)" })
      ).toBeDefined();
    });
    expect(screen.queryByText("#10")).toBeNull();
  });

  it("fails validation if form fields are missing or invalid", async () => {
    render(<Pagos />);

    // Espera a que carguen los clientes/membresías antes de interactuar con
    // los selects: si no, la opción "1" todavía no existe en el DOM y el
    // fireEvent.change de más abajo se pierde (carrera intermitente en CI).
    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Juan Perez" })).toBeDefined();
    });

    // 1. Missing client
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      expect(screen.getByText("Seleccione un cliente")).toBeDefined();
    });

    // Select client
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });

    // 1b. Missing membership
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      expect(screen.getByText("Seleccione la membresía asociada a este pago")).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Membresía"), { target: { value: "10" } });

    // 2. Monto zero or negative
    fireEvent.change(screen.getByLabelText("Monto (S/)"), { target: { value: "0" } });
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      expect(screen.getByText("El monto debe ser mayor a 0")).toBeDefined();
    });

    // Set monto
    fireEvent.change(screen.getByLabelText("Monto (S/)"), { target: { value: "120" } });

    // 3. Missing metodo_pago
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      expect(screen.getByText("Seleccione un método de pago")).toBeDefined();
    });
  });

  it("submits the form successfully to create a new payment", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Juan Perez" })).toBeDefined();
    });

    const fechaPagoInput = screen.getByLabelText("Fecha de pago");
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Membresía"), { target: { value: "10" } });
    fireEvent.change(screen.getByLabelText("Monto (S/)"), { target: { value: "120" } });
    fireEvent.change(screen.getByLabelText("Método de pago"), { target: { value: "YAPE" } });
    fireEvent.change(fechaPagoInput, { target: { value: "2026-06-02" } });
    // Evita una condición de carrera: sin esto, el clic puede dispararse
    // antes de que React procese estos cambios (mismo fix que en
    // Nutricion.test.jsx/Rutinas.test.jsx, que sí llegó a fallar en CI).
    await waitFor(() => expect(fechaPagoInput.value).toBe("2026-06-02"));

    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/pagos/", {
        id_cliente: 1,
        id_cliente_membresia: 10,
        monto: 120,
        metodo_pago: "YAPE",
        fecha_pago: "2026-06-02",
        estado: "PAGADO",
        observacion: null,
      });
    });
  });

  it("enters edit mode and updates payment via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("Editar")).toBeDefined();
    });

    // Click Edit button on the first payment row
    fireEvent.click(screen.getByText("Editar"));

    // Form title should change to "Editar pago"
    expect(screen.getByRole("heading", { name: "Editar pago" })).toBeDefined();

    // Change amount
    const montoInput = screen.getByLabelText("Monto (S/)");
    fireEvent.change(montoInput, { target: { value: "180" } });
    await waitFor(() => expect(montoInput.value).toBe("180"));

    // Submit form (button is now "Actualizar")
    fireEvent.click(screen.getByRole("button", { name: "Actualizar" }));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/pagos/1", {
        id_cliente_membresia: 10,
        monto: 180,
        metodo_pago: "EFECTIVO",
        fecha_pago: "2026-06-01",
        estado: "PAGADO",
        observacion: null,
      });
    });
  });

  it("anulates a payment with confirmation", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("Anular")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Anular"));

    expect(globalThis.confirm).toHaveBeenCalled();
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/pagos/1");
    });
  });

  it("does not anulate a payment if confirmation is cancelled", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));

    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("Anular")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Anular"));

    expect(globalThis.confirm).toHaveBeenCalled();
    expect(api.delete).not.toHaveBeenCalled();
  });

  it("filters the payments list by search query", async () => {
    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar...")).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText("Buscar...");
    
    // Search non-existent
    fireEvent.change(searchInput, { target: { value: "XYZ" } });
    await waitFor(() => {
      expect(screen.queryByRole("cell", { name: "Juan Perez" })).toBeNull();
    });

    // Search existing payment method
    fireEvent.change(searchInput, { target: { value: "EFECTIVO" } });
    await waitFor(() => {
      expect(screen.getByRole("cell", { name: "Juan Perez" })).toBeDefined();
    });
  });

  it("shows error if loading fails", async () => {
    api.get.mockRejectedValue(new Error("Loading failed"));
    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("Error al cargar los datos de pagos")).toBeDefined();
    });
  });

  it("shows error if payment creation fails", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "El cliente no está activo" } }
    });
    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Juan Perez" })).toBeDefined();
    });

    const metodoPagoSelect = screen.getByLabelText("Método de pago");
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Membresía"), { target: { value: "10" } });
    fireEvent.change(screen.getByLabelText("Monto (S/)"), { target: { value: "120" } });
    fireEvent.change(metodoPagoSelect, { target: { value: "YAPE" } });
    await waitFor(() => expect(metodoPagoSelect.value).toBe("YAPE"));

    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));

    await waitFor(() => {
      expect(screen.getByText("El cliente no está activo")).toBeDefined();
    });
  });

  it("shows error if payment update fails", async () => {
    api.put.mockRejectedValue({
      response: { data: { detail: "Error de red al actualizar" } }
    });
    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("Editar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Editar"));
    fireEvent.click(screen.getByRole("button", { name: "Actualizar" }));

    await waitFor(() => {
      expect(screen.getByText("Error de red al actualizar")).toBeDefined();
    });
  });

  it("shows error if payment anulation fails", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockRejectedValue(new Error("Anulate Error"));

    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("Anular")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Anular"));

    await waitFor(() => {
      expect(screen.getByText("Error al anular el pago")).toBeDefined();
    });
  });

  it("starts a checkout for a pending payment and shows the result in the modal", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/cliente-membresias/")) return Promise.resolve({ data: mockAsignaciones });
      return Promise.resolve({
        data: [{ ...mockPagos[0], estado: "PENDIENTE" }],
      });
    });
    api.post.mockResolvedValue({
      data: {
        id_pago: 1,
        url_checkout: "https://api.culqi.com/v2/orders/ord_test_123",
        qr_yape: "https://niubizqr.pagoefectivo.pe/abc.png",
        id_transaccion_externa: "ord_test_123",
      },
    });

    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("Cobrar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Cobrar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/pagos/1/checkout");
      expect(screen.getByText("Completar pago")).toBeDefined();
      expect(screen.getByAltText("Código QR para pagar con Yape")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Cerrar"));
    expect(screen.queryByText("Completar pago")).toBeNull();
  });

  it("shows a distinct badge and label for a self-service (AUTOSERVICIO) pending payment", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/cliente-membresias/")) return Promise.resolve({ data: mockAsignaciones });
      return Promise.resolve({
        data: [{ ...mockPagos[0], estado: "PENDIENTE", origen: "AUTOSERVICIO" }],
      });
    });

    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("En línea")).toBeDefined();
      expect(screen.getByText("Ver estado")).toBeDefined();
      expect(screen.queryByText("Cobrar")).toBeNull();
    });
  });

  it("shows an error when starting a checkout fails", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockClientes });
      if (url.includes("/cliente-membresias/")) return Promise.resolve({ data: mockAsignaciones });
      return Promise.resolve({
        data: [{ ...mockPagos[0], estado: "PENDIENTE" }],
      });
    });
    api.post.mockRejectedValue({ response: { data: { detail: "CULQI_SECRET_KEY no configurada" } } });

    render(<Pagos />);

    await waitFor(() => {
      expect(screen.getByText("Cobrar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Cobrar"));

    await waitFor(() => {
      expect(screen.getByText("CULQI_SECRET_KEY no configurada")).toBeDefined();
    });
  });
});
