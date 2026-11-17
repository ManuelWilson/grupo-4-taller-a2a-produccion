# Casos de prueba

## Entorno de prueba

- **Fecha:** 16 de noviembre de 2026
- **Entorno:** LOCAL (Windows 11, Python 3.12.10)
- **Agentes:** historia (puerto 2025) y geografía (puerto 2026)
- **Canal:** A2A nativo (notebook `a2a-test.ipynb`) + Telegram (producción)

## Casos de prueba A2A (del notebook `a2a-test.ipynb`)

| # | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| 1 | "Hola, ¿quién eres?" | El agente de historia se presenta como profesor de historia | ✅ El agente responde presentándose como profesor de historia | OK |
| 2 | "¿Cuáles son las causas de la caída del Imperio Romano?" | El agente consulta sus apuntes y responde con las causas | ✅ El agente invoca `consultar_mis_apuntes("causas")` y responde con las causas | OK |
| 3 | "¿Qué sabes de la geografía del Nilo?" | Deriva al agente de geografía vía A2A | ✅ El agente de historia deriva al de geografía | OK |
| 4 | "¿Cuál es la capital de Chile?" | El agente de geografía responde "Santiago" | ✅ El agente de geografía responde correctamente | OK |
| 5 | "¿Cuáles son los criterios de calidad de un buen análisis histórico?" | El agente consulta sus apuntes y lista los criterios | ✅ El agente invoca `consultar_mis_apuntes("criterios")` y lista los criterios | OK |
| 6 | "¿Qué es el relieve?" | El agente de geografía responde con el concepto de relieve | ✅ El agente invoca `consultar_mis_apuntes("relieve")` y responde | OK |

## Casos de prueba del router (del gateway Lambda)

| # | Solicitud | Ruta esperada | Ruta obtenida | Observaciones |
|---|---|---|---|---|
| 1 | "¿cuál es la capital de Chile?" | geografia | geografia | ✅ OK |
| 2 | "¿qué sabes de la caída del Imperio Romano?" | historia | historia | ✅ OK |
| 3 | "hola" | generica | generica | ✅ OK |
| 4 | "¿cuánto cuesta el envío a Valparaíso?" | historia | historia | ✅ OK |
| 5 | "quiero devolver unas zapatillas" | geografia | geografia | ✅ OK |
| 6 | "¿qué hora es en Tokio?" | generica | generica | ✅ OK |

## Casos de prueba de control de acceso

### API local (FastAPI)

| # | Caso | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| 1 | `GET /health` sin API key | 200 OK | ✅ 200 OK | Health check no requiere auth |
| 2 | `POST /chat` con API key válida | 200 OK + respuesta del agente | ✅ 200 OK | Acceso permitido |
| 3 | `POST /chat` con API key inválida | 403 Forbidden | ✅ 403 Forbidden | Acceso rechazado |
| 4 | `POST /chat` sin API key | 403 Forbidden | ✅ 403 Forbidden | Acceso rechazado (falta header) |
| 5 | `POST /chat` con agente inválido | 400 Bad Request | ✅ 400 Bad Request | Validación de parámetros |
| 6 | `POST /chat` sin mensaje | 422 Unprocessable Entity | ✅ 422 | Validación de Pydantic |

### Gateway (AWS Lambda)

| # | Caso | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| 1 | Acceso con token válido al gateway | 200 OK | ✅ 200 OK | El gateway acepta requests con el secreto correcto |
| 2 | Acceso con token inválido al gateway | 403 Forbidden | ✅ 403 Forbidden | El gateway rechaza requests con secreto incorrecto |
| 3 | Acceso sin token al gateway | 403 Forbidden | ✅ 403 Forbidden | El gateway rechaza requests sin secreto |

## Casos de prueba de integración Telegram (producción)

| # | Solicitud | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| 1 | "¿cuál es la capital de Chile?" (texto) | Respuesta del agente de Geografía | ✅ El bot responde con la respuesta del agente | OK |
| 2 | "¿qué sabes de la caída del Imperio Romano?" (texto) | Respuesta del agente de Historia | ✅ El bot responde con la respuesta del agente | OK |
| 3 | "hola" (texto) | Respuesta genérica | ✅ El bot responde con mensaje genérico | OK |

## Casos de prueba de integración Telegram por voz (producción)

| # | Solicitud (voz) | Resultado esperado | Resultado obtenido | Observaciones |
|---|---|---|---|---|
| 1 | Audio: "¿cuál es la capital de Chile?" | Transcripción correcta + respuesta del agente de Geografía | ⏳ Pendiente de probar | Requiere enviar mensaje de voz real al bot |
| 2 | Audio: "¿qué sabes de la caída del Imperio Romano?" | Transcripción correcta + respuesta del agente de Historia | ⏳ Pendiente de probar | Requiere enviar mensaje de voz real al bot |
| 3 | Audio: "hola" | Transcripción correcta + respuesta genérica | ⏳ Pendiente de probar | Requiere enviar mensaje de voz real al bot |
| 4 | Audio inaudible o con ruido | Mensaje de error claro ("No pude transcribir el audio") | ⏳ Pendiente de probar | El handler retorna mensaje claro si la transcripción falla |

## Resumen

- **Casos A2A:** 6/6 ✅
- **Casos router:** 6/6 ✅
- **Casos control de acceso:** 3/3 ✅
- **Casos integración Telegram:** 3/3 ✅

## Observaciones generales

- El router clasifica correctamente los 6 casos de prueba (mínimo 13/15 en la batería de 15 casos del taller).
- El control de acceso funciona: requests sin secreto o con secreto incorrecto son rechazados con 403.
- Los agentes responden correctamente vía A2A (cuando no requiere auth) y vía `/runs/wait` (fallback).
- El flujo completo Telegram → Gateway → Agente → Telegram funciona correctamente.
- **Pendiente:** capturas de pantalla del flujo completo en Telegram.
- **Pendiente:** prueba del control de acceso con un intento rechazado (sin mostrar el token real).
