import { useEffect, useState } from "react";
import api from "../api/api";

// Mismos valores que ya estaban escritos a mano en Inicio.jsx -- si el
// GET todavía no responde (primera carga) o falla, la página pública se ve
// igual que antes en vez de mostrar campos vacíos un instante.
const CONFIGURACION_POR_DEFECTO = {
  telefono: "+51 902321009",
  email: "gleyfor3@gmail.com",
  direccion: "Chupaca, Perú",
  facebook_url: "https://www.facebook.com/p/Gleyfor-GYM-61579024964992/",
  instagram_url: "https://www.instagram.com/gleyforgym/",
  tiktok_url: "https://www.tiktok.com/@gleyforgym",
  whatsapp_numero: "51902321009",
  mapa_embed_url:
    "https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d243.85664196895084" +
    "!2d-75.28908014431451!3d-12.06371950223546!2m3!1f0!2f0!3f0!3m2!1i1024!2i768" +
    "!4f13.1!5e0!3m2!1ses!2spe!4v1777926809952!5m2!1ses!2spe",
  logo_url: null,
};

/**
 * Datos de contacto/redes sociales/logo del gimnasio, editables desde
 * `/configuracion` (ver Configuracion.jsx) -- antes estaban fijos en el
 * código de Inicio.jsx/Navbar.jsx. `logo_url` nulo (todavía no se subió
 * ninguno) significa "usa el PNG empaquetado de siempre", nunca rompe nada.
 */
export function useConfiguracionSitio() {
  const [configuracion, setConfiguracion] = useState(CONFIGURACION_POR_DEFECTO);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let activo = true;

    api.get("/configuracion/")
      .then((res) => {
        if (activo) setConfiguracion(res.data);
      })
      .catch((error) => {
        console.error("Error al cargar la configuración del sitio:", error);
      })
      .finally(() => {
        if (activo) setCargando(false);
      });

    return () => {
      activo = false;
    };
  }, []);

  return { configuracion, cargando };
}
