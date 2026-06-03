# Plan de Pruebas

# SistemaGimnasioGleyforGym

## 1. Introducción

El presente documento define la estrategia de pruebas para el SistemaGimnasioGleyforGym.

Su propósito es garantizar que todas las funcionalidades implementadas funcionen correctamente y cumplan los requerimientos funcionales y no funcionales definidos para el proyecto.

---

# 2. Objetivos

## Objetivo General

Validar el correcto funcionamiento del sistema web y móvil del gimnasio GLEYFORGYM.

---

## Objetivos Específicos

- Verificar el funcionamiento de cada módulo.
- Detectar errores antes del despliegue.
- Validar la integración entre componentes.
- Garantizar la calidad de los datos.
- Verificar el cumplimiento de las reglas de negocio.

---

# 3. Alcance

Las pruebas cubrirán:

## Backend

- FastAPI
- JWT
- SQLAlchemy
- IA
- Cloudinary

---

## Frontend

- React
- Rutas
- Formularios
- Dashboards

---

## Aplicación Móvil

- Flutter
- Consumo de API

---

## Base de Datos

- PostgreSQL
- Relaciones
- Restricciones

---

# 4. Tipos de Prueba

## 4.1 Pruebas Unitarias

Validan componentes individuales.

Ejemplos:

- Cálculo de edad.
- Generación de JWT.
- Validación de contraseña.
- Reglas IA.

---

## 4.2 Pruebas de Integración

Validan interacción entre módulos.

Ejemplos:

- React ↔ FastAPI.
- FastAPI ↔ PostgreSQL.
- FastAPI ↔ Cloudinary.
- Flutter ↔ FastAPI.

---

## 4.3 Pruebas Funcionales

Validan requerimientos funcionales.

Ejemplos:

- Login.
- Crear cliente.
- Asignar membresía.
- Generar rutina.

---

## 4.4 Pruebas de Seguridad

Validan protección del sistema.

Ejemplos:

- JWT.
- Roles.
- Rutas protegidas.

---

## 4.5 Pruebas de Aceptación

Validan que el sistema cumple los objetivos del negocio.

---

# 5. Entorno de Pruebas

## Backend

```text
http://127.0.0.1:8000
```

---

## Swagger

```text
http://127.0.0.1:8000/docs
```

---

## Frontend

```text
http://localhost:5173
```

---

## Base de Datos

```text
PostgreSQL
```

---

# 6. Módulos a Validar

| Módulo | Prioridad |
|----------|----------|
| Login | Alta |
| Usuarios | Alta |
| Clientes | Alta |
| Membresías | Alta |
| Pagos | Alta |
| Asistencias | Alta |
| Progreso | Alta |
| Ejercicios | Alta |
| Comidas | Alta |
| Rutinas IA | Alta |
| Nutrición IA | Alta |
| Cloudinary | Media |
| Flutter | Media |

---

# 7. Criterios de Aceptación

Una prueba se considera aprobada cuando:

- Resultado esperado = resultado obtenido.
- No existen errores de ejecución.
- No existen errores de validación.
- Los datos se almacenan correctamente.

---

# 8. Criterios de Rechazo

Una prueba se considera fallida cuando:

- Existe excepción no controlada.
- No se guarda la información.
- Se rompe una regla de negocio.
- Se obtiene información incorrecta.

---

# 9. Cobertura Objetivo

| Tipo | Cobertura |
|----------|----------|
| Funcional | 100% |
| Integración | 90% |
| Seguridad | 90% |
| Unitarias | 80% |

---

# 10. Riesgos

## Alto

- Error en generación IA.
- Error en pagos.
- Error en autenticación.

---

## Medio

- Error en Cloudinary.
- Error en dashboards.

---

## Bajo

- Error visual.
- Error de estilos.

---

# 11. Resultado Esperado

El sistema debe permitir:

- Gestionar clientes.
- Gestionar membresías.
- Gestionar pagos.
- Gestionar progreso.
- Generar rutinas IA.
- Generar nutrición IA.

sin errores críticos.

---