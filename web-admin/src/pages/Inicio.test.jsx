import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Inicio from "./Inicio";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
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

const mockPlanes = [
  {
    id_membresia: 1,
    nombre: "Plan Fuerza",
    precio: 90,
    duracion_meses: 1,
    beneficios: "Acceso total\nEvaluación física",
    estado: "ACTIVO",
  },
];

describe("Inicio Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockPlanes });
    localStorage.clear();
  });

  it("renders landing sections, navbar, plans list and handles navigation", async () => {
    render(
      <MemoryRouter>
        <Inicio />
      </MemoryRouter>
    );

    expect(screen.getByText("GleyforGym: tu gimnasio inteligente en Chupaca")).toBeDefined();
    expect(screen.getByText("Todo lo que necesita un gimnasio moderno")).toBeDefined();

    await waitFor(() => {
      expect(screen.getByText("Plan Fuerza")).toBeDefined();
      expect(screen.getByText(/S\/.*90/)).toBeDefined();
      expect(screen.getByText("Acceso total")).toBeDefined();
    });

    const accessBtn = screen.getByText("Comenzar ahora");
    fireEvent.click(accessBtn);
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });

  it("navigates to dashboard if user has token", async () => {
    localStorage.setItem("token", "fake-token");
    render(
      <MemoryRouter>
        <Inicio />
      </MemoryRouter>
    );

    const accessBtn = screen.getAllByText("Ir a mi panel")[0];
    fireEvent.click(accessBtn);
    expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
  });
});
