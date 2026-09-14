// Exportación simple a CSV desde datos ya cargados en el frontend (sin
// librería nueva) — RF-175 pedía "generar reportes" y no había ninguna
// forma de exportar nada del sistema.
function escaparCelda(valor) {
  const texto = valor === null || valor === undefined ? "" : String(valor);
  if (/[",\n]/.test(texto)) {
    return `"${texto.replace(/"/g, '""')}"`;
  }
  return texto;
}

export function exportarCsv(nombreArchivo, columnas, filas) {
  const encabezado = columnas.map((c) => escaparCelda(c.etiqueta)).join(",");
  const lineas = filas.map((fila) =>
    columnas.map((c) => escaparCelda(typeof c.valor === "function" ? c.valor(fila) : fila[c.valor])).join(",")
  );

  const contenido = [encabezado, ...lineas].join("\n");
  const blob = new Blob(["﻿" + contenido], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombreArchivo;
  document.body.appendChild(enlace);
  enlace.click();
  document.body.removeChild(enlace);
  URL.revokeObjectURL(url);
}
