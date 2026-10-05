"""
Script de validacion cuantitativa del motor de recomendacion (rutinas y nutricion).

No requiere datos de produccion: construye un catalogo de ejercicios y comidas
representativo (variado en grupo muscular, nivel y objetivo) en una base SQLite
dedicada, y ejecuta la logica REAL del motor (app.ia.rutina / app.ia.nutricion,
sin ninguna modificacion) sobre todas las combinaciones de perfil de cliente
relevantes para el sistema.

Metricas reportadas (documentadas en docs/07_Gestion_Proyecto/Intervencion_Metodologica.md,
seccion 8.4):
  1. Tasa de ejercicios contraindicados (meta: 0%).
  2. Error absoluto medio (MAE) entre las calorias reales del plan nutricional
     generado y las calorias objetivo calculadas, en porcentaje.
  3. Cobertura: porcentaje de perfiles que reciben una rutina/plan completo,
     sin dias o franjas horarias sin opciones disponibles.

Ejecutar con: venv/Scripts/python.exe validacion_motor_recomendacion.py
"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
import app.models as models
from app.constants import (
    GRUPO_PECHO, GRUPO_TRICEPS, GRUPO_ESPALDA, GRUPO_BICEPS,
    GRUPO_PIERNAS, GRUPO_HOMBROS, GRUPO_ABDOMEN, GRUPO_FULL_BODY,
    NIVELES, OBJETIVOS, RESTRICCIONES_MEDICAS, RESTRICCION_NINGUNA,
    NIVELES_ACTIVIDAD,
)
from app.ia.rutina.recomendador_rutinas import (
    generar_rutina_inteligente, obtener_grupos_excluidos,
)
from app.ia.nutricion.recomendador_nutricion import seleccionar_comidas_para_plan
from app.ia.nutricion.calculos_nutricion import calcular_macros

DB_PATH = Path(__file__).resolve().parent / "validacion_motor.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

GRUPOS = [
    GRUPO_PECHO, GRUPO_TRICEPS, GRUPO_ESPALDA, GRUPO_BICEPS,
    GRUPO_PIERNAS, GRUPO_HOMBROS, GRUPO_ABDOMEN, GRUPO_FULL_BODY,
]

TIPOS_COMIDA = ["DESAYUNO", "MEDIA MAÑANA", "ALMUERZO", "MERIENDA", "CENA"]
RANGO_CALORIAS_POR_TIPO = {
    "DESAYUNO": (300, 500),
    "MEDIA MAÑANA": (100, 250),
    "ALMUERZO": (500, 800),
    "MERIENDA": (150, 300),
    "CENA": (400, 650),
}


def construir_catalogo(db):
    """Catalogo sintetico representativo: 2 ejercicios por grupo muscular x nivel
    (48 ejercicios) y 2 comidas por tipo x objetivo (60 comidas), variado a
    proposito para que el motor tenga opciones reales entre las que elegir."""
    id_ejercicio = 1
    for grupo in GRUPOS:
        for nivel in NIVELES:
            for variante in range(2):
                db.add(models.Ejercicio(
                    id_ejercicio=id_ejercicio,
                    nombre=f"{grupo} {nivel} variante {variante + 1}",
                    grupo_muscular=grupo,
                    nivel=nivel,
                    objetivo="General",
                    descripcion="Ejercicio sintetico de validacion",
                    instrucciones="N/A",
                    estado="ACTIVO",
                ))
                id_ejercicio += 1

    objetivos_catalogo = OBJETIVOS + ["GENERAL"]
    id_comida = 1
    for tipo in TIPOS_COMIDA:
        lo, hi = RANGO_CALORIAS_POR_TIPO[tipo]
        for objetivo in objetivos_catalogo:
            for variante in range(2):
                calorias = lo + (hi - lo) * variante // 1
                db.add(models.Comida(
                    id_comida_catalogo=id_comida,
                    nombre=f"{tipo.title()} sintetica {objetivo} #{variante + 1}",
                    descripcion=f"{tipo.title()} sintetica {objetivo} #{variante + 1}",
                    tipo_comida=tipo,
                    calorias=calorias,
                    proteinas=round(calorias * 0.2 / 4),
                    carbohidratos=round(calorias * 0.5 / 4),
                    grasas=round(calorias * 0.3 / 9),
                    estado="ACTIVO",
                    objetivo=objetivo,
                ))
                id_comida += 1
    db.commit()


def validar_rutinas(db):
    total = 0
    con_contraindicacion = 0
    completos_sin_avisos = 0
    huecos_por_restriccion = 0  # esperado: el grupo esta bloqueado a proposito
    huecos_por_catalogo = 0     # inesperado: el grupo estaba permitido y no habia opciones
    detalle_contraindicados = []

    restricciones = RESTRICCIONES_MEDICAS  # incluye NINGUNA
    for objetivo in OBJETIVOS:
        for nivel in NIVELES:
            for restriccion in restricciones:
                total += 1
                restriccion_cliente = None if restriccion == RESTRICCION_NINGUNA else restriccion
                cliente = SimpleNamespace(
                    objetivo=objetivo, nivel=nivel,
                    restricciones_medicas=restriccion_cliente,
                )
                resultado = generar_rutina_inteligente(db, cliente)

                grupos_excluidos = obtener_grupos_excluidos(restriccion_cliente)
                ejercicios_contraindicados = [
                    e for e in resultado["ejercicios"]
                    if e["grupo_muscular"] in grupos_excluidos
                ]
                if ejercicios_contraindicados:
                    con_contraindicacion += 1
                    detalle_contraindicados.append(
                        (objetivo, nivel, restriccion, len(ejercicios_contraindicados))
                    )

                if not resultado["avisos"]:
                    completos_sin_avisos += 1

                for aviso in resultado["avisos"]:
                    for grupo in aviso["grupos"]:
                        if grupo in grupos_excluidos:
                            huecos_por_restriccion += 1
                        else:
                            huecos_por_catalogo += 1

    return {
        "total": total,
        "con_contraindicacion": con_contraindicacion,
        "tasa_contraindicacion_pct": round(100 * con_contraindicacion / total, 2),
        "completos_sin_avisos": completos_sin_avisos,
        "cobertura_bruta_pct": round(100 * completos_sin_avisos / total, 2),
        "huecos_por_restriccion": huecos_por_restriccion,
        "huecos_por_catalogo": huecos_por_catalogo,
        "detalle_contraindicados": detalle_contraindicados,
    }


def validar_nutricion(db):
    comidas = db.query(models.Comida).all()

    pesos_estaturas_edades = [
        (55, 1.55, 22), (70, 1.70, 30), (90, 1.85, 45),
    ]
    sexos = ["M", "F"]

    total = 0
    errores_pct = []
    completos = 0

    for objetivo in OBJETIVOS:
        for nivel_actividad in NIVELES_ACTIVIDAD:
            for sexo in sexos:
                for peso, estatura, edad in pesos_estaturas_edades:
                    total += 1
                    cliente = SimpleNamespace(
                        peso=peso, estatura=estatura, fecha_nacimiento=None,
                        sexo=sexo, nivel_actividad=nivel_actividad, objetivo=objetivo,
                    )
                    # calculos_nutricion usa fecha_nacimiento para la edad; se
                    # fuerza la edad deseada vía un objeto con _calcular_edad
                    # ya resuelta no es posible sin DB, así que se aproxima
                    # usando el default solo si fecha_nacimiento es None.
                    macros = calcular_macros(cliente)
                    resultado = seleccionar_comidas_para_plan(cliente, comidas)

                    objetivo_kcal = macros["calorias"]
                    real_kcal = resultado["calorias_reales"]
                    error_pct = abs(real_kcal - objetivo_kcal) / objetivo_kcal * 100
                    errores_pct.append(error_pct)

                    if not resultado["avisos"]:
                        completos += 1

    mae_pct = round(sum(errores_pct) / len(errores_pct), 2)
    return {
        "total": total,
        "mae_calorico_pct": mae_pct,
        "completos": completos,
        "cobertura_pct": round(100 * completos / total, 2),
    }


def contar_catalogo(db):
    conteo = {}
    for grupo in GRUPOS:
        for nivel in NIVELES:
            n = db.query(models.Ejercicio).filter(
                models.Ejercicio.grupo_muscular == grupo,
                models.Ejercicio.nivel == nivel,
            ).count()
            conteo[(grupo, nivel)] = n
    return conteo


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    construir_catalogo(db)

    print("=== Catalogo de ejercicios por grupo muscular x nivel ===")
    conteo = contar_catalogo(db)
    for (grupo, nivel), n in conteo.items():
        print(f"  {grupo:12s} | {nivel:12s} | {n} ejercicios")

    print("\n=== Validacion motor de rutinas ===")
    res_rutinas = validar_rutinas(db)
    print(f"Perfiles evaluados (objetivo x nivel x restriccion): {res_rutinas['total']}")
    print(f"Perfiles con >=1 ejercicio contraindicado: {res_rutinas['con_contraindicacion']}")
    print(f"Tasa de contraindicacion: {res_rutinas['tasa_contraindicacion_pct']}%  <-- metrica critica, meta 0%")
    print(f"Perfiles sin ningun aviso (bruto): {res_rutinas['completos_sin_avisos']} ({res_rutinas['cobertura_bruta_pct']}%)")
    print(f"Huecos por restriccion medica activa (esperado/correcto): {res_rutinas['huecos_por_restriccion']}")
    print(f"Huecos por catalogo insuficiente (grupo permitido sin ejercicios): {res_rutinas['huecos_por_catalogo']}  <-- metrica de cobertura real")
    if res_rutinas["detalle_contraindicados"]:
        print("Detalle de contraindicaciones encontradas:")
        for d in res_rutinas["detalle_contraindicados"]:
            print(f"  {d}")

    print("\n=== Validacion motor de nutricion ===")
    res_nutricion = validar_nutricion(db)
    print(f"Perfiles evaluados (objetivo x nivel_actividad x sexo x cuerpo): {res_nutricion['total']}")
    print(f"Error absoluto medio (calorias reales vs objetivo): {res_nutricion['mae_calorico_pct']}%")
    print(f"Perfiles con plan completo (sin franjas vacias): {res_nutricion['completos']}")
    print(f"Cobertura: {res_nutricion['cobertura_pct']}%")

    db.close()
    engine.dispose()
    DB_PATH.unlink()


if __name__ == "__main__":
    main()
