import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import CORS_ORIGINS
from app.routes import (
    usuarios,
    clientes,
    entrenadores,
    membresias,
    cliente_membresias,
    pagos,
    asistencias,
    progreso,
    rutinas,
    nutricion,
    ejercicios,
    comidas,
    categorias,
    productos,
    proveedores,
    compras,
    inventario,
    ventas,
    reportes,
    auditoria,
    webhooks,
    avisos,
)

from app.routes.ia import ia_rutina, ia_nutricion

logger = logging.getLogger("gleyforgym")

INTERVALO_VENCIMIENTO_MEMBRESIAS_SEGUNDOS = 24 * 60 * 60  # una vez al día


async def _tarea_periodica_vencimiento_membresias():
    """RF06: antes esto solo corría cuando alguien pegaba a un GET de
    cliente-membresias; ahora corre sola en el servidor sin depender de que
    algún usuario abra esa pantalla ese día."""
    from app.database import SessionLocal
    from app.routes.cliente_membresias import actualizar_membresias_vencidas

    while True:
        db = SessionLocal()
        try:
            actualizar_membresias_vencidas(db)
        except Exception:
            logger.exception("Error actualizando membresías vencidas")
        finally:
            db.close()
        await asyncio.sleep(INTERVALO_VENCIMIENTO_MEMBRESIAS_SEGUNDOS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    tarea = asyncio.create_task(_tarea_periodica_vencimiento_membresias())
    yield
    tarea.cancel()


app = FastAPI(
    title="API GLEYFORGYM",
    description="API para la gestión del gimnasio GLEYFORGYM",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def catch_all_handler(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)

    origin = request.headers.get("origin", "")
    headers = {}
    if origin in CORS_ORIGINS or origin.endswith(".onrender.com"):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno. Intenta nuevamente más tarde."},
        headers=headers,
    )


app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(entrenadores.router, prefix="/entrenadores", tags=["Entrenadores"])
app.include_router(membresias.router, prefix="/membresias", tags=["Membresías"])
app.include_router(cliente_membresias.router, prefix="/cliente-membresias", tags=["Cliente Membresías"])
app.include_router(pagos.router, prefix="/pagos", tags=["Pagos"])
app.include_router(asistencias.router, prefix="/asistencias", tags=["Asistencias"])
app.include_router(progreso.router, prefix="/progreso", tags=["Progreso"])
app.include_router(rutinas.router, prefix="/rutinas", tags=["Rutinas"])
app.include_router(nutricion.router, prefix="/nutricion", tags=["Nutrición"])
app.include_router(ejercicios.router, prefix="/ejercicios", tags=["Ejercicios"])
app.include_router(comidas.router, prefix="/comidas", tags=["Comidas"])

app.include_router(categorias.router, prefix="/categorias", tags=["Categorías"])
app.include_router(productos.router, prefix="/productos", tags=["Productos"])
app.include_router(proveedores.router, prefix="/proveedores", tags=["Proveedores"])
app.include_router(compras.router, prefix="/compras", tags=["Compras"])
app.include_router(inventario.router, prefix="/inventario", tags=["Inventario"])
app.include_router(ventas.router, prefix="/ventas", tags=["Ventas"])

app.include_router(ia_rutina.router, prefix="/ia/rutina", tags=["IA Rutina"])
app.include_router(ia_nutricion.router, prefix="/ia/nutricion", tags=["IA Nutrición"])

app.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
app.include_router(auditoria.router, prefix="/auditoria", tags=["Auditoría"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(avisos.router, prefix="/avisos", tags=["Avisos"])


@app.get("/")
def root():
    return {"mensaje": "API GLEYFORGYM funcionando"}
