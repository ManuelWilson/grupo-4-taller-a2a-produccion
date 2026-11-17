# Comparativa de costos: AWS vs Heroku para los agentes A2A

Comparación para levantar los **3 servicios** del proyecto
(`gateway FastAPI` + `agente-profesor-historia` + `agente-profesor-geografia`)
vía Telegram, con el mismo stack (Python 3.12, FastAPI/Uvicorn, LangGraph).

---

## 1. Resumen ejecutivo (costo mensual, USD, 3 servicios)

| Proveedor / Opción | Bajo volumen | Medio (siempre activo) | Notas |
|---|---|---|---|
| **Heroku Eco dyno** | ~15 | ~15 | 3 dynos × $5. Duerme 30 min. |
| **Heroku Basic dyno** | ~21 | ~21 | 3 × $7. Siempre activo. |
| **AWS App Runner** (pausado 22h/día) | ~3 × 15.25 = **45.75** | — | Dev/test. |
| **AWS App Runner** (siempre activo, 1 vCPU/2 GB) | — | ~3 × 25.50 = **76.50** | + $1/app/mes + build. |
| **AWS EC2 t3.micro** (free tier 12 meses) | **0** (12 meses) | ~3 × 8.5 = **25.5** | Gestión manual (SSH, OS, seguridad). |
| **AWS ECS Fargate** (0.25 vCPU / 0.5 GB) | ~3 × 12 = **36** | ~3 × 12 = **36** | Pago por uso, sin sleep. |
| **AWS Lambda** (pay per request) | **< 1** | ~5–15 | Cold starts; requiere refactor (handler). |
| **AWS Elastic Beanstalk** | **0** (servicio) + EC2 | EC2 underlying | Gratis el servicio, pagas la VM. |

> Los precios son lista pública 2026 y varían por región. Verificar en la
> calculadora oficial antes de provisionar.

---

## 2. Heroku (referencia del ejemplo de la Sesión 2)

| Plan | Costo/dyno/mes | Siempre activo | RAM | Sleep |
|---|---|---|---|---|
| Eco | $5 | No (duerme 30 min) | 0.5 GB | 30 min inactividad |
| Basic | $7 | Sí | 0.5 GB | No |
| Standard-1X | $25 | Sí | 0.5 GB | No |
| Standard-2X | $50 | Sí | 1 GB | No |

- **3 servicios × Eco = $15/mes** (recomendado para pruebas/demo).
- **3 servicios × Basic = $21/mes** (mínimo para producción real sin sleep).
- Postgres Essential-0 (si se necesita checkpointer persistente): +$5/mes.
- HTTPS incluido, no hay costo de egress listado (soft limit 2 TB/mes/app).
- Despliegue desde el panel web, sin CLI; build automático desde GitHub.

## 3. AWS — opciones detalladas

### 3.1 AWS App Runner (más cercano a Heroku)

Gestionado, despliega desde código o imagen, auto-scaling, HTTPS incluido.

- **vCPU:** $0.064/vCPU-hora (solo activo).
- **Memoria:** $0.007/GB-hora (siempre, incluso inactivo, si provisionado).
- **Fee fijo:** $1/mes por aplicación activa.
- **Build fee:** por minuto de build (solo en deploys).

| Escenario | Por app/mes | × 3 servicios |
|---|---|---|
| Dev/test (activo 2 h/día, pausado el resto) | ~$15.25 | ~$45.75 |
| Producción (activo 8 h/día) | ~$25.50 | ~$76.50 |
| Alto volumen (picos 800 req/s) | ~$102 | ~$306 |

> App Runner puede **pausarse** para ahorrar; ideal para dev. En producción
> "siempre activo" compite con Heroku Basic ($7 vs $25.50 por app).

### 3.2 AWS EC2 (t3.micro / t4g.micro)

- **Free Tier:** 750 h/mes durante 12 meses (1 instancia ≈ 1 mes completo).
- **Después del free tier:** ~$8.5–$10/mes por instancia (on-demand).
- **3 instancias ≈ $25.5–$30/mes** (sin free tier).
- **Pros:** control total, más barato a largo plazo, ARM (t4g) más barato.
- **Contras:** gestión manual (OS, parches, seguridad, SSL, load balancer),
  no auto-scaling sin configuración extra. Egress $0.09/GB (100 GB gratis/mes).

### 3.3 AWS ECS Fargate (contenedores serverless)

- **0.25 vCPU / 0.5 GB:** ~$0.012/hora → ~$9–$12/mes por task.
- **3 tasks ≈ $27–$36/mes** (sin sleep, auto-scaling).
- **Pros:** sin gestión de servidores, integración con ALB, ECR.
- **Contras:** más complejo de configurar que Heroku/App Runner; ALB cuesta
  ~$16–$22/mes adicional si se usa.

### 3.4 AWS Lambda (serverless por invocación)

- **$0.20 por 1M de requests** + tiempo de cómputo (GB-s).
- **Para este proyecto:** si cada mensaje = 1 invocación y el agente tarda
  ~5 s con 0.5 GB → ~$0.0000083 por invocación.
- **1.000 msg/día ≈ 30.000/mes → ~$0.25/mes** (casi gratis).
- **Pros:** costo mínimo para bajo volumen, escala a cero.
- **Contras:** cold starts (2–5 s), límite de 15 min por ejecución, requiere
  refactor del código (handler Lambda), gestión de estado/checkpointer externo
  (DynamoDB/Postgres).

### 3.5 AWS Elastic Beanstalk

- **Servicio gratuito:** solo pagas los recursos subyacentes (EC2, ELB, etc.).
- Equivale a EC2 con gestión automática de despliegue.
- **Costo:** igual que EC2 (~$8.5–$10/mes por instancia) + ELB (~$16/mes)
  si se usa.

---

## 4. Comparativa Heroku vs AWS (resumen)

| Criterio | Heroku | AWS |
|---|---|---|
| **Costo mínimo (3 servicios, siempre activos)** | $21/mes (Basic × 3) | $25.5/mes (EC2 × 3) o $0 (Lambda, bajo volumen) |
| **Simplicidad de despliegue** | ⭐⭐⭐⭐⭐ (panel web) | ⭐⭐⭐ (más pasos) |
| **Auto-scaling** | Limitado (dynos) | Excelente (App Runner/Fargate/Lambda) |
| **Free tier** | No (Eco $5) | Sí (12 meses EC2, Lambda siempre) |
| **Gestión de servidores** | Ninguna | Variable (Lambda/Fargate = ninguna; EC2 = alta) |
| **HTTPS** | Incluido | Incluido (App Runner/Lambda) / manual (EC2) |
| **Cold starts** | No (Basic+) | Sí (Lambda, App Runner pausado) |
| **Egress** | 2 TB/mes/app (soft) | 100 GB/mes gratis, luego $0.09/GB |
| **Vendor lock-in** | Medio | Bajo (estándares) |

---

## 5. Recomendación para este proyecto

| Escenario | Recomendación | Costo/mes |
|---|---|---|
| **Demo / clase (bajo volumen)** | Heroku Eco ($15) o Render Free ($0) o AWS Lambda (<$1) | $0–$15 |
| **Producción pequeña (siempre activo, simple)** | Heroku Basic ($21) | $21 |
| **Producción media (auto-scaling, sin gestión)** | AWS App Runner ($76.50) o Fargate ($36) | $36–$77 |
| **Alto volumen / costo optimizado** | AWS Lambda + API Gateway | <$15 (hasta ~100k msg/día) |

### Recomendación final

- **Si priorizas simplicidad y el ejemplo de la Sesión 2 (Heroku panel):**
  Heroku Basic × 3 = **$21/mes**, sin cold starts, despliegue en minutos.
- **Si priorizas costo mínimo y volumen bajo:** AWS Lambda = **<$1/mes**,
  pero requiere refactor a handler y gestión de estado externo.
- **Si priorizas auto-scaling sin gestión:** AWS Fargate (3 tasks) ≈ **$36/mes**
  o App Runner (siempre activo) ≈ **$77/mes**.

> Para un proyecto académico/demo con 3 servicios pequeños, **Heroku Eco ($15/mes)**
> o **Render Free ($0)** son las opciones más razonables. AWS Lambda es la más
> barata si se acepta el refactor y los cold starts.

---

## 6. Costos adicionales a considerar (ambos proveedores)

| Concepto | Heroku | AWS |
|---|---|---|
| Base de datos (Postgres, para checkpointer) | Essential-0 $5/mes | RDS t3.micro free tier 12 meses, luego ~$15/mes |
| Redis (memoria compartida) | Redis Cloud add-on ~$19.58/mes | ElastiCache ~$12/mes o Upstash free tier |
| Dominio custom | Incluido (DNS externo) | Route 53 $0.50/zona/mes |
| Logs / monitoreo | Papertrail add-on (free tier) | CloudWatch (free tier 5 GB/mes) |
| Egress | 2 TB/mes/app (soft) | 100 GB/mes gratis, luego $0.09/GB |

---

## 7. Notas importantes

- Los precios de AWS son **pay-as-you-go** y muy sensibles a la configuración
  (vCPU, memoria, horas activas). Usar la **AWS Pricing Calculator** para
  estimaciones exactas.
- Heroku cobra **por dyno**; si tienes 3 procesos, pagas 3 dynos. No hay
  descuento por volumen en planes Eco/Basic.
- El **modelo Gemini** (`gemini-3.5-flash-lite`) es el mismo en ambos
  proveedores; el costo de IA es independiente del hosting (~$0.29–$29.40/mes
  según volumen, ver `evaluacion.md` sección 10.2).
- **Free tier de AWS** (12 meses) es ideal para desarrollo, pero no para
  producción real a largo plazo.

---

*Comparativa basada en precios públicos 2026 de Heroku y AWS (App Runner, EC2,
Fargate, Lambda, Elastic Beanstalk). Verificar antes de provisionar.*
