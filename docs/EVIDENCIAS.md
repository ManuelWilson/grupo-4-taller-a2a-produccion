# Evidencias

## Carpeta de evidencias

Las capturas de pantalla deben guardarse en la carpeta `evidencias/` (ver
`evidencias/README.md` para instrucciones detalladas).

## Capturas de ejecución local

### 0. Capturas tomadas (frontend web)

| Archivo | Qué muestra | Fecha |
|---|---|---|
| `evidencias/evidencia-flujo-historia.jpeg` | Frontend web mostrando consulta de historia ("En un párrafo corto, ¿cuál fue la principal causa de la caída del Imperio Romano?") y respuesta del agente de Historia (un párrafo corto sobre las causas) | Noviembre 2026 |
| `evidencias/evidencia-flujo-completo.jpeg` | Frontend web mostrando dos consultas: una de historia (caída del Imperio Romano) y una de geografía (río más largo de Chile), con respuestas cortas de ambos agentes | Noviembre 2026 |
| `evidencias/evidencia-control-acceso.jpeg` | Frontend web mostrando un intento de acceso con API key inválida ("clave-incorrecta") y el error "Forbidden: API key inválida o ausente." | Noviembre 2026 |
| `evidencias/evidencia-swagger-ui.jpeg` | Swagger UI mostrando los endpoints disponibles (/health, /chat, /docs) | Noviembre 2026 |

Ambas capturas muestran el flujo completo: solicitud del usuario → respuesta del agente, con el selector de agente, API key y URL de la API visibles.

**Nota sobre la pregunta de la capital de Chile:** En la primera versión de la captura, se preguntó al agente de Historia por la capital de Chile. El agente respondió con contexto histórico (fundación de Santiago por Pedro de Valdivia en 1541). Esto es válido porque el agente de Historia puede responder sobre la fundación de ciudades. Sin embargo, para la evidencia final se usó una pregunta más apropiada para Historia (caída del Imperio Romano) y otra para Geografía (río más largo de Chile), con respuestas limitadas a un párrafo para que toda la interacción sea visible en la captura.

### 1. Capturas tomadas (Telegram - producción)

| Archivo | Qué muestra | Fecha |
|---|---|---|
| `evidencias/evidencia-telegram-texto-y-audio.png` | Bot en Telegram respondiendo a un mensaje de texto y a un mensaje de voz. Muestra la transcripción del audio y la respuesta del agente. **(Producción real, no local.)** | Noviembre 2026 |
| `evidencias/evidencia-telegram-control-acceso-por-powershell.png` | Terminal mostrando un intento de acceso rechazado (403 Forbidden) al enviar un request al webhook sin el secreto `X-Telegram-Bot-Api-Secret-Token`. | Noviembre 2026 |

### 2. Capturas tomadas (Heroku - producción)

| Archivo | Qué muestra | Fecha |
|---|---|---|
| `evidencias/evidencia-heroku-ambos-agentes.png` | Dashboard de Heroku mostrando ambos agentes (`grupo4-agente-historia` y `grupo4-agente-geografia`) desplegados y en estado "Deployed". | Noviembre 2026 |
| `evidencias/evidencia-heroku-grupo4-agente-historia.png` | Deploy del agente de Historia en Heroku. Muestra la app desplegada, Config Vars y estado del build. | Noviembre 2026 |
| `evidencias/evidencia-heroku-grupo4-agente-geografia.png` | Deploy del agente de Geografía en Heroku. Muestra la app desplegada, Config Vars y estado del build. | Noviembre 2026 |

### 3. Capturas tomadas (AWS Lambda - producción)

| Archivo | Qué muestra | Fecha |
|---|---|---|
| `evidencias/evidencia-lambda-gateway-telegram.png` | Consola de AWS mostrando la función Lambda `gateway-telegram` (container image) con su configuración, variables de entorno y Function URL. | Noviembre 2026 |
| `evidencias/evidencia-lambda-gateway-telegram-zip.png` | Consola de AWS mostrando la función Lambda `gateway-telegram-zip` (zip) con su configuración, variables de entorno y Function URL. | Noviembre 2026 |

#### Caso: Control de acceso en Telegram (simulación)

- **Entorno:** PRODUCCIÓN (AWS Lambda)
- **Fecha:** Noviembre 2026
- **Solicitud:** POST al webhook de Telegram (`https://<function-url>/telegram`) con un payload de mensaje pero **sin** el header `X-Telegram-Bot-Api-Secret-Token`.
- **Resultado esperado:** El gateway responde `403 Forbidden` (acceso rechazado).
- **Resultado obtenido:** `HTTP Error: 403` / `Body: Forbidden`.
- **Observaciones:** El gateway valida el secreto del webhook en cada request. Si el secreto no coincide o está ausente, responde 403. En Telegram real, el bot siempre envía el secreto correcto (configurado con `setWebhook`), por lo que un usuario normal no puede generar un 403. La captura se obtuvo simulando un request sin secreto desde PowerShell, lo que demuestra que el control de acceso funciona correctamente.

**Prueba del control de acceso:** Se envió un request con API key inválida ("clave-incorrecta"). El sistema respondió con `403 Forbidden: API key inválida o ausente.` Esto demuestra que el control de acceso funciona correctamente.

### 1. Servidor de historia en puerto 2025

### 1. Servidor de historia en puerto 2025

- **Archivo:** `evidencia-captura-terminal-2025.png`
- **Entorno:** LOCAL (Windows 11, Python 3.12.10)
- **Fecha:** Octubre 2026
- **Solicitud:** Levantar el servidor con `langgraph dev --port 2025`
- **Resultado esperado:** El servidor inicia y publica la Agent Card en `/.well-known/agent-card.json`
- **Resultado obtenido:** El servidor inicia correctamente en `http://127.0.0.1:2025`
- **Observaciones:** Servidor funcionando. Agent Card disponible.

### 2. Notebook de pruebas A2A ejecutado

- **Archivo:** `agente-profesor-historia/notebooks/a2a-test.run.log`
- **Entorno:** LOCAL
- **Fecha:** Octubre 2026
- **Solicitud:** Ejecutar el notebook `a2a-test.ipynb` con ambos servidores arriba
- **Resultado esperado:** 18 celdas ejecutadas, 0 fallidas
- **Resultado obtenido:** 18 celdas ejecutadas, 0 fallidas
- **Observaciones:** Todas las pruebas A2A pasaron (descubrimiento, supervisor, diálogo A→B→A, checklist).

### 3. Flujo completo en Telegram (producción)

- **Entorno:** PRODUCCIÓN (Heroku + AWS Lambda)
- **Fecha:** Noviembre 2026
- **Solicitud:** "¿cuál es la capital de Chile?" al bot de Telegram
- **Resultado esperado:** El bot responde con la respuesta del agente de Geografía
- **Resultado obtenido:** El bot responde correctamente
- **Observaciones:** Flujo completo funcionando: Telegram → Lambda (router) → Agente (via /runs/wait) → Telegram.

### 3.5 Integración avanzada: Telegram por voz

- **Entorno:** PRODUCCIÓN (AWS Lambda + Heroku)
- **Fecha:** Noviembre 2026
- **Solicitud:** Mensaje de voz enviado al bot de Telegram
- **Resultado esperado:** El bot transcribe el audio y responde con texto
- **Resultado obtenido:** ⏳ Pendiente de probar con audio real
- **Observaciones:** La implementación está completa (descarga de audio + Google STT + procesamiento). Pendiente de prueba end-to-end con un mensaje de voz real.

### 4. Logs de ejecución

#### 4.0 Logs de AWS Lambda (CloudWatch)

- **Archivo:** `evidencias/lambda-logs.txt` (78 líneas)
- **Comando:** `aws logs tail /aws/lambda/gateway-telegram --since 24h --region us-east-1`
- **Entorno:** PRODUCCIÓN
- **Fecha:** Noviembre 2026
- **Contenido:** Clasificación del router, consulta al agente, errores de Telegram (chat not found), comando /start.
- **Observaciones:** Los logs muestran el flujo completo: clasificación → consulta → respuesta. Los errores son por chat_id de prueba (12345).

### 4.1 Logs de Heroku (agentes)

- **Archivos:** `evidencias/heroku-grupo4-agente-historia-logs.txt` (100 líneas), `evidencias/heroku-grupo4-agente-geografia-logs.txt` (100 líneas)
- **Comando:** API de Heroku (`POST /apps/{app}/log-sessions` + GET logplex_url)
- **Entorno:** PRODUCCIÓN
- **Fecha:** Noviembre 2026
- **Contenido:** Requests A2A recibidos, respuestas del agente, cold starts, errores.
- **Observaciones:** Los logs muestran el flujo completo: request → procesamiento → respuesta. Los cold starts se ven en "Init Duration".

#### 4.1 Gateway (AWS Lambda)

- **Entorno:** PRODUCCIÓN (AWS Lambda)
- **Fecha:** Noviembre 2026
- **Solicitud:** Request al gateway sin secreto / con secreto incorrecto
- **Resultado esperado:** 403 Forbidden
- **Resultado obtenido:** 403 Forbidden
- **Observaciones:** El gateway rechaza correctamente requests sin secreto o con secreto incorrecto.

#### 4.2 API local (FastAPI)

- **Entorno:** LOCAL (Windows 11, Python 3.12.10)
- **Fecha:** Noviembre 2026
- **Solicitud:** `POST /chat` con API key válida, inválida y ausente
- **Resultado esperado:** 200 OK (válida), 403 Forbidden (inválida/ausente)
- **Resultado obtenido:** 200 OK (válida), 403 Forbidden (inválida/ausente)
- **Observaciones:** La API FastAPI valida correctamente el header `X-API-Key`. Swagger en `/docs` permite probar con "Try it out".

## Evidencia honesta y protegida

- **Datos de prueba:** Todas las pruebas usan datos de prueba (chat_id 12345, preguntas genéricas).
- **Claves ocultas:** No se muestran `GOOGLE_API_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_SECRET` ni `HEROKU_API_KEY` en ninguna captura.
- **Lo probado vs lo pendiente:**
  - ✅ Probado: flujo A2A local, tests A2A (18 celdas), control de acceso (403), flujo Telegram end-to-end.
  - ⏳ Pendiente: capturas de pantalla del flujo en Telegram (solo texto).
  - ⏳ Pendiente: prueba con datos reales de un usuario (no solo chat_id de prueba).
  - ⏳ Pendiente: monitoreo de costos en producción.
- **No rotulado como producción:** Las pruebas locales se etiquetan como LOCAL; las de producción como PRODUCCIÓN.

## Capturas necesarias para reconstruir el caso

Para reconstruir el caso completo, se necesitan las siguientes capturas (pendientes de tomar):

1. **Captura del bot en Telegram** respondiendo a una consulta de historia.
2. **Captura del bot en Telegram** respondiendo a una consulta de geografía.
3. **Captura de los logs de Lambda** mostrando el router clasificando y el agente respondiendo.
4. **Captura de los logs de Heroku** mostrando el agente procesando la consulta.
5. **Captura del control de acceso** mostrando un intento rechazado (403).

Estas capturas deben ser legibles y con contexto (mostrar la pregunta, el sistema y la respuesta).

## Observaciones

- El agente de Historia y el de Geografía responden correctamente a consultas dentro de su dominio.
- El router clasifica correctamente los 6 casos de prueba (mínimo 13/15 en la batería de 15 casos).
- El control de acceso funciona: requests sin secreto o con secreto incorrecto son rechazados con 403.
- El flujo completo Telegram → Gateway → Agente → Telegram funciona correctamente.
- **Limitación:** Los agentes solo responden sobre los temas de sus apuntes (historia/geografía). No cubren otros temas.
- **Limitación:** El router puede clasificar incorrectamente mensajes ambiguos.
- **Limitación:** Los dynos Eco de Heroku se duermen tras 30 min de inactividad.
- **Simulación utilizada:** Las pruebas de control de acceso usaron chat_id de prueba (12345), no un usuario real.
