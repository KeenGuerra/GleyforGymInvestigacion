import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import DetallePlanNutricional from "./DetallePlanNutricional";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
  useParams: () => ({ id: "10" }),
}));

const mockPlan = {
  id_plan: 10,
  objetivo: "Dieta Hiperproteica",
  estado: "ACTIVO",
  generada_por_ia: true,
  fecha_creacion: "2026-06-01",
  calorias_diarias: 2500,
  proteinas: 150,
  carbohidratos: 200,
  grasas: 70,
  calorias_reales: 2480,
  proteinas_reales: 148,
  carbohidratos_reales: 198,
  grasas_reales: 68,
  comidas: [
    {
      id_comida: 5,
      tipo_comida: "Desayuno",
      descripcion: "Avena con plátano",
      calorias_aprox: 400,
      hora_recomendada: "08:00 AM",
    },
  ],
};

describe("DetallePlanNutricional Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockPlan });
  });

  it("renders the header and the plan's macros and meals", async () => {
    render(<DetallePlanNutricional />);
    await waitFor(() => {
      expect(screen.getByText("Dieta Hiperproteica")).toBeDefined();
      expect(screen.getByText("2500 kcal")).toBeDefined();
      expect(screen.getByText("2480 kcal")).toBeDefined();
      expect(screen.getByText("Avena con plátano")).toBeDefined();
    });
  });

  it("shows an empty state when the plan has no meals", async () => {
    api.get.mockResolvedValue({ data: { ...mockPlan, comidas: [] } });
    render(<DetallePlanNutricional />);

    await waitFor(() => {
      expect(screen.getByText("Este plan no tiene comidas")).toBeDefined();
    });
  });

  it("downloads the PDF when the button is clicked", async () => {
    URL.createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    URL.revokeObjectURL = vi.fn();
    const clickSpy = vi.fn();
    const crearElementoOriginal = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag) => {
      const el = crearElementoOriginal(tag);
      el.click = clickSpy;
      return el;
    });

    api.get.mockImplementation((url) => {
      if (url.includes("/pdf")) return Promise.resolve({ data: new Blob(["pdf"]) });
      return Promise.resolve({ data: mockPlan });
    });

    render(<DetallePlanNutricional />);
    await waitFor(() => expect(screen.getByText("Dieta Hiperproteica")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar PDF"));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/nutricion/10/pdf", { responseType: "blob" });
      expect(clickSpy).toHaveBeenCalled();
    });

    vi.restoreAllMocks();
  });

  it("shows an error when the PDF download fails", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/pdf")) return Promise.reject(new Error("fail"));
      return Promise.resolve({ data: mockPlan });
    });

    render(<DetallePlanNutricional />);
    await waitFor(() => expect(screen.getByText("Dieta Hiperproteica")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar PDF"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo descargar el PDF del plan")).toBeDefined();
    });
  });

  it("shows an error when loading the plan fails", async () => {
    api.get.mockRejectedValue(new Error("fail"));
    render(<DetallePlanNutricional />);

    await waitFor(() => {
      expect(screen.getByText("No se pudo cargar el detalle del plan nutricional.")).toBeDefined();
    });
  });
});
