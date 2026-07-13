from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import (
    usuarios,
    clientes,
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
)

from app.routes.ia import ia_rutina, ia_nutricion


app = FastAPI(
    title="API GLEYFORGYM",
    description="API para la gestión del gimnasio GLEYFORGYM",
    version="1.0.0"
)


ORIGINS = [
    "https://gleyforgym-frontend.onrender.com",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def catch_all_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in ORIGINS or origin.endswith(".onrender.com"):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=headers,
    )


app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
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


@app.get("/")
def root():
    return {"mensaje": "API GLEYFORGYM funcionando"}
