# GleyforGym

Sistema web de gestión integral para el gimnasio GLEYFORGYM: administración de clientes, membresías, pagos, asistencias y progreso físico, con generación de rutinas y planes nutricionales mediante un motor de recomendación basado en reglas.

Proyecto de tesis: *"Implementación de un sistema web con inteligencia artificial para mejorar la gestión de los procesos del gimnasio GLEYFORGYM - 2027"*.

## Alcance del proyecto

La tesis cubre formalmente el **sistema web**: backend (`backend/`) y panel de administración (`web-admin/`). El repositorio también incluye una aplicación móvil complementaria en Flutter (`mobile-app/`), que **no forma parte del alcance evaluado en la tesis** y se mantiene como componente independiente del ecosistema.

## Tecnologías

| Componente | Tecnología |
|---|---|
| Backend | FastAPI (Python) + SQLAlchemy |
| Base de datos | PostgreSQL |
| Frontend | React + Vite |
| Autenticación | JWT + bcrypt |
| Multimedia | Cloudinary |
| IA | Motor de recomendación basado en reglas (rutinas y nutrición) |
| Despliegue | Render (`render.yaml`) |

## Estructura del repositorio

```text
GleyforGym/
├── backend/        API FastAPI, modelos, lógica de negocio e IA, tests (pytest)
├── web-admin/       Panel de administración en React (tests con Vitest)
├── mobile-app/      App Flutter complementaria (fuera del alcance de la tesis)
└── docs/            Documentación del proyecto (ver abajo)
```

## Documentación

Toda la documentación técnica y de negocio vive en `docs/`, organizada por carpetas numeradas:

| Carpeta | Contenido |
|---|---|
| `02_Negocio/` | Reglas de negocio y matriz de roles/permisos |
| `03_Analisis/` | Requerimientos funcionales (RF) y no funcionales (RNF) |
| `04_Arquitectura/` | Arquitectura general, backend, frontend, base de datos, IA, multimedia |
| `05_Desarrollo/` | Guías de instalación/despliegue, convenciones, flujo Git, manual del desarrollador, roadmap, casos de prueba |
| `06_Operacion/` | Troubleshooting |
| `07_Gestion_Proyecto/` | Decisiones de arquitectura y **pendientes actuales del proyecto** |
| `09_mockups/` | Mockups de diseño visual |

Para saber qué está implementado y qué falta hoy, la referencia vigente es:
- [`docs/05_Desarrollo/Roadmap.md`](docs/05_Desarrollo/Roadmap.md) — estado general del proyecto.
- [`docs/07_Gestion_Proyecto/Pendientes.md`](docs/07_Gestion_Proyecto/Pendientes.md) — inventario detallado y priorizado de lo pendiente.

## Primeros pasos

Ver [`docs/05_Desarrollo/Guia_Instalacion.md`](docs/05_Desarrollo/Guia_Instalacion.md) para la instalación local completa, y [`docs/05_Desarrollo/Guia_Despliegue.md`](docs/05_Desarrollo/Guia_Despliegue.md) para el despliegue en producción (Render).

Resumen rápido:

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python create_db.py
uvicorn app.main:app --reload

# Frontend
cd web-admin
npm install
npm run dev
```

## Pruebas

- Backend: `pytest` (suite de integración sobre todos los módulos).
- Frontend: `npm run test -- --run` (Vitest + Testing Library).

El detalle de cobertura por módulo está en `docs/07_Gestion_Proyecto/Pendientes.md`; el checklist de casos de prueba funcionales está en `docs/05_Desarrollo/Casos_Prueba.md`.

## Versión actual

```text
v2.6
```
