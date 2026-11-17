"""API FastAPI para los agentes profesores (Historia y Geografía).

Expone los agentes ReAct por HTTP con control de acceso por token.
Permite probar el recorrido completo (solicitud → agente → respuesta)
sin usar notebooks ni el servidor langgraph dev.

Uso:
    uvicorn api.app:app --reload --port 8000

Variables de entorno (.env):
    GOOGLE_API_KEY, MODELO, API_KEY
"""
import os
import sys
import uuid
from typing import Optional

# Agregar los directorios src de los agentes al path (sin necesidad de pip install -e .)
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_BASE, "agente-profesor-historia", "src"))
sys.path.insert(0, os.path.join(_BASE, "agente-profesor-geografia", "src"))

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(os.path.join(_BASE, ".env"))

# ============================================================
# Configuración
# ============================================================
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODELO = os.environ.get("MODELO", "gemini-3.5-flash-lite")
API_KEY = os.environ.get("API_KEY", "cambia-esta-clave-en-produccion")

if not GOOGLE_API_KEY:
    raise RuntimeError("Falta GOOGLE_API_KEY en las variables de entorno.")

# ============================================================
# FastAPI app
# ============================================================
app = FastAPI(
    title="Agentes Profesores API",
    version="1.0.0",
    description="API para los agentes profesores de Historia y Geografía (A2A). "
                "Protegida con API key configurable.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================
# Modelos
# ============================================================
class ChatRequest(BaseModel):
    agente: str = Field(..., description="Agente a invocar: 'historia' o 'geografia'")
    mensaje: str = Field(..., description="Mensaje del usuario")
    thread_id: Optional[str] = Field(None, description="ID de conversación (opcional)")

class ChatResponse(BaseModel):
    agente: str
    respuesta: str
    thread_id: str

class HealthResponse(BaseModel):
    ok: bool
    modelo: str
    agentes: list[str]

# ============================================================
# Dependencia: validación de API key
# ============================================================
def verificar_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Valida que la API key sea correcta. Retorna 403 si no coincide."""
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: API key inválida o ausente.",
        )
    return x_api_key

# ============================================================
# Carga de agentes (lazy)
# ============================================================
_agentes = {}

def get_agente(nombre: str):
    """Carga el agente bajo demanda."""
    if nombre in _agentes:
        return _agentes[nombre]

    if nombre == "historia":
        from agente_profesor.graph import graph
        _agentes[nombre] = graph
        return graph
    elif nombre == "geografia":
        from agente_geografia.graph import graph
        _agentes[nombre] = graph
        return graph
    else:
        raise HTTPException(status_code=400, detail=f"Agente '{nombre}' no encontrado. Usa 'historia' o 'geografia'.")

# ============================================================
# Endpoints
# ============================================================
@app.get("/health", response_model=HealthResponse, tags=["salud"])
def health():
    """Health check del servicio."""
    return HealthResponse(ok=True, modelo=MODELO, agentes=["historia", "geografia"])

@app.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat(request: ChatRequest, _api_key: str = Depends(verificar_api_key)):
    """Envía un mensaje a un agente y devuelve la respuesta.

    Requiere header `X-API-Key` con la clave configurada en `API_KEY`.
    """
    if request.agente not in ("historia", "geografia"):
        raise HTTPException(status_code=400, detail="Agente debe ser 'historia' o 'geografia'.")

    thread_id = request.thread_id or str(uuid.uuid4())
    agente = get_agente(request.agente)

    try:
        result = agente.invoke(
            {"messages": [{"role": "user", "content": request.mensaje}]},
            config={"configurable": {"thread_id": thread_id}},
        )
        # Extraer la última respuesta del agente
        messages = result.get("messages", [])
        respuesta = ""
        for msg in reversed(messages):
            is_ai = False
            content = None
            if hasattr(msg, "content") and getattr(msg, "type", None) == "ai":
                is_ai = True
                content = msg.content
            elif isinstance(msg, dict) and msg.get("type") == "ai":
                is_ai = True
                content = msg.get("content", "")
            if is_ai and content:
                if isinstance(content, str):
                    respuesta = content
                elif isinstance(content, list):
                    # LangChain content blocks: [{'type': 'text', 'text': '...'}]
                    partes = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            partes.append(block.get("text", ""))
                        elif isinstance(block, str):
                            partes.append(block)
                    respuesta = "\n".join(p for p in partes if p)
                else:
                    respuesta = str(content)
                break
        if not respuesta:
            respuesta = "No se pudo obtener respuesta del agente."
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al invocar al agente: {str(e)[:200]}")

    return ChatResponse(agente=request.agente, respuesta=respuesta, thread_id=thread_id)

from fastapi.responses import FileResponse, HTMLResponse

@app.get("/", tags=["frontend"], response_class=HTMLResponse)
def root():
    """Sirve el frontend web (chat interactivo)."""
    frontend_path = os.path.join(_BASE, "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return {"ok": True, "docs": "/docs", "health": "/health"}
