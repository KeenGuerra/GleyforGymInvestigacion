import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import DashboardComprador from "./DashboardComprador";
import api from "../api/api";

const mockNavigate = vi.fn();

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

describe("DashboardComprador Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockNavigate.mockReset();
    api.get.mockResolvedValue({ data: [] });
  });

  it("renders the buyer-only account message", () => {
    render(<DashboardComprador />);
    expect(screen.getByText(/Tu cuenta es solo para comprar en la tienda/)).toBeDefined();
  });

  it("navigates to /hazte-socio when clicking 'Hazte socio ahora'", () => {
    render(<DashboardComprador />);
    fireEvent.click(screen.getByText("Hazte socio ahora"));
    expect(mockNavigate).toHaveBeenCalledWith("/hazte-socio");
  });

  it("navigates to /tienda when clicking 'Ir a la tienda'", () => {
    render(<DashboardComprador />);
    fireEvent.click(screen.getByText("Ir a la tienda"));
    expect(mockNavigate).toHaveBeenCalledWith("/tienda");
  });
});
