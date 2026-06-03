import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Membresias from "./Membresias";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockMembresias = [
  {
    id_membresia: 1,
    nombre: "Plan Básico",
    precio: 50,
    duracion_dias: 30,
    estado: "ACTIVO",
    descripcion: "Acceso básico",
    beneficios: "Cardio",
  },
];

describe("Membresias Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockMembresias });
  });

  // ── Caja negra: renderizado inicial ───────────────────────────────────────
  // "Plan Básico" aparece dos veces en el DOM: en <strong> (stats) y <h3> (card)
  it("renders the list of memberships and h1 header", async () => {
    render(<Membresias />);
    expect(screen.getByText("Planes de membresía")).toBeDefined();
    await waitFor(() => {
      // Usar getAllByText por el duplicado en stats + card
      const items = screen.getAllByText("Plan Básico");
      expect(items.length).toBeGreaterThanOrEqual(1);
    });
  });

  // ── Boundary Value: precio = 0 debe ser inválido ──────────────────────────
  it("shows form validation error when price is 0 (BVA: precio=0)", async () => {
    render(<Membresias />);
    fireEvent.click(screen.getByText("+ Crear plan"));

    await waitFor(() => expect(screen.getByLabelText("Nombre")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Nombre"), {
      target: { value: "Plan Test" },
    });
    fireEvent.change(screen.getByLabelText("Precio"), {
      target: { value: "0" },
    });

    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(screen.getByText(/precio inv/i)).toBeDefined();
    });
  });

  // ── Caja blanca: flujo de creación exitosa ────────────────────────────────
  it("submits the form data when inputs are valid", async () => {
    api.post.mockResolvedValue({ data: { id_membresia: 2 } });
    render(<Membresias />);
    fireEvent.click(screen.getByText("+ Crear plan"));

    await waitFor(() => expect(screen.getByLabelText("Nombre")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Plan Gold" } });
    fireEvent.change(screen.getByLabelText("Precio"), { target: { value: "100" } });
    fireEvent.change(screen.getByLabelText("Duración"), { target: { value: "30" } });

    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
  });

  it("enters edit mode and updates membership details via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Membresias />);

    await waitFor(() => {
      expect(screen.getAllByText("Editar").length).toBeGreaterThan(0);
    });

    fireEvent.click(screen.getAllByText("Editar")[0]);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Editar plan" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Plan Premium" } });
    fireEvent.click(screen.getByText("Actualizar"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalled();
    });
  });

  it("desactivates membership on confirm and handles API error", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Membresias />);
    await waitFor(() => {
      expect(screen.getByText("Desactivar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/membresias/1");
    });

    // Error case
    api.delete.mockRejectedValue(new Error("Network Error"));
    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo desactivar la membresía")).toBeDefined();
    });
  });

  it("does not deactivate membership if confirm is rejected", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    render(<Membresias />);

    await waitFor(() => {
      expect(screen.getByText("Desactivar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar"));
    expect(api.delete).not.toHaveBeenCalled();
  });
});
