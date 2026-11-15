# Pendientes del Proyecto

# SistemaGimnasioGleyforGym

## Introducción

Este documento lista todo lo que falta para considerar completo el sistema web (backend FastAPI + frontend web-admin). No incluye la aplicación móvil (Flutter), que se gestiona aparte.

Se generó tras completar tres rondas de revisión y corrección sobre el código (RBAC, motor de IA real, auditoría, autogestión de contraseñas, Avisos editables, KPIs de asistencia, paginación), verificando directamente contra el código actual — no contra supuestos ni documentación antigua.

Cada punto cita el archivo (y línea, cuando aplica) donde se verificó.

---

# Prioridad Alta

## P-01 Verificación de correo al registrarse

~~Resuelto (2026-11)~~: `Usuario` ahora tiene `correo_verificado`, `token_verificacion` y `token_verificacion_expira`. Al crear cualquier usuario (`POST /clientes/`, `POST /usuarios/`, `POST /entrenadores/`) se genera un token y se envía un correo de confirmación (`enviar_verificacion_correo()` en `app/correo.py`). Nueva página pública `web-admin/src/pages/VerificarCorreo.jsx` (ruta `/verificar-correo?token=...`) que confirma el correo automáticamente al abrirse. **Decisión de alcance**: no se bloquea el login de cuentas no verificadas — el campo solo registra el estado, para no romper el flujo actual (las cuentas de clientes/entrenadores las crea el staff del gimnasio, no es un auto-registro público).

---

## P-02 Conectar una pasarela de pago real

La arquitectura ya está lista:

```text
backend/app/pagos_gateway/base.py     → interfaz GatewayPago (ABC)
backend/app/pagos_gateway/mock.py     → MockGateway (simulación en memoria)
backend/app/pagos_gateway/culqi.py    → CulqiGateway (esqueleto, ver abajo)
backend/app/pagos_gateway/__init__.py → singleton `gateway`, punto único de cambio
```

**Avance (2026-11)**: se creó una cuenta real de Culqi (RUC de pruebas, panel DEVS) y se probó `CulqiGateway` contra el sandbox real, no solo simulado. Esto reveló dos diferencias con el esqueleto original:

1. La API de Órdenes exige además `client_details` (nombres, apellidos, correo, teléfono) y `expiration_date` — ya corregido en `culqi.py`. Por eso `GatewayPago.crear_checkout()` ahora recibe un tercer parámetro `cliente: dict`, y `pagos.py`/`ventas.py` arman ese dict desde `Cliente`/`Usuario` antes de llamar al gateway (sí fue necesario tocar las rutas, a diferencia de lo asumido originalmente).
2. La orden creada **no tiene un `checkout_url` genérico**: el cliente paga con el link de PagoEfectivo (`url_pe`) o escaneando el QR de Yape (`qr`) — ambos ya mapeados en el resultado de `crear_checkout()` (`url_checkout` + `qr_yape`).

`backend/tests/test_culqi_gateway.py` (12 pruebas) actualizado para reflejar el formato real. Aún con la llamada HTTP simulada en las pruebas, pero verificado manualmente contra `api.culqi.com` con las llaves de prueba.

**Sin confirmar todavía**: completar un pago real de prueba de punta a punta (pagar la orden y ver si `consultar_estado()`/el webhook realmente reportan "paid"/"completed" como se asume) — solo se probó crear y consultar una orden en estado "pending".

**Avance (2026-11, continuación)**: se construyó la pantalla de checkout en el frontend. `web-admin/src/components/CheckoutModal.jsx` (nuevo) muestra el link de pago (`url_checkout`) y el QR de Yape (`qr_yape`) devueltos por el backend. Conectado en:
- `Pagos.jsx`: botón "Cobrar" en cada pago con estado `PENDIENTE`, llama a `POST /pagos/{id}/checkout`.
- `Tienda.jsx` (pestaña "Mis pedidos"): botón "Pagar ahora" en cada pedido `PENDIENTE`, llama a `POST /ventas/{id}/checkout`.

Pruebas agregadas en `Pagos.test.jsx` y `Tienda.test.jsx` para ambos flujos (éxito y error). Suite de frontend: 42 archivos / 220 pruebas.

**Avance (2026-11, continuación 2) — los puntos 2 y 3 de abajo ya están resueltos**: `pagos_gateway/__init__.py` elige automáticamente `CulqiGateway` si `CULQI_SECRET_KEY` está configurada, o `MockGateway` si no (CI y cualquier máquina sin esa variable siguen sin cambios). `routes/webhooks.py` ya no confía en el campo `resultado` del payload cuando el gateway activo es real: solo lo usa para extraer el ID de la transacción (probando varias formas razonables — `id_transaccion_externa`, `data.object.id`, `data.id`, `object.id`, `id`, ya que Culqi no documenta públicamente el formato exacto de su webhook) y siempre revalida el estado llamando a `gateway.consultar_estado()` contra la API de Culqi antes de aplicar cualquier cambio. El secreto del webhook (`WEBHOOK_SECRET`) se acepta también por query string (`?secret=...`), porque el panel de Culqi no permite configurar headers personalizados en la URL de destino.

En autorrevisión antes de la primera prueba real se corrigieron dos bugs: `CulqiGateway.consultar_estado()` no manejaba un 404 de Culqi (orden no encontrada) y `_extraer_id_transaccion()` priorizaba el `id` de primer nivel del payload antes que las rutas anidadas, al revés de la convención común de webhooks (estilo Stripe) donde el nivel superior suele ser el ID del *evento*, no del recurso.

**Avance (2026-11, continuación 3) — bugs reales encontrados en la primera prueba real (no simulada)**: al intentar pagar de verdad desde "Mi Membresía" se encontraron y corrigieron tres problemas que solo aparecen contra la API real de Culqi (nunca los hubiera detectado el webhook simulado):
1. Culqi rechaza la orden con 400 si el teléfono del cliente llega vacío o mal formado — ahora `iniciar_checkout_pago`/`iniciar_checkout_venta` exigen un teléfono de exactamente 9 dígitos (Perú) antes de llamar a Culqi, con un mensaje claro en vez de un 500 genérico.
2. Culqi exige que `order_number` sea único **para siempre en toda la cuenta** (no solo en nuestra BD) — reintentar "Completar pago" sobre el mismo Pago/Venta volvía a llamar a `crear_checkout()` con la misma referencia y Culqi la rechazaba. Se agregó `GatewayPago.obtener_checkout()` para recuperar la orden ya creada en vez de crear una nueva (checkout idempotente).
3. La referencia (`pago-<id>`/`venta-<id>`) se arma solo con el ID autoincremental de nuestra BD, que no es único entre entornos/pruebas distintas contra la misma cuenta de Culqi — chocó con una orden de pruebas anteriores. Se agregó un sufijo aleatorio a la referencia.

**Avance (2026-11, continuación 4) — el pago de prueba de punta a punta en sandbox NO es posible, descubierto intentándolo de verdad**: se intentó completar un pago real contra una orden de prueba (QR de Yape) escaneándolo con una app de Yape real — el resultado fue un monto sin sentido (ninguna relación con el monto real de la orden), señal de que el QR de sandbox no es una transacción Yape válida. Se confirmó contra la documentación oficial de Culqi (`docs.culqi.com`):

- La página "Integración vs Producción" dice literalmente que el entorno de Integración (sandbox) **"te permite simular ventas usando nuestras tarjetas de prueba"** y que **"el entorno de Integración solo acepta tarjetas de prueba"** — no dice en ningún lado que Yape o PagoEfectivo funcionen en sandbox.
- El número de prueba `900 000 001` + código de 6 dígitos (documentado en "Tarjetas de prueba") es para el **"botón de pago Yape"** de Cargo Único (un checkout con campo de teléfono), no para el QR de la API de Órdenes que usa este backend.
- Ni la página de Webhooks ni la de Órdenes documentan ningún botón o endpoint para forzar manualmente una orden a estado "pagada" en sandbox.

**Conclusión**: el flujo de Yape/PagoEfectivo vía Órdenes que usa este sistema **no se puede probar de punta a punta en sandbox, solo en la cuenta real de producción**. Confirmar con tarjetas de prueba tampoco serviría — los cargos con tarjeta son síncronos (Culqi responde al toque, sin webhook) y necesitarían una integración nueva completa (tokenización con Culqi.js + endpoint de Cargos), que no existe hoy y no probaría el camino asíncrono (`order.status.changed`) que es justamente lo que hay que confirmar.

Falta:

1. **Ya no es posible confirmarlo en sandbox.** La única confirmación posible es la prueba real de producción descrita en P-22 (punto 4) — queda fusionado con ese pendiente, bloqueado por la misma causa (aprobación KYC de la cuenta real de Culqi).

Decisión ya tomada: **Culqi** es la opción recomendada para Perú (soporte Yape, sandbox gratuito para tarjetas, onboarding simple) frente a Niubiz/Izipay (más burocrático), MercadoPago (menos adopción de Yape) o Stripe (no opera en Perú/soles).

~~Resuelto (2026-11, decisión final) — Culqi eliminado por completo, a pedido~~: después de confirmar (ver arriba) que el pago real de punta a punta solo se podía probar con la cuenta de producción, nunca en sandbox, y mientras esa cuenta seguía bloqueada por KYC (ver P-22), se decidió no esperar más a Culqi: **todo pago es ahora por Yape, Plin o efectivo, confirmado a mano por el staff** — sin pasarela de pago de ningún tipo. Se eliminó:

- `backend/app/pagos_gateway/` completo (`base.py`, `mock.py`, `culqi.py`, `__init__.py`), `backend/app/routes/webhooks.py`, y las variables `CULQI_SECRET_KEY`/`CULQI_PUBLIC_KEY`/`WEBHOOK_SECRET` (`config.py`, `render.yaml`, `.env.example`).
- `POST /ventas/{id}/checkout` (ya estaba muerto: `Tienda.jsx` usa un QR de Yape estático desde antes) y `POST /pagos/{id}/checkout`.
- `web-admin/src/components/CheckoutModal.jsx`.
- Los estados que solo existían para el camino de webhook (`FALLIDO`/`REEMBOLSADO` en `Pago`, `FALLIDA` en `Venta`) y los métodos de pago `TARJETA`/`PAGOEFECTIVO`, que ya no tienen ningún camino que los produzca.

En su lugar, **el mismo patrón que ya tenía la Tienda online** (QR de Yape estático + confirmación manual del staff) se extendió a la compra de membresía por autoservicio (ver P-19): nuevo `POST /pagos/{id}/confirmar` (solo staff — ADMIN/ENTRENADOR/RECEPCIONISTA, nunca el propio socio) que marca el pago `PAGADO` y activa la `ClienteMembresia` ligada, reemplazando lo que antes hacía el webhook. Anular (`DELETE /pagos/{id}`) un pago de autoservicio aún `PENDIENTE` ahora también cancela la `ClienteMembresia` asociada (antes solo lo hacía el camino `FALLIDO` del webhook), para que el socio no quede bloqueado de volver a intentar comprar.

Los métodos de pago para el staff en mostrador siguen siendo exactamente los mismos de siempre: **YAPE, PLIN y EFECTIVO** (`Pagos.jsx`/`Ventas.jsx`) — esta decisión no les cambió nada.

---

## P-03 Envío real de correo

~~Resuelto (2026-11)~~: `backend/app/correo.py` con `enviar_correo()` probado primero con Gmail SMTP (`smtplib`), que funcionó enviando un correo real desde una máquina local. Al desplegar a producción (Render) se confirmó que las conexiones SMTP salientes a `smtp.gmail.com` no se completan (timeout, probado en los puertos 465 y 587) — limitación del hosting, no de las credenciales. Se reemplazó por la API HTTPS de Brevo (`BREVO_API_KEY`/`BREVO_SENDER_EMAIL`/`BREVO_SENDER_NAME`, opcionales — sin ellas sigue solo logueando, como antes), que sí funciona porque usa el puerto 443 (nunca bloqueado). El correo remitente debe verificarse una vez en el panel de Brevo (Senders) antes de poder usarse. Conectado en `solicitar_reset_password` (recuperación de contraseña) y reutilizado por `enviar_verificacion_correo()` (P-01). El envío ya no propaga errores (se loguea y sigue, igual que `registrar_auditoria()`) para no colgar ni tumbar la operación principal si el correo falla. Pruebas en `backend/tests/test_correo.py` (4 pruebas, con la llamada HTTP simulada).

---

## P-04 Cobertura de tests del módulo de Comercio

~~Resuelto (2026-11)~~: backend y frontend tienen ahora pruebas dedicadas. Backend: `backend/tests/test_comercio.py` (10 pruebas) eleva `categorias.py` 37%→88%, `proveedores.py` 43%→86%, `compras.py` 20%→83%, `ventas.py` 17%→69%, `inventario.py` 26%→56%, `productos.py` 23%→48%. Frontend: un archivo `*.test.jsx` por página (`Categorias`, `Productos`, `Proveedores`, `Compras`, `Inventario`, `Ventas`, `Tienda`) eleva esos siete archivos de un rango de 1.3%-2.8% a 87.9%-100%, y la cobertura total de frontend de 78.21% a 94.33%.

---

## P-19 Compra de membresía por autoservicio

~~Resuelto (2026-11)~~: antes solo ADMIN/ENTRENADOR podían asignar una membresía (`POST /cliente-membresias/`). Se agregó `POST /cliente-membresias/comprar` para que el propio socio compre un plan, siguiendo el mismo patrón solicitar → pagar → confirmar que ya usan las ventas de la tienda (ver P-02). Al comprar se crean una `ClienteMembresia` y un `Pago` en estado `PENDIENTE`.

**Avance (2026-11, con la eliminación de Culqi en P-02)**: el socio paga escaneando un QR de Yape estático en `MiMembresia.jsx` (botón "Pagar con Yape", mismo patrón que `Tienda.jsx`) y el staff confirma a mano con `POST /pagos/{id}/confirmar` cuando ve que la transferencia llegó — esto activa la `ClienteMembresia` (fechas reales, `fecha_inicio`/`fecha_fin` recalculadas al confirmarse). Si el socio nunca paga, el staff anula el pago (`DELETE /pagos/{id}`) y la `ClienteMembresia` pendiente se cancela con él, para que pueda reintentar. Se sigue bloqueando con 409 comprar un nuevo plan mientras ya hay uno `ACTIVA`/`PAUSADA`/`PENDIENTE`.

Ya no depende de ninguna pasarela ni de confirmación en producción: el flujo completo (comprar → pagar → confirmar → anular) se prueba de punta a punta en `test_compra_membresia.py`, sin bloqueo externo alguno.

---

## P-20 Bug: error de login silencioso (la sesión se cerraba ante cualquier 401)

~~Resuelto (2026-11)~~: el interceptor de respuesta de axios (`web-admin/src/api/api.js`) trataba cualquier 401 como "la sesión expiró" y hacía `localStorage.clear()` + `location.href = "/login"` (recarga completa de la página) — incluido el 401 que devuelve `POST /usuarios/login` cuando la contraseña es incorrecta. Eso borraba el mensaje de error que `Login.jsx` sí llegaba a poner (`setError("Correo o contraseña incorrectos")`) antes de que se viera, porque toda la página se remontaba. Por eso el síntoma reportado era "no dice nada, solo recarga".

Ahora el interceptor solo cierra sesión si **ya había** un token guardado antes de la petición; un 401 de un endpoint público (login, etc.) ya no dispara nada y cada pantalla muestra su propio error, como estaba pensado. Se revisaron además `Registro.jsx` y `ResetPassword.jsx` (no tenían este bug, ya validan y muestran errores correctamente) y se encontró el mismo patrón de fondo (catch que solo hacía `console.error`, sin avisar al usuario) en los tres dashboards (`DashboardAdmin.jsx`, `DashboardCliente.jsx`, `DashboardEntrenador.jsx`) — corregido en la misma pasada (ver P-21).

---

## P-21 Bootstrap para alertas/toasts

~~Resuelto (2026-11)~~: se agregó Bootstrap (`bootstrap` + `sass` como dependencias) a pedido, pero **solo** los componentes de alerta/toast, importados vía Sass en `web-admin/src/styles/bootstrap-custom.scss` — deliberadamente sin `reboot` (resetea tipografía/body global) ni `grid`/`buttons`/`card`/`badge`. La app ya tiene su propio tema (`index.css`, ~2185 líneas) con clases como `.btn-primary`/`.card`/`.badge`, los mismos nombres que usa Bootstrap por defecto; importarlo completo habría roto esa UI existente. Nuevo hook `useToast.js` + componente `ToastFeedback.jsx` (auto-cierre manejado por `setTimeout` en React, sin depender del runtime JS de Bootstrap), usados en los tres dashboards para avisar cuando falla la carga inicial (ver P-20).

**Avance (2026-11, continuación)**: quedaba un cuadro de confirmación nativo (`window.confirm`) en los 19 puntos de "¿Seguro que deseas...?" de todo el admin — aparecía como una barra simple arriba del navegador, sin ningún estilo. Se agregó la partial `bootstrap/scss/modal` al mismo archivo, un hook nuevo `useConfirmacion.js` (basado en promesas, para no cambiar la forma de cada sitio de llamada) y un componente `ConfirmModal.jsx` (overlay/estructura de Bootstrap, botones `.btn-primary`/`.btn-secondary` propios de la app) que reemplaza `window.confirm` en las 19 páginas. De paso se revisó qué tan unificado se veía el resto del diseño: `Tienda.jsx` tenía 36 estilos inline sueltos (el peor caso con diferencia), y había focos más chicos en `Inventario.jsx`, `Avisos.jsx`, `RevisionIA.jsx` y `MiMembresia.jsx`. Se movieron todos a clases nuevas en `index.css` que reutilizan las variables de diseño ya existentes (`--danger`, `--warning`, `--surface`, etc.) en vez de repetir valores sueltos — mismo resultado visual, código consistente con el resto del admin. Se dejaron inline, a propósito, los dos casos genuinamente calculados por instancia (el ancho en % de la barra de progreso de membresía, el color de ícono según tipo de aviso): convertirlos no unifica nada, solo esconde el mismo valor dinámico detrás de una variable CSS.

---

## P-22 Checklist para pasar a la cuenta real de Culqi (producción) — descartado junto con Culqi

~~Resuelto (2026-11) — ya no aplica~~: este checklist completo (reemplazar llaves, registrar webhook en Producción, limpiar pagos de prueba, probar con monto real) dejó de tener sentido al eliminarse Culqi por completo (ver P-02) — no hay cuenta real que activar, ni webhook que registrar, porque no hay pasarela de pago de ningún tipo. Todo pago es ahora por Yape/Plin/efectivo, confirmado a mano por el staff.

**Pendiente manual en producción (no es código)**: la membresía temporal **"Plan de Prueba Culqi S/6"** (`id_membresia=2`) que se había creado en producción específicamente para probar el paso 4 de este checklist ya no tiene ningún propósito — conviene desactivarla o renombrarla desde el panel admin (`Membresias.jsx`) para no confundir al staff, aunque no afecta el funcionamiento del sistema si se deja como está.

**Bloqueado** a la espera de que Culqi apruebe el KYC del comercio — sin fecha estimada, depende de Culqi, no de este proyecto.

---

## P-23 IA: confirmar Claude en vivo, cobertura de tests y documentación desactualizada

La integración híbrida con Claude (`app/ia/claude_client.py`/`orquestador.py`) ya funciona y tiene buena cobertura, pero investigando a fondo se encontraron tres huecos reales:

1. **Nunca se confirmó una llamada real a la API de Anthropic en producción** — todos los tests usan un doble del SDK (`_FakeMessages`/`_FakeClient`) o corren sin `ANTHROPIC_API_KEY`, cayendo siempre al motor de reglas.
2. **La documentación de arquitectura de la tesis quedaba desactualizada y contradecía el código**: `docs/04_Arquitectura/Arquitectura_IA.md` decía literalmente que el sistema "no utiliza todavía... Modelos LLM" — ya no era cierto, y tampoco mencionaba `claude_client.py`/`orquestador.py`/`anonimizacion.py` ni el flujo de revisión (pendiente/aprobada/rechazada).
3. Detalle menor: `render.yaml` reservaba el espacio para `ANTHROPIC_API_KEY` pero no para `CLAUDE_MODEL_IA`.

~~Resuelto (2026-11) — puntos 2 y 3~~: `Arquitectura_IA.md` actualizado (secciones 3, 4, 6, 8, 11, 13, 15, 18, 20, 21, 22) para reflejar la integración híbrida real, la anonimización y el flujo de revisión completo. `render.yaml` ya declara `CLAUDE_MODEL_IA`.

**Avance (2026-11)**: se agregaron pruebas que confirman el camino "Claude" **a través del endpoint HTTP real** (`POST /ia/rutina/generar/{id}` y `/ia/nutricion/generar/{id}`, no solo a nivel unitario dentro de `claude_client.py` como antes) — reutilizando el mismo doble de SDK ya existente en `test_claude_client.py`, ahora también duplicado en `test_backend.py` para probarlo end-to-end: `origen_ia == "claude"` cuando Claude responde válido, y `"reglas_respaldo"` cuando falla o se desvía. También se completó la cobertura de `test_flujo_revision_plan_nutricional` (le faltaban el 403 de CLIENTE en `/rechazar` y el 422 de motivo vacío, que la de rutinas ya tenía). Backend: 155→159 pruebas.

**Avance (2026-11, continuación) — bug real encontrado en la primera prueba real (no simulada)**: con la `ANTHROPIC_API_KEY` real puesta, la primera rutina generada cayó en "Reglas" en vez de "Claude". Reproducido directo contra la API: Claude devolvía `400 Bad Request` — *"For 'object' type, 'additionalProperties' must be explicitly set to false"*. El modo `strict: true` de las tool-use de Claude exige que **todo** objeto del schema (el de arriba y los anidados dentro de `items`) declare `additionalProperties: false` explícitamente; `_esquema_rutina()`/`_esquema_plan()` en `claude_client.py` no lo tenían. Nunca se detectó antes porque el doble de prueba del SDK que usan los tests no valida esta regla real de Anthropic — solo se vio llamando a la API de verdad. Corregido, con una prueba nueva (`test_esquemas_tool_use_tienen_additional_properties_false`) que verifica la estructura del schema directamente, para que no se repita sin depender de una llamada real.

~~Resuelto (2026-11)~~: con el fix puesto, se repitió la prueba real desde la web — la rutina generada ya muestra el origen **"Claude"** en `RevisionIA.jsx`. Queda confirmado de punta a punta: la integración real con la API de Anthropic funciona en producción. No queda nada pendiente de este punto.

---

# Prioridad Media

## P-05 Alertas de vencimiento de membresía

~~Resuelto (2026-11)~~: `DashboardAdmin.jsx` ahora muestra una tarjeta "Membresías por vencer" con las membresías `ACTIVA` cuya `fecha_fin` cae en los próximos 7 días, usando datos que `GET /cliente-membresias/` ya devolvía. Sin cambios de backend. La notificación por correo queda pendiente de P-03.

**Avance (2026-11, continuación)**: se agregó el recordatorio activo que faltaba. Nuevo `GET /reportes/membresias-por-vencer?dias=N` y una sección "Membresías por vencer" en `Reportes.jsx` con un botón "Enviar recordatorio por WhatsApp" por cliente. El envío es manual-asistido: arma un enlace `https://wa.me/51<telefono>?text=<mensaje>` con un mensaje prellenado (editable antes de enviar) y lo abre en una pestaña nueva — el staff solo confirma el envío en su WhatsApp Web/App ya logueado.

Se eligió este canal (y no una API de envío 100% automático como WhatsApp Business API de Meta o Twilio) a propósito: esas requieren crear y verificar una cuenta de negocio aparte (proceso externo, de días/semanas) y pagan por mensaje — el mismo tipo de bloqueo de aprobación que ya se vivió con Culqi en P-02/P-22. El enlace `wa.me` no necesita cuenta ni credenciales y funciona en producción desde el primer deploy. **Queda pendiente como mejora futura**: automatizar el envío (sin intervención del staff) el día que el gimnasio tenga una cuenta de WhatsApp Business API o SMS aprobada — bloqueado por esa aprobación externa, no por código.

---

## P-06 Exportación/impresión PDF de rutinas y planes nutricionales

~~Resuelto (2026-11)~~: se agregaron `generar_pdf_rutina()` y `generar_pdf_plan_nutricional()` en `backend/app/recibos.py` (mismo patrón de `reportlab` que el recibo de pago), expuestas en `GET /rutinas/{id}/pdf` y `GET /nutricion/{id}/pdf` (mismo control de acceso ADMIN/ENTRENADOR o el cliente dueño). Botón "Descargar PDF" agregado en `DetalleRutina.jsx`, `MiRutina.jsx`, `Nutricion.jsx` y `MiNutricion.jsx`.

---

## P-07 Reportes operativos consolidados

~~Resuelto (2026-11)~~: nuevos `GET /reportes/ingresos` y `GET /reportes/asistencias` (por rango `desde`/`hasta`, agrupados por día). Nueva página `web-admin/src/pages/Reportes.jsx` (ruta `/reportes`, solo ADMIN) con selector de fechas, tablas por día y exportación a CSV reutilizando `exportarCsv.js`.

**Avance (2026-11, continuación)**: tres frentes nuevos, todos en `reportes.py` + `Reportes.jsx` salvo donde se indica:

1. **Reportes de negocio**: `GET /reportes/productos-mas-vendidos` y `GET /reportes/ventas-por-metodo-pago` (mismo patrón por rango de fechas), con su tabla y export CSV.
2. **Instrumentación para el postest de la tesis** (ver matriz de operacionalización, Anexo 02/04): el sistema ya alimentaba F-07/F-08/F-09 (calidad de la IA); ahora también alimenta:
   - **I4 (F-04, tiempo de respuesta)**: middleware en `app/main.py` (`medir_tiempo_respuesta`) que guarda en `RegistroTiempoSistema` la duración de cada request de negocio (excluye `/docs` y `/reportes`), expuesto en `GET /reportes/sistema/tiempos-respuesta`.
   - **I5 (F-05, precisión de registros)**: `GET /reportes/sistema/registros-recientes`, lista acotada (vía `RegistroAuditoria`, ya existente) para que el evaluador verifique solo esos registros contra su documento de origen, en vez de todo el sistema.
   - **I12 (F-12, duplicidad)**: `GET /reportes/sistema/duplicidad`, hallazgos automáticos (pagos/membresías duplicados, DNIs repetidos, campos obligatorios vacíos) que complementan, no reemplazan, la revisión del evaluador.
   - **I15 (F-15, seguimiento de progreso)**: `GET /reportes/progreso-fisico`, % de clientes `ACTIVO` con algún `Progreso` registrado en el rango.
   - **I16 (F-16, exactitud de inventario)**: ver el punto de "Conteo físico de inventario" más abajo (vive en `inventario.py`, no en `reportes.py`).

   Los indicadores I1-I3 (entregables de desarrollo), I6 (pruebas funcionales, ya cubierto por la suite de pytest) e I10/I11/I13/I14/I17/I18 (tiempos de *proceso* humano) se dejan deliberadamente fuera de esta automatización: la metodología de la tesis exige cronometrarlos a mano en uso real, igual que en el pretest manual, para que ambas mediciones sean comparables.
3. **Boletas de venta** (antes no existía ningún comprobante para una `Venta`, solo para `Pago`): `generar_boleta_venta()` en `recibos.py` (mismo estilo que `generar_recibo_pago()`) + `GET /ventas/{id}/boleta`, con botón "Descargar boleta" en `Ventas.jsx`. De paso, `generar_recibo_pago()` ahora muestra también la membresía y el periodo cubierto cuando el pago está asociado a una.
4. **Conteo físico de inventario** (nuevo, soporta F-16/I16): tablas `ConteoInventario`/`DetalleConteoInventario`, `POST /inventario/conteos` (toma el stock del sistema como snapshot y lo compara contra lo que el staff cuenta físicamente) y `GET /inventario/conteos/{id}`, con una pestaña "Conteo físico" nueva en `Inventario.jsx` que calcula la diferencia y el % de exactitud automáticamente.

**Avance (2026-11, continuación 2)**: revisando qué reporte de negocio podía faltar, se encontró un hueco real: había reporte de ventas (ingresos, productos más vendidos, método de pago) pero ninguno de compras/gastos a proveedores — por lo tanto no existía ninguna vista con la utilidad neta del negocio (ingresos menos egresos). Se agregaron:
- `GET /reportes/compras`: egresos por día y por proveedor (compras `CONFIRMADA`), el complemento que le faltaba a `/reportes/ingresos`.
- `GET /reportes/resumen-general`: consolida en una sola vista ingresos (pagos de membresía + ventas de productos), egresos (compras), utilidad neta, asistencias del periodo, clientes nuevos, membresías vencidas y stock bajo (este último es una foto del momento, no depende del rango de fechas).

Ambos con su tabla/tarjetas y exportación a CSV en `Reportes.jsx`, como el resto de reportes del módulo. No se encontró ningún hueco en los reportes formales de la tesis (F-04/05/07/08/09/12/15/16): todos los indicadores que correspondía automatizar ya estaban cubiertos (ver el punto 2 de arriba); los que faltaban eran de negocio, no de tesis.

**Avance (2026-11, continuación 3) — reporte general completo en un solo Excel**: a pedido, se agregó `GET /reportes/general-completo/excel` (`app/reporte_excel.py`, con `openpyxl`) que junta en un solo archivo .xlsx **casi todos los datos del negocio**, una hoja por tema, en vez de exportar CSV por CSV y pegarlos a mano: Resumen (los mismos KPIs de `/resumen-general`), Ingresos, Egresos (por día y por proveedor), Ventas, Compras, Pagos, Membresías, Clientes, Asistencias (por día + top 10 clientes del periodo), Inventario (con alerta de stock bajo por producto) y Rutinas/Nutrición IA (totales y por estado de revisión). Botón "Descargar reporte completo (Excel)" en la sección "Resumen general del período" de `Reportes.jsx`.

---

## P-08 Tests de `Navbar.jsx` y `NotFound.jsx`

~~Resuelto (2026-11)~~: se agregaron `Navbar.test.jsx` (7 pruebas) y `NotFound.test.jsx` (1 prueba). Ambos componentes quedan en 100% de cobertura.

---

## P-09 CI/CD

~~Resuelto (2026-11)~~: se agregó `.github/workflows/tests.yml` con dos jobs (`backend`: `pytest`; `frontend`: `npm run lint` + `npm run test`) que corren en cada push/PR a `main`. Verificado que la suite de backend pasa sin `backend/.env` presente, igual que correrá en CI.

---

## P-10 Rate limiting de login solo en memoria

`backend/app/rate_limit.py` limita los intentos de login (5 intentos / 15 min) pero el conteo vive en memoria del proceso — es correcto para el despliegue actual (un solo worker en Render), pero si el backend se escala a múltiples workers, cada uno llevaría su propio conteo independiente.

**Decisión (2026-11)**: no se resuelve ahora. Se retoma junto con la migración de todo el despliegue a un VPS de Hostinger (pendiente, ver P-16): ahí sí tendría sentido correr varios workers para aprovechar el servidor, y ese es el momento correcto para agregar Redis y resolver esto de una vez, en vez de hacerlo ahora sin necesidad real.

---

## P-11 Password de desarrollo local hardcodeada

~~Resuelto (2026-11)~~: `DEFAULT_DB_URL` en `create_db.py` ahora lee de la variable de entorno opcional `DEFAULT_DB_URL` (con un default genérico `postgres:postgres`, ya no la contraseña real que se reutilizaba). Producción sigue sin verse afectada (usa `DATABASE_URL` inyectada por Render).

---

## P-18 Sin página en web-admin para Entrenadores ni Auditoría

~~Resuelto (2026-11)~~: se agregaron `web-admin/src/pages/Entrenadores.jsx` (CRUD completo) y `Auditoria.jsx` (vista de solo lectura con filtro por entidad), con sus rutas `/entrenadores` y `/auditoria` (solo ADMIN) y los enlaces correspondientes en el sidebar, cada una con su archivo de pruebas.

---

# Prioridad Baja

## P-12 Migrar `class Config:` a `ConfigDict` (Pydantic v2)

~~Resuelto (2026-11)~~: las 26 clases `class Config: from_attributes = True` en `schemas.py` se migraron a `model_config = ConfigDict(from_attributes=True)`. Sin warnings de deprecación de Pydantic en la suite de tests.

---

## P-13 Dockerización

~~Resuelto (2026-11)~~: `backend/Dockerfile`, `web-admin/Dockerfile` (build multi-stage con nginx) y `docker-compose.yml` en la raíz (`db` + `backend` + `frontend`, con healthcheck de PostgreSQL). Probado de punta a punta con `docker compose up --build`: las tres migraciones/seeds de `create_db.py` corren solas, y un login real contra `POST /usuarios/login` devuelve 200 con el admin sembrado. No reemplaza el despliegue de `render.yaml`, es solo para desarrollo local reproducible.

---

## P-15 Backups automatizados propios

El respaldo de la base de datos depende enteramente del plan gestionado de PostgreSQL en Render. No hay un `pg_dump` automatizado ni almacenado fuera de Render.

**Decisión (2026-11)**: no se resuelve ahora — hoy el entorno de Render es de desarrollo (los datos no tienen valor real todavía), así que no se justifica construir una solución de backups para un entorno que se va a reemplazar. Se implementa como parte de la migración a Hostinger (ver P-16), definiendo ahí la estrategia real para el entorno de producción final (backup nativo de Hostinger o `pg_dump` programado dentro del VPS).

---

## P-16 Riesgos del plan gratuito de Render

El despliegue actual usa el plan **free** de Render (`render.yaml`): esto implica *cold starts* tras períodos de inactividad y que la base de datos free expira a los 90 días si no se actualiza a un plan pago. Es un riesgo operativo real mientras el proyecto siga en este tier, independiente del código de la aplicación.

**Incidente (2026-11)**: ya ocurrió una vez — la base de datos expiró y se recreó vía "Manual Sync" del Blueprint, sin pérdida relevante porque el entorno sigue siendo de desarrollo. Puede volver a pasar cada 90 días mientras no se resuelva.

**Decisión (2026-11)**: no se paga un plan superior en Render. En vez de eso, se migrará **todo el despliegue** (backend + base de datos) a un **VPS de Hostinger** de pago, reutilizando `docker-compose.yml` (P-13). Queda pendiente de que el usuario compre el plan VPS (y, idealmente, un dominio propio para poder habilitar HTTPS con Let's Encrypt). Esta migración queda para el final del backlog; P-10 y P-15 se resuelven junto con ella.

---

## P-17 Documentar formalmente el módulo de Comercio y Avisos

~~Resuelto (2026-09)~~: `Requerimientos_Funcionales.md` ya incluye RF-176 a RF-226 cubriendo Entrenadores, Avisos, Auditoría y los seis submódulos de Comercio (categorías, productos, proveedores, compras, inventario, ventas).

---

## P-26 Lector de código de barras en Productos/Ventas/Compras

~~Resuelto (2026-11)~~: a pedido, se agregó soporte de código de barras al módulo de Comercio. Un lector USB/Bluetooth de los que se venden para mostrador funciona en modo "emulación de teclado" (HID): no necesita driver ni integración especial, solo escribe el código escaneado como si fuera un teclado y termina con Enter — por eso la implementación es un input normal con un `onKeyDown`, nada de hardware.

- `Producto.codigo_barras` (único, opcional) + migración (`create_db.py`) con columna e índice único para la base de datos ya desplegada.
- `GET /productos/por-codigo/{codigo}`: búsqueda exacta, con validación de duplicado al crear/editar un producto (400 si otro producto ya usa ese código).
- Campo "Código de barras" en el formulario de `Productos.jsx` (se puede escanear ahí mismo o escribirlo a mano).
- Input de escaneo dedicado en `Ventas.jsx` y `Compras.jsx`: agrega el producto al detalle apenas se escanea (o le suma 1 a la cantidad si ya estaba en la lista), sin tener que buscarlo manualmente en el selector — en compras, además precarga el precio unitario con el último precio de compra del producto.

**Alternativa sin lector físico, no implementada**: escanear con la cámara del celular/tablet desde el navegador (librería `html5-qrcode`/`zxing-js`), para probar el flujo sin comprar hardware. Queda como mejora futura si el gimnasio decide no comprar un lector USB/Bluetooth.

---

## P-25 Purga manual de `RegistroTiempoSistema` (crece más rápido que cualquier otra tabla)

~~Resuelto (2026-11)~~: revisando qué podía llenar la base de datos más rápido de lo necesario, se confirmó en producción que `RegistroTiempoSistema` (instrumentación del indicador I4/F-04 — una fila por cada request de negocio) ya tenía ~1,185 filas solo con uso de desarrollo/pruebas, muy por encima de `RegistroAuditoria` (17 filas en el mismo rango), que solo registra escrituras. Es la única tabla del sistema sin ningún valor histórico/de negocio una vez medido el indicador del postest — a diferencia de los registros de auditoría, movimientos de stock o entidades con soft-delete (rutinas, pagos, ventas, etc.), que sí alimentan reportes de la tesis o el historial del cliente y no deben borrarse.

Se agregó `DELETE /reportes/sistema/tiempos-respuesta?antes_de=YYYY-MM-DD` (solo ADMIN, a diferencia del resto del router de reportes que también permite ENTRENADOR, por ser una eliminación física) y un control en `Reportes.jsx` ("Mantenimiento: limpiar tiempos de respuesta") con selector de fecha y confirmación antes de borrar. **Deliberadamente manual, no automático**: este proyecto no tiene ningún cron/scheduler (ni Render Cron está disponible en el plan gratuito actual), así que agregar uno solo para esto sería invertir en infraestructura que ya se decidió posponer hasta la migración a Hostinger (ver P-10/P-15/P-16). El momento natural para usarlo es después de medir el indicador I4 del postest de la tesis (previsto para enero 2027) — a partir de ahí, los registros anteriores ya no sirven para nada.

---

## P-24 Facturación electrónica SUNAT — evaluado y descartado por ahora

El recibo/boleta en PDF (`backend/app/recibos.py`) es un comprobante interno, no un documento tributario válido ante SUNAT — ya lo dice su propio disclaimer. Se evaluaron las rutas disponibles para emitir boletas electrónicas reales:

1. **PDF interno actual** (gratis, ya implementado, sin validez tributaria).
2. **SEE-SOL de SUNAT**: gratis, SUNAT firma por el contribuyente (no exige certificado), pero es 100% manual vía el portal de SUNAT (Clave SOL) — sin API, no se puede integrar con este sistema sin que el staff digite cada venta dos veces.
3. **OSE/PSE comercial con API** (ej. NubeFacT): integrable vía backend, pero de pago (~S/70-120/mes por hasta 500 comprobantes, sin plan gratuito con cupo garantizado encontrado).
4. **Sistema propio ("SEE - Del Contribuyente")**: SUNAT ofrece un Certificado Digital Tributario (CDT) gratuito para esta vía (autorizado hasta el 31/12/2027 según la norma vigente), pero exige construir y mantener XML UBL 2.1 + firma XAdES-BES + envío SOAP (WS-Security) al webservice de SUNAT + decodificación de la CDR + QR + numeración propia de serie/correlativo + resumen diario de boletas — una integración del tamaño de la de Culqi, con mantenimiento perpetuo (SUNAT cambia la norma seguido) y cero margen de error (un XML mal armado no es un bug visual, es un comprobante que legalmente no existió).

**Decisión (2026-11)**: no se implementa ninguna de las opciones 2-4 por ahora. Además de quedar fuera del alcance original de la tesis (sección "Delimitación funcional": *"No incluye... facturación electrónica con SUNAT..."*), el gimnasio ya cobra en persona con un POS físico aparte (ver P-22) que probablemente ya emite boleta real por su cuenta — la "boleta" de este sistema solo cubre los pagos que pasan por Culqi (membresías/tienda online). El costo/riesgo de automatizarla no se justifica para ese volumen.

**Revisar más adelante solo si**: el negocio crece lo suficiente como para que SUNAT exija boleta electrónica real específicamente por las ventas/pagos que procesa este sistema — en ese caso, la ruta recomendada es contratar un OSE barato con API (opción 3), no construir la integración propia (opción 4).

---

# Fuera de este documento

No se repiten aquí las brechas ya resueltas en las tres rondas de revisión anteriores: RBAC completo, motor de IA real (restricciones médicas + fórmula Mifflin-St Jeor), auditoría y trazabilidad, autogestión de contraseñas + reset por admin, Avisos editables desde el panel, KPI de asistencias en el dashboard, y paginación en los listados de mayor volumen.

---
