import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "./App";
import api from "./api/api";

vi.mock("./api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe("App Router Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: [] });
  });

  it("renders Landing page (Inicio) by default on / path", async () => {
    render(<App />);
    expect(screen.getAllByText(/GLEYFORGYM/i).length).toBeGreaterThan(0);
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/membresias/");
    });
  });
});
