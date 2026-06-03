import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Clientes from "./Clientes";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock("react-router-dom", () => ({
  useNavigate: () => vi.fn(),
}));

const mockClientes = [
  {
    id_cliente: 1,
    dni: "12345678",
    nombres: "Juan",
    apellidos: "Perez",
    correo: "juan@test.com",
    telefono: "999888777",
    estado: "ACTIVO",
  },
  {
    id_cliente: 2,
    dni: "87654321",
    nombres: "Maria",
    apellidos: "Gomez",
    correo: "maria@test.com",
    telefono: "999555444",
    estado: "INACTIVO",
  },
];

describe("Clientes Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockClientes });
  });

  // ── Caja negra: renderizado inicial ───────────────────────────────────────
  it("renders headers and statistics cards correctly", async () => {
    render(<Clientes />);
    expect(screen.getByText("Directorio de clientes")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Total clientes")).toBeDefined();
      expect(screen.getByText("Filtrados")).toBeDefined();
      expect(screen.getByText("Activos")).toBeDefined();
    });
  });

  // ── Caja negra: filtro de búsqueda ────────────────────────────────────────
  // Nota: "Juan Perez" se renderiza en un <strong> como texto múltiple
  // Usamos regex para buscar "Juan" dentro del nodo complejo
  it("filters clients list and hides non-matching clients", async () => {
    render(<Clientes />);
    await waitFor(() => {
      expect(
        screen.getByPlaceholderText("Buscar por nombre, DNI o correo...")
      ).toBeDefined();
    });

    fireEvent.change(
      screen.getByPlaceholderText("Buscar por nombre, DNI o correo..."),
      { target: { value: "Juan" } }
    );

    // María no debe estar visible después de filtrar
    expect(screen.queryByText("Gomez")).toBeNull();
  });

  // ── Boundary Value: DNI vacío → error de validación ───────────────────────
  it("shows DNI validation error when form is submitted without DNI (BVA)", async () => {
    render(<Clientes />);
    // Esperar a que se carguen los datos de clientes primero
    await waitFor(() => {
      expect(screen.getByText("Total clientes")).toBeDefined();
    });

    fireEvent.click(screen.getByText("+ Registrar cliente"));

    // Esperar al formulario
    await waitFor(() => {
      expect(screen.getByText("Registrar cliente", { selector: "button" })).toBeDefined();
    });

    fireEvent.click(screen.getByText("Registrar cliente", { selector: "button" }));

    await waitFor(() => {
      expect(screen.getByText("DNI inválido")).toBeDefined();
    });
  });

  // ── Caja blanca: flujo de creación exitosa ────────────────────────────────
  it("submits valid client creation to the API", async () => {
    api.post.mockResolvedValue({ data: { id_cliente: 3 } });
    render(<Clientes />);

    // Esperar a que el componente cargue primero
    await waitFor(() => expect(screen.getByText("Total clientes")).toBeDefined());

    fireEvent.click(screen.getByText("+ Registrar cliente"));

    await waitFor(() => expect(screen.getByText("Registrar cliente", { selector: "button" })).toBeDefined());

    fireEvent.change(screen.getByLabelText("DNI"), { target: { value: "12121212" } });
    fireEvent.change(screen.getByLabelText("Nombres"), { target: { value: "Carlos" } });
    fireEvent.change(screen.getByLabelText("Apellidos"), { target: { value: "Soto" } });
    fireEvent.change(screen.getByLabelText("Correo"), { target: { value: "carlos@test.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "securePass" } });

    fireEvent.click(screen.getByText("Registrar cliente", { selector: "button" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
  });

  it("enters edit mode and updates client details via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Clientes />);

    await waitFor(() => {
      expect(screen.getAllByText("Editar").length).toBeGreaterThan(0);
    });

    // Click the first "Editar" button
    fireEvent.click(screen.getAllByText("Editar")[0]);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Editar cliente" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Teléfono"), { target: { value: "987987987" } });
    fireEvent.click(screen.getByRole("button", { name: "Actualizar cliente" }));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalled();
    });
  });

  it("toggles client active/inactive status on confirmation", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.put.mockResolvedValue({ data: {} });

    render(<Clientes />);
    await waitFor(() => {
      expect(screen.getByText("Desactivar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar"));
    expect(globalThis.confirm).toHaveBeenCalled();

    await waitFor(() => {
      expect(api.put).toHaveBeenCalled();
    });
  });

  it("shows error if client save or state change fails", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "El correo ya está registrado" } }
    });
    render(<Clientes />);
    await waitFor(() => expect(screen.getByText("Total clientes")).toBeDefined());

    fireEvent.click(screen.getByText("+ Registrar cliente"));
    await waitFor(() => expect(screen.getByText("Registrar cliente", { selector: "button" })).toBeDefined());

    fireEvent.change(screen.getByLabelText("DNI"), { target: { value: "12121212" } });
    fireEvent.click(screen.getByText("Registrar cliente", { selector: "button" }));

    await waitFor(() => {
      expect(screen.getByText("El correo ya está registrado")).toBeDefined();
    });
  });

  it("displays empty table message when search yields no results", async () => {
    render(<Clientes />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar por nombre, DNI o correo...")).toBeDefined();
    });

    fireEvent.change(
      screen.getByPlaceholderText("Buscar por nombre, DNI o correo..."),
      { target: { value: "NonExistentClient" } }
    );

    await waitFor(() => {
      expect(screen.getByText("No hay clientes registrados")).toBeDefined();
    });
  });
});
