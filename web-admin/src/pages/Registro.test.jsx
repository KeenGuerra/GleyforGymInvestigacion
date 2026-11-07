import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Registro from "./Registro";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
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

function renderRegistro() {
  return render(
    <MemoryRouter>
      <Registro />
    </MemoryRouter>
  );
}

describe("Registro Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders the form fields", () => {
    renderRegistro();

    expect(screen.getByLabelText("Correo electrónico")).toBeDefined();
    expect(screen.getByLabelText("Contraseña")).toBeDefined();
    expect(screen.getByLabelText("Confirmar contraseña")).toBeDefined();
  });

  it("validates password length before calling the API", async () => {
    renderRegistro();

    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "comprador@gmail.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "123" } });
    fireEvent.change(screen.getByLabelText("Confirmar contraseña"), { target: { value: "123" } });
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));

    await waitFor(() => {
      expect(screen.getByText("La contraseña debe tener al menos 6 caracteres")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("validates that passwords match before calling the API", async () => {
    renderRegistro();

    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "comprador@gmail.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "clave123" } });
    fireEvent.change(screen.getByLabelText("Confirmar contraseña"), { target: { value: "otraClave" } });
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));

    await waitFor(() => {
      expect(screen.getByText("Las contraseñas no coinciden")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("submits the registration and shows the verification message", async () => {
    api.post.mockResolvedValue({
      data: { mensaje: "Cuenta creada correctamente. Revisa tu correo para verificarla." },
    });

    renderRegistro();

    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "comprador@gmail.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "clave123" } });
    fireEvent.change(screen.getByLabelText("Confirmar contraseña"), { target: { value: "clave123" } });
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/usuarios/registro", {
        correo: "comprador@gmail.com",
        password: "clave123",
      });
      expect(screen.getByText("Cuenta creada correctamente. Revisa tu correo para verificarla.")).toBeDefined();
    });

    fireEvent.click(screen.getByText("Ir a iniciar sesión"));
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });

  it("shows the error returned by the backend when registration fails", async () => {
    api.post.mockRejectedValue({ response: { data: { detail: "Correo ya registrado" } } });

    renderRegistro();

    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "comprador@gmail.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "clave123" } });
    fireEvent.change(screen.getByLabelText("Confirmar contraseña"), { target: { value: "clave123" } });
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));

    await waitFor(() => {
      expect(screen.getByText("Correo ya registrado")).toBeDefined();
    });
  });

  it("navigates to login when clicking 'Inicia sesión'", () => {
    renderRegistro();
    fireEvent.click(screen.getByText("Inicia sesión"));
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });
});
