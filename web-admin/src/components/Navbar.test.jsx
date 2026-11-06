import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Navbar from "./Navbar";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function renderNavbar(props) {
  return render(
    <MemoryRouter>
      <Navbar {...props} />
    </MemoryRouter>
  );
}

describe("Navbar Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
  });

  it("renders the public links and the login button when logged out", () => {
    renderNavbar();

    expect(screen.getByText("Inicio")).toBeDefined();
    expect(screen.getByText("Avisos")).toBeDefined();
    expect(screen.getByText("Tienda")).toBeDefined();
    expect(screen.queryByText("Panel")).toBeNull();
    expect(screen.getByText("Iniciar sesión")).toBeDefined();
  });

  it("navigates to /login when the access button is clicked while logged out", () => {
    renderNavbar();

    fireEvent.click(screen.getByText("Iniciar sesión"));
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });

  it("shows the Panel link and navigates to /dashboard when logged in as ADMIN", () => {
    localStorage.setItem("token", "fake-token");
    localStorage.setItem("rol", "ADMIN");
    renderNavbar();

    expect(screen.getByText("Panel")).toBeDefined();
    const botonAcceso = screen.getByText("Admin");
    fireEvent.click(botonAcceso);
    expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
  });

  it("shows the correct label for ENTRENADOR and CLIENTE roles", () => {
    localStorage.setItem("token", "fake-token");
    localStorage.setItem("rol", "ENTRENADOR");
    const { unmount } = renderNavbar();
    expect(screen.getByText("Entrenador")).toBeDefined();
    unmount();

    localStorage.setItem("rol", "CLIENTE");
    renderNavbar();
    expect(screen.getByText("Mi panel")).toBeDefined();
  });

  it("does not show the cart button when cartCount is 0", () => {
    renderNavbar({ cartCount: 0 });
    expect(screen.queryByText(/Carrito/)).toBeNull();
  });

  it("shows the cart button with the count and triggers onCartClick", () => {
    const onCartClick = vi.fn();
    renderNavbar({ cartCount: 3, onCartClick });

    const botonCarrito = screen.getByText("Carrito (3)");
    fireEvent.click(botonCarrito);
    expect(onCartClick).toHaveBeenCalled();
  });

  it("navigates to / when the logo is clicked", () => {
    renderNavbar();
    fireEvent.click(screen.getByAltText("Logo GleyforGym").closest("button"));
    expect(mockNavigate).toHaveBeenCalledWith("/");
  });
});
