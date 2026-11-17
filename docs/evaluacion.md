# Evaluación de producción — Agentes A2A vía Telegram

Documento de evaluación para poner en producción los dos agentes del taller A2A
(`agente-profesor-historia` y `agente-profesor-geografia`) exponiéndolos por
Telegram, siguiendo la arquitectura y las prácticas de la **Curso 2 · Sesión 2
· Router, API y despliegue** (ejemplo: `?key=KEY-518D6797`).

---

## 1. Objetivo y alcance

- **Objetivo:** que un usuario final pueda escribirle al bot de Telegram y
  recibir respuestas de los agentes profesores de Historia y Geografía,
  enrutadas automáticamente según la consulta, con memoria por conversación.
- **Alcance:** despliegue de los 2 agentes LangGraph (A2A nativo) + 1 gateway
  FastAPI (router + webhook de Telegram) + integración GitHub/Heroku.
- **Fuera de alcance:** n8n, Neo4j, Redis, MCP Shopify, LangSmith (se mencionan
  como siguientes sesiones).

## 2. Inventario de componentes

| Componente | Proyecto / Puerto local | Modelo | Herramienta | Estado |
|---|---|---|---|---|
| Agente Profesor de Historia | `agente-profesor-historia` · 2025 | `gemini-3.5-flash-lite` | `consultar_mis_apuntes(tema)` | ReAct, A2A nativo |
| Agente Profesor de Geografía | `agente-profesor-geografia` · 2026 | `gemini-3.5-flash-lite` | `consultar_mis_apuntes(tema)` | ReAct, A2A nativo |
| Gateway / Router | FastAPI `api/app.py` (nuevo) | `gemini-3.5-flash-lite` | decisión estructurada | clasifica historia vs geografía |
| Bot de Telegram | @BotFather | — | webhook HTTPS | entrada/salida al usuario |

- Ambos agentes exponen su **Agent Card** en `/.well-known/agent-card.json` y su
  endpoint en `POST /a2a/{assistant_id}` (message/send, message/stream).
- El `contextId` de A2A se convierte en `thread_id`: la memoria por
  conversación viene gratis con `MemorySaver`/checkpointer.

## 3. Arquitectura objetivo (producción)

```
Usuario (Telegram)
   │  mensaje
   ▼
Telegram Bot API  ──webhook HTTPS──►  Gateway FastAPI (Heroku)
                                       │
                                       ├── GET  /health
                                       ├── POST /chat   (pruebas)
                                       └── POST /telegram (webhook)
                                              │
                                              ▼
                                       Grafo LangGraph "router"
                                       (decisión: historia | geografia | generica)
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      ▼                       ▼                       ▼
              A2A Client (httpx)      A2A Client (httpx)        respuesta genérica
                      │                       │
                      ▼                       ▼
          Agente Historia (Heroku)   Agente Geografía (Heroku)
          POST /a2a/{assistant_id}   POST /a2a/{assistant_id}
                      │                       │
                      └──────────► respuesta ◄──┘
                                       │
                                       ▼
                              Telegram sendMessage (chat_id, text)
```

**Claves de la arquitectura del ejemplo (Sesión 2):**
- El router es el único que piensa hoy; los nodos destino pueden ser cascarones
  que se llenan después.
- Cada capa se prueba antes de la siguiente: router en terminal → batería de
  casos → API local con Swagger/Bruno → GitHub → Heroku (`/health`, `/docs`) →
  Telegram.
- Las claves nunca viajan en el código: `.env` en local, `heroku config` en
  servidor. El repo lleva solo `.env.example`.

## 4. Tecnologías (del ejemplo)

| Capa | Tecnología | Notas |
|---|---|---|
| Lenguaje / runtime | Python 3.12 | `.python-version` con `3.12` |
| Agentes | LangGraph (`langgraph dev`) + LangChain 1.x + Gemini | A2A nativo |
| API | FastAPI + Uvicorn | `/health`, `/chat`, `/telegram`, `/docs` |
| Cliente HTTP | httpx | para A2A y para Telegram `sendMessage` |
| Validación | Pydantic | `ChatRequest`, `ChatResponse`, `Decision` |
| Despliegue | Heroku (panel web) o Render | Procfile + requirements.txt |
| Control de versiones | Git + GitHub | repo privado del grupo |
| Mensajería | Telegram Bot API (webhook, sin librerías de bot) | solo 2 llamadas HTTP |
| Observabilidad | Heroku logs (`--tail`) / Render logs | monitoreo básico |

## 5. Requisitos de producción

### 5.1 Infraestructura mínima (3 servicios)

1. **Gateway FastAPI** (router + webhook Telegram) — 1 dyno/servicio.
2. **Agente Historia** — 1 dyno/servicio (`langgraph dev --port $PORT` o
   LangGraph Platform).
3. **Agente Geografía** — 1 dyno/servicio.

> Alternativa de bajo costo: un solo servicio que levanta los 3 procesos con un
> `Procfile` multi-process (Heroku no lo soporta en un dyno; usar Render
> "Background Worker" o un contenedor). Para el curso se recomienda 3 servicios
> separados para mantener el aislamiento A2A.

### 5.2 Variables de entorno (`.env.example` completo)

```
# Modelo
GOOGLE_API_KEY=
MODELO=gemini-3.5-flash-lite

# Agentes A2A (URLs públicas tras el despliegue)
A2A_HISTORIA_URL=https://<app-historia>.herokuapp.com
A2A_HISTORIA_GRAPH=agente_profesor_historia
A2A_GEOGRAFIA_URL=https://<app-geografia>.herokuapp.com
A2A_GEOGRAFIA_GRAPH=agente_profesor_geografia

# Telegram
TELEGRAM_TOKEN=          # token de @BotFather
TELEGRAM_SECRET=cambiame # secreto del webhook
PUBLIC_URL=https://<app-gateway>.herokuapp.com

# Opcionales
PORT=8000
```

### 5.3 Archivos que Heroku/Render necesitan en el repo

- `Procfile`: `web: uvicorn api.app:app --host 0.0.0.0 --port $PORT`
- `.python-version`: `3.12`
- `requirements.txt` completo (incluye `langgraph`, `langchain`,
  `langchain-google-genai`, `fastapi`, `uvicorn`, `httpx`, `pydantic`,
  `python-dotenv`, `pytest`, `colorama`)
- `.gitignore` con `.env`, `.venv/`, `__pycache__/`, `.langgraph_api/`,
  `.pytest_cache/`, `*.egg-info/`

## 6. Plan de despliegue paso a paso (basado en la Sesión 2)

1. **Entorno:** venv, `.env`, `AGENTS.md`, `Procfile`, `.python-version`,
   `requirements.txt`, `.gitignore`.
2. **Grafo y API:** crear el agente `router` con salida estructurada
   (`Literal["historia", "geografia", "generica"]`), batería de casos
   (`tests/casos_router.json` + `scripts/test_router.py`), FastAPI con
   `/health`, `/chat`, `/telegram`, Swagger completo, colección Bruno.
3. **GitHub:** `git init` → `add` → `commit` → push al repo vacío (verificar
   que `.env` no aparezca en `git status`).
4. **Heroku web (panel):** New → Create app → Deploy → GitHub (conectar repo) →
   Settings → Config Vars (una por variable) → Deploy Branch (main) → Open app
   → probar `/health` y `/docs`.
5. **Telegram:** crear bot con @BotFather → token → `heroku config:set
   TELEGRAM_TOKEN ... TELEGRAM_SECRET ...` → commit/push →
   `scripts/set_webhook.py` → `scripts/webhook_info.py` → escribir los 6
   mensajes de prueba → verificar en `heroku logs --tail`.

   - Prueba previa sin desplegar: túnel `cloudflared --url http://localhost:8000`
     y usar esa URL como `PUBLIC_URL`.

## 7. Integración A2A en producción

- El gateway descubre el `assistant_id` de cada agente con
  `POST /assistants/search {"graph_id": "agente_profesor_historia"}` (y el de
  geografía) contra la URL pública del agente.
- Cada llamada A2A usa `POST /a2a/{assistant_id}` con `message/send` (o
  `message/stream`), pasando `contextId` = `chat_id` de Telegram para mantener
  la memoria por conversación.
- El gateway debe reintentar con backoff y devolver un mensaje amable si un
  agente no responde (timeout 30 s).

## 8. Seguridad

- Secretos solo en Config Vars / `.env` local; nunca en el repo.
- Verificar la cabecera `X-Telegram-Bot-Api-Secret-Token` contra
  `TELEGRAM_SECRET` en `/telegram`; si no coincide, `403`.
- `/chat` opcionalmente protegido con `X-API-Key`.
- No devolver claves ni stack traces al cliente; errores → `502` con mensaje
  claro y detalle solo en logs.
- HTTPS obligatorio (Telegram exige endpoint HTTPS; Heroku/Render lo proveen).
- Validar el body con Pydantic; `422` si falta `texto`.

## 9. Observabilidad y monitoreo

- Logs de Heroku (`heroku logs --tail`) / Render logs para ver al router
  decidir y a los agentes responder.
- `/health` para health checks (UptimeRobot o similar, cada 5 min) — evita
  que los dynos free se duerman.
- Registrar por request: ruta elegida, agente destino, latencia, tokens usados,
  costo estimado.
- Opcional: LangSmith (free tier 5k traces/mes) para trazas del grafo.

## 10. Costos

### 10.1 Costos fijos de infraestructura (mensual, USD)

| Servicio | Plan | Costo/mes | Notas |
|---|---|---|---|
| Heroku Gateway | Eco dyno | ~5 | 1 dyno |
| Heroku Agente Historia | Eco dyno | ~5 | 1 dyno |
| Heroku Agente Geografía | Eco dyno | ~5 | 1 dyno |
| **Subtotal hosting** | | **~15** | 3 dynos Eco |
| Render (alternativa) | Starter | ~7/servicio | ~21 para 3 servicios |
| Telegram Bot API | — | 0 | gratuito |
| GitHub (repo privado) | — | 0 | gratuito |
| HTTPS (*.herokuapp.com) | — | 0 | incluido |
| LangSmith (opcional) | Free tier | 0 | 5k traces/mes |

> Heroku no tiene plan gratuito. Para pruebas, Render ofrece free tier (con sleep)
> y el mismo `Procfile`. Lo que debe estar listo en cualquier caso: `Procfile`,
> `.python-version`, `requirements.txt` completo y que arranque en local con
> `PORT=8000`.

### 10.2 Costos variables — Google Gemini (gemini-3.5-flash-lite)

Precios de referencia (USD por 1M tokens):

| Modelo | Entrada | Salida |
|---|---|---|
| `gemini-3.5-flash-lite` | 0.10 | 0.40 |

Estimación por mensaje (router + 1 agente): ~500 tokens de entrada y ~200 de
salida → ~700 tokens/mensaje.

| Volumen (mensajes/día) | Tokens/mes | Costo Gemini/mes (USD) |
|---|---|---|
| 100 (bajo) | 2.1M | ~0.29 |
| 1.000 (medio) | 21M | ~2.94 |
| 10.000 (alto) | 210M | ~29.40 |

> Si se escala a `gemini-3.6-flash` (0.30 / 2.50 USD por 1M tokens) el costo
> se multiplica ~3-6×. Recomendado mantener `flash-lite` para el router y los
> agentes, y reservar el modelo fuerte solo para tareas complejas (patrón
> cheap-first de la Demo 11).

### 10.3 Costo total estimado por escenario (mensual, USD)

| Escenario | Volumen | Hosting | Gemini | Total |
|---|---|---|---|---|
| Desarrollo / pruebas | < 50 msg/día | 0 (Render free) | < 0.15 | **< 1** |
| Producción baja | 100 msg/día | 15 (Heroku 3 dynos) | 0.29 | **~15.3** |
| Producción media | 1.000 msg/día | 15 | 2.94 | **~17.9** |
| Producción alta | 10.000 msg/día | 15 (o escalar) | 29.40 | **~44.4** |

> Nota: los dynos Eco de Heroku se duermen tras 30 min de inactividad; para
> producción real considerar dynos Standard (~25 USD/mes cada uno) o Render
> Starter. El free tier de Render duerme a los 15 min.

## 11. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Cuota de Gemini agotada (402) | Monitorear uso; rotar clave; cachear respuestas; cheap-first |
| Agente A2A no responde / timeout | Reintentos con backoff; mensaje amable; fallback a respuesta genérica |
| Webhook mal configurado | `set_webhook.py` + `webhook_info.py`; verificar HTTPS y secreto |
| Fuga de claves en el repo | `.gitignore` + revisión de `git status` antes del commit |
| Dyno dormido (free tier) | Health checks cada 5 min o plan pagado |
| Memoria por conversación perdida | `thread_id = chat_id`; checkpointer persistente (Postgres) en producción |
| Router enruta mal | Batería de 15 casos; mínimo 13/15; temperatura 0 en el router |

## 12. Checklist de go-live

- [ ] `.env.example` completo y verificado contra `os.environ`/`os.getenv`
- [ ] `Procfile`, `.python-version`, `requirements.txt` en el repo
- [ ] `.gitignore` excluye `.env`, `.venv/`, `__pycache__/`, `.langgraph_api/`
- [ ] `git status` confirma que `.env` no está trackeado
- [ ] Repo privado en GitHub con primer commit `router + api + telegram`
- [ ] App Heroku/Render creada y conectada al repo
- [ ] Config Vars cargadas (GOOGLE_API_KEY, MODELO, A2A_*, TELEGRAM_*, PUBLIC_URL)
- [ ] Deploy Branch (main) exitoso; `/health` y `/docs` responden
- [ ] `scripts/set_webhook.py` ejecutado; `webhook_info.py` confirma webhook
- [ ] Prueba de los 6 mensajes del prompt 2 verificada en logs
- [ ] Agentes A2A desplegados y descubiertos (assistant_id obtenido)
- [ ] Health checks configurados
- [ ] Costos monitoreados (Gemini + hosting)

## 13. Notas finales

- El bot de Telegram no requiere librerías de bot: solo 2 llamadas HTTP
  (`setWebhook` y `sendMessage`).
- Para probar antes de desplegar, usar túnel `cloudflared --url http://localhost:8000`.
- Los nodos destino (preventa/postventa) del ejemplo son cascarones; en este
  proyecto los nodos destino llaman a los agentes A2A reales (Historia /
  Geografía), que ya tienen su propia lógica ReAct y herramientas.

---
*Generado a partir de la Curso 2 · Sesión 2 · Router, API y despliegue y del
inventario del proyecto `grupo-4-taller-a2a_no_entregable`.*
