# Dependencias externas

## Servicios externos requeridos

El agente necesita conexión a internet y los siguientes servicios externos para
funcionar. **Ejecutar en local no significa trabajar sin internet.**

### 1. Google Gemini API (obligatorio)

- **Servicio:** Google AI Studio (aistudio.google.com)
- **Variable:** `GOOGLE_API_KEY`
- **Modelo:** `gemini-3.5-flash-lite` (configurable con `MODELO`)
- **Costo:** ~$0.10 por 1M tokens de entrada, ~$0.40 por 1M tokens de salida
- **Cuota:** la clave debe tener cuota disponible; si se agota, el agente falla
  con error `402 RESOURCE_EXHAUSTED`
- **Cómo obtener:** https://aistudio.google.com/app/apikey

### 2. Google Cloud Speech-to-Text (solo para integración avanzada por voz)

- **Servicio:** Google Cloud Console (console.cloud.google.com)
- **Variable:** `GOOGLE_STT_API_KEY`
- **Costo:** Free tier 60 min/mes. Después $0.006 por 15s ($0.024/min)
- **Cómo obtener:** Habilitar "Cloud Speech-to-Text API" en un proyecto de Google Cloud → Create API Key
- **Formato de audio:** OGG/OPUS (el que envía Telegram) — no requiere conversión
- **Idioma:** `es-CL` (configurable con `STT_LANGUAGE_CODE`) → Create API Key

### 2. Telegram Bot API (solo en producción/despliegue)

- **Servicio:** Telegram (api.telegram.org)
- **Variables:** `TELEGRAM_TOKEN`, `TELEGRAM_SECRET`, `PUBLIC_URL`
- **Costo:** gratuito
- **Cómo obtener:** hablar con @BotFather en Telegram → `/newbot`
- **Dependencia:** requiere HTTPS (el webhook debe apuntar a una URL HTTPS)

### 3. Heroku (solo en producción/despliegue)

- **Servicio:** Heroku (dashboard.heroku.com)
- **Costo:** Eco dyno ~$5/mes por servicio (2 agentes = $10/mes)
- **Dependencia:** requiere cuenta verificada con tarjeta de crédito
- **Alternativa:** Render (free tier con sleep) o AWS (EC2 free tier)

### 4. AWS (solo para el gateway en producción)

- **Servicio:** AWS Lambda + ECR
- **Costo:** $0 (free tier: 1M requests/mes, 400k GB-s)
- **Dependencia:** requiere cuenta AWS con IAM configurado

## Dependencias de software (local)

| Dependencia | Versión | Propósito |
|---|---|---|
| Python | 3.11+ (probado con 3.12.10) | Runtime |
| langgraph | >=1.2 | Orquestación de agentes |
| langchain | >=1.3 | Framework de agentes |
| langchain-google-genai | >=4.3 | Integración con Gemini |
| langgraph-cli[inmem] | >=0.4 | Servidor local A2A |
| langgraph-api | >=0.15.1 | API del servidor |
| pydantic | >=2.7 | Validación de datos |
| python-dotenv | >=1.0 | Carga de variables de entorno |
| httpx | >=0.27 | Cliente HTTP (A2A, Telegram) |
| pytest | >=8 | Pruebas |
| nbformat | >=5.10 | Notebooks |
| ipykernel | >=6 | Kernel de Jupyter |
| colorama | (incluido) | Colores en terminal (Windows) |

## Dependencias de red

- **Internet:** requerido para Google Gemini API y (en producción) Telegram/Heroku/AWS.
- **Puertos locales:** 2025 (agente historia), 2026 (agente geografía).
- **HTTPS:** requerido en producción para Telegram webhook.

## Lo que NO necesita internet

- La instalación de dependencias (`pip install`) requiere internet la primera vez.
- Una vez instalado, el agente necesita internet para llamar a Gemini API.
- No hay modo offline: el agente no funciona sin conexión a Google AI Studio.
