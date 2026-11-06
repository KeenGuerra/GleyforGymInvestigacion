import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Auditoria from "./Auditoria";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockRegistros = [
  {
    id_registro: 1,
    id_usuario: 1,
    correo_usuario: "admin@gym.com",
    accion: "ANULAR",
    entidad: "Pago",
    id_entidad: 5,
    detalle: "monto=120",
    fecha: "2026-09-14T10:30:00Z",
  },
  {
    id_registro: 2,
    id_usuario: null,
    correo_usuario: null,
    accion: "WEBHOOK_PAGO",
    entidad: "Venta",
    id_entidad: 9,
    detalle: "resultado=EXITOSO",
    fecha: "2026-09-14T11:00:00Z",
  },
];

describe("Auditoria Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockRegistros });
  });

  it("renders the audit history on load", async () => {
    render(<Auditoria />);
    expect(screen.getByText("Historial de operaciones")).toBeDefined();

    await waitFor(() => {
      expect(screen.getByText("admin@gym.com")).toBeDefined();
      expect(screen.getByText("Sistema")).toBeDefined();
      expect(screen.getByText("ANULAR")).toBeDefined();
      expect(screen.getByText("monto=120")).toBeDefined();
    });

    expect(api.get).toHaveBeenCalledWith("/auditoria/", { params: {} });
  });

  it("refetches with the entidad filter when the select changes", async () => {
    render(<Auditoria />);
    await waitFor(() => expect(screen.getByText("admin@gym.com")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Filtrar por entidad"), {
      target: { value: "Pago" },
    });

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/auditoria/", { params: { entidad: "Pago" } });
    });
  });

  it("filters the loaded records by search term", async () => {
    render(<Auditoria />);
    await waitFor(() => expect(screen.getByText("admin@gym.com")).toBeDefined());

    fireEvent.change(
      screen.getByPlaceholderText("Buscar por usuario, acción o detalle..."),
      { target: { value: "EXITOSO" } }
    );

    await waitFor(() => {
      expect(screen.queryByText("admin@gym.com")).toBeNull();
      expect(screen.getByText("WEBHOOK_PAGO")).toBeDefined();
    });
  });

  it("shows an empty message when there are no records", async () => {
    render(<Auditoria />);
    await waitFor(() => expect(screen.getByText("admin@gym.com")).toBeDefined());

    fireEvent.change(
      screen.getByPlaceholderText("Buscar por usuario, acción o detalle..."),
      { target: { value: "inexistente" } }
    );

    await waitFor(() => {
      expect(screen.getByText("No hay registros de auditoría para este filtro")).toBeDefined();
    });
  });

  it("shows an error message when loading fails", async () => {
    api.get.mockRejectedValue(new Error("Network Error"));
    render(<Auditoria />);

    await waitFor(() => {
      expect(screen.getByText("Error al cargar el historial de auditoría")).toBeDefined();
    });
  });
});
