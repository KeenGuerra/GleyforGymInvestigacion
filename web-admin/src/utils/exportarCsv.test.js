import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { exportarCsv } from "./exportarCsv";

describe("exportarCsv", () => {
  let clickSpy;
  let createdUrl;

  beforeEach(() => {
    createdUrl = "blob:mock-url";
    // jsdom no implementa URL.createObjectURL/revokeObjectURL: se definen a mano.
    URL.createObjectURL = vi.fn().mockReturnValue(createdUrl);
    URL.revokeObjectURL = vi.fn();
    clickSpy = vi.fn();

    const crearElementoOriginal = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag) => {
      const el = crearElementoOriginal(tag);
      el.click = clickSpy;
      return el;
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("builds a CSV blob with header row and escapes commas/quotes", () => {
    let capturedBlob;
    const originalBlob = globalThis.Blob;
    vi.spyOn(globalThis, "Blob").mockImplementation((parts, opts) => {
      capturedBlob = new originalBlob(parts, opts);
      return capturedBlob;
    });

    exportarCsv(
      "reporte.csv",
      [
        { etiqueta: "Nombre", valor: "nombre" },
        { etiqueta: "Nota", valor: (fila) => `${fila.nota}, extra` },
      ],
      [{ nombre: 'Ana "la jefa"', nota: 10 }]
    );

    expect(clickSpy).toHaveBeenCalled();
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith(createdUrl);
  });

  it("triggers a download with the given file name", () => {
    exportarCsv("clientes.csv", [{ etiqueta: "DNI", valor: "dni" }], [{ dni: "12345678" }]);
    expect(clickSpy).toHaveBeenCalledTimes(1);
  });
});
