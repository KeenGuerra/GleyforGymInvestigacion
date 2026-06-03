# MATRIZ DE TRAZABILIDAD

# SistemaGimnasioGleyforGym

## Introducción

La matriz de trazabilidad permite verificar que todos los requerimientos funcionales del sistema se encuentran asociados a historias de usuario, casos de uso y casos de prueba.

Esta matriz garantiza la cobertura funcional del proyecto y facilita las actividades de análisis, desarrollo, validación y mantenimiento.

---

# MÓDULO: USUARIOS

| RF                            | Historia de Usuario       | Caso de Uso               | Caso de Prueba            |
| ----------------------------- | ------------------------- | ------------------------- | ------------------------- |
| RF-001 Registrar usuario      | HU-001 Registrar usuario  | CU-002 Gestionar Usuarios | CP-001 Registrar Usuario  |
| RF-004 Iniciar sesión         | HU-005 Iniciar sesión     | CU-001 Iniciar Sesión     | CP-002 Login Correcto     |
| RF-010 Actualizar usuario     | HU-002 Modificar usuario  | CU-002 Gestionar Usuarios | CP-003 Modificar Usuario  |
| RF-011 Cambiar estado usuario | HU-003 Desactivar usuario | CU-002 Gestionar Usuarios | CP-004 Desactivar Usuario |
| RF-015 Cerrar sesión          | HU-006 Cerrar sesión      | CU-001 Iniciar Sesión     | CP-005 Cerrar Sesión      |

---

# MÓDULO: CLIENTES

| RF                               | Historia de Usuario              | Caso de Uso               | Caso de Prueba             |
| -------------------------------- | -------------------------------- | ------------------------- | -------------------------- |
| RF-016 Registrar cliente         | HU-008 Registrar cliente         | CU-003 Gestionar Clientes | CP-006 Registrar Cliente   |
| RF-020 Consultar clientes        | HU-010 Consultar clientes        | CU-003 Gestionar Clientes | CP-007 Consultar Clientes  |
| RF-023 Actualizar cliente        | HU-009 Actualizar cliente        | CU-003 Gestionar Clientes | CP-008 Modificar Cliente   |
| RF-024 Activar cliente           | HU-012 Activar cliente           | CU-003 Gestionar Clientes | CP-009 Activar Cliente     |
| RF-025 Desactivar cliente        | HU-013 Desactivar cliente        | CU-003 Gestionar Clientes | CP-010 Desactivar Cliente  |
| RF-027 Consultar detalle cliente | HU-011 Consultar detalle cliente | CU-003 Gestionar Clientes | CP-011 Ver Detalle Cliente |

---

# MÓDULO: MEMBRESÍAS

| RF                                   | Historia de Usuario                  | Caso de Uso                 | Caso de Prueba               |
| ------------------------------------ | ------------------------------------ | --------------------------- | ---------------------------- |
| RF-036 Registrar membresía           | HU-016 Registrar membresía           | CU-004 Gestionar Membresías | CP-012 Registrar Membresía   |
| RF-042 Actualizar membresía          | HU-017 Modificar membresía           | CU-004 Gestionar Membresías | CP-013 Modificar Membresía   |
| RF-045 Gestionar beneficios          | HU-019 Gestionar beneficios          | CU-004 Gestionar Membresías | CP-014 Registrar Beneficios  |
| RF-047 Mostrar membresías en landing | HU-020 Visualizar planes disponibles | CU-004 Gestionar Membresías | CP-015 Visualizar Membresías |

---

# MÓDULO: CLIENTE MEMBRESÍAS

| RF                               | Historia de Usuario                 | Caso de Uso              | Caso de Prueba                 |
| -------------------------------- | ----------------------------------- | ------------------------ | ------------------------------ |
| RF-051 Asignar membresía         | HU-021 Asignar membresía            | CU-005 Asignar Membresía | CP-016 Asignar Membresía       |
| RF-056 Registrar precio asignado | HU-021 Asignar membresía            | CU-005 Asignar Membresía | CP-017 Validar Precio Asignado |
| RF-061 Pausar membresía          | HU-022 Pausar membresía             | CU-005 Asignar Membresía | CP-018 Pausar Membresía        |
| RF-062 Reactivar membresía       | HU-023 Reactivar membresía          | CU-005 Asignar Membresía | CP-019 Reactivar Membresía     |
| RF-064 Finalizar membresía       | HU-025 Consultar membresía personal | CU-005 Asignar Membresía | CP-020 Finalización Automática |

---

# MÓDULO: PAGOS

| RF                                 | Historia de Usuario                | Caso de Uso                    | Caso de Prueba         |
| ---------------------------------- | ---------------------------------- | ------------------------------ | ---------------------- |
| RF-066 Registrar pago              | HU-026 Registrar pago              | CU-006 Gestionar Pagos         | CP-021 Registrar Pago  |
| RF-072 Consultar pagos por cliente | HU-028 Consultar pagos por cliente | CU-006 Gestionar Pagos         | CP-022 Consultar Pagos |
| RF-074 Validar monto positivo      | HU-026 Registrar pago              | CU-006 Gestionar Pagos         | CP-023 Validar Monto   |
| RF-077 Mostrar pagos al cliente    | HU-031 Visualizar mis pagos        | CU-017 Consultar Pagos Cliente | CP-024 Ver Mis Pagos   |

---

# MÓDULO: ASISTENCIAS

| RF                                       | Historia de Usuario                      | Caso de Uso                  | Caso de Prueba               |
| ---------------------------------------- | ---------------------------------------- | ---------------------------- | ---------------------------- |
| RF-081 Registrar asistencia              | HU-033 Registrar asistencia              | CU-007 Gestionar Asistencias | CP-025 Registrar Asistencia  |
| RF-087 Consultar asistencias por cliente | HU-035 Consultar asistencias por cliente | CU-007 Gestionar Asistencias | CP-026 Consultar Asistencias |
| RF-089 Mostrar asistencias al cliente    | HU-036 Visualizar mis asistencias        | CU-007 Gestionar Asistencias | CP-027 Ver Mis Asistencias   |

---

# MÓDULO: PROGRESO

| RF                                 | Historia de Usuario                    | Caso de Uso                      | Caso de Prueba            |
| ---------------------------------- | -------------------------------------- | -------------------------------- | ------------------------- |
| RF-091 Registrar progreso físico   | HU-038 Registrar progreso físico       | CU-008 Gestionar Progreso Físico | CP-028 Registrar Progreso |
| RF-099 Registrar brazo izquierdo   | HU-041 Registrar medidas corporales    | CU-008 Gestionar Progreso Físico | CP-029 Registrar Medidas  |
| RF-105 Consultar progreso físico   | HU-042 Consultar historial de progreso | CU-008 Gestionar Progreso Físico | CP-030 Consultar Progreso |
| RF-109 Mostrar progreso al cliente | HU-044 Visualizar mi progreso          | CU-008 Gestionar Progreso Físico | CP-031 Ver Mi Progreso    |

---

# MÓDULO: EJERCICIOS

| RF                          | Historia de Usuario             | Caso de Uso                 | Caso de Prueba              |
| --------------------------- | ------------------------------- | --------------------------- | --------------------------- |
| RF-111 Registrar ejercicio  | HU-046 Registrar ejercicio      | CU-009 Gestionar Ejercicios | CP-032 Registrar Ejercicio  |
| RF-117 Subir video          | HU-052 Subir video de ejercicio | CU-009 Gestionar Ejercicios | CP-033 Subir Video          |
| RF-120 Consultar ejercicios | HU-048 Consultar ejercicios     | CU-009 Gestionar Ejercicios | CP-034 Consultar Ejercicios |

---

# MÓDULO: COMIDAS

| RF                              | Historia de Usuario                   | Caso de Uso              | Caso de Prueba                 |
| ------------------------------- | ------------------------------------- | ------------------------ | ------------------------------ |
| RF-126 Registrar comida         | HU-056 Registrar comida               | CU-010 Gestionar Comidas | CP-035 Registrar Comida        |
| RF-132 Consultar comidas        | HU-058 Consultar catálogo nutricional | CU-010 Gestionar Comidas | CP-036 Consultar Comidas       |
| RF-135 Utilizar comidas activas | HU-062 Activar comida                 | CU-010 Gestionar Comidas | CP-037 Validar Comidas Activas |

---

# MÓDULO: RUTINAS IA

| RF                                    | Historia de Usuario                 | Caso de Uso                     | Caso de Prueba                    |
| ------------------------------------- | ----------------------------------- | ------------------------------- | --------------------------------- |
| RF-136 Generar rutina IA              | HU-064 Generar rutina personalizada | CU-011 Generar Rutina IA        | CP-038 Generar Rutina             |
| RF-140 Seleccionar ejercicios activos | HU-067 Utilizar ejercicios activos  | CU-011 Generar Rutina IA        | CP-039 Validar Ejercicios Activos |
| RF-145 Mostrar rutina al cliente      | HU-071 Visualizar mi rutina         | CU-014 Consultar Rutina Cliente | CP-040 Ver Mi Rutina              |

---

# MÓDULO: NUTRICIÓN IA

| RF                                  | Historia de Usuario                   | Caso de Uso                        | Caso de Prueba                 |
| ----------------------------------- | ------------------------------------- | ---------------------------------- | ------------------------------ |
| RF-146 Generar nutrición IA         | HU-074 Generar plan nutricional       | CU-012 Generar Nutrición IA        | CP-041 Generar Nutrición       |
| RF-150 Seleccionar comidas activas  | HU-077 Seleccionar comidas activas    | CU-012 Generar Nutrición IA        | CP-042 Validar Comidas Activas |
| RF-155 Mostrar nutrición al cliente | HU-080 Visualizar mi plan nutricional | CU-015 Consultar Nutrición Cliente | CP-043 Ver Mi Nutrición        |

---

# MÓDULO: SEGURIDAD

| RF                                  | Historia de Usuario                    | Caso de Uso           | Caso de Prueba         |
| ----------------------------------- | -------------------------------------- | --------------------- | ---------------------- |
| RF-156 Autenticar usuarios          | HU-082 Acceder según rol               | CU-001 Iniciar Sesión | CP-044 Validar Login   |
| RF-158 Validar JWT                  | HU-085 Mantener sesión segura          | CU-001 Iniciar Sesión | CP-045 Validar JWT     |
| RF-164 Impedir acceso no autorizado | HU-084 Restringir acceso no autorizado | CU-001 Iniciar Sesión | CP-046 Acceso Denegado |

---

# MÓDULO: DASHBOARD

| RF                              | Historia de Usuario                        | Caso de Uso                     | Caso de Prueba              |
| ------------------------------- | ------------------------------------------ | ------------------------------- | --------------------------- |
| RF-166 Dashboard administrativo | HU-086 Visualizar dashboard administrativo | CU-018 Dashboard Administrativo | CP-047 Dashboard Admin      |
| RF-167 Dashboard entrenador     | HU-087 Visualizar dashboard entrenador     | CU-019 Dashboard Entrenador     | CP-048 Dashboard Entrenador |
| RF-168 Dashboard cliente        | HU-088 Visualizar dashboard cliente        | CU-020 Dashboard Cliente        | CP-049 Dashboard Cliente    |

---

# Resumen

La matriz de trazabilidad garantiza que:

* Todo requerimiento funcional tiene respaldo de negocio.
* Toda historia de usuario se encuentra relacionada con funcionalidades reales.
* Todos los casos de uso tienen requerimientos asociados.
* Todos los requerimientos pueden ser validados mediante pruebas.

Esto asegura la cobertura funcional completa del SistemaGimnasioGleyforGym.
