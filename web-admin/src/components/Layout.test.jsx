import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Layout from "./Layout";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("Layout Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
  });

  it("renders sidebar with ADMIN links when role is ADMIN", () => {
    localStorage.setItem("rol", "ADMIN");
    localStorage.setItem("correo", "admin@gym.com");

    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );

    expect(screen.getByText("Panel administrativo")).toBeDefined();
    expect(screen.getByText("Clientes")).toBeDefined();
    expect(screen.getByText("Usuarios")).toBeDefined();
    expect(screen.getByText("Planes")).toBeDefined();
    expect(screen.getByText("Asistencias")).toBeDefined();
    expect(screen.getAllByText("ADMIN").length).toBeGreaterThan(0);
    expect(screen.getByText("admin@gym.com")).toBeDefined();
  });

  it("renders sidebar with CLIENTE links when role is CLIENTE", () => {
    localStorage.setItem("rol", "CLIENTE");
    localStorage.setItem("correo", "client@gym.com");

    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );

    expect(screen.getByText("Panel cliente")).toBeDefined();
    expect(screen.getByText("Mi perfil")).toBeDefined();
    expect(screen.getByText("Mi rutina")).toBeDefined();
    expect(screen.getByText("Mi nutrición")).toBeDefined();
    expect(screen.getAllByText("CLIENTE").length).toBeGreaterThan(0);
  });

  it("clears localStorage and navigates to home on logout click", () => {
    localStorage.setItem("rol", "ADMIN");
    localStorage.setItem("correo", "admin@gym.com");

    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );

    const logoutBtn = screen.getByText("Cerrar sesión");
    fireEvent.click(logoutBtn);

    expect(localStorage.getItem("rol")).toBeNull();
    expect(mockNavigate).toHaveBeenCalledWith("/");
  });

  it("renders sidebar with ENTRENADOR links when role is ENTRENADOR", () => {
    localStorage.setItem("rol", "ENTRENADOR");
    localStorage.setItem("correo", "trainer@gym.com");

    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );

    expect(screen.getByText("Panel entrenador")).toBeDefined();
    expect(screen.getByText("Clientes")).toBeDefined();
    expect(screen.getByText("Asistencias")).toBeDefined();
    expect(screen.getByText("Progreso")).toBeDefined();
    expect(screen.getByText("Ejercicios")).toBeDefined();
    expect(screen.getAllByText("ENTRENADOR").length).toBeGreaterThan(0);
  });
});
