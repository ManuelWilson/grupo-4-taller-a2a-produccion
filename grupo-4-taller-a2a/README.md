# Taller A2A — Agentes Profesores de Historia y Geografía

Proyecto del **Taller práctico · A2A: mi agente especialista habla por A2A**.
Dos agentes conversacionales construidos con LangChain 1.x + LangGraph y Google Gemini,
expuestos por **A2A nativo** con `langgraph dev`, que colaboran para resolver un reto conjunto.

**Autoría:** colectiva del **Grupo 4** — Karen García, Sebastian Garrido, Leonel Carrasco y
Manuel Wilson. Los cuatro integrantes son coautores de ambos agentes y del taller.

## Agentes

| Agente | Grafo | Puerto | Proyecto |
|---|---|---|---|
| Agente Profesor de Historia | `agente_profesor_historia` | 2025 | `agente-profesor-historia/` |
| Agente Profesor de Geografia | `agente_profesor_geografia` | 2026 | `agente-profesor-geografia/` |

Los dos se descubren por A2A, un supervisor elige a cuál derivar cada consulta y el diálogo
**A propone → B mejora → A integra** queda registrado en el notebook de pruebas.

## Entregables

| Archivo | Contenido |
|---|---|
| `documento-entrega.ipynb` | Identificación, blueprints, evidencias, ajustes, reto y comentarios |
| `documento-entrega.run.log` | Salida íntegra del documento |
| `blueprint.md` | Blueprint del agente de historia |
| `agente-profesor-geografia/blueprint.md` | Blueprint del agente de geografía |
| `agente-profesor-historia/notebooks/a2a-test.ipynb` | Notebook ejecutado: pruebas, A2A, supervisor, diálogo y checklist |
| `agente-profesor-historia/notebooks/a2a-test.run.log` | Salida íntegra (18 celdas · 0 fallidas) |
| `evidencia-captura-terminal-2025.png` | Evidencia del servidor de historia en el puerto 2025 |
| `plan.json` | Plan de trabajo y registro de evidencias del taller |

## Opción elegida de implementación

**Opción 2: Un canal de atención (Telegram) + Servicio FastAPI (gateway).**

El proyecto implementa dos agentes conversacionales (profesores de Historia y
Geografía) expuestos por A2A nativo con `langgraph dev`. En producción, se
conectan a Telegram mediante un gateway FastAPI en AWS Lambda.

Problema que resuelve: los agentes solo eran accesibles vía notebooks y servidor
local. Esta implementación permite que un usuario final interactúe con ellos
mediante mensajes de texto en Telegram, con enrutamiento automático y memoria
por conversación.

Partes del trabajo anterior reutilizadas: agentes ReAct (LangGraph), herramientas
`consultar_mis_apuntes`, blueprints, A2A nativo, memoria por conversación,
prompts y tests A2A.

## Requisitos

- Python 3.11 o superior (probado con 3.12.10)
- Una `GOOGLE_API_KEY` válida con cuota disponible
- Dos terminales para los servidores
- Conexión a internet (Google Gemini API)

## Instalación

Cada agente tiene su propio entorno virtual:

```powershell
cd agente-profesor-historia
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements-core.txt
.venv\Scripts\python.exe -m pip install -e .

cd ..\agente-profesor-geografia
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements-core.txt
.venv\Scripts\python.exe -m pip install -e .
```

Para ejecutar los notebooks, el entorno de historia necesita además `nbformat`, `nbclient` e
`ipykernel`:

```powershell
.venv\Scripts\python.exe -m pip install nbformat nbclient ipykernel
.venv\Scripts\python.exe -m ipykernel install --user --name agente-historia
```

## Configuración

Copiá `.env.example` a `.env` en cada proyecto y completá `GOOGLE_API_KEY`. El archivo `.env`
no se incluye en la entrega.

```env
GOOGLE_API_KEY=tu_clave
MODELO=gemini-3.5-flash-lite
```

## Levantar los servidores

```powershell
# Terminal 1 · historia (2025)
cd agente-profesor-historia
.venv\Scripts\python.exe -m langgraph_cli dev --port 2025

# Terminal 2 · geografía (2026)
cd agente-profesor-geografia
.venv\Scripts\python.exe -m langgraph_cli dev --port 2026
```

Comprobar que están arriba:

```powershell
Invoke-WebRequest http://127.0.0.1:2025/ok
Invoke-WebRequest http://127.0.0.1:2026/ok
```

## Ejecutar

```powershell
# Notebook de pruebas y evidencia principal (requiere ambos servidores)
cd agente-profesor-historia\notebooks
jupyter lab a2a-test.ipynb

# Documento de entrega (no requiere servidores)
jupyter lab ../../documento-entrega.ipynb

# Tests A2A de cada agente (con su servidor arriba)
cd ..\..
cd agente-profesor-historia; .venv\Scripts\python.exe -m pytest -q
cd ..\agente-profesor-geografia; .venv\Scripts\python.exe -m pytest -q
```

El notebook `a2a-test.ipynb` incluye: configuración y descubrimiento del `assistant_id`, las tres
pruebas del taller (personalidad, apuntes con caso y memoria por `thread_id`), Agent Card y tarea
A2A, actualización de tarjetas, descubrimiento multi-servidor, supervisor, diálogo A → B → A y un
checklist final.

## Estructura

```
.
├── documento-entrega.ipynb
├── documento-entrega.run.log
├── blueprint.md
├── evidencia-captura-terminal-2025.png
├── plan.json
├── README.md
├── api/                          # API FastAPI con control de acceso
│   └── app.py                    # Endpoints: /health, /chat, /docs, /
├── frontend/                     # Frontend web (chat interactivo)
│   └── index.html                # Chat con selector de agente y API key
├── evidencias/                   # Capturas de pantalla del flujo funcionando
│   └── README.md                 # Instrucciones para tomar capturas
├── agente-profesor-historia/
│   ├── langgraph.json
│   ├── notebooks/a2a-test.ipynb
│   ├── notebooks/a2a-test.run.log
│   ├── scripts/setup_entorno.py
│   ├── src/agente_profesor/{graph,prompts,herramientas}.py
│   └── tests/test_a2a_historia.py
├── agente-profesor-geografia/
│   ├── blueprint.md
│   ├── langgraph.json
│   ├── notebooks/a2a-test.ipynb
│   ├── src/agente_geografia/{graph,prompts,herramientas}.py
│   └── tests/test_a2a_geografia.py
└── taller/   # material de la consigna (no forma parte del zip)
```

## Canal de atención local (API FastAPI + Frontend web)

El proyecto incluye una API FastAPI (`api/app.py`) y un frontend web
(`frontend/index.html`) que exponen los agentes con control de acceso por
token (`X-API-Key`).

## Integración avanzada (Telegram por voz)

El gateway en producción soporta mensajes de voz de Telegram:

1. **Detección:** el handler verifica si el update tiene `message.voice`.
2. **Descarga:** descarga el audio de Telegram (formato OGG/OPUS).
3. **Transcripción:** envía el audio a Google Cloud Speech-to-Text (`es-CL`).
4. **Procesamiento:** el texto transcrito se procesa por el router y el agente.
5. **Respuesta:** la respuesta se envía como texto a Telegram.

**Costo adicional:** ~$0.02 para 100 mensajes (dentro del free tier de 60 min/mes).

**Variables de entorno:** `GOOGLE_STT_API_KEY`, `STT_LANGUAGE_CODE`.

### Uso

```powershell
# Desde la raíz del proyecto
cd grupo-4-taller-a2a_no_entregable
pip install fastapi uvicorn
uvicorn api.app:app --reload --port 8000
```

Luego abre `http://localhost:8000` en el navegador para usar el frontend web,
o `http://localhost:8000/docs` para Swagger UI.

### Endpoints

| Endpoint | Método | Auth | Descripción |
|---|---|---|---|
| `/health` | GET | No | Health check |
| `/chat` | POST | `X-API-Key` | Envía mensaje a un agente |
| `/docs` | GET | No | Swagger UI (prueba con "Try it out") |
| `/` | GET | No | Frontend web (chat) |

### Frontend web

El frontend (`frontend/index.html`) es un chat interactivo que permite:
- Seleccionar el agente (Historia o Geografía).
- Configurar la API key y la URL de la API.
- Enviar mensajes y ver las respuestas.
- Ver el historial de conversación.

### Ejemplo de uso

```powershell
# Health check
Invoke-WebRequest http://localhost:8000/health

# Chat (con API key)
Invoke-WebRequest -Uri http://localhost:8000/chat -Method POST -Headers @{"X-API-Key"="cambia-esta-clave-en-produccion"} -ContentType "application/json" -Body '{"agente": "historia", "mensaje": "¿cuál es la capital de Chile?"}'

# Swagger
# Abrir http://localhost:8000/docs en el navegador

# Frontend web
# Abrir http://localhost:8000 en el navegador
```

### Control de acceso

- El endpoint `/chat` requiere el header `X-API-Key` con la clave configurada en `API_KEY`.
- Si la clave es inválida o ausente, responde `403 Forbidden`.
- El endpoint `/health` y `/docs` no requieren autenticación.

## Entrega

El paquete final es `grupo-4-taller-a2a.zip`. Incluye el documento, los dos blueprints, la captura
del servidor 2025 y los dos proyectos completos con sus notebooks ejecutados y sus logs. Excluye
`.venv/`, `.env`, `.langgraph_api/`, `__pycache__/`, `.pytest_cache/` y `*.egg-info/`.

## Preparación manual

### Cuentas necesarias

1. **Google AI Studio** (obligatorio): https://aistudio.google.com/app/apikey
   - Crear API key con cuota disponible.
   - Costo: ~$0.10/1M tokens entrada, ~$0.40/1M tokens salida.
   - Variable: `GOOGLE_API_KEY`.

2. **Telegram** (solo producción): https://t.me/BotFather
   - Crear bot con `/newbot`.
   - Costo: gratuito.
   - Variables: `TELEGRAM_TOKEN`, `TELEGRAM_SECRET`.

3. **Heroku** (solo producción): https://dashboard.heroku.com
   - Cuenta verificada con tarjeta (no se cobra si no se usa).
   - Costo: Eco dyno ~$5/mes por servicio.

4. **AWS** (solo gateway en producción): https://console.aws.amazon.com
   - Cuenta con IAM configurado.
   - Costo: $0 (free tier).

### Permisos y autorizaciones

- El agente necesita acceso a Google Gemini API (modelo `gemini-3.5-flash-lite`).
- En producción, el gateway necesita acceso a los agentes en Heroku (URLs públicas).
- El bot de Telegram necesita permiso para enviar mensajes.

### Vinculación del dispositivo

- **Telegram:** crear bot con @BotFather, copiar token, generar secreto, configurar webhook.
- **Heroku:** crear app, conectar GitHub, configurar Config Vars, Deploy Branch.
- **AWS:** crear ECR, construir imagen, crear Lambda, crear Function URL.

### Recursos de pago

| Recurso | Costo | Cómo evitar cargos inesperados |
|---|---|---|
| Google Gemini API | ~$0.10/1M tokens entrada | Usar `gemini-3.5-flash-lite`. Monitorear uso en Google AI Studio. |
| Heroku Eco dyno | $5/mes por servicio | Usar Render free tier para pruebas. |
| AWS Lambda | $0 (free tier) | Configurar timeout bajo (30s) y memoria mínima (512MB). |

### Cómo evitar acciones accidentales

1. No subir `.env` al repositorio (verificar con `git status`).
2. Usar datos de prueba (no enviar mensajes reales a usuarios reales).
3. Monitorear costos de Gemini en Google AI Studio.
4. Detener procesos con `Ctrl+C` (local) o escalar a 0 dynos (Heroku).

## Configuración de puertos, direcciones y secretos

### Puertos

| Servicio | Puerto | Variable |
|---|---|---|
| Agente Historia | 2025 | `A2A_HISTORIA_URL` |
| Agente Geografía | 2026 | `A2A_GEOGRAFIA_URL` |
| Gateway (local) | 8000 | `PORT` |

### Direcciones

- **Local:** `http://127.0.0.1:2025` (historia), `http://127.0.0.1:2026` (geografía)
- **Producción:** URLs de Heroku (ej. `https://grupo4-agente-historia-XXXX.herokuapp.com`)

### Secretos

- `GOOGLE_API_KEY`: clave de Google AI Studio
- `TELEGRAM_TOKEN`: token de @BotFather
- `TELEGRAM_SECRET`: secreto aleatorio para verificar webhook
- `HEROKU_API_KEY`: API key de Heroku (solo para CLI)
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`: credenciales de AWS

### Datos a conservar

- **Memoria por conversación:** el `thread_id` (derivado del `chat_id` de Telegram) se conserva en el checkpointer de LangGraph.
- **Apuntes de los agentes:** cuaderno `APUNTES` en `herramientas.py` (no cambia entre ejecuciones).
- **Configuración:** variables de entorno en `.env` (local) o Config Vars (Heroku).

### Servicios externos requeridos

- **Google Gemini API:** obligatorio para que los agentes funcionen.
- **Telegram Bot API:** solo en producción (canal de atención).
- **Heroku:** solo en producción (alojamiento de agentes).
- **AWS Lambda:** solo para el gateway en producción.

## Límites conocidos

- Los agentes solo responden sobre los temas de sus apuntes (historia/geografía). No cubren otros temas.
- El router puede clasificar incorrectamente mensajes ambiguos (mínimo 13/15 aciertos).
- Los dynos Eco de Heroku se duermen tras 30 min de inactividad (primer mensaje tarda ~10-30s).
- La memoria por conversación se pierde si el servidor se reinicia (sin checkpointer persistente).
- El agente de Historia no tiene acceso a fuentes externas; responde con su conocimiento y apuntes.
- El agente de Geografía no cubre historia, logística, viajes ni administración.
- No hay control de acceso en el servidor local (`langgraph dev` sin auth).
- No hay frontend web; la interacción es solo vía notebooks o Telegram (producción).

## Verificación de arranque desde el README

Para verificar que las instrucciones funcionan al clonar en otra carpeta:

1. Clonar el repositorio en una carpeta nueva.
2. Seguir los pasos de instalación del README.
3. Levantar ambos servidores (`langgraph dev --port 2025` y `--port 2026`).
4. Ejecutar el notebook `a2a-test.ipynb`.
5. Verificar que las 18 celdas se ejecutan sin errores.

**Resultado de la verificación:** ✅ Las instrucciones funcionan correctamente al clonar en otra carpeta (probado en Windows 11, Python 3.12.10).

## Documentación adicional

El proyecto incluye los siguientes documentos de soporte:

| Documento | Descripción |
|---|---|
| `OPCION_ELEGIDA.md` | Declaración de la opción de implementación elegida y el problema que resuelve |
| `DEPENDENCIAS_EXTERNAS.md` | Servicios externos requeridos (Google Gemini, Telegram, Heroku, AWS) y dependencias de red |
| `VERSIONES.md` | Versiones del entorno (Python, librerías, modelo, servicios externos) |
| `PREPARACION_MANUAL.md` | Cuentas, permisos, vinculación del dispositivo, recursos de pago y cómo evitar acciones accidentales |
| `CASOS_PRUEBA.md` | Tabla de 18 casos de prueba (A2A, router, control de acceso, integración Telegram) |
| `EVIDENCIAS.md` | Evidencias de ejecución con explicación, observaciones y capturas pendientes |
| `blueprint.md` | Blueprint del agente de historia |
| `agente-profesor-geografia/blueprint.md` | Blueprint del agente de geografía |
| `plan.json` | Plan de trabajo y registro de evidencias |
| `ARQUITECTURA.md` | Arquitectura final completa (componentes, flujo, decisiones, costos, seguridad, monitoreo) |
| `OPCION_ELEGIDA.md` | Declaración de la opción de implementación elegida |
| `DEPENDENCIAS_EXTERNAS.md` | Servicios externos requeridos y dependencias de red |
| `VERSIONES.md` | Versiones del entorno (Python, librerías, modelo, servicios) |
| `PREPARACION_MANUAL.md` | Cuentas, permisos, vinculación del dispositivo, recursos de pago |
| `CASOS_PRUEBA.md` | Tabla de 18 casos de prueba (A2A, router, control de acceso, Telegram) |
| `EVIDENCIAS.md` | Evidencias de ejecución con explicación y observaciones |
| `faltante.md` | Listado de faltantes vs pauta del PDF (actualizado) |

## Solución de problemas

- **`ValueError: Unable to configure formatter 'simple'`**: en Windows falta `colorama`
  (`pip install colorama`); ya está en `requirements-core.txt`.
- **`ModuleNotFoundError: No module named 'agente_profesor'`**: falta `pip install -e .`.
- **`402 RESOURCE_EXHAUSTED`**: la clave de Gemini no tiene cuota. Recargá créditos en AI Studio
  o usá otra clave. La incidencia quedó documentada en `documento-entrega.ipynb` (sección 4.6).
- **El `.venv` apunta a otra máquina**: revisá `home` y `executable` en `.venv/pyvenv.cfg` y el
  `.pth` editable de `site-packages`; deben apuntar a este equipo.
- **Puerto ocupado**: usá otro puerto y ajustá la URL en el `.env` (`A2A_HISTORIA_URL`,
  `A2A_SEGUNDO_URL`).
