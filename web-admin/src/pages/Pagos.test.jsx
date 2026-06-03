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
  { id_cliente_membresia: 10, id_cliente: 1, estado: "ACTIVA" },
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

  it("fails validation if form fields are missing or invalid", async () => {
    render(<Pagos />);
    
    // 1. Missing client
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      expect(screen.getByText("Seleccione un cliente")).toBeDefined();
    });

    // Select client
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });

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
      expect(screen.getByLabelText("Cliente")).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Membresía"), { target: { value: "10" } });
    fireEvent.change(screen.getByLabelText("Monto (S/)"), { target: { value: "120" } });
    fireEvent.change(screen.getByLabelText("Método de pago"), { target: { value: "YAPE" } });
    fireEvent.change(screen.getByLabelText("Fecha de pago"), { target: { value: "2026-06-02" } });

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
    fireEvent.change(screen.getByLabelText("Monto (S/)"), { target: { value: "180" } });

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
      expect(screen.getByLabelText("Cliente")).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Monto (S/)"), { target: { value: "120" } });
    fireEvent.change(screen.getByLabelText("Método de pago"), { target: { value: "YAPE" } });

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
});
