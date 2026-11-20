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
    expect(screen.getByText("Todo lo que necesitas para entrenar mejor")).toBeDefined();

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

  it("renders the contact section from the editable site configuration, not hardcoded values", async () => {
    api.get.mockImplementation((url) => {
      if (url === "/configuracion/") {
        return Promise.resolve({
          data: {
            telefono: "+51 111222333",
            email: "nuevo@gleyforgym.com",
            direccion: "Nueva sede, Huancayo",
            facebook_url: "https://facebook.com/nueva",
            instagram_url: null,
            tiktok_url: null,
            whatsapp_numero: "51111222333",
            mapa_embed_url: "https://maps.example.com/nuevo",
            logo_url: null,
          },
        });
      }
      return Promise.resolve({ data: mockPlanes });
    });

    render(
      <MemoryRouter>
        <Inicio />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Nueva sede, Huancayo")).toBeDefined();
      expect(screen.getByText("+51 111222333")).toBeDefined();
      expect(screen.getByText("nuevo@gleyforgym.com")).toBeDefined();
    });
    expect(screen.getByLabelText("Facebook").getAttribute("href")).toBe("https://facebook.com/nueva");
    expect(screen.queryByLabelText("Instagram")).toBeNull();
    expect(screen.getByTitle("Mapa gimnasio").getAttribute("src")).toBe("https://maps.example.com/nuevo");
  });
});
