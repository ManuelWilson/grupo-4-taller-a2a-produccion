# Logs de ejecución — Evidencia

## Logs de AWS Lambda (CloudWatch)

- **Archivo:** `lambda-logs.txt` (en esta carpeta)
- **Comando usado:** `aws logs tail /aws/lambda/gateway-telegram --since 24h --region us-east-1`
- **Líneas:** 78
- **Entorno:** PRODUCCIÓN (AWS Lambda)
- **Fecha:** Noviembre 2026

### Contenido relevante

Los logs muestran:
- Clasificación del router: `route=historia` o `route=geografia` con motivo.
- Consulta al agente: `status=ok`, `chars`, `latency_ms`, `a2a_task_id`.
- Errores: `telegram_error` con `detail: HTTP 400: Bad Request: chat not found` (chat_id de prueba).
- Comando `/start`: `route=comando`, respuesta con mensaje de bienvenida.

### Ejemplo de log de consulta exitosa

```
{"ts": "2026-11-16T13:50:40.086+00:00", "level": "INFO", "logger": "gateway.service", "event": "clasificacion", "route": "historia", "method": "keywords", "reason": "palabras clave: revolucion francesa"}
{"ts": "2026-11-16T13:50:42.109+00:00", "level": "INFO", "logger": "gateway.service", "event": "consulta", "route": "historia", "agents": "historia", "status": "ok", "chars": 285, "latency_ms": 2023}
```

## Logs de Heroku

- **Estado:** ✅ Obtenidos vía API de Heroku (nueva API key).
- **Archivos:** `heroku-grupo4-agente-historia-logs.txt` (100 líneas), `heroku-grupo4-agente-geografia-logs.txt` (100 líneas)
- **Comando:** API de Heroku (`POST /apps/{app}/log-sessions` + GET logplex_url)
- **Entorno:** PRODUCCIÓN
- **Fecha:** Noviembre 2026
- **Contenido:** Requests A2A recibidos, respuestas del agente, cold starts, errores.
- **Observaciones:** Los logs muestran el flujo completo: request → procesamiento → respuesta. Los cold starts se ven en "Init Duration".

### Cómo obtener los logs de Heroku

1. Ve a [dashboard.heroku.com](https://dashboard.heroku.com).
2. Selecciona la app (`grupo4-agente-historia` o `grupo4-agente-geografia`).
3. Haz clic en **More** (arriba a la derecha) → **View logs**.
4. Copia los logs y guárdalos en un archivo en esta carpeta.
5. Toma captura de pantalla y guárdala como `evidencia-heroku-logs.png`.

### Qué buscar en los logs de Heroku

- `POST /a2a/...` — requests A2A recibidos.
- `200 OK` / `401 Unauthorized` — respuestas del servidor.
- `INFO` / `ERROR` — mensajes del servidor de LangGraph.
- `Init Duration` — tiempo de cold start.

## Evidencia honesta

- Los logs de Lambda muestran requests reales (update_id, chat_id hasheado).
- Los logs de Heroku no se pudieron obtener automáticamente (API key inválida).
- La evidencia se puede obtener manualmente desde el panel web de Heroku.
- No se incluyen datos sensibles (chat_id hasheado, sin tokens ni claves).
