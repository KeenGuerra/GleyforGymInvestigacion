import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MiNutricion from "./MiNutricion";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockPlan = {
  id_plan: 1,
  objetivo: "PERDIDA_PESO",
  fecha_creacion: "2026-06-01",
  generada_por_ia: true,
  calorias_diarias: 2000,
  proteinas: 150,
  carbohidratos: 200,
  grasas: 60,
  comidas: [
    {
      id_comida: 10,
      tipo_comida: "DESAYUNO",
      descripcion: "Avena con plátano y huevos revueltos",
      calorias_aprox: 450,
      hora_recomendada: "08:00 AM",
    },
  ],
};

describe("MiNutricion Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    localStorage.setItem("id_usuario", "10");

    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1, nombres: "Juan" } });
      }
      if (url.includes("/nutricion/cliente/")) {
        return Promise.resolve({ data: [mockPlan] });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders headers and loads user nutritional plans with meals list", async () => {
    render(<MiNutricion />);
    await waitFor(() => {
      expect(screen.getByText("Hola Juan, aquí puedes revisar tus planes alimenticios.")).toBeDefined();
      expect(screen.getByText("PERDIDA_PESO")).toBeDefined();
      expect(screen.getByText("2000")).toBeDefined();
      expect(screen.getByText("Avena con plátano y huevos revueltos")).toBeDefined();
      expect(screen.getByText("DESAYUNO")).toBeDefined();
    });
  });

  it("downloads the plan PDF when the button is clicked", async () => {
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
      if (url.includes("/clientes/usuario/")) return Promise.resolve({ data: { id_cliente: 1, nombres: "Juan" } });
      if (url.includes("/nutricion/cliente/")) return Promise.resolve({ data: [mockPlan] });
      return Promise.resolve({ data: [] });
    });

    render(<MiNutricion />);
    await waitFor(() => expect(screen.getByText("Descargar PDF")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar PDF"));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/nutricion/1/pdf", { responseType: "blob" });
      expect(clickSpy).toHaveBeenCalled();
    });

    vi.restoreAllMocks();
  });

  it("shows an error when the plan PDF download fails", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/pdf")) return Promise.reject(new Error("fail"));
      if (url.includes("/clientes/usuario/")) return Promise.resolve({ data: { id_cliente: 1, nombres: "Juan" } });
      if (url.includes("/nutricion/cliente/")) return Promise.resolve({ data: [mockPlan] });
      return Promise.resolve({ data: [] });
    });

    render(<MiNutricion />);
    await waitFor(() => expect(screen.getByText("Descargar PDF")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar PDF"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo descargar el PDF del plan")).toBeDefined();
    });
  });
});
