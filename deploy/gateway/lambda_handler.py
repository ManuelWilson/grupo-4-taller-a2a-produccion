import os
import json
import uuid
import httpx

from pydantic import BaseModel, Field
from typing import Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# ============================================================
# Variables de entorno (configurar en Lambda Config Vars)
# ============================================================
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_SECRET = os.environ.get("TELEGRAM_SECRET", "")
MODELO = os.environ.get("MODELO", "gemini-3.5-flash-lite")

# Google Cloud Speech-to-Text (para mensajes de voz de Telegram)
GOOGLE_STT_API_KEY = os.environ.get("GOOGLE_STT_API_KEY", "")
STT_LANGUAGE_CODE = os.environ.get("STT_LANGUAGE_CODE", "es-CL")

A2A_HISTORIA_URL = os.environ.get("A2A_HISTORIA_URL", "")
A2A_GEOGRAFIA_URL = os.environ.get("A2A_GEOGRAFIA_URL", "")
A2A_HISTORIA_ASSISTANT_ID = os.environ.get("A2A_HISTORIA_ASSISTANT_ID", "")
A2A_GEOGRAFIA_ASSISTANT_ID = os.environ.get("A2A_GEOGRAFIA_ASSISTANT_ID", "")

llm = ChatGoogleGenerativeAI(model=MODELO)


# ============================================================
# Router: decide a qué agente va el mensaje
# ============================================================
class Decision(BaseModel):
    ruta: Literal["historia", "geografia", "generica"] = Field(
        description="A qué agente va el mensaje."
    )
    motivo: str = Field(description="Una frase: por qué esa ruta.")


def router(texto: str) -> Decision:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Eres un router. Clasifica el mensaje del usuario: "
         "'historia' si es sobre historia, 'geografia' si es sobre geografía, "
         "'generica' si no tiene que ver con ninguna de las dos."),
        ("human", "{texto}"),
    ])
    chain = prompt | llm.with_structured_output(Decision)
    return chain.invoke({"texto": texto})


# ============================================================
# Llamada A2A a un agente (HTTP)
# ============================================================
def call_a2a(url: str, assistant_id: str, text: str, context_id: str) -> str:
    """Llama a un agente y devuelve el texto de respuesta.
    Intenta A2A primero; si requiere auth (401), cae a /runs/wait (LangGraph)."""
    if not url or not assistant_id:
        return ""
    # Intentar A2A primero
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{url}/a2a/{assistant_id}",
                json={
                    "jsonrpc": "2.0",
                    "id": "1",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "messageId": str(uuid.uuid4()),
                            "role": "user",
                            "parts": [{"type": "text", "text": text}],
                            "contextId": context_id,
                        }
                    },
                },
                headers={"Accept": "application/json"},
            )
            data = resp.json()
            result = data.get("result", {})

            # Extraer de history
            for msg in reversed(result.get("history", [])):
                if msg.get("role") == "agent":
                    for part in msg.get("parts", []):
                        if part.get("kind") == "text":
                            print("[a2a] OK (A2A)")
                            return part.get("text", "")

            # Fallback: buscar en artifacts
            for artifact in result.get("artifacts", []):
                for part in artifact.get("parts", []):
                    if part.get("kind") == "text" or part.get("type") == "text":
                        print("[a2a] OK (A2A artifacts)")
                        return part.get("text", "")

            # Fallback: buscar en messages
            for msg in reversed(result.get("messages", [])):
                if msg.get("role") in ("assistant", "agent"):
                    for part in msg.get("parts", []):
                        if part.get("kind") == "text" or part.get("type") == "text":
                            print("[a2a] OK (A2A messages)")
                            return part.get("text", "")

            print(f"[a2a] No se pudo extraer. result keys: {list(result.keys())}")
            print(f"[a2a] full data: {str(data)[:500]}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("[a2a] 401 Unauthorized, cayendo a /runs/wait")
        else:
            print(f"[a2a] HTTP {e.response.status_code}: {str(e)[:200]}")
    except Exception as e:
        print(f"[a2a] ERROR: {e}")

    # Fallback a /runs/wait (LangGraph directo)
    print("[runs] Intentando /runs/wait...")
    try:
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(
                f"{url}/runs/wait",
                json={
                    "assistant_id": assistant_id,
                    "input": {"messages": [{"type": "human", "content": text}]},
                },
                headers={"Content-Type": "application/json"},
            )
            data = resp.json()
            messages = data.get("messages", [])
            for msg in reversed(messages):
                if msg.get("type") == "ai":
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        print("[runs] OK (/runs/wait)")
                        return content
                    if isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                print("[runs] OK (/runs/wait)")
                                return part.get("text", "")
            print(f"[runs] No se pudo extraer. keys: {list(data.keys())}")
            return "No se pudo obtener respuesta del agente."
    except Exception as e:
        print(f"[runs] ERROR: {e}")
        return (
            "No se pudo contactar al agente. "
            "Verifica que el servicio esté disponible e intenta de nuevo. "
            f"(detalle: {str(e)[:100]})"
        )


# ============================================================
# Enviar mensaje a Telegram
# ============================================================
def send_telegram(chat_id: int, text: str) -> bool:
    """Envía un mensaje a Telegram. Retorna True si fue exitoso."""
    if not TELEGRAM_TOKEN:
        print("[telegram] ERROR: TELEGRAM_TOKEN no configurado")
        return False
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text},
            )
            if resp.status_code != 200:
                print(f"[telegram] ERROR: status={resp.status_code} body={resp.text[:200]}")
                return False
            return True
    except Exception as e:
        print(f"[telegram] ERROR: {e}")
        return False


# ============================================================
# Descarga de audio de Telegram
# ============================================================
def descargar_audio_telegram(file_id: str) -> bytes:
    """Descarga un archivo de audio de Telegram y retorna los bytes."""
    if not TELEGRAM_TOKEN or not file_id:
        return b""
    try:
        # 1. Obtener file_path
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile",
                params={"file_id": file_id},
            )
            data = resp.json()
            if not data.get("ok"):
                print(f"[telegram] getFile error: {data}")
                return b""
            file_path = data["result"]["file_path"]

            # 2. Descargar el archivo
            download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            resp = client.get(download_url, timeout=30.0)
            if resp.status_code == 200:
                print(f"[telegram] Audio descargado: {len(resp.content)} bytes")
                return resp.content
            else:
                print(f"[telegram] Error descargando audio: {resp.status_code}")
                return b""
    except Exception as e:
        print(f"[telegram] Error en descargar_audio: {e}")
        return b""


# ============================================================
# Transcripción de audio con Google Cloud Speech-to-Text
# ============================================================
def transcribir_audio(audio_bytes: bytes) -> str:
    """Transcribe audio (OGG/OPUS de Telegram) a texto usando Google STT."""
    if not GOOGLE_STT_API_KEY or not audio_bytes:
        return ""
    try:
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        payload = {
            "config": {
                "encoding": "OGG_OPUS",
                "sampleRateHertz": 48000,
                "languageCode": STT_LANGUAGE_CODE,
            },
            "audio": {
                "content": audio_b64,
            },
        }
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_STT_API_KEY}"
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                print(f"[stt] Error: {resp.status_code} {resp.text[:200]}")
                return ""
            data = resp.json()
            results = data.get("results", [])
            if not results:
                print("[stt] No se detectó texto en el audio")
                return ""
            transcript = results[0].get("alternatives", [{}])[0].get("transcript", "")
            print(f"[stt] Transcripción: {transcript[:100]}")
            return transcript
    except Exception as e:
        print(f"[stt] ERROR: {e}")
        return ""


# ============================================================
# Handler principal de Lambda
# ============================================================
def lambda_handler(event, context):
    # Verificar secreto del webhook
    headers = event.get("headers", {}) or {}
    secret = (
        headers.get("x-telegram-bot-api-secret-token")
        or headers.get("X-Telegram-Bot-Api-Secret-Token")
    )
    if TELEGRAM_SECRET and secret != TELEGRAM_SECRET:
        return {"statusCode": 403, "body": "Forbidden"}

    # Parsear body
    try:
        body = json.loads(event.get("body", "{}") or "{}")
    except Exception:
        return {"statusCode": 400, "body": "Bad request"}

    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    voice = message.get("voice")

    # Si es un mensaje de voz, descargar y transcribir
    if voice and not text:
        file_id = voice.get("file_id")
        if not file_id:
            send_telegram(chat_id, "No pude procesar el audio. Envía un mensaje de texto.")
            return {"statusCode": 200, "body": "OK"}
        print(f"[handler] Mensaje de voz recibido, file_id={file_id}")
        audio_bytes = descargar_audio_telegram(file_id)
        if not audio_bytes:
            send_telegram(chat_id, "No pude descargar el audio. Intenta de nuevo.")
            return {"statusCode": 200, "body": "OK"}
        text = transcribir_audio(audio_bytes)
        if not text:
            send_telegram(chat_id, "No pude transcribir el audio. Envía un mensaje de texto.")
            return {"statusCode": 200, "body": "OK"}
        print(f"[handler] Texto transcrito: {text[:100]}")

    # Ignorar updates sin texto
    if not chat_id or not text:
        return {"statusCode": 200, "body": "OK"}

    # Router: decidir a qué agente va
    try:
        decision = router(text)
        ruta = decision.ruta
        print(f"[router] ruta={ruta} motivo={decision.motivo}")
    except Exception as e:
        print(f"[router] ERROR: {e}")
        ruta = "generica"
        respuesta = (
            "No pude clasificar tu mensaje. "
            "Intenta reformularlo o pregunta por historia o geografía."
        )

    # Llamar al agente correspondiente
    respuesta = ""
    # context_id debe ser un UUID válido para A2A (thread_id)
    context_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"telegram-{chat_id}"))

    if ruta == "historia":
        respuesta = call_a2a(
            A2A_HISTORIA_URL,
            A2A_HISTORIA_ASSISTANT_ID,
            text,
            context_id,
        )
    elif ruta == "geografia":
        respuesta = call_a2a(
            A2A_GEOGRAFIA_URL,
            A2A_GEOGRAFIA_ASSISTANT_ID,
            text,
            context_id,
        )
    else:
        respuesta = (
            "Este chat es para consultas de historia y geografía. "
            "¿En qué puedo ayudarte?"
        )

    if not respuesta:
        respuesta = "No se pudo obtener respuesta del agente."

    print(f"[handler] chat_id={chat_id} text={text[:50]} ruta={ruta} respuesta_len={len(respuesta)}")

    # Enviar respuesta a Telegram
    send_telegram(chat_id, respuesta)

    # Siempre responder 200 OK a Telegram
    return {"statusCode": 200, "body": "OK"}
