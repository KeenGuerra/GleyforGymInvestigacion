import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ResetPassword from "./ResetPassword";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    post: vi.fn(),
  },
}));

function renderConToken(token = "abc123") {
  return render(
    <MemoryRouter initialEntries={[`/reset-password?token=${token}`]}>
      <ResetPassword />
    </MemoryRouter>
  );
}

describe("ResetPassword Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("rejects mismatched passwords without calling the API", () => {
    renderConToken();

    fireEvent.change(screen.getByLabelText("Nueva contraseña"), { target: { value: "clave123" } });
    fireEvent.change(screen.getByLabelText("Confirmar contraseña"), { target: { value: "otraClave" } });
    fireEvent.click(screen.getByText("Restablecer contraseña"));

    expect(screen.getByText("Las contraseñas no coinciden")).toBeDefined();
    expect(api.post).not.toHaveBeenCalled();
  });

  it("submits the token and new password on success", async () => {
    api.post.mockResolvedValue({ data: { mensaje: "Contraseña actualizada correctamente" } });

    renderConToken("token-valido");

    fireEvent.change(screen.getByLabelText("Nueva contraseña"), { target: { value: "clave123" } });
    fireEvent.change(screen.getByLabelText("Confirmar contraseña"), { target: { value: "clave123" } });
    fireEvent.click(screen.getByText("Restablecer contraseña"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/usuarios/reset-password", {
        token: "token-valido",
        password_nueva: "clave123",
      });
      expect(screen.getByText("Contraseña actualizada correctamente")).toBeDefined();
    });
  });

  it("shows the API error when the token is invalid or expired", async () => {
    api.post.mockRejectedValue({ response: { data: { detail: "El enlace de recuperación es inválido o expiró" } } });

    renderConToken("token-vencido");

    fireEvent.change(screen.getByLabelText("Nueva contraseña"), { target: { value: "clave123" } });
    fireEvent.change(screen.getByLabelText("Confirmar contraseña"), { target: { value: "clave123" } });
    fireEvent.click(screen.getByText("Restablecer contraseña"));

    await waitFor(() => {
      expect(screen.getByText("El enlace de recuperación es inválido o expiró")).toBeDefined();
    });
  });
});
