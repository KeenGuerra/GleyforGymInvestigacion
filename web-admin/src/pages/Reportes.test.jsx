import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Reportes from "./Reportes";
import api from "../api/api";

vi.mock("../api/api", () => ({
  default: {
    get: vi.fn(),
    delete: vi.fn(),
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

const mockProductosMasVendidos = [
  { producto: "Proteína", cantidad_vendida: 5, ingresos: 250 },
];

const mockVentasPorMetodo = {
  desde: "2026-06-01",
  hasta: "2026-06-30",
  total: 250,
  por_metodo: [{ metodo_pago: "EFECTIVO", monto: 250, cantidad: 5 }],
};

describe("Reportes Page Component", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.get.mockImplementation((url) => {
      if (url === "/reportes/ingresos") return Promise.resolve({ data: mockIngresos });
      if (url === "/reportes/asistencias") return Promise.resolve({ data: mockAsistencias });
      if (url === "/reportes/productos-mas-vendidos") return Promise.resolve({ data: mockProductosMasVendidos });
      if (url === "/reportes/ventas-por-metodo-pago") return Promise.resolve({ data: mockVentasPorMetodo });
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

  it("shows the combined total (memberships + product sales) once both load", async () => {
    render(<Reportes />);
    fireEvent.click(screen.getByText("Generar reporte"));

    await waitFor(() => {
      expect(
        screen.getByText("Ingresos totales del período (membresías + ventas de productos):")
      ).toBeDefined();
      expect(screen.getByText("S/ 600.50")).toBeDefined();
    });
  });

  it("fills the date range with today's date and generates the report when clicking 'Hoy'", async () => {
    render(<Reportes />);
    fireEvent.click(screen.getByText("Hoy"));

    const hoy = new Date().toISOString().slice(0, 10);
    await waitFor(() => {
      expect(screen.getByLabelText("Desde").value).toBe(hoy);
      expect(screen.getByLabelText("Hasta").value).toBe(hoy);
      expect(api.get).toHaveBeenCalledWith(
        "/reportes/ingresos",
        expect.objectContaining({ params: { desde: hoy, hasta: hoy } })
      );
    });
  });

  it("fills the date range with the first day of the month when clicking 'Este mes'", async () => {
    render(<Reportes />);
    fireEvent.click(screen.getByText("Este mes"));

    const hoy = new Date();
    const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1).toISOString().slice(0, 10);
    await waitFor(() => {
      expect(screen.getByLabelText("Desde").value).toBe(primerDia);
      expect(api.get).toHaveBeenCalledWith(
        "/reportes/ingresos",
        expect.objectContaining({ params: expect.objectContaining({ desde: primerDia }) })
      );
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

  it("exports F-07, F-08 and F-09 for the thesis", async () => {
    URL.createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    URL.revokeObjectURL = vi.fn();
    const clickSpy = vi.fn();
    const crearElementoOriginal = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag) => {
      const el = crearElementoOriginal(tag);
      el.click = clickSpy;
      return el;
    });

    api.get.mockImplementation((url) => {
      if (url === "/reportes/ia/kcal") {
        return Promise.resolve({
          data: [{ codigo_cliente: "C-001", kcal_plan: 2100, kcal_objetivo: 2200, desviacion_pct: -4.5 }],
        });
      }
      if (url === "/reportes/ia/decisiones") {
        return Promise.resolve({
          data: [{ codigo_cliente: "C-001", codigo_rutina: "R-001", decision: "aprobada", cambios_realizados: null, fecha: "2026-11-01" }],
        });
      }
      if (url === "/reportes/ia/restricciones") {
        return Promise.resolve({
          data: [{ codigo_cliente: "C-001", tipo: "rutina", objetivo: "Bajar de peso", restricciones_registradas: "RODILLA", viola_restriccion: false }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Reportes />);

    fireEvent.click(screen.getByText("F-07: kcal plan vs. objetivo"));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith("/reportes/ia/kcal"));

    fireEvent.click(screen.getByText("F-08: decisiones de revisión"));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith("/reportes/ia/decisiones"));

    fireEvent.click(screen.getByText("F-09: verificación de restricciones"));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith("/reportes/ia/restricciones"));

    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(3));

    vi.restoreAllMocks();
  });

  it("shows an error when a thesis export fails", async () => {
    api.get.mockImplementation((url) => {
      if (url === "/reportes/ia/kcal") return Promise.reject(new Error("fail"));
      return Promise.resolve({ data: [] });
    });

    render(<Reportes />);
    fireEvent.click(screen.getByText("F-07: kcal plan vs. objetivo"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo exportar F-07")).toBeDefined();
    });
  });

  it("exports F-04, F-05, F-12 and F-15 (instrumentación del postest)", async () => {
    URL.createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    URL.revokeObjectURL = vi.fn();
    const clickSpy = vi.fn();
    const crearElementoOriginal = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag) => {
      const el = crearElementoOriginal(tag);
      el.click = clickSpy;
      return el;
    });

    api.get.mockImplementation((url) => {
      if (url === "/reportes/sistema/tiempos-respuesta") {
        return Promise.resolve({ data: [{ modulo: "clientes", tiempo_promedio_ms: 12.5, n_operaciones: 3 }] });
      }
      if (url === "/reportes/sistema/registros-recientes") {
        return Promise.resolve({
          data: [{ entidad: "Pago", id_entidad: 1, accion: "CREAR", detalle: "monto=100", fecha: "2026-06-10" }],
        });
      }
      if (url === "/reportes/sistema/duplicidad") {
        return Promise.resolve({
          data: [{ tipo_hallazgo: "PAGO_DUPLICADO", entidad: "Pago", id_entidad: "1, 2", detalle: "2 pagos idénticos" }],
        });
      }
      if (url === "/reportes/progreso-fisico") {
        return Promise.resolve({
          data: { total_clientes_activos: 1, con_seguimiento: 1, porcentaje: 100, detalle: [{ codigo_cliente: "C-001", tiene_seguimiento: true }] },
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Reportes />);

    fireEvent.click(screen.getByText("F-04: tiempo de respuesta"));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(
      "/reportes/sistema/tiempos-respuesta", expect.objectContaining({ params: expect.any(Object) })
    ));

    fireEvent.click(screen.getByText("F-05: registros recientes"));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(
      "/reportes/sistema/registros-recientes", expect.objectContaining({ params: expect.any(Object) })
    ));

    fireEvent.click(screen.getByText("F-12: duplicidad de registros"));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(
      "/reportes/sistema/duplicidad", expect.objectContaining({ params: expect.any(Object) })
    ));

    fireEvent.click(screen.getByText("F-15: seguimiento de progreso"));
    await waitFor(() => expect(api.get).toHaveBeenCalledWith(
      "/reportes/progreso-fisico", expect.objectContaining({ params: expect.any(Object) })
    ));

    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(4));

    vi.restoreAllMocks();
  });

  it("deletes old response-time records on confirm and shows how many were removed", async () => {
    api.get.mockResolvedValue({ data: [] });
    api.delete.mockResolvedValue({ data: { eliminados: 42 } });
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));

    render(<Reportes />);
    await waitFor(() => expect(screen.getByText("Eliminar registros antiguos")).toBeDefined());

    fireEvent.change(screen.getByLabelText("Eliminar registros anteriores a"), {
      target: { value: "2026-10-01" },
    });
    fireEvent.click(screen.getByText("Eliminar registros antiguos"));

    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith("/reportes/sistema/tiempos-respuesta", {
        params: { antes_de: "2026-10-01" },
      });
      expect(screen.getByText("Se eliminaron 42 registros.")).toBeDefined();
    });
  });

  it("does not delete old response-time records if the user cancels the confirmation", async () => {
    api.get.mockResolvedValue({ data: [] });
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));

    render(<Reportes />);
    await waitFor(() => expect(screen.getByText("Eliminar registros antiguos")).toBeDefined());

    fireEvent.click(screen.getByText("Eliminar registros antiguos"));

    expect(globalThis.confirm).toHaveBeenCalled();
    expect(api.delete).not.toHaveBeenCalled();
  });

  it("shows an error when deleting old response-time records fails", async () => {
    api.get.mockResolvedValue({ data: [] });
    api.delete.mockRejectedValue(new Error("delete failed"));
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));

    render(<Reportes />);
    await waitFor(() => expect(screen.getByText("Eliminar registros antiguos")).toBeDefined());

    fireEvent.click(screen.getByText("Eliminar registros antiguos"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo limpiar los registros de tiempo de respuesta")).toBeDefined();
    });
  });

  it("shows a 'por vencer' membership and sends a WhatsApp reminder with a prefilled message", async () => {
    const openSpy = vi.fn();
    vi.stubGlobal("open", openSpy);

    api.get.mockImplementation((url) => {
      if (url === "/reportes/membresias-por-vencer") {
        return Promise.resolve({
          data: [{
            id_cliente_membresia: 10,
            id_cliente: 1,
            nombre_cliente: "Juan Perez",
            telefono_cliente: "987654321",
            nombre_membresia: "Plan Mensual",
            fecha_fin: "2026-06-20",
            dias_restantes: 3,
          }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Reportes />);
    fireEvent.click(screen.getByText("Consultar"));

    await waitFor(() => expect(screen.getByText("Juan Perez")).toBeDefined());
    expect(screen.getByText("3 día(s)")).toBeDefined();

    fireEvent.click(screen.getByText("Enviar recordatorio por WhatsApp"));

    expect(openSpy).toHaveBeenCalledTimes(1);
    const [url, target] = openSpy.mock.calls[0];
    expect(url).toContain("https://wa.me/51987654321?text=");
    const mensaje = decodeURIComponent(url.split("text=")[1]);
    // Formato con negrita (*texto*) de WhatsApp y fecha en formato largo,
    // no el ISO crudo -- se ve mejor en el chat del cliente.
    expect(mensaje).toBe(
      "¡Hola Juan! 👋\n\n" +
      "Tu membresía *Plan Mensual* vence el *20 de junio de 2026* 📅\n\n" +
      "Renueva a tiempo y sigue entrenando sin interrupciones 💪\n\n" +
      "*GLEYFORGYM* 🏋️"
    );
    expect(target).toBe("_blank");

    vi.unstubAllGlobals();
  });

  it("blocks the WhatsApp reminder when the client has no valid 9-digit phone", async () => {
    const openSpy = vi.fn();
    vi.stubGlobal("open", openSpy);

    api.get.mockImplementation((url) => {
      if (url === "/reportes/membresias-por-vencer") {
        return Promise.resolve({
          data: [{
            id_cliente_membresia: 11,
            id_cliente: 2,
            nombre_cliente: "Ana Torres",
            telefono_cliente: null,
            nombre_membresia: "Plan Anual",
            fecha_fin: "2026-06-25",
            dias_restantes: 5,
          }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Reportes />);
    fireEvent.click(screen.getByText("Consultar"));

    await waitFor(() => expect(screen.getByText("Ana Torres")).toBeDefined());
    fireEvent.click(screen.getByText("Enviar recordatorio por WhatsApp"));

    expect(openSpy).not.toHaveBeenCalled();
    await waitFor(() => {
      expect(screen.getByText(/no tiene un teléfono válido de 9 dígitos/)).toBeDefined();
    });

    vi.unstubAllGlobals();
  });

  it("shows clients with a pending balance, their total owed, and sends a WhatsApp reminder", async () => {
    const openSpy = vi.fn();
    vi.stubGlobal("open", openSpy);

    api.get.mockImplementation((url) => {
      if (url === "/reportes/saldos-pendientes") {
        return Promise.resolve({
          data: [{
            id_cliente_membresia: 20,
            id_cliente: 1,
            nombre_cliente: "Juan Perez",
            telefono_cliente: "987654321",
            nombre_membresia: "Plan Mensual",
            precio_asignado: 100,
            monto_pagado: 30,
            saldo_pendiente: 70,
          }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<Reportes />);
    fireEvent.click(screen.getByText("Consultar saldos pendientes"));

    await waitFor(() => expect(screen.getByText("Juan Perez")).toBeDefined());
    expect(screen.getByText("Falta S/ 70.00")).toBeDefined();
    expect(screen.getByText(/Total adeudado:/)).toBeDefined();
    expect(screen.getByText("S/ 70.00")).toBeDefined();

    fireEvent.click(screen.getByText("Enviar recordatorio por WhatsApp"));

    expect(openSpy).toHaveBeenCalledTimes(1);
    const [url] = openSpy.mock.calls[0];
    expect(url).toContain("https://wa.me/51987654321?text=");
    const mensaje = decodeURIComponent(url.split("text=")[1]);
    expect(mensaje).toBe(
      "¡Hola Juan! 👋\n\n" +
      "Tienes un saldo pendiente de *S/ 70.00* por tu membresía *Plan Mensual* 💳\n\n" +
      "Puedes completar el pago cuando pases por el gimnasio.\n\n" +
      "*GLEYFORGYM* 🏋️"
    );

    vi.unstubAllGlobals();
  });

  it("shows an empty message when no client has a pending balance", async () => {
    api.get.mockResolvedValue({ data: [] });

    render(<Reportes />);
    fireEvent.click(screen.getByText("Consultar saldos pendientes"));

    await waitFor(() => {
      expect(screen.getByText("No hay clientes con saldo pendiente.")).toBeDefined();
    });
  });

  it("shows an error when consulting pending balances fails", async () => {
    api.get.mockRejectedValue(new Error("fail"));

    render(<Reportes />);
    fireEvent.click(screen.getByText("Consultar saldos pendientes"));

    await waitFor(() => {
      expect(screen.getByText("No se pudo consultar los saldos pendientes")).toBeDefined();
    });
  });
});
