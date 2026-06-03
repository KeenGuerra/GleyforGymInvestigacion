# Registro de Riesgos del Proyecto

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento identifica los riesgos que pueden afectar al desarrollo, operación y mantenimiento del sistema.

Incluye:

- Riesgos técnicos
- Riesgos operativos
- Riesgos de negocio
- Plan de mitigación

---

# 2. Riesgos Técnicos

| ID | Riesgo | Probabilidad | Impacto | Nivel | Mitigación |
|----|--------|--------------|---------|-------|------------|
| T-001 | Fallo en servidor backend | Media | Alto | Alto | Monitoreo, backup, replicación |
| T-002 | Caída de PostgreSQL | Media | Alto | Alto | Backup diario, redundancia |
| T-003 | Error en IA Rutinas | Baja | Medio | Medio | Validación de reglas, logs |
| T-004 | Error en IA Nutrición | Baja | Medio | Medio | Validación de reglas, logs |
| T-005 | Cloudinary no disponible | Baja | Medio | Medio | Backup local temporal, reintento automático |
| T-006 | Fallo en autenticación JWT | Baja | Alto | Alto | Revisar librerías y pruebas unitarias |
| T-007 | Despliegue incorrecto Frontend | Media | Medio | Medio | Checklist de despliegue, revisión de rutas |
| T-008 | Fallos en Flutter | Baja | Medio | Medio | Validación en múltiples dispositivos |

---

# 3. Riesgos Operativos

| ID | Riesgo | Probabilidad | Impacto | Nivel | Mitigación |
|----|--------|--------------|---------|-------|------------|
| O-001 | Usuario no capacitado | Media | Medio | Medio | Manuales, tutoriales, capacitación |
| O-002 | Pérdida de datos cliente | Baja | Alto | Alto | Backup diario, control de versiones |
| O-003 | Incumplimiento de procesos | Media | Medio | Medio | Procedimientos claros, SOP |

---

# 4. Riesgos de Negocio

| ID | Riesgo | Probabilidad | Impacto | Nivel | Mitigación |
|----|--------|--------------|---------|-------|------------|
| B-001 | Cambios de normativa | Baja | Medio | Medio | Adaptación rápida, revisión legal |
| B-002 | Falta de adopción por usuarios | Media | Alto | Alto | UI/UX amigable, campañas de comunicación |
| B-003 | Competencia con otras apps | Media | Medio | Medio | Mejorar funcionalidades, marketing |

---

# 5. Clasificación de Riesgos

- **Alto:** Probabilidad media/alta y/o impacto alto → requiere acción inmediata.
- **Medio:** Probabilidad o impacto medio → monitorizar.
- **Bajo:** Probabilidad baja y impacto bajo → registro y seguimiento.

---

# 6. Plan de Mitigación

1. **Backup de base de datos:** Diario con retención de 30 días.
2. **Monitoreo de servidores:** Alertas por caídas.
3. **Pruebas continuas:** Unitarias, integración y funcionales.
4. **Manual de usuario y capacitación:** Reducir errores operativos.
5. **Revisión periódica de Cloudinary y dependencias:** Garantizar disponibilidad.
6. **Documentación completa:** Facilitar mantenimiento futuro.

---

# 7. Estado Actual

- Riesgos identificados: 13
- Riesgos mitigados: 2 (Pruebas unitarias y documentación)
- Riesgos pendientes: 11