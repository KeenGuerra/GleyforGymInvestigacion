// Vocabulario compartido entre los formularios de Clientes, MiPerfil, Ejercicios
// y Comidas, para que el matching del motor de IA no dependa de strings escritos
// a mano de forma distinta en cada pantalla (debe coincidir con backend/app/constants.py).

export const OBJETIVOS = [
  "Bajar de peso",
  "Ganar masa muscular",
  "Mejorar resistencia",
  "Ganar fuerza",
  "Mantener condición física",
];

export const NIVELES = ["Principiante", "Intermedio", "Avanzado"];

export const GRUPOS_MUSCULARES = [
  "Pecho",
  "Tríceps",
  "Espalda",
  "Bíceps",
  "Piernas",
  "Hombros",
  "Abdomen",
  "Full body",
];

// Catálogo cerrado de restricciones médicas (antes texto libre). El "value" es
// el código que guarda el backend en Cliente.restricciones_medicas.
export const RESTRICCIONES_MEDICAS = [
  { value: "RODILLA", label: "Lesión de rodilla" },
  { value: "HOMBRO", label: "Lesión de hombro" },
  { value: "ESPALDA", label: "Lesión de espalda o columna" },
  { value: "MUNECA_CODO", label: "Lesión de muñeca o codo" },
  { value: "CADERA", label: "Lesión de cadera" },
];

export const NIVELES_ACTIVIDAD = [
  { value: "SEDENTARIO", label: "Sedentario (poco o nada de ejercicio)" },
  { value: "LIGERO", label: "Ligera (1-3 días/semana)" },
  { value: "MODERADO", label: "Moderada (3-5 días/semana)" },
  { value: "ACTIVO", label: "Activa (6-7 días/semana)" },
  { value: "MUY_ACTIVO", label: "Muy activa (trabajo físico o 2 veces al día)" },
];

// Helpers para convertir entre el string "RODILLA,HOMBRO" que guarda el
// backend y el array de códigos que maneja un <input type="checkbox"> múltiple.
export function codigosATexto(codigos) {
  return codigos && codigos.length > 0 ? codigos.join(",") : "";
}

export function textoACodigos(texto) {
  return texto ? texto.split(",").map((c) => c.trim()).filter(Boolean) : [];
}

// Convierte "RODILLA,HOMBRO" en "Lesión de rodilla, Lesión de hombro" para mostrar en pantalla.
export function etiquetasRestricciones(texto) {
  const codigos = textoACodigos(texto);
  if (codigos.length === 0) return "Ninguna";
  return codigos
    .map((c) => RESTRICCIONES_MEDICAS.find((r) => r.value === c)?.label || c)
    .join(", ");
}

export function etiquetaNivelActividad(valor) {
  return NIVELES_ACTIVIDAD.find((n) => n.value === valor)?.label || "No especificado";
}
