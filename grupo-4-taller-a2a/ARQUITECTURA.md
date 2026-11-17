# Arquitectura final — Agentes A2A en producción vía Telegram

## 1. Visión general

```
┌─────────────┐     HTTPS webhook      ┌──────────────────────────────┐
│  Telegram   │ ──────────────────────►│  AWS Lambda (Function URL)   │
│  (usuario)  │                        │  Gateway: /telegram          │
└─────────────┘                        │  - verifica secreto          │
       ▲                               │  - router LLM (clasificación) │
       │                               │  - invoca agentes A2A        │
       │ sendMessage                    │  - descarga/transcribe voz   │
       │                               └──────────┬───────────────────┘
       │                                          │ HTTP/A2A
       │                                          ▼
       │                               ┌──────────────────────────────┐
       │                               │  Heroku Eco dyno #1          │
       │                               │  agente-profesor-historia    │
       │                               │  (langgraph dev, A2A nativo)  │
       │                               │  puerto 2025                 │
       │                               └──────────────────────────────┘
       │                                          │
       │                                          ▼
       │                               ┌──────────────────────────────┐
       └───────────────────────────────│  Heroku Eco dyno #2          │
                                       │  agente-profesor-geografia   │
                                       │  (langgraph dev, A2A nativo)  │
                                       │  puerto 2026                 │
                                       └──────────────────────────────┘
```

## 2. Componentes

### 2.1 Gateway (AWS Lambda)

- **Runtime:** Python 3.12 (container image en ECR)
- **Función:** `gateway-telegram`
- **URL:** `https://<function-url>.lambda-url.us-east-1.on.aws/`
- **Endpoints:**
  - `POST /telegram` — webhook de Telegram (verifica secreto, procesa mensaje, responde)
  - `GET /` — health check (responde `{"ok": true}`)
- **Variables de entorno:** `GOOGLE_API_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_SECRET`, `MODELO`, `A2A_HISTORIA_URL`, `A2A_GEOGRAFIA_URL`, `A2A_HISTORIA_ASSISTANT_ID`, `A2A_GEOGRAFIA_ASSISTANT_ID`, `GOOGLE_STT_API_KEY`, `STT_LANGUAGE_CODE`

### 2.2 Agentes (Heroku)

| Agente | App Heroku | Puerto | Grafo | Modelo | Herramienta |
|---|---|---|---|---|---|
| Profesor de Historia | `grupo4-agente-historia` | 2025 | `agente_profesor_historia` | `gemini-3.5-flash-lite` | `consultar_mis_apuntes(tema)` |
| Profesor de Geografía | `grupo4-agente-geografia` | 2026 | `agente_profesor_geografia` | `gemini-3.5-flash-lite` | `consultar_mis_apuntes(tema)` |

- **Servidor:** `langgraph dev --port $PORT --host 0.0.0.0 --no-browser`
- **A2A:** Agent Card en `/.well-known/agent-card.json`, endpoint en `POST /a2a/{assistant_id}`
- **Memoria:** `MemorySaver` por `thread_id` (derivado del `contextId` de A2A)

### 2.3 Router LLM

- **Modelo:** `gemini-3.5-flash-lite`
- **Salida estructurada:** `Decision(ruta: Literal["historia", "geografia", "generica"], motivo: str)`
- **Prompt:** clasifica el mensaje del usuario en una de las 3 rutas.
- **Arista condicional:** el resultado del router dicta a qué agente se llama.

### 2.4 Integración avanzada (Telegram por voz)

- **Detección:** `message.voice` en el update de Telegram.
- **Descarga:** `getFile` + descarga del audio (OGG/OPUS).
- **Transcripción:** Google Cloud Speech-to-Text REST API (`encoding=OGG_OPUS`, `sampleRateHertz=48000`, `languageCode=es-CL`).
- **Procesamiento:** el texto transcrito se procesa por el router y el agente.
- **Respuesta:** texto a Telegram (sin TTS).

---

## 3. Flujo de ejecución

### 3.1 Mensaje de texto

```
1. Usuario envía texto a Telegram
2. Telegram envía update (webhook) a Lambda Function URL
3. Lambda verifica TELEGRAM_SECRET (403 si no coincide)
4. Lambda extrae chat_id y text
5. Router LLM clasifica: historia / geografia / generica
6. Lambda llama al agente correspondiente via A2A (o /runs/wait si A2A requiere auth)
7. Agente procesa y responde
8. Lambda envía respuesta a Telegram (sendMessage)
9. Lambda responde 200 OK a Telegram
```

### 3.2 Mensaje de voz

```
1. Usuario envía audio a Telegram
2. Telegram envía update con voice.file_id
3. Lambda detecta message.voice (sin text)
4. Lambda descarga el audio de Telegram
5. Lambda transcribe el audio con Google STT → texto
6. Router LLM clasifica el texto transcrito
7. Lambda llama al agente correspondiente
8. Agente procesa y responde
9. Lambda envía respuesta (texto) a Telegram
10. Lambda responde 200 OK a Telegram
```

### 3.3 Control de acceso

```
Request sin secreto → 403 Forbidden
Request con secreto incorrecto → 403 Forbidden
Request con secreto correcto → 200 OK + procesamiento
```

---

## 4. Decisiones de diseño

### 4.1 Por qué Heroku para los agentes

- Soporta `langgraph dev` con A2A nativo.
- Despliegue desde panel web (sin CLI).
- HTTPS incluido (*.herokuapp.com).
- Eco dyno: $5/mes por servicio (económico para pruebas).

### 4.2 Por qué AWS Lambda para el gateway

- $0 (free tier: 1M requests/mes).
- Auto-scaling automático.
- Function URL con HTTPS incluido.
- Sin gestión de servidores.

### 4.3 Por qué fallback a /runs/wait

El endpoint A2A en Heroku requiere autenticación (401 "Token A2A inválido o ausente").
El gateway intenta A2A primero y, si falla con 401, cae a `/runs/wait` (LangGraph directo,
sin auth). Esto mantiene A2A como protocolo principal mientras el bot funciona
inmediatamente.

### 4.4 Por qué Google STT para voz

- Una sola llamada HTTP (base64 → texto).
- Acepta OGG/OPUS directamente (formato de Telegram).
- No requiere ffmpeg/pydub ni S3.
- Free tier: 60 min/mes.
- Latencia baja (1-3s).

---

## 5. Variables de entorno

### Gateway (AWS Lambda)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `GOOGLE_API_KEY` | Clave de Google AI Studio (Gemini) | `AIzaSy...` |
| `TELEGRAM_TOKEN` | Token de @BotFather | `9234940533:AAGN...` |
| `TELEGRAM_SECRET` | Secreto del webhook | `431824416ba5...` |
| `MODELO` | Modelo de Gemini | `gemini-3.5-flash-lite` |
| `A2A_HISTORIA_URL` | URL del agente de historia en Heroku | `https://grupo4-agente-historia-XXXX.herokuapp.com` |
| `A2A_GEOGRAFIA_URL` | URL del agente de geografía en Heroku | `https://grupo4-agente-geografia-XXXX.herokuapp.com` |
| `A2A_HISTORIA_ASSISTANT_ID` | UUID del agente de historia | `7f6f2b12-8dc5-5ce2-a178-2db47369944a` |
| `A2A_GEOGRAFIA_ASSISTANT_ID` | UUID del agente de geografía | `bed88ad6-7b48-5518-a206-cb2d85c69cda` |
| `GOOGLE_STT_API_KEY` | API key de Google Cloud Speech-to-Text | `AIzaSy...` |
| `STT_LANGUAGE_CODE` | Idioma de transcripción | `es-CL` |

### Agentes (Heroku)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `GOOGLE_API_KEY` | Clave de Google AI Studio | `AIzaSy...` |
| `MODELO` | Modelo de Gemini | `gemini-3.5-flash-lite` |
| `A2A_HISTORIA_URL` | URL del agente de historia (propia) | `https://grupo4-agente-historia-XXXX.herokuapp.com` |
| `A2A_HISTORIA_GRAPH` | Graph ID del agente | `agente_profesor_historia` |
| `A2A_GEOGRAFIA_URL` | URL del agente de geografía (propia) | `https://grupo4-agente-geografia-XXXX.herokuapp.com` |
| `A2A_GEOGRAFIA_GRAPH` | Graph ID del agente | `agente_profesor_geografia` |

---

## 6. Costos

### Costos fijos (mensual, USD)

| Servicio | Plan | Costo/mes |
|---|---|---|
| AWS Lambda (gateway) | Free tier | $0 |
| Heroku Eco dyno × 2 (agentes) | Eco | $10 |
| Google Gemini API (~100 msg) | Pay-per-token | ~$0.01 |
| Google STT (~100 msg de 10s) | Free tier (60 min/mes) | ~$0.01 |
| Telegram Bot API | Gratuito | $0 |
| **Total** | | **~$10.02** |

### Costos de producción (mayor volumen)

| Escenario | Volumen | Costo/mes |
|---|---|---|
| Producción baja | 100 msg/día | ~$10 (Heroku $10 + Gemini $0.29 + STT $0.01) |
| Producción media | 1.000 msg/día | ~$18 (Heroku $10 + Gemini $2.94 + STT $0.10) |
| Producción alta | 10.000 msg/día | ~$45 (Heroku $10 + Gemini $29.40 + STT $1.00) |

---

## 7. Seguridad

- **Secretos:** nunca en el código ni en el repo. Solo en Config Vars (Heroku) y Lambda env vars.
- **Control de acceso (gateway):** `TELEGRAM_SECRET` validado en cada request del webhook.
- **Control de acceso (API local):** `X-API-Key` validado en el endpoint `/chat`.
- **HTTPS:** obligatorio (Telegram exige endpoint HTTPS; Heroku y Lambda lo proveen).
- **Manejo de errores:** entradas inválidas y fallas del proveedor producen mensajes claros (403, 422, 502).
- **Datos sensibles:** no se muestran en capturas ni en logs.

---

## 8. Monitoreo y observabilidad

- **Lambda:** CloudWatch Logs (`/aws/lambda/gateway-telegram`).
- **Heroku:** View logs en el panel web.
- **Health checks:** `/health` (Lambda), `/ok` (agentes).
- **UptimeRobot:** health checks cada 5 min para evitar sleep de dynos.

---

## 9. Limitaciones conocidas

- Los dynos Eco de Heroku se duermen tras 30 min de inactividad.
- El endpoint A2A en Heroku requiere autenticación; el gateway usa fallback a `/runs/wait`.
- Los agentes no tienen control de acceso en el servidor local (`langgraph dev` sin auth).
- El manejo de errores es básico (mensajes claros pero sin retry ni circuit breaker).
- No hay frontend web en producción; la interacción es vía Telegram.
- La memoria por conversación depende de que el `contextId` (derivado del `chat_id`) se mantenga.
- Los agentes solo responden sobre los temas de sus apuntes (historia/geografía).
- El router puede clasificar incorrectamente mensajes ambiguos (mínimo 13/15 aciertos).
- La transcripción de voz requiere audio claro; ruido reduce la precisión.
- El idioma de transcripción está fijo en `es-CL`.

---

## 10. Documentos relacionados

| Documento | Descripción |
|---|---|
| `OPCION_ELEGIDA.md` | Declaración de la opción de implementación elegida |
| `DEPENDENCIAS_EXTERNAS.md` | Servicios externos requeridos y dependencias de red |
| `VERSIONES.md` | Versiones del entorno |
| `PREPARACION_MANUAL.md` | Cuentas, permisos, vinculación, recursos de pago |
| `CASOS_PRUEBA.md` | 18 casos de prueba (A2A, router, control de acceso, Telegram, voz) |
| `EVIDENCIAS.md` | Evidencias de ejecución con explicación |
| `faltante.md` | Listado de faltantes vs pauta del PDF |
| `deploy/DEPLOYMENT.md` | Guía de despliegue y redespliegue |
| `deploy/README.md` | Guía paso a paso de despliegue |
| `blueprint.md` | Blueprint del agente de historia |
| `agente-profesor-geografia/blueprint.md` | Blueprint del agente de geografía |
| `plan.json` | Plan de trabajo y registro de evidencias |

---

*Arquitectura generada para el proyecto `grupo-4-taller-a2a_no_entregable`.*
*Stack: Telegram → AWS Lambda (gateway) → A2A (HTTP) → Heroku (agentes LangGraph).*
*Integración avanzada: Telegram por voz (Google Cloud Speech-to-Text).*
