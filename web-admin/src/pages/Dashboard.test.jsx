import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Dashboard from "./Dashboard";

// ─── Subcomponentes mockeados para no propagar errores de API ────────────────
vi.mock("./DashboardAdmin", () => ({
  default: () => <div>Admin Dashboard Content</div>,
}));
vi.mock("./DashboardEntrenador", () => ({
  default: () => <div>Entrenador Dashboard Content</div>,
}));
vi.mock("./DashboardCliente", () => ({
  default: () => <div>Cliente Dashboard Content</div>,
}));

describe("Dashboard Page Routing Component", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders Admin Dashboard when role is ADMIN", () => {
    localStorage.setItem("rol", "ADMIN");
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    expect(screen.getByText("Admin Dashboard Content")).toBeDefined();
  });

  it("renders Trainer Dashboard when role is ENTRENADOR", () => {
    localStorage.setItem("rol", "ENTRENADOR");
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    expect(screen.getByText("Entrenador Dashboard Content")).toBeDefined();
  });

  it("renders Client Dashboard when role is CLIENTE", () => {
    localStorage.setItem("rol", "CLIENTE");
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    expect(screen.getByText("Cliente Dashboard Content")).toBeDefined();
  });

  it("renders error state when role is unknown or missing", () => {
    // No rol en localStorage
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    expect(screen.getByText("No se pudo identificar el rol")).toBeDefined();
  });
});
