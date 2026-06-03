# Flujo de Trabajo Git

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento define el flujo de trabajo Git utilizado en el proyecto SistemaGimnasioGleyforGym.

El objetivo es mantener un desarrollo organizado, seguro y colaborativo, evitando conflictos y asegurando la estabilidad del código.

---

# 2. Estructura de Ramas

El proyecto utiliza una estrategia basada en ramas.

```text
main
│
└── develop
    │
    ├── feature/backend
    ├── feature/frontend
    ├── feature/mobile
    ├── feature/ia
    └── feature/documentacion
```

---

# 3. Descripción de las Ramas

## main

Representa la versión estable del sistema.

Características:

- Código listo para producción.
- Sin errores críticos.
- Versiones liberadas.

No se debe desarrollar directamente aquí.

---

## develop

Representa la integración de funcionalidades.

Características:

- Recibe cambios de todas las ramas feature.
- Se utiliza para pruebas generales.
- Antes de pasar a main debe estar validada.

---

## feature/*

Se utilizan para desarrollar funcionalidades específicas.

Ejemplos:

```text
feature/backend
feature/frontend
feature/mobile
feature/ia
feature/documentacion
```

---

# 4. Flujo de Desarrollo

## Paso 1

Actualizar develop.

```bash
git checkout develop

git pull origin develop
```

---

## Paso 2

Crear rama feature.

Ejemplo:

```bash
git checkout -b feature/frontend
```

---

## Paso 3

Realizar cambios.

---

## Paso 4

Agregar cambios.

```bash
git add .
```

---

## Paso 5

Crear commit.

```bash
git commit -m "feat: agregar módulo de progreso físico"
```

---

## Paso 6

Subir cambios.

```bash
git push origin feature/frontend
```

---

## Paso 7

Realizar Pull Request hacia develop.

```text
feature/frontend
        ↓
     develop
```

---

## Paso 8

Validar funcionamiento.

---

## Paso 9

Integrar develop en main.

```text
develop
   ↓
main
```

---

# 5. Flujo Visual

```text
main
 │
 │
 ▼
develop
 │
 ├─────────────┐
 │             │
 ▼             ▼
feature     feature
backend     frontend
 │             │
 └──────┬──────┘
        │
        ▼
     develop
        │
        ▼
       main
```

---

# 6. Convención de Commits

Se utilizará el estándar Conventional Commits.

---

## Nuevas funcionalidades

```bash
git commit -m "feat: agregar generación de rutinas IA"
```

---

## Corrección de errores

```bash
git commit -m "fix: corregir cálculo de edad"
```

---

## Refactorización

```bash
git commit -m "refactor: mejorar estructura de rutas"
```

---

## Documentación

```bash
git commit -m "docs: agregar arquitectura backend"
```

---

## Estilos

```bash
git commit -m "style: mejorar diseño dashboard"
```

---

## Pruebas

```bash
git commit -m "test: agregar pruebas de login"
```

---

# 7. Convención de Branches

## Backend

```text
feature/backend
```

---

## Frontend

```text
feature/frontend
```

---

## Flutter

```text
feature/mobile
```

---

## IA

```text
feature/ia
```

---

## Documentación

```text
feature/documentacion
```

---

# 8. Reglas Importantes

## Regla 1

Nunca trabajar directamente sobre:

```text
main
```

---

## Regla 2

Toda funcionalidad nueva debe pasar por:

```text
feature/*
```

---

## Regla 3

Toda rama feature debe integrarse primero a:

```text
develop
```

---

## Regla 4

Solo versiones estables pasan a:

```text
main
```

---

# 9. Flujo Utilizado en GLEYFORGYM

Actualmente se recomienda:

```text
main
│
develop
│
├── feature/frontend
├── feature/backend
├── feature/mobile
├── feature/ia
└── feature/documentacion
```

---

# 10. Proceso de Integración

## Integrar feature a develop

```bash
git checkout develop

git merge feature/frontend
```

---

## Subir develop

```bash
git push origin develop
```

---

## Integrar develop a main

```bash
git checkout main

git merge develop
```

---

## Subir main

```bash
git push origin main
```

---

# 11. Flujo con GitHub Desktop

## Crear rama

```text
Current Branch
↓
New Branch
```

---

## Cambios

```text
Commit to feature/*
```

---

## Publicar

```text
Push Origin
```

---

## Integrar

```text
Branch
↓
Merge into Current Branch
```

---

# 12. Checklist Antes de Merge

Verificar:

- Backend compila.
- Frontend compila.
- Flutter compila.
- Swagger funciona.
- No existen conflictos.
- No existen credenciales expuestas.
- Se respetó la regla usuario/cliente.
- Se ejecutaron pruebas básicas.

---

# 13. Versionado Recomendado

## Versión Actual

```text
v2.0
```

---

## Próxima Versión

```text
v2.1
```

---

## Futuras

```text
v2.5
v3.0
v4.0
```

---

# 14. Estado Actual

## Ramas Principales

✅ main

✅ develop

---

## Ramas de Trabajo Recomendadas

✅ feature/backend

✅ feature/frontend

✅ feature/mobile

✅ feature/ia

✅ feature/documentacion

---

## Objetivo

Mantener un flujo de trabajo organizado, seguro y escalable para la evolución del SistemaGimnasioGleyforGym.

---