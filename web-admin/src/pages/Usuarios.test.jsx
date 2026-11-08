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

  it("allows creating a user with the RECEPCIONISTA role and counts it in the stats", async () => {
    api.get.mockResolvedValue({
      data: [...mockUsuarios, { id_usuario: 2, correo: "recepcion@gym.com", rol: "RECEPCIONISTA", estado: "ACTIVO", fecha_creacion: "2026-06-01T12:00:00Z" }],
    });
    render(<Usuarios />);

    await waitFor(() => {
      expect(screen.getByText("recepcion@gym.com")).toBeDefined();
    });
    expect(screen.getByText("Recepcionistas")).toBeDefined();

    fireEvent.click(screen.getByText("+ Crear usuario"));
    await waitFor(() => {
      expect(screen.getByLabelText("Rol")).toBeDefined();
    });

    expect(screen.getByRole("option", { name: "RECEPCIONISTA" })).toBeDefined();
  });

  it("does not offer ENTRENADOR as a role when creating a new user (it's created from the Entrenadores screen instead)", async () => {
    render(<Usuarios />);

    fireEvent.click(screen.getByText("+ Crear usuario"));
    await waitFor(() => {
      expect(screen.getByLabelText("Rol")).toBeDefined();
    });

    expect(screen.queryByRole("option", { name: "ENTRENADOR" })).toBeNull();
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

  it("shows an Activar button instead of Desactivar for an INACTIVO user, and reactivates it", async () => {
    api.get.mockResolvedValue({ data: [{ ...mockUsuarios[0], estado: "INACTIVO" }] });
    api.put.mockResolvedValue({ data: {} });

    render(<Usuarios />);
    await waitFor(() => expect(screen.getByText("Activar")).toBeDefined());
    expect(screen.queryByText("Desactivar")).toBeNull();

    fireEvent.click(screen.getByText("Activar"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/usuarios/1", { estado: "ACTIVO" });
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

  it("resets a user's password via the admin flow", async () => {
    api.post.mockResolvedValue({ data: { mensaje: "Contraseña restablecida correctamente" } });

    render(<Usuarios />);
    await waitFor(() => expect(screen.getByText("entrenador@gym.com")).toBeDefined());

    fireEvent.click(screen.getByText("Restablecer contraseña", { selector: "button" }));

    await waitFor(() => expect(screen.getByLabelText("Nueva contraseña")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Nueva contraseña"), { target: { value: "claveNueva123" } });
    fireEvent.click(screen.getByText("Guardar nueva contraseña"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/usuarios/1/reset-password-admin", {
        password_nueva: "claveNueva123",
      });
      expect(screen.getByText("Contraseña restablecida correctamente ✔")).toBeDefined();
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
