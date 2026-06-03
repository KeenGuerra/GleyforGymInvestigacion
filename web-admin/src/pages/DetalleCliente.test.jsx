import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DetalleCliente from "./DetalleCliente";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
  useParams: () => ({ id: "1" }),
}));

const mockDetalle = {
  cliente: {
    id_cliente: 1,
    nombres: "Juan",
    apellidos: "Perez",
    correo: "juan@test.com",
    dni: "12345678",
    telefono: "999888777",
    objetivo: "PERDIDA_PESO",
    nivel: "PRINCIPIANTE",
    peso: 80,
    estatura: 1.75,
    estado: "ACTIVO",
  },
  membresia_actual: {
    nombre: "Plan Oro",
    fecha_fin: "2026-09-01",
    estado: "ACTIVA",
  },
  ultimo_pago: {
    monto: 100,
    fecha_pago: "2026-06-01",
    metodo_pago: "YAPE",
  },
  ultimo_progreso: {
    peso: 79.5,
    porcentaje_grasa: 18.5,
    porcentaje_musculo: 40.2,
  },
};

describe("DetalleCliente Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockDetalle });
  });

  it("renders header and client details cards", async () => {
    render(<DetalleCliente />);
    await waitFor(() => {
      expect(screen.getByText("Juan Perez")).toBeDefined();
      expect(screen.getByText("juan@test.com")).toBeDefined();
      expect(screen.getByText("Plan Oro")).toBeDefined();
      expect(screen.getByText("79.5 kg")).toBeDefined();
      expect(screen.getByText("18.5 %")).toBeDefined();
    });
  });
});
