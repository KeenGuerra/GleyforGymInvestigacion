import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Entrenadores from "./Entrenadores";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockEntrenadores = [
  {
    id_entrenador: 1,
    id_usuario: 10,
    dni: "71234567",
    nombres: "Carlos",
    apellidos: "Ramos",
    telefono: "987654321",
    especialidad: "Musculación",
    estado: "ACTIVO",
  },
];

describe("Entrenadores Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockEntrenadores });
  });

  it("renders headers and loads the trainers list", async () => {
    render(<Entrenadores />);
    expect(screen.getByText("Lista de entrenadores")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("71234567")).toBeDefined();
      expect(screen.getByText("Carlos")).toBeDefined();
      expect(screen.getByText("Musculación")).toBeDefined();
    });
  });

  it("does not show the internal database id -- DNI is already the real identifier", async () => {
    render(<Entrenadores />);
    await waitFor(() => {
      expect(screen.getByText("71234567")).toBeDefined();
    });
    expect(screen.queryByText("ID")).toBeNull();
    expect(screen.queryByText("#1")).toBeNull();
  });

  it("filters trainers based on search term", async () => {
    render(<Entrenadores />);
    await waitFor(() => expect(screen.getByText("71234567")).toBeDefined());

    fireEvent.change(
      screen.getByPlaceholderText("Buscar por DNI, nombre o especialidad..."),
      { target: { value: "noexiste" } }
    );

    await waitFor(() => {
      expect(screen.getByText("No hay entrenadores registrados")).toBeDefined();
    });
  });

  it("shows form and calls post on registering a new trainer", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Entrenadores />);

    fireEvent.click(screen.getByText("+ Registrar entrenador"));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Registrar entrenador" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("DNI"), { target: { value: "70000000" } });
    fireEvent.change(screen.getByLabelText("Nombres"), { target: { value: "Ana" } });
    fireEvent.change(screen.getByLabelText("Apellidos"), { target: { value: "López" } });
    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "ana@gym.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "secret123" } });

    fireEvent.click(screen.getByText("Registrar entrenador", { selector: "button[type=submit]" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/entrenadores/", {
        dni: "70000000",
        nombres: "Ana",
        apellidos: "López",
        telefono: null,
        especialidad: null,
        correo: "ana@gym.com",
        password: "secret123",
      });
    });
  });

  it("validates required fields before submitting", async () => {
    render(<Entrenadores />);
    fireEvent.click(screen.getByText("+ Registrar entrenador"));

    await waitFor(() => expect(screen.getByLabelText("DNI")).toBeDefined());
    fireEvent.click(screen.getByText("Registrar entrenador", { selector: "button[type=submit]" }));

    await waitFor(() => {
      expect(screen.getByText("Ingrese el DNI")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("enters edit mode and updates trainer details via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Entrenadores />);

    await waitFor(() => expect(screen.getByText("Editar")).toBeDefined());
    fireEvent.click(screen.getByText("Editar"));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Editar entrenador" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Estado"), { target: { value: "INACTIVO" } });
    fireEvent.click(screen.getByText("Actualizar entrenador"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/entrenadores/1", {
        dni: "71234567",
        nombres: "Carlos",
        apellidos: "Ramos",
        telefono: "987654321",
        especialidad: "Musculación",
        estado: "INACTIVO",
      });
    });
  });

  it("deactivates a trainer on confirm", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Entrenadores />);
    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());

    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/entrenadores/1");
    });
  });

  it("shows an Activar button instead of Desactivar for an INACTIVO trainer, and reactivates it", async () => {
    api.get.mockResolvedValue({ data: [{ ...mockEntrenadores[0], estado: "INACTIVO" }] });
    api.put.mockResolvedValue({ data: {} });

    render(<Entrenadores />);
    await waitFor(() => expect(screen.getByText("Activar")).toBeDefined());
    expect(screen.queryByText("Desactivar")).toBeNull();

    fireEvent.click(screen.getByText("Activar"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/entrenadores/1", { estado: "ACTIVO" });
    });
  });

  it("does not deactivate when confirm is cancelled", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    render(<Entrenadores />);

    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    expect(api.delete).not.toHaveBeenCalled();
  });

  it("shows error message when creation fails", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "El DNI ya está registrado" } },
    });
    render(<Entrenadores />);

    fireEvent.click(screen.getByText("+ Registrar entrenador"));
    await waitFor(() => expect(screen.getByLabelText("DNI")).toBeDefined());

    fireEvent.change(screen.getByLabelText("DNI"), { target: { value: "70000000" } });
    fireEvent.change(screen.getByLabelText("Nombres"), { target: { value: "Ana" } });
    fireEvent.change(screen.getByLabelText("Apellidos"), { target: { value: "López" } });
    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "ana@gym.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "secret123" } });
    fireEvent.click(screen.getByText("Registrar entrenador", { selector: "button[type=submit]" }));

    await waitFor(() => {
      expect(screen.getByText("El DNI ya está registrado")).toBeDefined();
    });
  });

  it("shows a generic error message when loading the list fails", async () => {
    api.get.mockRejectedValue(new Error("Network Error"));
    render(<Entrenadores />);

    await waitFor(() => {
      expect(screen.getByText("Error al cargar entrenadores")).toBeDefined();
    });
  });
});
