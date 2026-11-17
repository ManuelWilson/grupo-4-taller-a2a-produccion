# Carpeta de evidencias

Guarda aquí las capturas de pantalla del flujo funcionando.

## Capturas requeridas (según la pauta del PDF)

1. **evidencia-flujo-historia.png** — Frontend web o Swagger mostrando una consulta de historia y la respuesta del agente.
2. **evidencia-flujo-geografia.png** — Frontend web o Swagger mostrando una consulta de geografía y la respuesta del agente.
3. **evidencia-control-acceso.png** — Captura mostrando un intento rechazado (403) sin API key.
4. **evidencia-flujo-telegram.png** — Captura del bot en Telegram respondiendo a una consulta (si aplica).
5. **evidencia-terminal.png** — Captura de la terminal mostrando el servidor corriendo.

## Reglas

- No incluir claves, tokens ni datos personales en las capturas.
- Las capturas deben ser legibles y con contexto (mostrar la pregunta, el sistema y la respuesta).
- Acompañar cada captura con una explicación breve en EVIDENCIAS.md.
- Distinguir lo probado, lo pendiente y cualquier simulación utilizada.

## Cómo tomar las capturas

### Frontend web (http://localhost:8000)
1. Abre http://localhost:8000 en el navegador.
2. Selecciona el agente (Historia o Geografía).
3. Escribe una pregunta y presiona Enviar.
4. Toma captura de la pantalla mostrando la pregunta y la respuesta.

### Swagger UI (http://localhost:8000/docs)
1. Abre http://localhost:8000/docs.
2. Expande POST /chat -> Try it out.
3. Ingresa los parámetros y ejecuta.
4. Toma captura del request y la respuesta.

### Control de acceso (403)
1. En Swagger o con curl, envía un request sin API key.
2. Toma captura del error 403.

### Terminal
1. Toma captura de la terminal mostrando el servidor corriendo y los logs.
