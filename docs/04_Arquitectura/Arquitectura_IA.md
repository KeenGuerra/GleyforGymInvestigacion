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
        ├── orquestador.py       # Capa híbrida: decide Claude vs motor de reglas
        ├── claude_client.py     # Llamada real a la API de Anthropic (Claude)
        ├── anonimizacion.py     # Códigos de cliente (nunca nombre/DNI/teléfono/correo a Claude)
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

`orquestador.py` es el punto de entrada real que usan las rutas (`ia_rutina.py`/`ia_nutricion.py`): si hay `ANTHROPIC_API_KEY` configurada, le pide a Claude que elija/ordene entre los candidatos que el motor de reglas ya filtró; si Claude no está configurado, falla, o se desvía de lo permitido, el resultado final es exactamente el que ya devolvía el motor de reglas por su cuenta — Claude nunca reemplaza esa capa, solo la complementa de forma opcional.

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
Motor de reglas (filtra candidatos por nivel/objetivo/restricciones)
   │
   ├─────────────┐
   │             │
   ▼             ▼
Rutinas IA   Nutrición IA
   │             │
   ▼             ▼
¿Hay ANTHROPIC_API_KEY?
   │
   ├── Sí ──▶ Claude elige/ordena entre los candidatos (orquestador.py)
   │              │
   │              ▼ (si falla o se desvía de lo permitido)
   └── No ──▶ Resultado del motor de reglas, tal cual
   │
   ▼
Base de Datos (estado_revision = pendiente, hasta que ADMIN/ENTRENADOR apruebe)
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

### orquestador.py / claude_client.py (capa híbrida, opcional)

Responsable de:

- Armar los candidatos ya filtrados por `recomendador_rutinas.py` y pasárselos a Claude (vía `claude_client.elegir_rutina_con_claude()`), con los datos del cliente anonimizados (`anonimizacion.py`).
- Validar que la respuesta de Claude solo use ejercicios de la lista de candidatos permitida — si usa uno fuera de catálogo, falla la validación, o Claude no está configurado, el resultado final es el del motor de reglas sin cambios.
- Registrar `origen_ia` (`"claude"` o `"reglas_respaldo"`), el modelo usado y el tiempo de respuesta, para que el staff vea en la pantalla de revisión de dónde salió cada rutina.

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
Aplicar reglas (candidatos por día)
   │
   ▼
¿Hay ANTHROPIC_API_KEY? ── Sí ──▶ Claude elige/ordena entre los candidatos
   │                                  │ (si falla/se desvía)
   No                                 ▼
   │                           Motor de reglas, tal cual
   ▼                                  │
Generar rutina ◀──────────────────────┘
   │
   ▼
Guardar rutina (estado_revision = pendiente)
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

## 11. Endpoints

```http
POST /ia/rutina/generar/{id_cliente}
```

Ejemplo:

```http
POST /ia/rutina/generar/15
```

La rutina generada queda con `estado_revision = pendiente` — el cliente no la ve hasta que un ADMIN/ENTRENADOR la revise. Endpoints de revisión (`backend/app/routes/rutinas.py`):

```http
GET  /rutinas/pendientes                — lista las que esperan revisión (ADMIN/ENTRENADOR)
PUT  /rutinas/{id_rutina}/ejercicios    — editar antes de aprobar (ADMIN/ENTRENADOR)
POST /rutinas/{id_rutina}/aprobar       — aprueba; si se editó antes, queda "aprobada_con_cambios"
POST /rutinas/{id_rutina}/rechazar      — rechaza, exige un motivo
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

### orquestador.py / claude_client.py (capa híbrida, opcional)

Mismo rol que en rutinas (sección 6): Claude elige/ordena entre las comidas candidatas ya filtradas por objetivo y restricciones alimentarias, con el dato adicional de que su elección debe acercarse al objetivo calórico diario dentro de un margen de ±5% — si se desvía más que eso, no está configurado, o falla, el resultado final es el del motor de reglas sin cambios.

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
Calcular requerimientos (Mifflin-St Jeor)
   │
   ▼
Seleccionar comidas candidatas (motor de reglas)
   │
   ▼
¿Hay ANTHROPIC_API_KEY? ── Sí ──▶ Claude elige entre las candidatas (±5% del objetivo calórico)
   │                                  │ (si falla/se desvía)
   No                                 ▼
   │                           Motor de reglas, tal cual
   ▼                                  │
Construir plan ◀───────────────────────┘
   │
   ▼
Guardar plan nutricional (estado_revision = pendiente)
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

## 18. Endpoints

```http
POST /ia/nutricion/generar/{id_cliente}
```

Ejemplo:

```http
POST /ia/nutricion/generar/15
```

Mismo flujo de revisión que las rutinas (sección 11), en `backend/app/routes/nutricion.py`:

```http
GET  /nutricion/pendientes             — lista las que esperan revisión (ADMIN/ENTRENADOR)
PUT  /nutricion/{id_plan}/comidas      — editar antes de aprobar (ADMIN/ENTRENADOR)
POST /nutricion/{id_plan}/aprobar      — aprueba; si se editó antes, queda "aprobada_con_cambios"
POST /nutricion/{id_plan}/rechazar     — rechaza, exige un motivo
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
Reglas de negocio (siempre activas, son la base y el respaldo)
+
Selección inteligente con un modelo de lenguaje (Claude, de forma híbrida y opcional)
```

El modelo LLM (Claude) nunca reemplaza al motor de reglas ni decide solo: únicamente elige/ordena entre candidatos que las reglas ya filtraron (nivel, objetivo, restricciones médicas/alimentarias, presupuesto calórico), y cualquier respuesta fuera de ese catálogo permitido se descarta automáticamente. Si no hay `ANTHROPIC_API_KEY` configurada, si Claude falla, o si se desvía de lo permitido, el sistema sigue funcionando exactamente igual que con el motor de reglas solo.

No utiliza todavía:

```text
Machine Learning propio / modelos entrenados con los datos del gimnasio
Deep Learning
Redes Neuronales propias
Fine-tuning de ningún modelo
```

---

# 21. Evolución Futura

Versiones futuras podrán incluir:

- Modelos de Machine Learning entrenados con los datos propios del gimnasio (no solo un LLM de terceros usado como está).
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

✅ Integración híbrida con Claude (opcional, con respaldo automático al motor de reglas)

✅ Anonimización de los datos enviados al modelo (nunca nombre/DNI/teléfono/correo)

✅ Flujo de revisión (pendiente → aprobada / aprobada_con_cambios / rechazada) antes de que el cliente vea el resultado

✅ Persistencia en PostgreSQL

✅ Integración con FastAPI

---

## Futuro

🔲 Machine Learning

🔲 Analítica predictiva

🔲 Recomendaciones adaptativas

🔲 Aprendizaje automático

---