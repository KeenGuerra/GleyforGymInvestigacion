import { describe, it, expect, vi } from "vitest";
import api from "./api";

describe("Configuración de API Axios", () => {
  it("debe usar la URL base correcta", () => {
    expect(api.defaults.baseURL).toBeDefined();
    expect(api.defaults.baseURL).toContain("http://");
  });

  it("debe agregar cabecera de Authorization si existe token en localStorage", () => {
    const mockStorage = {
      token: "token_de_prueba_jwt",
    };

    vi.stubGlobal("localStorage", {
      getItem: (key) => mockStorage[key],
      setItem: (key, value) => { mockStorage[key] = value; },
      clear: () => { delete mockStorage.token; }
    });

    // Simular el interceptor de petición
    const mockConfig = { headers: {} };
    const requestInterceptor = api.interceptors.request.handlers[0].fulfilled;
    const result = requestInterceptor(mockConfig);

    expect(result.headers.Authorization).toBe("Bearer token_de_prueba_jwt");

    vi.unstubAllGlobals();
  });

  it("debe limpiar localStorage y redirigir al login en caso de 401", async () => {
    const mockStorage = {
      token: "token_de_prueba_jwt",
    };

    let cleared = false;
    let redirected = false;

    vi.stubGlobal("localStorage", {
      getItem: (key) => mockStorage[key],
      clear: () => { cleared = true; }
    });

    vi.stubGlobal('location', {
      _href: '',
      get href() { return this._href; },
      set href(val) {
        this._href = val;
        redirected = true;
      }
    });

    // Interceptor de respuesta de error
    const errorInterceptor = api.interceptors.response.handlers[0].rejected;
    const mockError = {
      response: { status: 401 }
    };

    try {
      await errorInterceptor(mockError);
    } catch {
      // Ignorar el rechazo de la promesa
    }

    expect(cleared).toBe(true);
    expect(redirected).toBe(true);

    vi.unstubAllGlobals();
  });

  it("NO debe limpiar localStorage ni redirigir en caso de 403 (sesión válida, acción prohibida)", async () => {
    let cleared = false;
    let redirected = false;

    vi.stubGlobal("localStorage", {
      getItem: () => "token_de_prueba_jwt",
      clear: () => { cleared = true; }
    });

    vi.stubGlobal('location', {
      _href: '',
      get href() { return this._href; },
      set href(val) {
        this._href = val;
        redirected = true;
      }
    });

    const errorInterceptor = api.interceptors.response.handlers[0].rejected;
    const mockError = {
      response: { status: 403, data: { detail: "Acceso restringido a: ADMIN" } }
    };

    try {
      await errorInterceptor(mockError);
    } catch {
      // Ignorar el rechazo de la promesa; cada pantalla maneja su propio mensaje de error
    }

    expect(cleared).toBe(false);
    expect(redirected).toBe(false);

    vi.unstubAllGlobals();
  });
});
