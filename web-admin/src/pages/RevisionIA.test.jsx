import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import RevisionIA from "./RevisionIA";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
  },
}));

const mockClientes = [{ id_cliente: 1, nombres: "Juan", apellidos: "Perez" }];

const mockRutinaPendiente = {
  id_rutina: 10,
  id_cliente: 1,
  nombre: "Rutina IA para ganancia muscular",
  objetivo: "Ganar masa muscular",
  estado_revision: "pendiente",
  fecha_creacion: "2026-11-01T10:00:00",
  editado_antes_revision: false,
  observaciones_revision: null,
};

const mockPlanPendiente = {
  id_plan: 20,
  id_cliente: 1,
  objetivo: "Bajar de peso",
  estado_revision: "pendiente",
  fecha_creacion: "2026-11-02T10:00:00",
  editado_antes_revision: false,
  observaciones_revision: null,
  comidas: [
    { tipo_comida: "DESAYUNO", descripcion: "Avena", calorias_aprox: 400, hora_recomendada: "08:00", id_comida_catalogo: 1 },
  ],
};

function mockDefault() {
  api.get.mockImplementation((url) => {
    if (url === "/clientes/") return Promise.resolve({ data: mockClientes });
    if (url === "/rutinas/pendientes") return Promise.resolve({ data: [mockRutinaPendiente] });
    if (url === "/nutricion/pendientes") return Promise.resolve({ data: [mockPlanPendiente] });
    return Promise.resolve({ data: [] });
  });
}

describe("RevisionIA Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockDefault();
  });

  it("renders the pending routines and plans with client names", async () => {
    render(<RevisionIA />);

    await waitFor(() => {
      expect(screen.getByText("Rutina IA para ganancia muscular")).toBeDefined();
      expect(screen.getByText("Plan nutricional #20")).toBeDefined();
      expect(screen.getAllByText("Juan Perez").length).toBe(2);
    });
  });

  it("approves a routine and reloads the list", async () => {
    api.post.mockResolvedValue({ data: { mensaje: "ok", estado_revision: "aprobada" } });

    render(<RevisionIA />);
    await waitFor(() => expect(screen.getByText("Rutina IA para ganancia muscular")).toBeDefined());

    fireEvent.click(screen.getAllByText("Aprobar")[0]);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/rutinas/10/aprobar");
    });
  });

  it("rejects a routine with a reason from the prompt", async () => {
    vi.stubGlobal("prompt", vi.fn().mockReturnValue("No cumple el nivel del cliente"));
    api.post.mockResolvedValue({ data: { mensaje: "ok", estado_revision: "rechazada" } });

    render(<RevisionIA />);
    await waitFor(() => expect(screen.getByText("Rutina IA para ganancia muscular")).toBeDefined());

    fireEvent.click(screen.getAllByText("Rechazar")[0]);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/rutinas/10/rechazar", { motivo: "No cumple el nivel del cliente" });
    });
  });

  it("does not reject when the prompt is cancelled", async () => {
    vi.stubGlobal("prompt", vi.fn().mockReturnValue(null));

    render(<RevisionIA />);
    await waitFor(() => expect(screen.getByText("Rutina IA para ganancia muscular")).toBeDefined());

    fireEvent.click(screen.getAllByText("Rechazar")[0]);

    expect(api.post).not.toHaveBeenCalled();
  });

  it("opens the plan editor, removes a meal and saves the changes", async () => {
    api.put.mockResolvedValue({ data: { mensaje: "ok" } });

    render(<RevisionIA />);
    await waitFor(() => expect(screen.getByText("Plan nutricional #20")).toBeDefined());

    const filaPlan = screen.getByText("Plan nutricional #20").closest("tr");
    fireEvent.click(within(filaPlan).getByText("Editar"));

    await waitFor(() => expect(screen.getByText("Editando plan nutricional")).toBeDefined());
    expect(screen.getByDisplayValue("Avena")).toBeDefined();

    fireEvent.click(screen.getByText("Quitar"));
    fireEvent.click(screen.getByText("Guardar cambios"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/nutricion/20/comidas", {
        comidas: [],
        observaciones_revision: null,
      });
    });
  });

  it("adds a catalog meal using its real name, not its short description tag", async () => {
    const mockComidas = [
      { id_comida_catalogo: 5, nombre: "Yogur griego con frutos secos", descripcion: "Snack proteico", tipo_comida: "SNACK", calorias: 220 },
    ];
    api.get.mockImplementation((url) => {
      if (url === "/clientes/") return Promise.resolve({ data: mockClientes });
      if (url === "/rutinas/pendientes") return Promise.resolve({ data: [mockRutinaPendiente] });
      if (url === "/nutricion/pendientes") return Promise.resolve({ data: [mockPlanPendiente] });
      if (url === "/comidas/") return Promise.resolve({ data: mockComidas });
      return Promise.resolve({ data: [] });
    });
    api.put.mockResolvedValue({ data: { mensaje: "ok" } });

    render(<RevisionIA />);
    await waitFor(() => expect(screen.getByText("Plan nutricional #20")).toBeDefined());

    const filaPlan = screen.getByText("Plan nutricional #20").closest("tr");
    fireEvent.click(within(filaPlan).getByText("Editar"));

    await waitFor(() => expect(screen.getByText("Editando plan nutricional")).toBeDefined());

    const selectComida = screen
      .getByText("Agregar comida del catálogo")
      .parentElement.querySelector("select");
    fireEvent.change(selectComida, { target: { value: "5" } });

    fireEvent.click(screen.getByText("Guardar cambios"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/nutricion/20/comidas", {
        comidas: [
          { tipo_comida: "DESAYUNO", descripcion: "Avena", calorias_aprox: 400, hora_recomendada: "08:00", id_comida_catalogo: 1 },
          { tipo_comida: "SNACK", descripcion: "Yogur griego con frutos secos", calorias_aprox: 220, hora_recomendada: "", id_comida_catalogo: 5 },
        ],
        observaciones_revision: null,
      });
    });
  });

  it("shows an error when loading the review tray fails", async () => {
    api.get.mockRejectedValue(new Error("fail"));

    render(<RevisionIA />);

    await waitFor(() => {
      expect(screen.getByText("Error al cargar la bandeja de revisión")).toBeDefined();
    });
  });
});
