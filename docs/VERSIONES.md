# Versiones del entorno

## Runtime

| Componente | Versión | Notas |
|---|---|---|
| Python | 3.12.10 | Probado con 3.12.10 (py -3.12) |
| pip | 24.0+ | Gestor de paquetes |

## Dependencias Python (familia LangChain 1.x)

| Paquete | Versión mínima | Versión probada | Propósito |
|---|---|---|---|
| langgraph | >=1.2 | 1.2.x | Orquestación de agentes (grafo ReAct) |
| langchain | >=1.3 | 1.3.x | Framework de agentes |
| langchain-core | >=1.6 | 1.6.x | Núcleo de LangChain |
| langchain-google-genai | >=4.3 | 4.3.x | Integración con Google Gemini |
| langgraph-cli[inmem] | >=0.4 | 0.4.x | Servidor local (`langgraph dev`) |
| langgraph-api | >=0.15.1 | 0.15.x | API del servidor LangGraph |
| pydantic | >=2.7 | 2.7+ | Validación de datos y salida estructurada |
| python-dotenv | >=1.0 | 1.0+ | Carga de variables de entorno |
| httpx | >=0.27 | 0.27+ | Cliente HTTP (A2A, Telegram) |
| pytest | >=8 | 8+ | Pruebas unitarias |
| nbformat | >=5.10 | 5.10+ | Notebooks Jupyter |
| ipykernel | >=6 | 6+ | Kernel de Jupyter |
| colorama | (incluido en requirements-core) | — | Colores en terminal (Windows) |

## Modelo de IA

| Componente | Versión | Notas |
|---|---|---|
| Google Gemini | gemini-3.5-flash-lite | Configurable con `MODELO` en `.env` |
| Google Generative AI SDK | >=4.3 (langchain-google-genai) | Cliente Python para Gemini |
| Google Cloud Speech-to-Text | API v1 | Para transcripción de audio (Telegram por voz) |
| Idioma STT | es-CL | Configurable con `STT_LANGUAGE_CODE` |

## Servicios externos

| Servicio | Versión/API | Notas |
|---|---|---|
| Google AI Studio | API v1 | Requiere `GOOGLE_API_KEY` |
| Telegram Bot API | v6.x | Requiere `TELEGRAM_TOKEN` y `TELEGRAM_SECRET` |
| Heroku | Eco dyno | $5/mes por servicio |
| AWS Lambda | Python 3.12 runtime | Gateway con Function URL |

## Sistema operativo

| Componente | Versión | Notas |
|---|---|---|
| Windows | 10/11 | Probado en Windows 11 |
| PowerShell | 5.1+ | Para comandos de instalación |

## Cómo generar esta lista

Para regenerar la lista de versiones instaladas:

```powershell
cd agente-profesor-historia
.venv\Scripts\python.exe -m pip freeze > requirements-installed.txt
```

O para ver las versiones de los paquetes principales:

```powershell
.venv\Scripts\python.exe -c "import langgraph, langchain, langchain_google_genai, pydantic; print('langgraph', langgraph.__version__); print('langchain', langchain.__version__); print('langchain-google-genai', langchain_google_genai.__version__); print('pydantic', pydantic.VERSION)"
```
