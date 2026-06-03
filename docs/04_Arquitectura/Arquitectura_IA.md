# Arquitectura de Inteligencia Artificial

# SistemaGimnasioGleyforGym

## 1. Introducción

El SistemaGimnasioGleyforGym incorpora módulos de inteligencia artificial para generar automáticamente:

- Rutinas de entrenamiento personalizadas.
- Planes nutricionales personalizados.

La inteligencia artificial utiliza información real almacenada en la base de datos para adaptar las recomendaciones a las características de cada cliente.

---

## 2. Objetivo

El objetivo principal es automatizar la personalización de rutinas y planes nutricionales, reduciendo el trabajo manual de los entrenadores y mejorando la experiencia de los clientes.

---

## 3. Ubicación en el Proyecto

```text
backend
│
└── app
    │
    └── ia
        │
        ├── rutina
        │   ├── recomendador_rutinas.py
        │   └── reglas_rutinas.py
        │
        └── nutricion
            ├── calculos_nutricion.py
            ├── planes_comida.py
            └── recomendador_nutricion.py
```

---

## 4. Arquitectura General

```text
Cliente
   │
   ▼
Datos Personales
Objetivo
Nivel
Peso
Estatura
Restricciones
   │
   ▼
Motor IA
   │
   ├─────────────┐
   │             │
   ▼             ▼
Rutinas IA   Nutrición IA
   │             │
   ▼             ▼
Base de Datos
```

---

# MÓDULO IA DE RUTINAS

## 5. Objetivo

Generar rutinas personalizadas utilizando:

- Objetivo físico.
- Nivel de experiencia.
- Estado físico.
- Catálogo de ejercicios.

---

## 6. Componentes

### recomendador_rutinas.py

Responsable de:

- Analizar datos del cliente.
- Seleccionar ejercicios.
- Construir la rutina.

---

### reglas_rutinas.py

Responsable de:

- Aplicar reglas de entrenamiento.
- Determinar series.
- Determinar repeticiones.
- Determinar descansos.

---

## 7. Datos Utilizados

La IA consulta:

```text
clientes
```

Campos utilizados:

```text
objetivo
nivel
peso
estatura
edad
```

---

También consulta:

```text
ejercicios
```

Campos utilizados:

```text
grupo_muscular
nivel
objetivo
estado
```

---

## 8. Flujo de Generación

```text
Cliente
   │
   ▼
Objetivo
Nivel
Datos físicos
   │
   ▼
Filtrar ejercicios activos
   │
   ▼
Aplicar reglas
   │
   ▼
Generar rutina
   │
   ▼
Guardar rutina
```

---

## 9. Reglas Principales

### Hipertrofia

```text
3 - 5 series
8 - 12 repeticiones
```

---

### Fuerza

```text
4 - 6 series
3 - 6 repeticiones
```

---

### Resistencia

```text
2 - 4 series
15 - 20 repeticiones
```

---

### Pérdida de grasa

```text
Circuitos
Mayor volumen
Menor descanso
```

---

## 10. Restricciones

La IA únicamente utiliza ejercicios:

```text
estado = ACTIVO
```

---

No puede generar rutinas para:

```text
clientes inexistentes
```

---

## 11. Endpoint

```http
POST /ia/rutina/generar/{id_cliente}
```

Ejemplo:

```http
POST /ia/rutina/generar/15
```

---

# MÓDULO IA DE NUTRICIÓN

## 12. Objetivo

Generar planes nutricionales personalizados.

---

## 13. Componentes

### calculos_nutricion.py

Responsable de:

- Calcular calorías.
- Calcular macronutrientes.

---

### planes_comida.py

Responsable de:

- Construir la distribución alimentaria.

---

### recomendador_nutricion.py

Responsable de:

- Seleccionar comidas.
- Generar el plan completo.

---

## 14. Datos Utilizados

Información del cliente:

```text
peso
estatura
edad
sexo
objetivo
restricciones_medicas
```

---

Catálogo nutricional:

```text
comidas
```

Campos utilizados:

```text
calorias
proteinas
carbohidratos
grasas
objetivo
estado
```

---

## 15. Flujo de Generación

```text
Cliente
   │
   ▼
Peso
Estatura
Objetivo
Restricciones
   │
   ▼
Calcular requerimientos
   │
   ▼
Seleccionar comidas
   │
   ▼
Construir plan
   │
   ▼
Guardar plan nutricional
```

---

## 16. Reglas Nutricionales

### Ganancia muscular

Prioridad:

```text
Proteínas altas
Superávit calórico
```

---

### Pérdida de grasa

Prioridad:

```text
Déficit calórico
Proteína elevada
```

---

### Mantenimiento

Prioridad:

```text
Balance energético
```

---

## 17. Restricciones

La IA únicamente utiliza comidas:

```text
estado = ACTIVO
```

---

Debe respetar:

```text
restricciones_medicas
```

---

No puede generar planes para:

```text
clientes inexistentes
```

---

## 18. Endpoint

```http
POST /ia/nutricion/generar/{id_cliente}
```

Ejemplo:

```http
POST /ia/nutricion/generar/15
```

---

# 19. Ventajas de la IA

## Automatización

Reduce el trabajo manual de los entrenadores.

---

## Personalización

Cada cliente recibe recomendaciones adaptadas.

---

## Escalabilidad

Permite atender más clientes sin aumentar personal.

---

## Consistencia

Las recomendaciones siguen reglas definidas.

---

# 20. Limitaciones Actuales

Actualmente la IA está basada en:

```text
Reglas de negocio
+
Selección inteligente
```

No utiliza todavía:

```text
Machine Learning
Deep Learning
Redes Neuronales
Modelos LLM
```

---

# 21. Evolución Futura

Versiones futuras podrán incluir:

- Machine Learning.
- Recomendadores avanzados.
- Predicción de progreso físico.
- Ajustes automáticos de rutina.
- Ajustes automáticos de nutrición.
- Integración con dispositivos wearables.

---

# 22. Estado Actual

## Implementado

✅ IA Rutinas

✅ IA Nutrición

✅ Generación automática

✅ Persistencia en PostgreSQL

✅ Integración con FastAPI

---

## Futuro

🔲 Machine Learning

🔲 Analítica predictiva

🔲 Recomendaciones adaptativas

🔲 Aprendizaje automático

---