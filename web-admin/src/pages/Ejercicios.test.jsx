import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Ejercicios from "./Ejercicios";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockEjercicios = [
  {
    id_ejercicio: 1,
    nombre: "Sentadilla",
    grupo_muscular: "Piernas",
    nivel: "PRINCIPIANTE",
    objetivo: "FUERZA",
    estado: "ACTIVO",
    descripcion: "Un gran ejercicio",
    instrucciones: "Baja y sube",
    video_url: "http://example.com/video.mp4",
  },
];

describe("Ejercicios Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes("/ejercicios/")) return Promise.resolve({ data: mockEjercicios });
      return Promise.resolve({ data: [] });
    });
  });

  it("renders headers and loads exercises cards list", async () => {
    render(<Ejercicios />);
    expect(screen.getByText("Gestión de ejercicios")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Sentadilla")).toBeDefined();
      expect(screen.getByText("Piernas")).toBeDefined();
    });
  });

  it("fails validation for incorrect input values during registration", async () => {
    render(<Ejercicios />);
    
    // Open form
    fireEvent.click(screen.getByText("+ Registrar ejercicio"));

    // 1. Missing name
    fireEvent.click(screen.getByRole("button", { name: "Guardar ejercicio" }));
    await waitFor(() => {
      expect(screen.getByText("Ingrese el nombre del ejercicio")).toBeDefined();
    });

    // Fill name
    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Sentadilla" } });

    // 2. Missing muscle group
    fireEvent.click(screen.getByRole("button", { name: "Guardar ejercicio" }));
    await waitFor(() => {
      expect(screen.getByText("Ingrese el grupo muscular")).toBeDefined();
    });

    // Fill muscle group
    fireEvent.change(screen.getByLabelText("Grupo muscular"), { target: { value: "Piernas" } });

    // 3. Missing level
    fireEvent.click(screen.getByRole("button", { name: "Guardar ejercicio" }));
    await waitFor(() => {
      expect(screen.getByText("Seleccione el nivel")).toBeDefined();
    });
  });

  it("submits the form successfully with video file", async () => {
    api.post.mockResolvedValue({ data: {} });
    render(<Ejercicios />);

    fireEvent.click(screen.getByText("+ Registrar ejercicio"));

    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Curl de bíceps" } });
    fireEvent.change(screen.getByLabelText("Grupo muscular"), { target: { value: "Bíceps" } });
    fireEvent.change(screen.getByLabelText("Nivel"), { target: { value: "PRINCIPIANTE" } });
    
    // Select video file
    const file = new File(["test"], "test.mp4", { type: "video/mp4" });
    const videoInput = screen.getByLabelText("Video");
    
    fireEvent.change(videoInput, { target: { files: [file] } });
    
    fireEvent.click(screen.getByRole("button", { name: "Guardar ejercicio" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
  });

  it("handles cancel button properly", async () => {
    render(<Ejercicios />);
    fireEvent.click(screen.getByText("+ Registrar ejercicio"));
    expect(screen.getByRole("heading", { name: "Registrar ejercicio" })).toBeDefined();

    fireEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("heading", { name: "Registrar ejercicio" })).toBeNull();
  });

  it("desactivates an exercise on confirmation", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Ejercicios />);

    await waitFor(() => {
      expect(screen.getByText("Desactivar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar"));

    expect(globalThis.confirm).toHaveBeenCalled();
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/ejercicios/1");
    });
  });

  it("does not deactivate an exercise if confirmation is cancelled", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));

    render(<Ejercicios />);

    await waitFor(() => {
      expect(screen.getByText("Desactivar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar"));

    expect(globalThis.confirm).toHaveBeenCalled();
    expect(api.delete).not.toHaveBeenCalled();
  });

  it("filters exercises cards based on search input", async () => {
    render(<Ejercicios />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Buscar...")).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText("Buscar...");
    fireEvent.change(searchInput, { target: { value: "Espalda" } });

    await waitFor(() => {
      expect(screen.queryByText("Sentadilla")).toBeNull();
    });
  });

  it("shows error if loading fails", async () => {
    api.get.mockRejectedValue(new Error("Network Error"));
    render(<Ejercicios />);

    await waitFor(() => {
      expect(screen.getByText("No se pudieron cargar los ejercicios")).toBeDefined();
    });
  });

  it("renders Sin video placeholder if exercise has no video url", async () => {
    api.get.mockImplementation((url) => {
      if (url.includes("/ejercicios/")) {
        return Promise.resolve({
          data: [{ ...mockEjercicios[0], video_url: null }]
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Ejercicios />);
    await waitFor(() => {
      expect(screen.getByText("Sin video")).toBeDefined();
    });
  });

  it("shows error if exercise creation fails", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "El nombre de ejercicio ya existe" } }
    });
    render(<Ejercicios />);
    fireEvent.click(screen.getByText("+ Registrar ejercicio"));

    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Sentadilla" } });
    fireEvent.change(screen.getByLabelText("Grupo muscular"), { target: { value: "Piernas" } });
    fireEvent.change(screen.getByLabelText("Nivel"), { target: { value: "PRINCIPIANTE" } });

    fireEvent.click(screen.getByRole("button", { name: "Guardar ejercicio" }));

    await waitFor(() => {
      expect(screen.getByText("El nombre de ejercicio ya existe")).toBeDefined();
    });
  });

  it("shows error if exercise deactivation fails", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockRejectedValue(new Error("Delete Error"));

    render(<Ejercicios />);
    await waitFor(() => {
      expect(screen.getByText("Desactivar")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo desactivar el ejercicio")).toBeDefined();
    });
  });
});
