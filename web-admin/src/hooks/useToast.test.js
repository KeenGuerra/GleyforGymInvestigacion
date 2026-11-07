import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useToast } from "./useToast";

describe("useToast", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("starts with no toast", () => {
    const { result } = renderHook(() => useToast());
    expect(result.current.toast).toBeNull();
  });

  it("mostrarError sets a danger toast", () => {
    const { result } = renderHook(() => useToast());
    act(() => result.current.mostrarError("Algo falló"));
    expect(result.current.toast).toEqual({ tipo: "danger", mensaje: "Algo falló" });
  });

  it("mostrarExito sets a success toast", () => {
    const { result } = renderHook(() => useToast());
    act(() => result.current.mostrarExito("Todo bien"));
    expect(result.current.toast).toEqual({ tipo: "success", mensaje: "Todo bien" });
  });

  it("auto-closes after the timeout", () => {
    const { result } = renderHook(() => useToast());
    act(() => result.current.mostrarError("Error temporal"));
    expect(result.current.toast).not.toBeNull();

    act(() => vi.advanceTimersByTime(5000));
    expect(result.current.toast).toBeNull();
  });

  it("cerrarToast clears the toast immediately", () => {
    const { result } = renderHook(() => useToast());
    act(() => result.current.mostrarError("Error temporal"));
    act(() => result.current.cerrarToast());
    expect(result.current.toast).toBeNull();
  });
});
