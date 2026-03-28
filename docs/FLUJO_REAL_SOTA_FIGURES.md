# Flujo completo real (sin mocks) — SOTA, expectativas y figuras para el paper

Esta guía enlaza el modo **operador real** (Perplexity + Notion + métricas) con redacción académica y gráficos listos para publicación.

## ¿Cuál es el “nuevo SOTA” y quién elige el ámbito?

- **La app no fija un SOTA global** (no hay un número único “nuevo récord” hasta que **vos** definas tarea, métrica y baseline).
- **Vos** elegís el ámbito editando `mission.md`: `topic`, `paper_target`, y (en misiones v2) `quality_gates` con `sota_baseline_value`, márgenes, etc.
- **Perplexity** ayuda con literatura y redacción de secciones; **no sustituye** definir baseline y experimento: eso va en la misión y en `outputs/metrics.json` que genera tu código de evaluación.
- Si el `mission.md` sigue en placeholder (`topic: Research topic`), **aún no hay** contribución acotada: reemplazá el tema por tu pregunta de investigación real antes de un run largo.

## 1. Orden recomendado de verificación (todo real)

| Paso | Comando / acción | Qué demuestra |
|------|------------------|---------------|
| A | `pytest -m "not integration and not notion_real" -q` | Base sin red costosa (ni Notion opcional). |
| B | `pytest tests/test_perplexity_integration.py -m integration -v` | **Perplexity real** (consume cuota). |
| C | `pytest tests/test_notion_smoke_optional.py -m notion_real -v` | **Notion real** (token + escritura en `NOTION_SMOKE_PAGE_ID`). |
| D | UI `npm run dev:all` o `paper-web` + misión con `enable_notion` | Flujo humano completo hacia tu página de paper. |
| E | `paper-parallel batch ... --max-concurrent 10` | Paralelo real (ver `PRUEBAS_NIVELES_5_10_NOTION.md`). |

No hay “mock” en B/C: son llamadas a APIs externas.

## 2. Protocolo de “nuevo SOTA” (expectativas honestas)

El hipervisor de triaje (`paper_pipeline/hypervisor/triage.py`) clasifica resultados usando **`outputs/metrics.json`** con campos alineados a `TriageMetrics`:

- `main` — métrica principal medida.
- `baseline` — referencia (literatura, replica, o cota declarada en la misión).
- `coverage`, `math_checks`, `anomaly_detected`, etc.

**Interpretación académica (no automática):**

- **Tier 2** (“SOTA match”): resultado **dentro de tolerancia** del baseline → *replication / parity*, no necesariamente novedad.
- **Tier 3** (breakthrough): métrica **por encima del baseline + margen** o anomalía explícita → candidato a **claim fuerte**; sigue requiriendo **significancia**, **comparabilidad** y **revisión por pares**.

Para el texto del paper en **inglés**, podés generar un párrafo neutro a partir de números en Python:

```python
from paper_pipeline.reporting import sota_claim_paragraph_en

text = sota_claim_paragraph_en(
    metric_name="accuracy",
    measured=0.91,
    baseline=0.88,
    beats_baseline=True,
    tolerance=0.01,
)
```

Ajustá el tono a la venue (ML vs HCI vs teoría); el párrafo es plantilla **Results**, no conclusión final.

## 3. Figuras para el paper (barra principal vs baseline)

Instalación:

```bash
pip install -e ".[figures]"
```

Con un `outputs/metrics.json` válido (p. ej. tras un experimento que escriba `main` y opcionalmente `baseline`):

```bash
paper-report-figures path/to/outputs/metrics.json -o figures/main_vs_baseline.png --metric-label Accuracy --lang en
```

Salida: PNG 300 dpi, tipografía serif, apta para LaTeX/Word con retoques menores.

## 4. Cursor en el circuito

- **Misma integración Notion** que en Cursor MCP → mismas páginas que el pipeline.
- **Cursor CLI** (`paper-cursor-agent`) cuando quieras cierres de código local; no sustituye la validez estadística del experimento.
- Para claims de SOTA, dejá trazabilidad: `outputs/metrics.json`, `triage_report.json`, y logs en Notion o export TSV de misiones.

## 5. Checklist mínimo antes de afirmar SOTA en el paper

1. **Definición** de tarea, split y métrica **idénticas** al baseline citado.
2. **Varianza** (semillas, intervalos) o tests adecuados a la disciplina.
3. **Límites** (datos, sesgo, generalización) en *Limitations*.
4. Figura reproducible (`paper-report-figures`) + números en tabla suplementaria si aplica.

---

*Referencia de estructura de revisión de papers: marco de pregunta, método, hallazgos e implicancias (estándar de revisiones sistemáticas).*
