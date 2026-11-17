# Requisitos para levantar en producción

Lista de lo que necesito que me entregues para poder levantar los agentes A2A
(`agente-profesor-historia` y `agente-profesor-geografia`) en producción vía
Telegram, siguiendo la arquitectura de la Curso 2 · Sesión 2.

---

## 1. Cuentas y accesos (obligatorios)

- [ ] **GitHub:** cuenta con permiso para crear un repositorio privado del grupo.
- [ ] **Heroku** (o **Render**): cuenta con método de pago (Heroku no tiene plan
      gratuito; Render tiene free tier con sleep). Indica cuál eliges.
- [ ] **Google AI Studio:** `GOOGLE_API_KEY` con cuota disponible (no agotada).
- [ ] **Telegram:** cuenta para crear el bot con @BotFather.

## 2. Secretos y variables (a completar)

Entrega estos valores (nunca los subas al repo, van en Config Vars / `.env`):

| Variable | Quién la da | Notas |
|---|---|---|
| `GOOGLE_API_KEY` | Google AI Studio | Con cuota suficiente |
| `MODELO` | Decisión del grupo | Por defecto `gemini-3.5-flash-lite` |
| `TELEGRAM_TOKEN` | @BotFather (`/newbot`) | Token del bot |
| `TELEGRAM_SECRET` | Tú lo eliges | Cadena aleatoria, igual en ambos lados |
| `PUBLIC_URL` | Heroku/Render | `https://<app>.herokuapp.com` |
| `A2A_HISTORIA_URL` | Tras desplegar agente historia | URL pública del servicio |
| `A2A_GEOGRAFIA_URL` | Tras desplegar agente geografía | URL pública del servicio |

## 3. Decisiones de infraestructura

- [ ] **Proveedor de hosting:** Heroku (Eco ~5 USD/dyno/mes) o Render (free/starter).
- [ ] **Nombre de la app Gateway** (debe ser único en Heroku): `________________`
- [ ] **Región:** US o EU.
- [ ] **Presupuesto mensual máximo aceptable:** `______ USD`.
- [ ] **¿Usar LangSmith** para trazas? (free tier 5k traces/mes) Sí / No.

## 4. Entregables de código (debes proporcionarlos)

- [ ] **Repositorio GitHub** (privado) con:
  - `Procfile`: `web: uvicorn api.app:app --host 0.0.0.0 --port $PORT`
  - `.python-version`: `3.12`
  - `requirements.txt` completo (langgraph, langchain, langchain-google-genai,
    fastapi, uvicorn, httpx, pydantic, python-dotenv, pytest, colorama)
  - `.gitignore` (`.env`, `.venv/`, `__pycache__/`, `.langgraph_api/`, etc.)
  - `.env.example` con **todas** las variables del punto 2.
- [ ] **Código del gateway** (`api/app.py`) con `/health`, `/chat`, `/telegram`,
      Swagger completo y manejo de errores.
- [ ] **Agente router** (`src/router/`) con salida estructurada y las 3 rutas
      (historia, geografia, generica).
- [ ] **Scripts:** `scripts/set_webhook.py`, `scripts/webhook_info.py`,
      `scripts/test_router.py`.
- [ ] **Pruebas:** `tests/casos_router.json` (15 casos) y `tests/test_router.py`
      (mínimo 13/15 aciertos).
- [ ] **Colección Bruno** (`bruno/`) con health, chat-preventa, chat-postventa,
      chat-generica.
- [ ] **README.md** con comandos de ejecución local y despliegue.

## 5. Entregables de los agentes A2A

- [ ] **Proyectos de los agentes** (historia y geografía) con `langgraph.json`,
      `src/.../graph.py`, `prompts.py`, `herramientas.py`.
- [ ] **URLs públicas** de ambos agentes tras el despliegue.
- [ ] **assistant_id** de cada agente (obtenido con
      `POST /assistants/search {"graph_id": "..."}`).
- [ ] **Evidencia de funcionamiento:** captura del servidor en puerto 2025
      (como `evidencia-captura-terminal-2025.png`) y logs de prueba.

## 6. Validaciones que debo verificar antes del go-live

- [ ] `git status` confirma que `.env` **no** está trackeado.
- [ ] `/health` responde `{"ok": true, "modelo": "..."}` en local y en Heroku.
- [ ] `/docs` (Swagger) permite probar `/chat` con "Try it out".
- [ ] Batería de router: ≥ 13/15 aciertos.
- [ ] `set_webhook.py` ejecutado y `webhook_info.py` confirma webhook HTTPS
      apuntando a `/telegram`.
- [ ] Los 6 mensajes de prueba del prompt 2 verificados en `heroku logs --tail`.
- [ ] Health checks configurados (UptimeRobot o similar) para evitar sleep.

## 7. Formato de entrega

Entrega todo en uno de estos formatos:

- **Opción A:** Repositorio GitHub privado compartido conmigo (URL + acceso).
- **Opción B:** Archivo `.zip` (`grupo-4-taller-a2a.zip`) con la estructura del
  proyecto (excluyendo `.venv/`, `.env`, `.langgraph_api/`, `__pycache__/`,
  `*.egg-info/`).

Incluye también:
- `documento-entrega.ipynb` y su log.
- Blueprints de ambos agentes.
- Plan de trabajo (`plan.json`).
- Captura de evidencia del servidor.

## 8. Contacto y soporte

- **Responsable del despliegue:** `________________`
- **Canal de comunicación:** `________________`
- **Ventana de mantenimiento acordada:** `________________`

---

*Una vez entregues estos elementos, puedo proceder con el despliegue paso a paso
siguiendo el plan de `evaluacion.md`.*
