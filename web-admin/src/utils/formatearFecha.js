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

// El mismo problema de arriba pero al revés: `Date.prototype.toISOString()`
// siempre da la fecha en UTC, así que usarlo para calcular "hoy" (ej. para
// rellenar un input de fecha por defecto) falla en cualquier momento entre
// ~19:00 y medianoche hora de Perú -- UTC ya está en el día siguiente, y el
// formulario se abre con la fecha de mañana. Se arma el string "YYYY-MM-DD"
// a partir de los componentes LOCALES del Date (año/mes/día), nunca de su
// representación UTC.
export function obtenerFechaLocalISO(fecha = new Date()) {
  const anio = fecha.getFullYear();
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return `${anio}-${mes}-${dia}`;
}
