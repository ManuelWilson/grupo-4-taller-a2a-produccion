# Proyecto: Agentes A2A — Implementación y Despliegue

Repositorio completo del taller de implementación de agentes A2A (Historia y
Geografía) con despliegue en producción vía Telegram.

---

## Estructura del proyecto

```
entregable-final/
├── README.md                          # Esta guía (reproducción)
├── .env.example                       # Plantilla de variables de entorno
├── .gitignore                         # Excluye .env, .venv, etc.
├── ARQUITECTURA.md                    # Arquitectura final completa
├── evaluacion.md                      # Evaluación de producción (costos, etc.)
├── requisitos.md                      # Requisitos para levantar en producción
├── comparativa-aws-heroku.md          # Comparativa de costos AWS vs Heroku
│
├── grupo-4-taller-a2a/                # Proyecto principal del taller
│   ├── README.md                      # README del proyecto (instalación, comandos)
│   ├── api/                           # API FastAPI con control de acceso
│   │   └── app.py                     # Endpoints: /health, /chat, /docs, /
│   ├── frontend/                      # Frontend web (chat interactivo)
│   │   └── index.html                 # Chat con selector de agente
│   ├── evidencias/                    # Capturas y logs
│   │   ├── *.jpeg, *.png              # Capturas de pantalla
│   │   ├── lambda-logs.txt            # Logs de AWS Lambda
│   │   ├── heroku-*-logs.txt          # Logs de Heroku
│   │   ├── README.md                  # Instrucciones para evidencias
│   │   ├── LOGS.md                    # Documentación de logs
│   │   ├── CASOS_PRUEBA.md            # Tabla de 18+ casos de prueba
│   │   └── EVIDENCIAS.md             # Evidencias con explicación
│   ├── agente-profesor-historia/      # Agente 1 (LangGraph, A2A)
│   ├── agente-profesor-geografia/     # Agente 2 (LangGraph, A2A)
│   ├── OPCION_ELEGIDA.md             # Opción de implementación elegida
│   ├── DEPENDENCIAS_EXTERNAS.md      # Servicios externos y dependencias
│   ├── VERSIONES.md                  # Versiones del entorno
│   ├── PREPARACION_MANUAL.md         # Cuentas, permisos, preparación
│   ├── blueprint.md                  # Blueprint del agente de historia
│   ├── plan.json                     # Plan de trabajo
│   └── documento-entrega.ipynb       # Documento de entrega
│
└── deploy/                            # Despliegue en la nube
    ├── gateway/                       # AWS Lambda (gateway)
    │   ├── lambda_handler.py          # Handler principal
    │   ├── Dockerfile                 # Imagen Docker
    │   ├── requirements.txt           # Dependencias del gateway
    │   └── .env.example               # Plantilla de variables
    ├── agents/                        # Agentes para Heroku
    │   ├── historia/                  # Agente historia (con Procfile)
    │   └── geografia/                 # Agente geografía (con Procfile)
    ├── scripts/                       # Utilidades Telegram
    │   ├── set_webhook.py
    │   └── webhook_info.py
    └── DEPLOYMENT.md                  # Guía de despliegue y redespliegue
```

---

## Reproducción paso a paso

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

### 2. Configurar variables de entorno

```powershell
# Copiar la plantilla
cp .env.example .env

# Editar .env con tus credenciales:
# - GOOGLE_API_KEY (de Google AI Studio: https://aistudio.google.com/app/apikey)
# - MODELO=gemini-3.5-flash-lite
# - API_KEY (clave para la API local, ej: cambia-esta-clave-en-produccion)
```

Para el directorio del proyecto:
```powershell
cd grupo-4-taller-a2a
cp agente-profesor-historia/.env.example agente-profesor-historia/.env
cp agente-profesor-geografia/.env.example agente-profesor-geografia/.env
# Editar ambos .env con tu GOOGLE_API_KEY
```

### 3. Crear entornos virtuales e instalar dependencias

```powershell
# Agente de Historia
cd agente-profesor-historia
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements-core.txt
.venv\Scripts\python.exe -m pip install -e .

# Agente de Geografía
cd ..\agente-profesor-geografia
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements-core.txt
.venv\Scripts\python.exe -m pip install -e .

# API FastAPI (canal de atención local)
cd ..
pip install fastapi uvicorn python-dotenv
```

### 4. Levantar los agentes

```powershell
# Terminal 1 — Agente de Historia (puerto 2025)
cd agente-profesor-historia
.venv\Scripts\python.exe -m langgraph dev --port 2025

# Terminal 2 — Agente de Geografía (puerto 2026)
cd agente-profesor-geografia
.venv\Scripts\python.exe -m langgraph dev --port 2026
```

### 5. Probar los agentes

```powershell
# Verificar que están arriba
Invoke-WebRequest http://127.0.0.1:2025/ok
Invoke-WebRequest http://127.0.0.1:2026/ok

# Notebook de pruebas (requiere ambos servidores)
cd agente-profesor-historia\notebooks
jupyter lab a2a-test.ipynb

# Tests A2A
cd ..\..
cd agente-profesor-historia; .venv\Scripts\python.exe -m pytest -q
cd ..\agente-profesor-geografia; .venv\Scripts\python.exe -m pytest -q
```

### 6. Levantar el canal de atención local (API + Frontend)

```powershell
cd grupo-4-taller-a2a
python -m uvicorn api.app:app --reload --port 8000
```

Abrir en el navegador:
- **Frontend web:** http://localhost:8000 (chat interactivo)
- **Swagger UI:** http://localhost:8000/docs (prueba con "Try it out")

### 7. Despliegue en producción (opcional, +1 punto)

Ver `deploy/DEPLOYMENT.md` para la guía completa de despliegue en Heroku + AWS Lambda.

Resumen:
1. Crear 2 apps en Heroku (historia y geografía).
2. Conectar repos de GitHub.
3. Configurar Config Vars.
4. Deploy Branch.
5. Obtener `assistant_id` de cada agente.
6. Construir imagen Docker del gateway y subir a ECR.
7. Crear Lambda function + Function URL.
8. Configurar variables de entorno en Lambda.
9. Configurar webhook de Telegram.
10. Probar end-to-end.

---

## Checklist de verificación

- [ ] Los agentes responden en `/ok` (puertos 2025 y 2026).
- [ ] El notebook `a2a-test.ipynb` ejecuta 18 celdas sin errores.
- [ ] Los tests A2A pasan (`pytest -q`).
- [ ] La API FastAPI responde en `/health` y `/docs`.
- [ ] El frontend web funciona en `http://localhost:8000`.
- [ ] El control de acceso funciona (403 sin API key, 200 con API key).
- [ ] (Opcional) El bot de Telegram responde en producción.

---

## Documentación adicional

Ver `grupo-4-taller-a2a/README.md` para la documentación completa del proyecto.

Ver `deploy/DEPLOYMENT.md` para la guía de despliegue y redespliegue.

Ver `ARQUITECTURA.md` para la arquitectura final completa.

Ver `evaluacion.md` para la evaluación de producción.

Ver `requisitos.md` para los requisitos de producción.

Ver `comparativa-aws-heroku.md` para la comparativa de costos.

---

## Contacto

- **Grupo 4:** Karen García, Sebastian Garrido, Leonel Carrasco, Manuel Wilson.
- **Proyecto:** Taller A2A — Agentes Profesores de Historia y Geografía.
- **Curso:** Agentic AI / Curso 2.