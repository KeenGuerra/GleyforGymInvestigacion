import { useCallback, useEffect, useState } from "react";
import api from "../api/api";

/**
 * Resuelve el registro Cliente del usuario CLIENTE logueado a partir del
 * id_usuario guardado en localStorage. Antes cada página Mi*.jsx repetía
 * este mismo fetch por su cuenta.
 */
export function useClienteActual() {
  const [cliente, setCliente] = useState(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);

  const recargarCliente = useCallback(async () => {
    try {
      setError("");
      const idUsuario = localStorage.getItem("id_usuario");
      const res = await api.get(`/clientes/usuario/${idUsuario}`);
      setCliente(res.data);
      return res.data;
    } catch (error) {
      console.error(error);
      setError("No se pudo cargar tu información de cliente.");
      return null;
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    recargarCliente();
  }, [recargarCliente]);

  return { cliente, setCliente, error, cargando, recargarCliente };
}
