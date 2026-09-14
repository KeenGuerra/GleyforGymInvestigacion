import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

// Única forma de cerrar sesión en toda la app (botón de logout y el
// interceptor de abajo), para no tener dos implementaciones que limpien
// el storage y redirijan de forma distinta.
export function cerrarSesion() {
  localStorage.clear();
  globalThis.location.href = "/login";
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Solo un 401 (token ausente/invalido/expirado) implica que la sesion ya
    // no sirve. Un 403 es "no tienes permiso para esto" con una sesion
    // valida: no debe cerrar sesion, cada pantalla ya muestra ese error.
    if (error.response?.status === 401) {
      cerrarSesion();
    }

    return Promise.reject(error);
  }
);

export default api;