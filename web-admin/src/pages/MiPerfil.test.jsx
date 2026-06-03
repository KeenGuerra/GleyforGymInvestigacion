import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MiPerfil from "./MiPerfil";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    put: vi.fn(),
  },
}));

const mockCliente = {
  id_cliente: 1,
  nombres: "Juan",
  apellidos: "Perez",
  correo: "juan@test.com",
  telefono: "999888777",
  direccion: "Av. Test 123",
  edad: 30,
  peso: 75,
  estatura: 1.75,
  objetivo: "Perder peso",
  nivel: "INTERMEDIO",
  restricciones_medicas: "Ninguna",
  estado: "ACTIVO",
  membresia_activa: null,
};

describe("MiPerfil Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.setItem("correo", "juan@test.com");
    api.get.mockResolvedValue({ data: mockCliente });
  });

  // ── Caja negra: renderizado con datos ─────────────────────────────────────
  it("renders profile loading and then loaded data", async () => {
    render(<MiPerfil />);
    await waitFor(() => {
      expect(screen.getByText("Juan Perez")).toBeDefined();
    });
    expect(screen.getByText("Datos personales")).toBeDefined();
  });

  // ── Caja blanca: toggle modo edición ─────────────────────────────────────
  it("toggles edit mode and updates profile", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<MiPerfil />);

    await waitFor(() => {
      expect(screen.getByText("Juan Perez")).toBeDefined();
    });

    // Abrir formulario de edición
    fireEvent.click(screen.getByText("Editar perfil"));
    expect(screen.getByText("Editar mi información")).toBeDefined();

    fireEvent.change(screen.getByLabelText(/teléfono/i), {
      target: { value: "111222333" },
    });

    fireEvent.click(screen.getByText("Guardar cambios"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalled();
    });
  });
});
