import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Login from "./Login";
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

describe("Login Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
  });

  it("renders form elements and lets user write in inputs", () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    expect(screen.getByLabelText("Correo electrónico")).toBeDefined();
    expect(screen.getByLabelText("Contraseña")).toBeDefined();
    expect(screen.getByText("Acceder al sistema", { selector: "button" })).toBeDefined();

    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "test@gym.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "123456" } });

    expect(screen.getByLabelText("Correo electrónico").value).toBe("test@gym.com");
    expect(screen.getByLabelText("Contraseña").value).toBe("123456");
  });

  it("submits the credentials and sets local storage and navigates on success", async () => {
    api.post.mockResolvedValue({
      data: {
        token: "jwt-token",
        usuario: { id_usuario: 5, rol: "ADMIN", correo: "test@gym.com" },
      },
    });

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "test@gym.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "123456" } });
    fireEvent.click(screen.getByText("Acceder al sistema", { selector: "button" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/usuarios/login", {
        correo: "test@gym.com",
        password: "123456",
      });
      expect(localStorage.getItem("token")).toBe("jwt-token");
      expect(localStorage.getItem("rol")).toBe("ADMIN");
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("shows error message when login api fails", async () => {
    api.post.mockRejectedValue(new Error("Login failed"));

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText("Correo electrónico"), { target: { value: "wrong@gym.com" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "wrongpass" } });
    fireEvent.click(screen.getByText("Acceder al sistema", { selector: "button" }));

    await waitFor(() => {
      expect(screen.getByText("Correo o contraseña incorrectos")).toBeDefined();
    });
  });
});
