import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Rutinas from "./Rutinas";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockClientes = [
  { id_cliente: 1, nombres: "Juan", apellidos: "Perez", estado: "ACTIVO" },
];

const mockRutinas = [
  {
    id_rutina: 10,
    id_cliente: 1,
    nombre: "Rutina Hipertrofia Pecho",
    objetivo: "HIPERTROFIA",
    nivel: "INTERMEDIO",
    fecha_creacion: "2026-06-01",
    generada_por_ia: true,
    estado: "ACTIVA",
  },
];

describe("Rutinas Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) {
        return Promise.resolve({ data: mockClientes });
      }
      if (url.includes("/rutinas/")) {
        return Promise.resolve({ data: mockRutinas });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders header, stats and lists routines", async () => {
    render(
      <MemoryRouter>
        <Rutinas />
      </MemoryRouter>
    );
    expect(screen.getByText("Rutinas personalizadas")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Rutina Hipertrofia Pecho")).toBeDefined();
      expect(screen.getByText("Juan Perez")).toBeDefined();
    });
  });

  it("filters routines based on search term", async () => {
    render(
      <MemoryRouter>
        <Rutinas />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar por cliente, rutina, objetivo, nivel o estado...")).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText("Buscar por cliente, rutina, objetivo, nivel o estado...");
    fireEvent.change(searchInput, { target: { value: "Fuerza" } });

    await waitFor(() => {
      expect(screen.queryByText("Rutina Hipertrofia Pecho")).toBeNull();
    });
  });

  it("triggers IA generation on button click when client is selected", async () => {
    api.post.mockResolvedValue({ data: { id_rutina: 11, nombre: "Rutina generada" } });
    render(
      <MemoryRouter>
        <Rutinas />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Generar rutina IA", { selector: "button" })).toBeDefined();
    });

    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "1" } });
    fireEvent.click(screen.getByText("Generar rutina IA", { selector: "button" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/ia/rutina/generar/1");
      expect(mockNavigate).toHaveBeenCalledWith("/rutinas/11/detalle");
    });
  });
});
