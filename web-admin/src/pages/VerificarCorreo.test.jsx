import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import VerificarCorreo from "./VerificarCorreo";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    post: vi.fn(),
  },
}));

function renderConToken(token) {
  const ruta = token ? `/verificar-correo?token=${token}` : "/verificar-correo";
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <VerificarCorreo />
    </MemoryRouter>
  );
}

describe("VerificarCorreo Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("shows an error immediately when there is no token", async () => {
    renderConToken();

    await waitFor(() => {
      expect(
        screen.getByText("Este enlace no incluye un token válido. Solicita uno nuevo.")
      ).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("verifies the email automatically when a token is present", async () => {
    api.post.mockResolvedValue({ data: { mensaje: "Correo verificado correctamente" } });

    renderConToken("token-valido");

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/usuarios/verificar-correo", { token: "token-valido" });
      expect(screen.getByText("Correo verificado correctamente")).toBeDefined();
    });
  });

  it("shows the API error when the token is invalid or expired", async () => {
    api.post.mockRejectedValue({
      response: { data: { detail: "El enlace de verificación es inválido o expiró" } },
    });

    renderConToken("token-vencido");

    await waitFor(() => {
      expect(screen.getByText("El enlace de verificación es inválido o expiró")).toBeDefined();
    });
  });
});
