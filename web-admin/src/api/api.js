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
    // Un 401 solo implica sesion invalida si YA habia una sesion (token
    // guardado antes de esta peticion). Si no habia token, es un 401
    // "normal" de un endpoint publico (ej. contraseña incorrecta en
    // /usuarios/login) y la pantalla ya muestra su propio error — no hay
    // nada que cerrar ni por qué recargar la página. Un 403 es "no tienes
    // permiso para esto" con una sesion valida: no debe cerrar sesion,
    // cada pantalla ya muestra ese error.
    const habiaSesion = !!localStorage.getItem("token");
    if (error.response?.status === 401 && habiaSesion) {
      cerrarSesion();
    }

    return Promise.reject(error);
  }
);

export default api;