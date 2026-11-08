import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Proveedores from "./Proveedores";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockProveedores = [
  {
    id_proveedor: 1,
    razon_social: "Nutrición SAC",
    ruc: "20123456789",
    telefono: "999888777",
    correo: "contacto@nutricion.com",
    direccion: "Av. Siempre Viva 123",
    contacto: "Juan Pérez",
    estado: "ACTIVO",
  },
];

function getField(container, name) {
  return container.querySelector(`[name="${name}"]`);
}

describe("Proveedores Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockResolvedValue({ data: mockProveedores });
  });

  it("renders headers and loads the suppliers list", async () => {
    render(<Proveedores />);
    expect(screen.getByText("Lista de proveedores")).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText("Nutrición SAC")).toBeDefined();
      expect(screen.getByText("RUC: 20123456789")).toBeDefined();
    });
  });

  it("filters suppliers based on search term", async () => {
    render(<Proveedores />);
    await waitFor(() => expect(screen.getByText("Nutrición SAC")).toBeDefined());

    fireEvent.change(screen.getByPlaceholderText("Buscar..."), { target: { value: "noexiste" } });

    await waitFor(() => {
      expect(screen.getByText("No hay proveedores.")).toBeDefined();
    });
  });

  it("shows the load error message when loading suppliers fails", async () => {
    api.get.mockRejectedValue(new Error("Network Error"));
    render(<Proveedores />);

    await waitFor(() => {
      expect(screen.getByText("Error al cargar proveedores")).toBeDefined();
    });
  });

  it("shows form and calls post on creating a supplier", async () => {
    api.post.mockResolvedValue({ data: {} });
    const { container } = render(<Proveedores />);

    fireEvent.click(screen.getByText("+ Nuevo proveedor"));
    await waitFor(() => expect(getField(container, "razon_social")).not.toBeNull());

    fireEvent.change(getField(container, "razon_social"), { target: { value: "Fit Foods EIRL" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/proveedores/", {
        razon_social: "Fit Foods EIRL",
        ruc: null,
        telefono: null,
        correo: null,
        direccion: null,
        contacto: null,
        estado: "ACTIVO",
      });
    });
  });

  it("validates razon social before submitting", async () => {
    render(<Proveedores />);
    fireEvent.click(screen.getByText("+ Nuevo proveedor"));

    await waitFor(() => expect(screen.getByText("Guardar")).toBeDefined());
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(screen.getByText("Ingrese la razón social")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("rejects an invalid RUC", async () => {
    const { container } = render(<Proveedores />);
    fireEvent.click(screen.getByText("+ Nuevo proveedor"));

    await waitFor(() => expect(getField(container, "razon_social")).not.toBeNull());
    fireEvent.change(getField(container, "razon_social"), { target: { value: "Fit Foods EIRL" } });
    fireEvent.change(getField(container, "ruc"), { target: { value: "123" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(screen.getByText("El RUC debe tener entre 11 y 13 dígitos numéricos")).toBeDefined();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it("enters edit mode and updates a supplier via PUT", async () => {
    api.put.mockResolvedValue({ data: {} });
    const { container } = render(<Proveedores />);

    await waitFor(() => expect(screen.getByText("Editar")).toBeDefined());
    fireEvent.click(screen.getByText("Editar"));

    await waitFor(() => expect(screen.getByRole("heading", { name: "Editar proveedor" })).toBeDefined());

    fireEvent.change(getField(container, "telefono"), { target: { value: "911222333" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/proveedores/1", {
        razon_social: "Nutrición SAC",
        ruc: "20123456789",
        telefono: "911222333",
        correo: "contacto@nutricion.com",
        direccion: "Av. Siempre Viva 123",
        contacto: "Juan Pérez",
        estado: "ACTIVO",
      });
    });
  });

  it("deactivates a supplier on confirm", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    api.delete.mockResolvedValue({ data: {} });

    render(<Proveedores />);
    await waitFor(() => expect(screen.getByText("Editar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/proveedores/1");
    });
  });

  it("shows an Activar button instead of Desactivar for an INACTIVO supplier, and reactivates it", async () => {
    api.get.mockResolvedValue({ data: [{ ...mockProveedores[0], estado: "INACTIVO" }] });
    api.put.mockResolvedValue({ data: {} });

    render(<Proveedores />);
    await waitFor(() => expect(screen.getByText("Activar")).toBeDefined());
    expect(screen.queryByText("Desactivar")).toBeNull();

    fireEvent.click(screen.getByText("Activar"));

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith("/proveedores/1", { estado: "ACTIVO" });
    });
  });

  it("does not deactivate when confirm is cancelled", async () => {
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    render(<Proveedores />);

    await waitFor(() => expect(screen.getByText("Desactivar")).toBeDefined());
    fireEvent.click(screen.getByText("Desactivar"));

    expect(api.delete).not.toHaveBeenCalled();
  });

  it("shows an error message when creation fails", async () => {
    api.post.mockRejectedValue({ response: { data: { detail: "RUC duplicado" } } });
    const { container } = render(<Proveedores />);

    fireEvent.click(screen.getByText("+ Nuevo proveedor"));
    await waitFor(() => expect(getField(container, "razon_social")).not.toBeNull());

    fireEvent.change(getField(container, "razon_social"), { target: { value: "Fit Foods EIRL" } });
    fireEvent.click(screen.getByText("Guardar"));

    await waitFor(() => {
      expect(screen.getByText("RUC duplicado")).toBeDefined();
    });
  });
});
