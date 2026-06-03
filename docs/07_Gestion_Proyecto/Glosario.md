# Glosario de Términos

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento define los términos, abreviaturas y conceptos más importantes utilizados en el SistemaGimnasioGleyforGym para facilitar la comprensión de la documentación.

---

# 2. Términos Técnicos

| Término | Definición |
|---------|------------|
| FastAPI | Framework Python utilizado para construir el backend del sistema. |
| React | Librería de JavaScript para construir la interfaz web. |
| Flutter | Framework de Google para desarrollo de aplicaciones móviles y web. |
| PostgreSQL | Sistema de gestión de bases de datos relacional utilizado por el sistema. |
| JWT | JSON Web Token, utilizado para autenticación y control de acceso por rol. |
| Cloudinary | Servicio en la nube para almacenamiento de videos y archivos multimedia. |
| SQLAlchemy | ORM de Python que permite interactuar con PostgreSQL usando clases de Python. |
| Pydantic | Librería Python para validación de datos en FastAPI. |
| Vite | Herramienta de construcción para proyectos frontend modernos en React. |
| ProtectedRoute | Componente de React que restringe rutas según el rol de usuario. |
| IA | Inteligencia Artificial utilizada para generar rutinas de ejercicio y planes nutricionales. |
| API | Interfaz de programación que permite la comunicación entre frontend, backend y app móvil. |
| CRUD | Create, Read, Update, Delete – operaciones básicas de manejo de datos. |

---

# 3. Términos Funcionales

| Término | Definición |
|---------|------------|
| Usuario | Persona con acceso al sistema, puede tener distintos roles: ADMIN, ENTRENADOR o CLIENTE. |
| Cliente | Socio del gimnasio, representa el negocio principal del sistema. |
| id_usuario | Identificador único de un usuario en el sistema. |
| id_cliente | Identificador único de un cliente/socio en el sistema. |
| Membresía | Plan contratado por un cliente, con duración, precio y beneficios. |
| precio_asignado | Precio de la membresía al momento de asignarse, se mantiene fijo para el cliente. |
| Estado de Membresía | Puede ser ACTIVA, PAUSADA, TERMINADA o CANCELADA. |
| Progreso | Registro de evolución física del cliente, incluyendo peso, % grasa, masa magra y medidas corporales. |
| Rutina IA | Rutina de ejercicios generada automáticamente por el sistema basado en objetivos y nivel del cliente. |
| Nutrición IA | Plan de comidas generado automáticamente por el sistema considerando peso, objetivo y restricciones. |
| Beneficios | Ventajas incluidas en una membresía (acceso, rutinas, asesorías, etc.). |
| Dashboard | Panel de control que muestra información resumida según el rol del usuario. |
| Mi Perfil | Sección donde el cliente visualiza sus datos personales y físicos. |
| Mi Rutina | Sección donde el cliente visualiza su rutina generada. |
| Mi Nutrición | Sección donde el cliente visualiza su plan nutricional. |
| Mis Pagos | Sección donde el cliente visualiza su historial de pagos. |
| Mi Progreso | Sección donde el cliente visualiza su historial físico. |
| Cloudinary URL | Dirección que permite acceder al video almacenado en Cloudinary. |
| Fecha Inicio | Fecha en la que inicia la membresía asignada. |
| Fecha Fin | Fecha en la que finaliza la membresía asignada, calculada automáticamente. |
| Pausar Membresía | Acción que suspende temporalmente la membresía. |
| Reactivar Membresía | Acción que reanuda una membresía pausada. |
| Masa Magra | Cantidad de masa corporal exenta de grasa (músculo, hueso, agua, etc.), calculada en base al peso y porcentaje de grasa. |
| Medidas Corporales Detalladas | Conjunto de mediciones anatómicas que segmentan brazos y piernas por lado (izquierdo y derecho) además de pecho y cintura, para un control preciso de la simetría muscular. |

---

# 4. Abreviaturas

| Abreviatura | Significado |
|-------------|------------|
| CRUD | Create, Read, Update, Delete |
| JWT | JSON Web Token |
| IA | Inteligencia Artificial |
| UI | User Interface |
| UX | User Experience |
| PDF | Portable Document Format |

---

# 5. Notas

- Todos los términos deben ser consistentes en la documentación y el sistema.
- Los términos funcionales están vinculados directamente con los módulos y pantallas de la aplicación.
- Este glosario puede actualizarse a medida que se incorporen nuevas funcionalidades o conceptos.

---

# 6. Versión

```text
SistemaGimnasioGleyforGym
Versión v2.6
```

---