import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ToastFeedback from "./ToastFeedback";

describe("ToastFeedback", () => {
  it("renders nothing when there is no toast", () => {
    const { container } = render(<ToastFeedback toast={null} onClose={() => {}} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("shows the message and calls onClose when the close button is clicked", () => {
    const onClose = vi.fn();
    render(<ToastFeedback toast={{ tipo: "danger", mensaje: "No se pudo cargar" }} onClose={onClose} />);

    expect(screen.getByText("No se pudo cargar")).toBeDefined();

    fireEvent.click(screen.getByRole("button", { name: /cerrar/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
