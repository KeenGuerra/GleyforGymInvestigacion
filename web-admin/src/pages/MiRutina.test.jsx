import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MiRutina from "./MiRutina";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

describe("MiRutina Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    localStorage.setItem("id_usuario", "10");

    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1, nombres: "Juan" } });
      }
      if (url.includes("/rutinas/cliente/")) {
        return Promise.resolve({
          data: [
            {
              id_rutina: 15,
              nombre: "Hipertrofia de hombros",
              objetivo: "HIPERTROFIA",
              nivel: "AVANZADO",
              dias_semana: 4,
              fecha_creacion: "2026-06-01",
              generada_por_ia: false,
              estado: "ACTIVA",
            },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders active routines and navigates to details on button click", async () => {
    render(<MiRutina />);
    await waitFor(() => {
      expect(screen.getByText("Hola Juan, aquí puedes revisar tus rutinas asignadas.")).toBeDefined();
      expect(screen.getByText("Hipertrofia de hombros")).toBeDefined();
      expect(screen.getByText("Ver detalle con videos")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Ver detalle con videos"));
    expect(mockNavigate).toHaveBeenCalledWith("/rutinas/15/detalle");
  });

  it("downloads the routine PDF when the button is clicked", async () => {
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
      if (url.includes("/rutinas/cliente/")) {
        return Promise.resolve({
          data: [{ id_rutina: 15, nombre: "Hipertrofia de hombros", estado: "ACTIVA" }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<MiRutina />);
    await waitFor(() => expect(screen.getByText("Descargar PDF")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar PDF"));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/rutinas/15/pdf", { responseType: "blob" });
      expect(clickSpy).toHaveBeenCalled();
    });

    vi.restoreAllMocks();
  });

  it("shows an error when the routine PDF download fails", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/pdf")) return Promise.reject(new Error("fail"));
      if (url.includes("/clientes/usuario/")) return Promise.resolve({ data: { id_cliente: 1, nombres: "Juan" } });
      if (url.includes("/rutinas/cliente/")) {
        return Promise.resolve({
          data: [{ id_rutina: 15, nombre: "Hipertrofia de hombros", estado: "ACTIVA" }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<MiRutina />);
    await waitFor(() => expect(screen.getByText("Descargar PDF")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar PDF"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo descargar el PDF de la rutina")).toBeDefined();
    });
  });
});
