import { useCallback, useRef, useState } from "react";

const DURACION_MS = 5000;

/**
 * Notificaciones flotantes (toast) para pantallas sin un slot de error
 * inline, como los dashboards. El auto-cierre se maneja con setTimeout en
 * vez del runtime JS de Bootstrap (bootstrap.bundle.js), para no mezclar su
 * ciclo de vida imperativo con el renderizado declarativo de React.
 */
export function useToast() {
  const [toast, setToast] = useState(null);
  const timeoutRef = useRef(null);

  const cerrarToast = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setToast(null);
  }, []);

  const mostrar = useCallback((tipo, mensaje) => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setToast({ tipo, mensaje });
    timeoutRef.current = setTimeout(() => setToast(null), DURACION_MS);
  }, []);

  const mostrarError = useCallback((mensaje) => mostrar("danger", mensaje), [mostrar]);
  const mostrarExito = useCallback((mensaje) => mostrar("success", mensaje), [mostrar]);

  return { toast, mostrarError, mostrarExito, cerrarToast };
}
