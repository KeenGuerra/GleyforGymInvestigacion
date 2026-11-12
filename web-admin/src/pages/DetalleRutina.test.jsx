import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
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

const mockCliente = { id_cliente: 7, nombres: "Carlos Perez", apellidos: "Ramos", telefono: "987654321" };

const mockRutina = {
  id_rutina: 3,
  id_cliente: 7,
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
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: mockCliente });
      return Promise.resolve({ data: mockRutina });
    });
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
      return Promise.resolve({ data: mockRutina });
    });

    render(<DetalleRutina />);
    await waitFor(() => expect(screen.getByText("Rutina Fuerza de Piernas")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar PDF"));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/rutinas/3/pdf", { responseType: "blob" });
      expect(clickSpy).toHaveBeenCalled();
    });

    vi.restoreAllMocks();
  });

  it("sends a short WhatsApp notice about the routine, not the full exercise list", async () => {
    const openSpy = vi.fn();
    vi.stubGlobal("open", openSpy);

    render(<DetalleRutina />);
    await waitFor(() => expect(screen.getByText("Rutina Fuerza de Piernas")).toBeDefined());

    fireEvent.click(screen.getByText("Enviar por WhatsApp"));

    expect(openSpy).toHaveBeenCalledTimes(1);
    const [url, target] = openSpy.mock.calls[0];
    expect(url).toContain("https://wa.me/51987654321?text=");
    const mensaje = decodeURIComponent(url.split("text=")[1]);
    expect(mensaje).toBe(
      "¡Hola Carlos! 👋\n\n" +
      "Tu rutina *Rutina Fuerza de Piernas* (INTERMEDIO, HIPERTROFIA) ya está lista 💪\n\n" +
      "Entra a la app para verla completa.\n\n" +
      "*GLEYFORGYM* 🏋️"
    );
    expect(target).toBe("_blank");
    expect(mensaje).not.toContain("Sentadillas libres");

    vi.unstubAllGlobals();
  });

  it("blocks the WhatsApp message when the client has no valid 9-digit phone", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/")) return Promise.resolve({ data: { ...mockCliente, telefono: null } });
      return Promise.resolve({ data: mockRutina });
    });
    const openSpy = vi.fn();
    vi.stubGlobal("open", openSpy);

    render(<DetalleRutina />);
    await waitFor(() => expect(screen.getByText("Rutina Fuerza de Piernas")).toBeDefined());

    fireEvent.click(screen.getByText("Enviar por WhatsApp"));

    expect(openSpy).not.toHaveBeenCalled();
    await waitFor(() => {
      expect(screen.getByText(/no tiene un teléfono válido de 9 dígitos/)).toBeDefined();
    });

    vi.unstubAllGlobals();
  });

  it("shows an error when the PDF download fails", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/pdf")) return Promise.reject(new Error("fail"));
      return Promise.resolve({ data: mockRutina });
    });

    render(<DetalleRutina />);
    await waitFor(() => expect(screen.getByText("Rutina Fuerza de Piernas")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar PDF"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo descargar el PDF de la rutina")).toBeDefined();
    });
  });
});
