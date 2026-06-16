📄 README PARA GENERACIÓN AUTOMÁTICA – GLEYFORGYM (GOBIERNO IA V3)
🧠 CONTEXTO GENERAL DEL PROYECTO

El sistema GleyforGym es una plataforma SaaS de gestión de gimnasio con inteligencia artificial adaptativa.

Está compuesto por:

Backend: FastAPI (Python)
Frontend Web: React + Vite
App móvil: Flutter
Base de datos: PostgreSQL
IA: Motor de recomendación de rutinas y nutrición
Auth: JWT
Storage multimedia: Cloudinary

El sistema permite la gestión completa de:
usuarios, clientes, membresías, pagos, asistencias, progreso físico, ejercicios, rutinas y planes nutricionales.

🎯 OBJETIVO DE ESTA SOLICITUD

Generar automáticamente el contenido estructurado del sistema para poder llenar una plantilla de Gobierno de IA V3, incluyendo:

Procesos del negocio
Requerimientos funcionales y no funcionales
Flujos BPMN
Actividades del sistema
Artefactos de software
Ciclo de vida de IA (AI-DLC)
Dependencias entre módulos
Versionado del sistema
Control de cambios
Módulos del sistema
Indicadores de dashboard
🧩 MÓDULOS DEL SISTEMA

Genera contenido considerando estos módulos:

🔐 Autenticación
Login JWT
Roles: ADMIN, ENTRENADOR, CLIENTE
👤 Clientes
Registro de datos personales y biométricos
Relación usuario-cliente
🏋️ Ejercicios
Catálogo con videos
Grupos musculares
📊 Rutinas
Rutinas manuales y generadas por IA
Asignación por días
🍎 Nutrición
Catálogo de comidas
Planes nutricionales IA
💳 Pagos y Membresías
Gestión de suscripciones
Historial de pagos
📈 Progreso
Peso, grasa corporal, masa magra
Medidas corporales
🤖 IA
Generación de rutinas personalizadas
Generación de planes nutricionales
Basado en objetivo, nivel y restricciones
⚙️ ARQUITECTURA TÉCNICA
Backend: FastAPI (REST)
ORM: SQLAlchemy
DB: PostgreSQL
Frontend: React + Vite
Mobile: Flutter
Seguridad: JWT
IA: Python (reglas + recomendador)
Multimedia: Cloudinary
🔁 FLUJO GENERAL DEL SISTEMA
Usuario inicia sesión
Sistema valida JWT
Se identifica rol del usuario
Se obtiene cliente asociado (si aplica)
Se cargan módulos según rol
Cliente interactúa con:
rutinas
nutrición
progreso
IA genera recomendaciones personalizadas
Datos se almacenan en PostgreSQL
🧱 REQUERIMIENTO PRINCIPAL

Genera estructura completa para una plantilla de gobierno de software/IA que incluya:

1. PROCESOS

Procesos del negocio del gimnasio.

2. ACTIVIDADES BPMN

Actividades detalladas por proceso.

3. FLUJOS BPMN

Flujo completo del sistema (inicio → decisiones → procesos → fin).

4. REQUERIMIENTOS
Funcionales (RF01–RFxx)
No funcionales (RNF01–RNFxx)
5. ARTEFACTOS

Archivos del sistema backend/frontend/mobile.

6. CONTROL DE VERSIONES

Historial de cambios tipo Git.

7. DEPENDENCIAS

Relaciones entre módulos.

8. AI-DLC (Ciclo de vida IA)

Para rutinas y nutrición:

intención
diseño
desarrollo
validación
despliegue
9. DASHBOARD

KPIs del sistema:

clientes activos
pagos
rutinas generadas IA
progreso promedio
⚠️ REGLAS IMPORTANTES PARA LA GENERACIÓN
Todo debe estar alineado al sistema GleyforGym
No inventar módulos externos
Mantener consistencia entre procesos, requerimientos y flujos
Usar lenguaje técnico pero estructurado
Pensado para ser usado en una plantilla Excel de gobierno de software e IA
Cada elemento debe ser trazable (proceso → requerimiento → actividad → flujo)
📌 FORMATO DE SALIDA ESPERADO

Devuelve la información en:

Listas estructuradas
Tablas cuando sea posible
IDs (RF01, RNF01, P01, etc.)
Lenguaje listo para ser copiado a Excel
🚀 FIN DEL PROMPT

Genera toda la estructura completa del sistema GleyforGym lista para ser usada en una plantilla de Gobierno de IA V3.