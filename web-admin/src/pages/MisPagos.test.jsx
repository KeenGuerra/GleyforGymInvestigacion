import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import MisPagos from "./MisPagos";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
  },
}));

vi.mock("../utils/descargarArchivo", () => ({
  descargarBlob: vi.fn(),
}));

const mockPagos = [
  {
    id_pago: 101,
    monto: 150,
    metodo_pago: "YAPE",
    fecha_pago: "2026-06-01",
    estado: "COMPLETADO",
    observacion: "Pago puntual",
  },
];

describe("MisPagos Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    localStorage.setItem("id_usuario", "10");

    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) {
        return Promise.resolve({ data: { id_cliente: 1 } });
      }
      if (url.includes("/pagos/cliente/")) {
        return Promise.resolve({ data: mockPagos });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it("renders active user payment history list card", async () => {
    render(<MisPagos />);
    expect(screen.getByText("Historial de pagos")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("S/ 150.00")).toBeDefined();
      expect(screen.getByText("YAPE")).toBeDefined();
      expect(screen.getByText("Pago puntual")).toBeDefined();
    });
  });

  it("downloads the receipt when the button is clicked", async () => {
    const { descargarBlob } = await import("../utils/descargarArchivo");
    const blobFalso = new Blob(["%PDF-fake"], { type: "application/pdf" });
    api.get.mockImplementation((url) => {
      if (url.includes("/clientes/usuario/")) return Promise.resolve({ data: { id_cliente: 1 } });
      if (url.includes("/pagos/cliente/")) return Promise.resolve({ data: mockPagos });
      if (url.includes("/recibo")) return Promise.resolve({ data: blobFalso });
      return Promise.resolve({ data: [] });
    });

    render(<MisPagos />);
    await waitFor(() => expect(screen.getByText("Descargar recibo")).toBeDefined());

    fireEvent.click(screen.getByText("Descargar recibo"));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/pagos/101/recibo", { responseType: "blob" });
      expect(descargarBlob).toHaveBeenCalledWith(blobFalso, "recibo-pago-101.pdf");
    });
  });
});
