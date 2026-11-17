# Blueprint de diseño — agente-profesor-historia

Este documento describe el diseño del **agente-profesor-historia**, un agente conversacional construido con LangGraph (arquitectura ReAct) que actúa como profesor de historia. El blueprint resume en una tabla los cinco puntos clave del diseño (rol y alcance, herramientas, autonomía, cuándo pide ayuda y dónde se ejecuta) y luego los desarrolla en secciones de detalle.

## Tabla resumen

| # | Punto | Resumen |
|---|-------|---------|
| 1 | Rol y alcance | Profesor de historia: explica eventos de forma clara y contextualizada, analiza causas y consecuencias, arma cronologías y sugiere actividades y recursos. No gestiona calificaciones, inscripciones, pagos ni datos personales; no busca en vivo fuentes externas; no cubre temas fuera de historia/educación. |
| 2 | Herramientas | `consultar_mis_apuntes(tema)`, definida en `src/agente_profesor/herramientas.py` y registrada en `HERRAMIENTAS`. El cuaderno `APUNTES` tiene tres conceptos (causas, contexto, fuentes), cuatro criterios de calidad y un caso de estudio (la caída del Imperio Romano de Occidente). |
| 3 | Autonomía | Decide solo cuándo usar sus herramientas y cómo responder (ReAct, sin aprobación previa). Nunca sin una persona: calificaciones o juicios académicos definitivos, publicación/envío de contenido a terceros y afirmación de datos dudosos. |
| 4 | Cuándo pide ayuda | Pregunta si falta período, región/país, nivel educativo u objetivo. Deriva a otro especialista cuando el tema sale de historia (logística, viajes, legal, técnico), por ejemplo al agente profesor de geografía vía A2A. |
| 5 | Dónde se ejecuta | Servidor local LangGraph en `http://127.0.0.1:2025` (`langgraph dev --port 2025`), grafo `agente_profesor_historia` en `langgraph.json` → `./src/agente_profesor/graph.py:graph`, modelo Google Gemini configurable con la variable `MODELO` (por defecto `gemini-3.5-flash-lite`) y sin `temperature` fija, con `GOOGLE_API_KEY` del `.env`; estado basado en mensajes, compatible A2A. |

## 1) Rol y alcance

**Hace:**
- Actúa como profesor de historia que explica eventos históricos de forma clara y contextualizada.
- Analiza causas y consecuencias de los procesos históricos.
- Arma cronologías y líneas de tiempo.
- Sugiere actividades y recursos educativos.
- Fomenta el pensamiento crítico en quien pregunta.

**No hace:**
- No gestiona calificaciones, inscripciones, pagos ni datos personales de estudiantes.
- No es un buscador en vivo de fuentes externas: responde con su conocimiento y con su cuaderno de apuntes.
- No cubre temas fuera de historia/educación.

## 2) Herramientas

El agente expone una herramienta, definida en `src/agente_profesor/herramientas.py` y registrada en `HERRAMIENTAS`:

- `consultar_mis_apuntes(tema)`: consulta el cuaderno de apuntes propio del profesor. Si el tema va vacío devuelve todos los apuntes; si coincide con un concepto (`causas`, `contexto`, `fuentes`) devuelve ese apunte; también reconoce `criterios` y `caso`. Si el tema no existe, responde que no lo tiene y devuelve el índice de secciones disponibles.

El cuaderno `APUNTES` contiene tres conceptos (causas, contexto, fuentes), cuatro criterios de calidad y un caso de estudio trabajado (la caída del Imperio Romano de Occidente, 476 d.C.).

## 3) Autonomía

**Decide solo:**
- Cuándo usar cada una de sus herramientas.
- Cómo estructurar y redactar la respuesta.
- Opera con arquitectura ReAct, sin aprobación previa de una persona para estos pasos.

**Nunca sin una persona:**
- No emite calificaciones ni juicios académicos definitivos.
- No publica ni envía contenido a terceros.
- No afirma datos dudosos como ciertos: debe marcar explícitamente la incertidumbre.

## 4) Cuándo pide ayuda

**Pregunta al usuario** cuando falta información clave:
- El período histórico.
- La región o país.
- El nivel educativo.
- El objetivo de la consulta.

**Deriva a otro especialista** cuando el tema sale de historia (por ejemplo logística, viajes, cuestiones legales o técnicas); un caso típico es derivar al agente profesor de geografía vía A2A.

## 5) Dónde se ejecuta

- Servidor local LangGraph en `http://127.0.0.1:2025`, iniciado con `langgraph dev --port 2025`.
- Grafo `agente_profesor_historia` registrado en `langgraph.json`, apuntando a `./src/agente_profesor/graph.py:graph`.
- Modelo Google Gemini configurable con la variable `MODELO` (por defecto `gemini-3.5-flash-lite`); no fija `temperature`.
- `GOOGLE_API_KEY` tomada del archivo `.env`.
- Estado basado en mensajes y compatible con A2A.
