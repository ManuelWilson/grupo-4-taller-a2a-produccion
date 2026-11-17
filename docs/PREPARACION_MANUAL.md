# Preparación manual

## Cuentas necesarias

### 1. Google AI Studio (obligatorio)

- **URL:** https://aistudio.google.com/app/apikey
- **Qué hacer:** crear una API key con cuota disponible.
- **Costo:** Gemini `gemini-3.5-flash-lite` cobra por token (~$0.10/1M entrada, ~$0.40/1M salida).
- **Variable:** `GOOGLE_API_KEY`
- **Permisos:** la clave debe tener acceso al modelo `gemini-3.5-flash-lite`.

### 2. Telegram (solo para despliegue en producción)

- **URL:** https://t.me/BotFather
- **Qué hacer:** crear un bot con `/newbot`, elegir nombre y username (debe terminar en `bot`).
- **Costo:** gratuito.
- **Variables:** `TELEGRAM_TOKEN`, `TELEGRAM_SECRET`.
- **Permisos:** el bot debe tener permiso para enviar mensajes.

### 3. Heroku (solo para despliegue en producción)

- **URL:** https://dashboard.heroku.com
- **Qué hacer:** crear cuenta, verificar con tarjeta de crédito (no se cobra si no se usa).
- **Costo:** Eco dyno ~$5/mes por servicio (2 agentes = $10/mes).
- **Variables:** `HEROKU_API_KEY` (solo para CLI/automatización).

### 4. AWS (solo para el gateway en producción)

- **URL:** https://console.aws.amazon.com
- **Qué hacer:** crear cuenta, configurar IAM user con permisos para Lambda, ECR, IAM.
- **Costo:** $0 (free tier: 1M requests/mes, 400k GB-s).
- **Variables:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_ACCOUNT_ID`.

## Aplicaciones y permisos

### Agentes (local)

- Cada agente necesita su propio entorno virtual (`.venv`).
- El entorno virtual debe tener Python 3.11+.
- Las dependencias se instalan con `pip install -r requirements-core.txt` y `pip install -e .`.
- El servidor se levanta con `langgraph dev --port 2025` (historia) y `--port 2026` (geografía).

### Agentes (producción en Heroku)

- Cada agente es una app separada en Heroku.
- Config Vars: `GOOGLE_API_KEY`, `MODELO`, `A2A_HISTORIA_URL` (o `A2A_GEOGRAFIA_URL`), `A2A_HISTORIA_GRAPH` (o `A2A_GEOGRAFIA_GRAPH`).
- Procfile: `web: python -m langgraph_cli dev --port $PORT --host 0.0.0.0 --no-browser`
- `.python-version`: `3.12`

### Gateway (producción en AWS Lambda)

- La imagen Docker se construye con `deploy/gateway/Dockerfile`.
- Se sube a ECR y se despliega como Lambda function.
- Config Vars: `GOOGLE_API_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_SECRET`, `MODELO`, `A2A_HISTORIA_URL`, `A2A_GEOGRAFIA_URL`, `A2A_HISTORIA_ASSISTANT_ID`, `A2A_GEOGRAFIA_ASSISTANT_ID`.
- Function URL con AuthType NONE (protegida por secreto de Telegram).

## Vinculación del dispositivo

### Telegram

1. Crear bot con @BotFather (`/newbot`).
2. Copiar el token (`TELEGRAM_TOKEN`).
3. Generar un secreto aleatorio (`TELEGRAM_SECRET`).
4. Configurar el webhook con `setWebhook` apuntando a la URL del gateway.
5. Verificar con `getWebhookInfo`.

### Heroku

1. Crear app en el panel web.
2. Conectar repositorio de GitHub.
3. Configurar Config Vars.
4. Deploy Branch.

### AWS

1. Crear repositorio ECR.
2. Construir imagen Docker.
3. Subir a ECR.
4. Crear Lambda function.
5. Crear Function URL.
6. Configurar variables de entorno.

## Recursos de pago

| Recurso | Costo | Cómo evitar cargos inesperados |
|---|---|---|
| Google Gemini API | ~$0.10/1M tokens entrada, ~$0.40/1M tokens salida | Usar `gemini-3.5-flash-lite` (el más barato). Monitorear uso en Google AI Studio. |
| Heroku Eco dyno | $5/mes por servicio | Usar Render free tier (con sleep) para pruebas. |
| AWS Lambda | $0 (free tier) | Configurar timeout bajo (30s) y memoria mínima (512MB). |
| Telegram Bot API | $0 | Gratuito. |
| GitHub | $0 | Repos privados gratuitos. |

## Cómo evitar acciones accidentales

1. **No subir `.env` al repositorio:** verificar con `git status` antes de cada commit.
2. **Usar datos de prueba:** no enviar mensajes reales a usuarios reales durante pruebas.
3. **Controlar costos de Gemini:** monitorear el uso en Google AI Studio; establecer límites de presupuesto.
4. **Detener procesos:** usar `Ctrl+C` para detener `langgraph dev`; en Heroku, escalar a 0 dynos.
5. **No compartir tokens:** revocar tokens comprometidos inmediatamente.

## Cómo detener los procesos

### Local
```powershell
# Detener los servidores
Ctrl+C en cada terminal donde corre langgraph dev
```

### Heroku
```powershell
# Escalar a 0 dynos (detiene el servicio)
heroku ps:scale web=0 --app grupo4-agente-historia
heroku ps:scale web=0 --app grupo4-agente-geografia
```

### AWS Lambda
- La Lambda no se "detiene"; solo se invoca cuando recibe requests.
- Para deshabilitar: eliminar la Function URL o la función.

### Telegram
- Eliminar el webhook:
  ```powershell
  python -c "import urllib.request, json, os; [os.environ.update({k:v}) for k,v in [l.strip().split('=',1) for l in open('.env') if '=' in l and not l.startswith('#')]]; import urllib.request; urllib.request.urlopen(f'https://api.telegram.org/bot{os.environ[\"TELEGRAM_TOKEN\"]}/deleteWebhook?drop_pending_updates=true')"
  ```
