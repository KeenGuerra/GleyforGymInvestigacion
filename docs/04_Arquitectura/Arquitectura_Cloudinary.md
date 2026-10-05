# Arquitectura Cloudinary

# SistemaGimnasioGleyforGym

> Este archivo estaba vacío (0 bytes) hasta 2026-09. El flujo de subida de video ya estaba documentado en `Arquitectura_Multimedia.md`; este documento se centra en la configuración del **servicio** Cloudinary en sí (credenciales, recursos que usa el sistema, límites del plan) para no duplicar contenido.

---

## 1. Rol de Cloudinary en el sistema

Cloudinary es el único servicio externo de almacenamiento de archivos binarios del sistema. PostgreSQL nunca almacena el binario del video/imagen, solo la URL pública y el `public_id` devueltos por Cloudinary.

Verificado en código: `backend/app/routes/ejercicios.py` (video de ejercicio) y `backend/app/routes/productos.py` (imagen de producto, campos `imagen_url`/`cloudinary_public_id` en `models.Producto`) son los dos puntos de integración reales — el segundo no estaba documentado antes de esta actualización.

---

## 2. Configuración de credenciales

Variable de entorno única (`backend/.env`, ver `render.yaml`):

```env
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

En Render, esta variable se configura manualmente en el dashboard (no se autogenera como `SECRET_KEY`), según `render.yaml`.

---

## 3. Recursos que usa el sistema

| Recurso | Módulo | Campo en BD |
|---|---|---|
| Video de ejercicio | Ejercicios (`routes/ejercicios.py`) | `ejercicios.video_url`, `ejercicios.cloudinary_public_id` |
| Imagen de producto | Comercio (`routes/productos.py`) | `productos.imagen_url`, `productos.cloudinary_public_id` |

No se usa Cloudinary para fotos de perfil de clientes/entrenadores ni para comprobantes PDF (esos se generan con `reportlab` en `backend/app/recibos.py` y no pasan por Cloudinary).

---

## 4. Plan y límites

El proyecto usa el plan gratuito de Cloudinary. No hay política de purga ni migración a un plan pago documentada; es un riesgo operativo del mismo tipo que el plan free de Render (ver `Pendientes.md` P-16), pero no está registrado explícitamente como pendiente — se deja anotado aquí para que el equipo lo evalúe.

---

## 5. Seguridad

Los recursos se suben como públicos (sin URLs firmadas). Ver `Arquitectura_Multimedia.md` sección 12 para el detalle y las mejoras futuras propuestas (URLs firmadas, contenido privado).

---

## 6. Relación con otros documentos

- `Arquitectura_Multimedia.md`: flujo completo de subida de video de ejercicio, payload, y consumo desde el frontend.
- `Arquitectura_BaseDatos.md`: definición de los campos `video_url`/`cloudinary_public_id` (tabla `ejercicios`) e `imagen_url`/`cloudinary_public_id` (tabla `productos`).
