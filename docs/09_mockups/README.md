# 09. Mockups del Proyecto GleyforGym

Este documento detalla las propuestas de diseño visual (mockups) para el sistema **GleyforGym**, las cuales muestran de manera profesional y detallada las pantallas operativas reales del proyecto tanto para el cliente móvil como para el administrador web. Estas interfaces representan visualmente los requerimientos de la plataforma SaaS y la integración de la Inteligencia Artificial Adaptativa.

---

## 1. Concepto de Diseño Visual (Dark Luxury)

Las interfaces han sido diseñadas con un estilo visual **Dark Luxury Glassmorphic**, que utiliza:
*   **Base de Color:** Fondos oscuros profundos (`#09090b` y `#121214`) para reducir el cansancio visual durante el entrenamiento.
*   **Acentos de Color:** Cian eléctrico para elementos relacionados con el progreso físico, verde brillante para la sección de nutrición saludable, y naranja enérgico para estados de membresía y botones de acción principal (CTA).
*   **Componentes de Cristal:** Tarjetas translúcidas con bordes iluminados y difuminados de fondo (*backdrop-filter*) para dar una apariencia moderna y de alta fidelidad.

---

## 2. Mockup de Rutinas de Entrenamiento (Aplicación Móvil - Vista Cliente)

Este mockup representa la pantalla principal del socio donde se visualiza la rutina de ejercicios recomendada por el motor de **Inteligencia Artificial Adaptativa** según su perfil, objetivo físico y restricciones médicas.

### Elementos Clave:
*   **Progreso de Entrenamiento:** Un indicador circular en cian que motiva al usuario indicando el avance de su sesión del día.
*   **Tarjetas de Ejercicio:** Muestran el nombre del ejercicio (e.g. Sentadillas, Press de Banca), las series, repeticiones, y un botón para reproducir el video demostrativo desde Cloudinary.

![Mockup - Rutinas de Entrenamiento IA](file:///d:/GleyforGymInvestigacion/docs/09_mockups/routine_mockup.png)

---

## 3. Mockup de Plan Alimenticio (Aplicación Móvil - Vista Cliente)

Este mockup muestra la interfaz de **Nutrición Personalizada con IA**, donde el sistema calcula los macronutrientes del usuario y le prescribe su plan de comidas.

### Elementos Clave:
*   **Distribución de Macros:** Gráfico e indicadores de la cantidad de proteínas, carbohidratos y grasas recomendadas.
*   **Desglose de Comidas:** Bloques estructurados para Desayuno, Almuerzo y Cena, detallando los alimentos recomendados y las calorías estimadas.

![Mockup - Plan Nutricional IA](file:///d:/GleyforGymInvestigacion/docs/09_mockups/nutrition_mockup.png)

---

## 4. Mockup del Panel Administrativo (Portal Web - Vista Administrador)

Este mockup muestra el **Dashboard del Administrador** en la plataforma web, el cual recopila y presenta las estadísticas clave del negocio y el estado de los módulos.

### Elementos Clave:
*   **Métricas del Negocio:** Visualización en tiempo real de clientes registrados, membresías vigentes e ingresos monetarios del mes.
*   **Gráfico de Asistencia:** Gráfico estadístico de la afluencia semanal de socios en el gimnasio.
*   **Sección de Acciones Rápidas:** Accesos directos a los módulos de asignación de membresías, registro de cobros y marcación de asistencias.

![Mockup - Portal Web Administrador](file:///d:/GleyforGymInvestigacion/docs/09_mockups/dashboard_mockup.png)

---

## 5. Alineación con los Objetivos del Proyecto

Estos mockups representan de manera directa los procesos clave de negocio definidos en la tesis:
1.  **Proceso P06 & RF08 (Generación de Rutinas IA):** Representado fielmente en la interfaz del cliente móvil de rutinas.
2.  **Proceso P07 & RF09 (Generación de Nutrición IA):** Representado en la interfaz de comidas y macronutrientes.
3.  **Proceso P03 & RF12 (KPIs y Dashboard):** Representado en el panel administrativo del administrador web.
