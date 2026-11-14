import { useCallback, useRef, useState } from "react";

/**
 * Confirmación modal propia (clases de Bootstrap, ver ConfirmModal.jsx y
 * ../styles/bootstrap-custom.scss) en vez de window.confirm() -- el diálogo
 * nativo del navegador aparece como una barra simple arriba de la ventana,
 * sin el estilo de la app.
 *
 * confirmarAccion(mensaje) devuelve una promesa que resuelve true/false
 * según lo que elija el usuario, para poder seguir escribiendo
 * "if (!(await confirmarAccion(...))) return;" en vez de reescribir cada
 * función que ya hacía esa misma pregunta con el diálogo nativo.
 */
export function useConfirmacion() {
  const [pregunta, setPregunta] = useState(null);
  const resolverRef = useRef(null);

  const confirmarAccion = useCallback((mensaje) => {
    return new Promise((resolve) => {
      resolverRef.current = resolve;
      setPregunta(mensaje);
    });
  }, []);

  const responderConfirmacion = useCallback((valor) => {
    setPregunta(null);
    if (resolverRef.current) {
      resolverRef.current(valor);
      resolverRef.current = null;
    }
  }, []);

  return { pregunta, confirmarAccion, responderConfirmacion };
}
