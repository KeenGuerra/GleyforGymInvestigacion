import { describe, it, expect } from "vitest";
import { formatearFecha, obtenerFechaLocalISO } from "./formatearFecha";

describe("formatearFecha", () => {
  it("returns the exact same calendar day for a date-only string, regardless of the machine's timezone", () => {
    // Referencia segura: mediodía UTC nunca cruza a otro día sin importar
    // el huso horario local -- sirve para saber cuál es el día/mes/año
    // "verdadero" de "2026-06-20" sin depender del bug que se corrige.
    const referencia = new Date("2026-06-20T12:00:00Z");

    const resultado = formatearFecha("2026-06-20");

    expect(resultado).toContain(String(referencia.getUTCDate()));
    expect(resultado).not.toContain("19");
  });

  it("does not shift a date that already has a time component", () => {
    const resultado = formatearFecha("2026-06-20T15:30:00");
    expect(resultado).toContain("20");
  });

  it("returns an empty string for null/undefined/empty input", () => {
    expect(formatearFecha(null)).toBe("");
    expect(formatearFecha(undefined)).toBe("");
    expect(formatearFecha("")).toBe("");
  });

  it("forwards formatting options to toLocaleDateString", () => {
    const resultado = formatearFecha("2026-06-20", { day: "numeric", month: "long", year: "numeric" });
    expect(resultado).toBe("20 de junio de 2026");
  });

  it("matches the plain toLocaleDateString('es-PE') output (default short format) when no options are given", () => {
    const resultado = formatearFecha("2026-06-20");
    expect(resultado).toBe(new Date("2026-06-20T00:00:00").toLocaleDateString("es-PE"));
  });
});

describe("obtenerFechaLocalISO", () => {
  it("uses the Date object's local components, not its UTC representation", () => {
    // Construido con el constructor numerico (hora local explicita), no a
    // partir de un string -- asi el resultado no depende de la zona horaria
    // de la maquina que corre el test, solo de que la funcion lea
    // getFullYear/getMonth/getDate en vez de pasar por toISOString() (que
    // siempre da la fecha en UTC y es justo el bug que se corrige: a las
    // 23:00 hora de Peru, toISOString() ya muestra el dia siguiente).
    const finDeMes = new Date(2026, 10, 30, 23, 0, 0);
    expect(obtenerFechaLocalISO(finDeMes)).toBe("2026-11-30");
  });

  it("pads month and day to two digits", () => {
    expect(obtenerFechaLocalISO(new Date(2026, 0, 5))).toBe("2026-01-05");
  });

  it("defaults to the current moment when called without arguments", () => {
    expect(obtenerFechaLocalISO()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});
