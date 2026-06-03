# Arquitectura Multimedia

# SistemaGimnasioGleyforGym

## 1. Introducción

El SistemaGimnasioGleyforGym utiliza Cloudinary como plataforma de almacenamiento multimedia para los videos de ejercicios.

La finalidad es evitar almacenar archivos pesados dentro del servidor o la base de datos PostgreSQL, mejorando el rendimiento y la escalabilidad del sistema.

---

## 2. Objetivo

Centralizar el almacenamiento de contenido multimedia relacionado con ejercicios físicos.

Beneficios:

- Menor carga en el servidor.
- Menor tamaño de la base de datos.
- Mejor velocidad de acceso.
- Escalabilidad.
- Distribución optimizada de contenido.

---

## 3. Tecnología Utilizada

| Componente | Tecnología |
|------------|------------|
| Multimedia | Cloudinary |
| Backend | FastAPI |
| Base de Datos | PostgreSQL |
| Comunicación | API REST |

---

## 4. Arquitectura General

```text
Entrenador/Admin
        │
        ▼
Frontend React
        │
        ▼
FastAPI
        │
        ▼
Cloudinary
        │
        ▼
Video URL
        │
        ▼
PostgreSQL
```

---

## 5. Flujo de Subida

### Paso 1

El administrador selecciona un video.

```text
Ejercicios.jsx
```

---

### Paso 2

El frontend envía:

```text
multipart/form-data
```

---

### Paso 3

FastAPI recibe:

```text
video
nombre
grupo_muscular
objetivo
nivel
descripcion
```

---

### Paso 4

FastAPI envía el video a Cloudinary.

---

### Paso 5

Cloudinary devuelve:

```json
{
  "secure_url": "...",
  "public_id": "..."
}
```

---

### Paso 6

Se almacena en PostgreSQL:

```text
video_url
cloudinary_public_id
```

---

## 6. Tabla Relacionada

### ejercicios

Campos multimedia:

| Campo | Descripción |
|---------|---------|
| video_url | URL pública del video |
| cloudinary_public_id | Identificador interno Cloudinary |

---

## 7. Variables de Entorno

Archivo:

```text
backend/.env
```

Configuración:

```env
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

---

## 8. Integración Backend

Dependencias necesarias:

```bash
pip install cloudinary
pip install python-multipart
```

---

Configuración típica:

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="...",
    api_key="...",
    api_secret="..."
)
```

---

## 9. Endpoint Relacionado

### Crear Ejercicio

```http
POST /ejercicios/
```

Tipo:

```text
multipart/form-data
```

Campos:

```text
nombre
grupo_muscular
nivel
objetivo
descripcion
instrucciones
estado
video
```

---

## 10. Consumo desde Frontend

Cuando el cliente visualiza una rutina:

```text
MiRutina
    │
    ▼
DetalleRutina
    │
    ▼
video_url
    │
    ▼
Cloudinary
```

---

## 11. Beneficios de Cloudinary

### Rendimiento

Los videos no se almacenan en PostgreSQL.

---

### Escalabilidad

Permite almacenar miles de videos.

---

### Optimización

Cloudinary optimiza automáticamente la entrega multimedia.

---

### Disponibilidad

Alta disponibilidad mediante infraestructura Cloudinary.

---

## 12. Seguridad

Actualmente:

```text
Videos públicos
```

---

Futuras mejoras:

```text
URLs firmadas
Control de acceso
Videos privados
```

---

## 13. Limitaciones Actuales

Actualmente:

- Solo videos de ejercicios.
- No se almacenan imágenes de progreso.
- No se almacenan fotografías de clientes.

---

## 14. Evolución Futura

Posibles mejoras:

- Galería de ejercicios.
- Imágenes de progreso físico.
- Fotografías de clientes.
- Videos de seguimiento.
- Almacenamiento de documentos PDF.
- CDN optimizada.

---

## 15. Estado Actual

### Implementado

✅ Cloudinary

✅ Subida de videos

✅ Asociación a ejercicios

✅ Almacenamiento de URL

✅ Integración FastAPI

✅ Integración React

---

### Futuro

🔲 Imágenes de progreso

🔲 Videos privados

🔲 CDN avanzada

🔲 Multimedia para app móvil

---