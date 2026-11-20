import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Configuracion from "./Configuracion";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    put: vi.fn(),
  },
}));

const mockConfiguracion = {
  telefono: "+51 902321009",
  email: "gleyfor3@gmail.com",
  direccion: "Chupaca, Perú",
  facebook_url: "https://facebook.com/gleyforgym",
  instagram_url: "",
  tiktok_url: "",
  whatsapp_numero: "51902321009",
  mapa_embed_url: "https://maps.example.com",
  logo_url: null,
};

describe("Configuracion Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockConfiguracion });
  });

  it("loads and shows the current configuration in the form", async () => {
    render(<Configuracion />);

    await waitFor(() => {
      expect(screen.getByLabelText("Teléfono").value).toBe("+51 902321009");
      expect(screen.getByLabelText("Email").value).toBe("gleyfor3@gmail.com");
      expect(screen.getByLabelText("Dirección").value).toBe("Chupaca, Perú");
    });
  });

  it("saves the form via PUT /configuracion/", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Configuracion />);

    await waitFor(() => expect(screen.getByLabelText("Teléfono").value).toBe("+51 902321009"));

    fireEvent.change(screen.getByLabelText("Teléfono"), { target: { value: "+51 999999999" } });
    fireEvent.click(screen.getByText("Guardar configuración"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/configuracion/", expect.objectContaining({
        telefono: "+51 999999999",
      }));
    });
    await waitFor(() => expect(screen.getByText("Configuración guardada correctamente.")).toBeDefined());
  });

  it("uploads a new logo via PUT /configuracion/media when a file is chosen", async () => {
    // jsdom no implementa URL.createObjectURL (se usa para la vista previa
    // del logo recién elegido, antes de guardar) -- mismo patrón ya usado en
    // DetalleRutina.test.jsx/Reportes.test.jsx para este mismo caso.
    URL.createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    api.put.mockResolvedValue({ data: {} });
    render(<Configuracion />);

    await waitFor(() => expect(screen.getByLabelText("Teléfono").value).toBe("+51 902321009"));

    const archivo = new File(["img"], "logo.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText("Logo del gimnasio"), { target: { files: [archivo] } });
    fireEvent.click(screen.getByText("Guardar configuración"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith(
        "/configuracion/media",
        expect.any(FormData),
        expect.objectContaining({ headers: { "Content-Type": "multipart/form-data" } })
      );
    });
    const mediaCall = api.put.mock.calls.find((call) => call[0] === "/configuracion/media");
    expect(mediaCall[1].get("logo")).toBe(archivo);
  });

  it("does not call the media endpoint when no logo file is chosen", async () => {
    api.put.mockResolvedValue({ data: {} });
    render(<Configuracion />);

    await waitFor(() => expect(screen.getByLabelText("Teléfono").value).toBe("+51 902321009"));
    fireEvent.click(screen.getByText("Guardar configuración"));

    await waitFor(() => expect(api.put).toHaveBeenCalledWith("/configuracion/", expect.any(Object)));
    expect(api.put).toHaveBeenCalledTimes(1);
  });

  it("shows an error when saving fails", async () => {
    api.put.mockRejectedValue({ response: { data: { detail: "Error de red" } } });
    render(<Configuracion />);

    await waitFor(() => expect(screen.getByLabelText("Teléfono").value).toBe("+51 902321009"));
    fireEvent.click(screen.getByText("Guardar configuración"));

    await waitFor(() => {
      expect(screen.getByText("Error de red")).toBeDefined();
    });
  });

  it("shows an error when loading fails", async () => {
    api.get.mockRejectedValue(new Error("network error"));
    render(<Configuracion />);

    await waitFor(() => {
      expect(screen.getByText("No se pudo cargar la configuración del sitio")).toBeDefined();
    });
  });
});
