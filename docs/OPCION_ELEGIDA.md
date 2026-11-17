# Opción elegida de implementación

## Opción seleccionada

**Opción 2: Un canal de atención (Telegram) + Servicio FastAPI (gateway).**

El proyecto implementa un agente conversacional multi-especialista (Historia y
Geografía) expuesto a través de Telegram mediante un gateway FastAPI en AWS
Lambda, con los agentes desplegados en Heroku y comunicándose por A2A (Agent-
to-Agent protocol).

## Problema que resuelve

Los agentes profesores de Historia y Geografía del taller A2A solo eran
accesibles vía notebooks y servidor local (`langgraph dev`). No existía una
forma para que un usuario final interactuara con ellos de manera natural
(mensajes de texto) sin conocimientos técnicos.

Esta implementación resuelve eso: un usuario puede escribir al bot de Telegram
y recibir respuestas de los agentes especializados, enrutadas automáticamente
según la consulta, con memoria por conversación.

## Qué partes del trabajo anterior se reutilizan

| Componente del taller A2A | Reutilizado en producción |
|---|---|
| Agentes `agente_profesor_historia` y `agente_profesor_geografia` (ReAct, LangGraph) | ✅ Desplegados en Heroku sin cambios |
| Herramientas `consultar_mis_apuntes(tema)` | ✅ Reutilizadas tal cual |
| Blueprints de diseño (rol, alcance, autonomía, etc.) | ✅ Documentados y respetados |
| A2A nativo (Agent Card + endpoint `/a2a/{assistant_id}`) | ✅ Usado por el gateway para invocar agentes |
| Memoria por conversación (`thread_id` → `contextId`) | ✅ Preservada vía A2A contextId |
| Prompts (SYSTEM_PROMPT, SYSTEM_GEOGRAFIA) | ✅ Reutilizados sin cambios |
| Tests A2A (`a2a-test.ipynb`) | ✅ Reutilizados para verificar funcionamiento |

## Qué se agregó

| Componente nuevo | Descripción |
|---|---|
| Gateway FastAPI (Lambda) | Router LLM + webhook de Telegram + invocación A2A |
| Router con salida estructurada | Clasifica mensajes en `historia`, `geografia` o `generica` |
| Webhook de Telegram | Recibe mensajes de Telegram y responde vía `sendMessage` |
| Fallback a `/runs/wait` | Cuando A2A requiere auth en Heroku, usa LangGraph directo |
| Despliegue en Heroku | 2 agentes en Eco dynos |
| Despliegue en AWS Lambda | Gateway con Function URL |
| Documentación de despliegue | `deploy/DEPLOYMENT.md` con pasos, redespliegue, rollback, troubleshooting |

## Integración avanzada (opcional, +1 punto)

**Opción elegida:** Telegram por voz (mensajes de audio).

El gateway detecta mensajes de voz (`message.voice`), descarga el audio de Telegram
(OGG/OPUS), lo transcribe con Google Cloud Speech-to-Text (`es-CL`) y procesa
el texto transcrito por el router y el agente. La respuesta se envía como texto
a Telegram.

### Componentes

| Componente | Descripción |
|---|---|
| `descargar_audio_telegram(file_id)` | Descarga el audio de Telegram usando `getFile` + URL de descarga |
| `transcribir_audio(audio_bytes)` | Envía el audio (OGG/OPUS) a Google STT REST API, retorna texto transcrito |
| Detección de `message.voice` | En el handler, si el update tiene voz (y no texto), transcribe y procesa |

### Costos adicionales

- Google STT free tier: 60 minutos de audio por mes.
- Después: $0.006 por 15 segundos ($0.024/min).
- Para 100 mensajes de 10s: ~$0.01 (dentro del free tier).

### Limitaciones

- Solo transcribe y responde con texto (no TTS).
- El audio debe ser claro; ruido de fondo reduce la precisión.
- El idioma está fijo en `es-CL` (configurable con `STT_LANGUAGE_CODE`).

## Limitaciones conocidas

- Los dynos Eco de Heroku se duermen tras 30 min de inactividad (primer mensaje tarda ~10-30s).
- El endpoint A2A en Heroku requiere autenticación; el gateway usa fallback a `/runs/wait`.
- Los agentes no tienen control de acceso (autenticación) en el servidor local.
- El manejo de errores es básico (mensajes claros pero sin retry ni circuit breaker).
- No hay frontend web; la interacción es solo vía Telegram.
- La memoria por conversación depende de que el `contextId` (derivado del `chat_id`) se mantenga.
- Los agentes solo responden sobre los temas de sus apuntes (historia/geografía); no cubren otros temas.
- El router puede clasificar incorrectamente mensajes ambiguos (mínimo 13/15 aciertos en pruebas).
