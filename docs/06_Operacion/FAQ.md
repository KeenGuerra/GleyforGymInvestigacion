# Preguntas Frecuentes (FAQ)

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento reúne las preguntas más frecuentes relacionadas con el uso del SistemaGimnasioGleyforGym.

Su objetivo es resolver dudas comunes sin necesidad de asistencia técnica.

---

# Acceso al Sistema

## ¿Cómo ingreso al sistema?

Ingresar a:

```text
http://localhost:5173
```

Presionar:

```text
Iniciar Sesión
```

e ingresar correo y contraseña.

---

## ¿Qué hago si olvidé mi contraseña?

Actualmente la recuperación de contraseña debe ser realizada por un administrador del sistema.

Futuras versiones incorporarán recuperación mediante correo electrónico.

---

## ¿Por qué aparece "Correo o contraseña incorrectos"?

Posibles causas:

- Correo incorrecto.
- Contraseña incorrecta.
- Usuario desactivado.
- Error de escritura.

Verificar nuevamente los datos ingresados.

---

## ¿Por qué no puedo acceder aunque mis credenciales son correctas?

Posibles causas:

- Usuario inactivo.
- Problema de conexión con el servidor.
- Token expirado.

Cerrar sesión e intentar nuevamente.

---

# Usuarios

## ¿Cuál es la diferencia entre Usuario y Cliente?

### Usuario

Representa:

```text
Acceso al sistema
```

Incluye:

```text
Correo
Contraseña
Rol
```

---

### Cliente

Representa:

```text
Socio real del gimnasio
```

Incluye:

```text
Datos personales
Peso
Estatura
Objetivo
Membresía
```

---

## ¿Por qué es importante esta diferencia?

Porque los procesos del gimnasio utilizan:

```text
id_cliente
```

y no:

```text
id_usuario
```

---

# Clientes

## ¿La edad se registra manualmente?

No.

La edad se calcula automáticamente utilizando:

```text
fecha_nacimiento
```

---

## ¿Puedo modificar la edad manualmente?

No.

La edad siempre es calculada por el sistema.

---

## ¿Qué sucede al desactivar un cliente?

Automáticamente:

```text
cliente.estado = INACTIVO

usuario.estado = INACTIVO
```

---

# Membresías

## ¿Por qué el precio de mi membresía es diferente al precio actual del plan?

Porque el sistema utiliza:

```text
precio_asignado
```

y conserva el valor histórico de contratación.

---

## ¿Qué significa ACTIVA?

La membresía está vigente y puede utilizarse normalmente.

---

## ¿Qué significa PAUSADA?

La membresía fue suspendida temporalmente.

---

## ¿Qué significa TERMINADA?

La membresía concluyó su período contratado.

---

## ¿Qué significa CANCELADA?

La membresía fue anulada antes de finalizar.

---

## ¿Qué pasó con el estado VENCIDA?

Ese estado ya no se utiliza.

Ahora el sistema utiliza:

```text
TERMINADA
```

---

# Pagos

## ¿Cómo verifico mis pagos?

Ingresar a:

```text
Mis Pagos
```

---

## ¿Puedo modificar pagos realizados?

Solo los administradores tienen autorización para gestionar pagos.

---

## ¿Qué métodos de pago puede registrar el sistema?

Dependerá de la configuración del gimnasio.

Ejemplos:

```text
Efectivo
Transferencia
Yape
Plin
Tarjeta
```

---

# Asistencias

## ¿Quién registra las asistencias?

Normalmente:

```text
Administrador
Entrenador
```

---

## ¿Puedo consultar mis asistencias?

Esta funcionalidad puede incorporarse en futuras versiones.

---

# Progreso Físico

## ¿Qué información se registra?

```text
Peso
Porcentaje de grasa
Masa grasa
Masa magra
Pecho
Cintura
Brazo izquierdo
Brazo derecho
Pierna izquierda
Pierna derecha
```

---

## ¿Por qué se registran ambos brazos y piernas?

Para obtener mediciones más precisas y detectar asimetrías corporales.

---

## ¿Cada cuánto tiempo debo registrar mi progreso?

Se recomienda:

```text
Cada 15 o 30 días
```

---

# Rutinas IA

## ¿Cómo se genera una rutina?

La inteligencia artificial utiliza:

```text
Objetivo
Nivel
Peso
Estatura
Edad
Ejercicios activos
```

---

## ¿Por qué no aparece mi rutina?

Posibles causas:

- No se ha generado una rutina.
- No existen ejercicios activos.
- Error de generación.

---

## ¿La IA reemplaza al entrenador?

No.

La IA es una herramienta de apoyo para acelerar la personalización.

---

# Nutrición IA

## ¿Cómo se genera un plan nutricional?

La IA utiliza:

```text
Peso
Estatura
Objetivo
Restricciones médicas
Comidas activas
```

---

## ¿Por qué no aparece mi plan nutricional?

Posibles causas:

- No existe un plan generado.
- No existen comidas activas.
- Error de generación.

---

## ¿La IA considera restricciones médicas?

Sí.

Las restricciones registradas en el cliente son utilizadas durante la generación.

---

# Ejercicios

## ¿Por qué algunos ejercicios tienen video?

Porque el sistema utiliza:

```text
Cloudinary
```

para almacenar videos demostrativos.

---

## ¿Dónde se almacenan los videos?

En:

```text
Cloudinary
```

No se almacenan directamente en PostgreSQL.

---

# Seguridad

## ¿Qué es JWT?

JWT es el mecanismo utilizado para autenticar usuarios.

Permite verificar que cada solicitud sea realizada por un usuario autorizado.

---

## ¿Dónde se almacena la sesión?

En el navegador mediante:

```text
localStorage
```

---

## ¿Qué ocurre al cerrar sesión?

Se eliminan:

```text
token
rol
id_usuario
correo
```

---

# Flutter

## ¿La aplicación móvil utiliza la misma base de datos?

Sí.

Tanto Flutter como React consumen el mismo backend FastAPI.

---

## ¿Flutter se conecta directamente a PostgreSQL?

No.

El flujo correcto es:

```text
Flutter
    ↓
FastAPI
    ↓
PostgreSQL
```

---

# Cloudinary

## ¿Qué sucede si Cloudinary deja de funcionar?

Los videos no podrán visualizarse ni cargarse hasta restablecer la conexión.

---

## ¿Por qué aparece el error "Must supply api_key"?

Posibles causas:

- CLOUDINARY_URL incorrecto.
- Variables de entorno no cargadas.
- Dependencias faltantes.

---

# Desarrollo

## ¿Qué puerto utiliza FastAPI?

```text
8000
```

---

## ¿Qué puerto utiliza React?

```text
5173
```

---

## ¿Qué puerto utiliza PostgreSQL?

```text
5432
```

---

# Regla Más Importante del Proyecto

```text
usuarios = acceso

clientes = negocio
```

---

## Flujo Correcto

```text
Login
   ↓
id_usuario
   ↓
GET /clientes/usuario/{id_usuario}
   ↓
id_cliente
   ↓
Procesos del gimnasio
```

---

## Nunca utilizar

```text
id_usuario
```

para:

- Rutinas
- Nutrición
- Pagos
- Asistencias
- Progreso
- Membresías

---

# Versión

```text
SistemaGimnasioGleyforGym
Versión 2.0 Web
```

---