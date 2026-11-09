// Las fechas "solo fecha" (YYYY-MM-DD, sin hora) se interpretan como
// medianoche UTC por el estándar ISO 8601 -- en un huso horario negativo
// (ej. Perú, UTC-5, el de los usuarios reales de este gimnasio) eso se
// muestra un día antes al convertir a hora local. Forzamos "T00:00:00"
// (sin zona) para que se parsee como medianoche LOCAL en vez de UTC, y la
// fecha mostrada sea la correcta. Si el string ya trae hora (contiene
// "T"), se deja tal cual.
export function formatearFecha(fecha, opciones) {
  if (!fecha) return "";
  const texto = String(fecha);
  const conHoraLocal = texto.includes("T") ? texto : `${texto}T00:00:00`;
  return new Date(conHoraLocal).toLocaleDateString("es-PE", opciones);
}
