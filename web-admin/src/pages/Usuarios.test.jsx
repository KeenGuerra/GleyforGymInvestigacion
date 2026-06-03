import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Usuarios from "./Usuarios";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockUsuarios = [
  {
    id_usuario: 1,
    correo: "entrenador@gym.com",
    rol: "ENTRENADOR",
    estado: "ACTIVO",
    fecha_creacion: "2026-06-01T12:00:00Z",
  },
];

describe("Usuarios Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockUsuarios });
  });

  it("renders headers and loads users list", async () => {
    render(<Usuarios />);
    expect(screen.getByText("Lista de usuarios internos")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("entrenador@gym.com")).toBeDefined();
      expect(screen.getByText("1/6/2026")).toBeDefined(); // Formatted date
    });
  });

  it("filters user list based on search term", async () => {
    render(<Usuarios />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar por correo, rol o estado...")).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText("Buscar por correo, rol o estado...");
    fireEvent.change(searchInput, { target: { value: "admin" } });

    await waitFor(() => {
      expect(screen.queryByText("entrenador@gym.com")).toBeNull();
    });
  });

  it("shows form and calls post on submitting a new user", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Usuarios />);

    await waitFor(() => {
      expect(screen.getByText("+ Crear usuario")).toBeDefined();
    });

    fireEvent.click(screen.getByText("+ Crear usuario"));

    await waitFor(() => {
      expect(screen.getByText("Crear usuario interno", { selector: "h2" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "new@gym.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "secret123" } });
    fireEvent.change(screen.getByLabelText("Rol"), { target: { value: "ADMIN" } });

    fireEvent.click(screen.getByText("Crear usuario"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
  });

  it("enters edit mode and updates user details via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Usuarios />);

    await waitFor(() => {
      expect(screen.getByText("Editar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Editar"));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Editar usuario interno" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Estado"), { target: { value: "INACTIVO" } });
    fireEvent.click(screen.getByText("Actualizar usuario"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalled();
    });
  });

  it("desactivates user on confirm and handles API error", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Usuarios />);
    await waitFor(() => {
      expect(screen.getByText("Desactivar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/usuarios/1");
    });

    // Error case
    api.delete.mockRejectedValue(new Error("Network Error"));
    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(screen.getByText("Error al desactivar usuario")).toBeDefined();
    });
  });

  it("does not deactivate user if confirm is cancelled", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    render(<Usuarios />);

    await waitFor(() => {
      expect(screen.getByText("Desactivar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar"));
    expect(api.delete).not.toHaveBeenCalled();
  });

  it("shows error if user creation fails", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "El correo ya existe" } }
    });
    render(<Usuarios />);
    fireEvent.click(screen.getByText("+ Crear usuario"));

    await waitFor(() => expect(screen.getByLabelText("Correo electrónico")).toBeDefined());
    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "dup@gym.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "secret123" } });
    fireEvent.click(screen.getByText("Crear usuario"));

    await waitFor(() => {
      expect(screen.getByText("El correo ya existe")).toBeDefined();
    });
  });

  it("displays empty message when search yields no users", async () => {
    render(<Usuarios />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar por correo, rol o estado...")).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText("Buscar por correo, rol o estado...");
    fireEvent.change(searchInput, { target: { value: "NonExistentUser" } });

    await waitFor(() => {
      expect(screen.getByText("No hay usuarios internos registrados")).toBeDefined();
    });
  });
});
