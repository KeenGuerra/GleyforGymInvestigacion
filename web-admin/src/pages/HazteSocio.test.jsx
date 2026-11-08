import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import HazteSocio from "./HazteSocio";
import api from "../api/api";

const mockNavigate = vi.fn();

vi.mock("../api/api", () => ({
  default: {
    post: vi.fn(),
  },
}));

vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

function llenarFormulario() {
  fireEvent.change(screen.getByLabelText("DNI"), { target: { value: "12345678" } });
  fireEvent.change(screen.getByLabelText("Nombres"), { target: { value: "Ana" } });
  fireEvent.change(screen.getByLabelText("Apellidos"), { target: { value: "Torres" } });
}

describe("HazteSocio Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockNavigate.mockReset();
    localStorage.clear();
  });

  it("redirects to /mi-membresia on mount if the user is already a socio", () => {
    localStorage.setItem("tiene_cliente", "true");
    render(<HazteSocio />);
    expect(mockNavigate).toHaveBeenCalledWith("/mi-membresia");
  });

  it("does not redirect when the user is not a socio yet", () => {
    localStorage.setItem("tiene_cliente", "false");
    render(<HazteSocio />);
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("submits the form, marks tiene_cliente and navigates to /mi-membresia", async () => {
    localStorage.setItem("tiene_cliente", "false");
    api.post.mockResolvedValue({ data: { id_cliente: 1, dni: "12345678" } });

    render(<HazteSocio />);
    llenarFormulario();
    fireEvent.click(screen.getByText("Hazte socio"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        "/clientes/hazte-socio",
        expect.objectContaining({ dni: "12345678", nombres: "Ana", apellidos: "Torres" })
      );
      expect(localStorage.getItem("tiene_cliente")).toBe("true");
      expect(mockNavigate).toHaveBeenCalledWith("/mi-membresia");
    });
  });

  it("shows the backend error message when the request fails", async () => {
    localStorage.setItem("tiene_cliente", "false");
    api.post.mockRejectedValue({ response: { data: { detail: "Ya tienes un perfil de socio" } } });

    render(<HazteSocio />);
    llenarFormulario();
    fireEvent.click(screen.getByText("Hazte socio"));

    await waitFor(() => {
      expect(screen.getByText("Ya tienes un perfil de socio")).toBeDefined();
    });
  });
});
