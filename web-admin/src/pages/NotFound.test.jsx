import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import NotFound from "./NotFound";

describe("NotFound Page Component", () => {
  it("renders the 404 message and a link back to the home page", () => {
    render(
      <MemoryRouter>
        <NotFound />
      </MemoryRouter>
    );

    expect(screen.getByText("404")).toBeDefined();
    expect(screen.getByText("Página no encontrada")).toBeDefined();

    const link = screen.getByText("Volver al inicio");
    expect(link.getAttribute("href")).toBe("/");
  });
});
