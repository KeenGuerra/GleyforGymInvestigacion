import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Reportes from "./Reportes";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockIngresos = {
  desde: "2026-06-01",
  hasta: "2026-06-30",
  total: 350.5,
  por_dia: [{ fecha: "2026-06-05", monto: 350.5 }],
};

const mockAsistencias = {
  desde: "2026-06-01",
  hasta: "2026-06-30",
  total: 3,
  por_dia: [{ fecha: "2026-06-05", cantidad: 3 }],
};

describe("Reportes Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url === "/reportes/ingresos") return Promise.resolve({ data: mockIngresos });
      if (url === "/reportes/asistencias") return Promise.resolve({ data: mockAsistencias });
      return Promise.resolve({ data: [] });
    });
  });

  it("renders the header and date inputs", () => {
    render(<Reportes />);
    expect(screen.getByText("Reportes operativos")).toBeDefined();
    expect(screen.getByLabelText("Desde")).toBeDefined();
    expect(screen.getByLabelText("Hasta")).toBeDefined();
  });

  it("generates the report and shows totals for both sections", async () => {
    render(<Reportes />);

    fireEvent.click(screen.getByText("Generar reporte"));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        "/reportes/ingresos",
        expect.objectContaining({ params: expect.any(Object) })
      );
      expect(screen.getByText("Ingresos por día")).toBeDefined();
      expect(screen.getAllByText("S/ 350.50").length).toBeGreaterThan(0);
      expect(screen.getByText("Asistencias por día")).toBeDefined();
      expect(screen.getAllByText("3").length).toBeGreaterThan(0);
    });
  });

  it("shows a validation error when the date range is missing", async () => {
    render(<Reportes />);

    fireEvent.change(screen.getByLabelText("Desde"), { target: { value: "" } });
    fireEvent.click(screen.getByText("Generar reporte"));

    await waitFor(() => {
      expect(screen.getByText("Selecciona una fecha de inicio y de fin")).toBeDefined();
    });
    expect(api.get).not.toHaveBeenCalled();
  });

  it("shows a validation error when desde is after hasta", async () => {
    render(<Reportes />);

    fireEvent.change(screen.getByLabelText("Desde"), { target: { value: "2026-06-30" } });
    fireEvent.change(screen.getByLabelText("Hasta"), { target: { value: "2026-06-01" } });
    fireEvent.click(screen.getByText("Generar reporte"));

    await waitFor(() => {
      expect(
        screen.getByText("La fecha de inicio no puede ser posterior a la fecha de fin")
      ).toBeDefined();
    });
  });

  it("shows an error when the request fails", async () => {
    api.get.mockRejectedValue(new Error("fail"));
    render(<Reportes />);

    fireEvent.click(screen.getByText("Generar reporte"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo generar el reporte")).toBeDefined();
    });
  });

  it("shows the empty message when a report has no rows", async () => {
    api.get.mockImplementation((url) => {
      if (url === "/reportes/ingresos") {
        return Promise.resolve({ data: { ...mockIngresos, total: 0, por_dia: [] } });
      }
      if (url === "/reportes/asistencias") {
        return Promise.resolve({ data: { ...mockAsistencias, total: 0, por_dia: [] } });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Reportes />);
    fireEvent.click(screen.getByText("Generar reporte"));

    await waitFor(() => {
      expect(screen.getByText("No hay ingresos registrados en este rango.")).toBeDefined();
      expect(screen.getByText("No hay asistencias registradas en este rango.")).toBeDefined();
    });
  });

  it("exports the ingresos and asistencias reports as CSV", async () => {
    URL.createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    URL.revokeObjectURL = vi.fn();
    const clickSpy = vi.fn();
    const crearElementoOriginal = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag) => {
      const el = crearElementoOriginal(tag);
      el.click = clickSpy;
      return el;
    });

    render(<Reportes />);
    fireEvent.click(screen.getByText("Generar reporte"));

    await waitFor(() => expect(screen.getByText("Ingresos por día")).toBeDefined());

    fireEvent.click(screen.getAllByText("Exportar CSV")[0]);
    fireEvent.click(screen.getAllByText("Exportar CSV")[1]);

    expect(clickSpy).toHaveBeenCalledTimes(2);

    vi.restoreAllMocks();
  });
});
