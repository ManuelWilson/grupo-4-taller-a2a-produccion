# Guía de despliegue — Agentes A2A vía Telegram

## Arquitectura

```
Telegram → AWS Lambda (gateway) → A2A (HTTP) → Agentes en Heroku (LangGraph)
```

## Estructura

```
deploy/
├── gateway/          # Lambda Function URL (webhook + router)
│   ├── lambda_handler.py
│   ├── Dockerfile
│   └── requirements.txt
├── agents/           # Agentes A2A (Heroku)
│   ├── historia/
│   │   ├── Procfile
│   │   ├── .python-version
│   │   └── requirements.txt
│   └── geografia/
│       ├── Procfile
│       ├── .python-version
│       └── requirements.txt
├── scripts/          # Utilidades Telegram
│   ├── set_webhook.py
│   └── webhook_info.py
└── README.md
```

## Pasos de despliegue

### 1. Desplegar los agentes en Heroku

Para cada agente (historia y geografía):

1. Crear app en Heroku: `grupo4-agente-historia` y `grupo4-agente-geografia`.
2. Conectar el repositorio de GitHub.
3. Config Vars:
   - `GOOGLE_API_KEY` = tu clave de Google AI Studio
   - `MODELO` = `gemini-3.5-flash-lite`
   - `PORT` = (Heroku lo asigna automáticamente)
4. Deploy Branch (main).
5. Verificar: `https://<app>.herokuapp.com/ok` y `/.well-known/agent-card.json?assistant_id=<uuid>`.

Obtener el `assistant_id` de cada agente:
```bash
curl -X POST https://<app>.herokuapp.com/assistants/search \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "agente_profesor_historia"}'
```

### 2. Desplegar el gateway en AWS Lambda

1. Crear imagen Docker:
   ```bash
   cd deploy/gateway
   docker build -t gateway-lambda .
   ```
2. Subir a ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   docker tag gateway-lambda:latest <account>.dkr.ecr.us-east-1.amazonaws.com/gateway-lambda:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/gateway-lambda:latest
   ```
3. Crear Lambda function desde la imagen.
4. Crear Function URL (Auth: NONE, o con IAM si prefieres).
5. Configurar variables de entorno en Lambda:
   - `GOOGLE_API_KEY`
   - `TELEGRAM_TOKEN`
   - `TELEGRAM_SECRET`
   - `MODELO`
   - `A2A_HISTORIA_URL` = URL del agente historia en Heroku
   - `A2A_GEOGRAFIA_URL` = URL del agente geografía en Heroku
   - `A2A_HISTORIA_ASSISTANT_ID` = assistant_id del agente historia
   - `A2A_GEOGRAFIA_ASSISTANT_ID` = assistant_id del agente geografía
6. Configurar timeout: 30–60 segundos.

### 3. Configurar el webhook de Telegram

```bash
export TELEGRAM_TOKEN="tu_token"
export TELEGRAM_SECRET="tu_secreto"
export PUBLIC_URL="https://<function-url>.lambda-url.us-east-1.on.aws"

python deploy/scripts/set_webhook.py
python deploy/scripts/webhook_info.py
```

### 4. Probar

Escribir al bot en Telegram los 6 mensajes de prueba y verificar en CloudWatch Logs (Lambda) y Heroku logs.

## Costos (prueba mínima, ≤ 100 iteraciones)

| Servicio | Costo/mes |
|---|---|
| AWS Lambda (gateway) | $0 (free tier) |
| Heroku Eco dyno × 2 (agentes) | $10 |
| Google Gemini API (100 msg) | ~$0.01 |
| Telegram Bot API | $0 |
| **Total** | **~$10.01** |

## Notas

- Los dynos Eco de Heroku se duermen tras 30 min de inactividad.
- Lambda Function URL tiene timeout máximo de 15 min (suficiente para Gemini).
- Para producción real, considerar Heroku Basic ($7/dyno) o AWS Fargate.
