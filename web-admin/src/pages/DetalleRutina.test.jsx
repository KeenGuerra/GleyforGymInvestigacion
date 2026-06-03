import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DetalleRutina from "./DetalleRutina";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
  useParams: () => ({ id: "3" }),
}));

const mockRutina = {
  id_rutina: 3,
  nombre: "Rutina Fuerza de Piernas",
  descripcion: "Enfoque en cuádriceps y glúteos",
  objetivo: "HIPERTROFIA",
  nivel: "INTERMEDIO",
  dias_semana: 3,
  estado: "ACTIVA",
  generada_por_ia: true,
  ejercicios: [
    {
      id_rutina_ejercicio: 21,
      nombre: "Sentadillas libres",
      grupo_muscular: "Piernas",
      dia_semana: "Lunes",
      series: 4,
      repeticiones: "10-12",
      descanso_segundos: 90,
      descripcion: "Bajar a 90 grados",
      instrucciones: "Mantener la espalda recta",
      video_url: "http://example.com/video.mp4",
    },
  ],
};

describe("DetalleRutina Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockRutina });
  });

  it("renders headers and loads routine exercises with details", async () => {
    render(<DetalleRutina />);
    await waitFor(() => {
      expect(screen.getByText("Rutina Fuerza de Piernas")).toBeDefined();
      expect(screen.getByText("Enfoque en cuádriceps y glúteos")).toBeDefined();
      expect(screen.getByText("Sentadillas libres")).toBeDefined();
      expect(screen.getByText("Bajar a 90 grados")).toBeDefined();
      expect(screen.getByText("Mantener la espalda recta")).toBeDefined();
    });
  });
});
