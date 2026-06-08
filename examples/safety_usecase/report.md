# Informe de reproducibilidad — caso de uso P2 (paper ancla)

**Paper ancla:** *From Memorization to Reasoning in the Spectrum of Loss Curvature* — Merullo et al., arXiv:2510.24256  
**Objetivo del caso de uso:** demostrar cómo **paper-pipeline** puede apoyar un flujo de investigación donde importan **trazabilidad** y **auditoría de claims** (tema alineado con *trustworthy ML* e interpretabilidad mecánica), sin afirmar una réplica numérica completa del paper en este repositorio.

Este documento es **honesto por diseño**: lo que está automatizado y versionado en CI se distingue de lo que exige credenciales, GPU o juicio humano.

---

## 1. Cómo enmarcamos “safety” aquí

No usamos “AI safety” en el sentido estrecho (alineación, riesos de despliegue). El ancla 2510.24256 conecta **geometría del loss** (curvatura / K-FAC) con **comportamiento observable** (memorización vs razonamiento). Ese encaje es **evidencia de aplicabilidad** para equipos que necesitan procesos **reproducibles y auditables** al estudiar memorización y edición de pesos — coherente con el Claim C del plan [mio.md](../../docs/superpowers/plans/mio.md), sin inflar el alcance.

---

## 2. Qué queda **reproducido en CI** (sin red, sin claves)

| Artefacto | Descripción | Contrato |
|-----------|-------------|----------|
| `fixture_draft.md` | Texto mínimo temático + líneas que disparan heurísticas | Entrada fija |
| `outputs/evidence/claims.json` | Candidatos a claims (cuantitativos / rendimiento) | Salida de [`claim_extractor`](../../paper_pipeline/validation/claim_extractor.py), determinista |
| `outputs/evidence/claims_evidence_checklist.json` | Checklist con `evidence_status: unverified` | Misma ruta que en `run_pipeline` post-calidad |
| `outputs/manifest.json` | SHA-256 del fixture + conteo de claims | Detecta drift del fixture sin timestamps volátiles |

**Verificación:** `pytest tests/test_safety_usecase_repro.py` y, opcionalmente, `python scripts/safety_usecase_repro.py` desde la raíz del repo.

---

## 3. Qué **no** incluye este paquete (límites explícitos)

- **No** ejecuta el pipeline completo con **Perplexity** ni genera `draft_paper.md` real para 2510.24256 sin `PERPLEXITY_SESSION_TOKEN` y coste asociado.
- **No** ejecuta el **experiment_runner** ni réplicas GPU del paper; un run interno de misión puede seguir en *tier* bajo o *replication degraded* si el benchmark integrado no valida K-FAC completo (véase `MODE_NARRATIVE_VS_EMPIRICAL.md`).
- La extracción de claims es **heurística** (regex); no valida citas bibliográficas ni correctitud estadística.
- Los números del fixture (**15%**, **2%**) son **ilustrativos** para probar el extractor; **no** son mediciones reproducidas del paper ancla en este repo.

---

## 4. Tiempo humano estimado (orden de magnitud)

Solo para planificación; no es medición empírica (Claim A futuro).

| Fase | Actividad | Tiempo indicativo |
|------|-----------|-------------------|
| A | Configurar `mission.md`, objetivo arXiv alineado | 30–90 min |
| B | Secciones Perplexity + ensamblado de borrador | 1–4 h + cuota API |
| C | Curación de claims + checklist manual | 30–120 min |
| D | Código / experimentos / GPU fuera del modo narrativo | horas a días |
| E | **Este caso P2** (fixture + script + informe) | &lt; 1 h una vez el contrato existe |

---

## 5. Comandos de reproducción

Desde la raíz de `paper-pipeline`:

```bash
pip install -e ".[dev]"
python scripts/safety_usecase_repro.py
pytest tests/test_safety_usecase_repro.py -q
```

Tras editar `fixture_draft.md`, volver a ejecutar el script y **revisar el diff** de `outputs/` antes de commitear.

---

## 6. Relación con misiones “reales”

Una misión de desarrollo previa (p. ej. bajo `data/missions/*/`) puede contener `draft_paper.md` y `metrics.json` con triaje **insufficient_metrics**: sirve como **contraste** con este P2 — el producto puede producir borradores ricos mientras la réplica empírica sigue siendo un esfuerzo aparte. No se exige tener esa misión para validar P2.

---

## 7. Criterio de aceptación P2 (plan vivo)

- [x] Reporte presente y **explícito** sobre límites.
- [x] Comando documentado (`safety_usecase_repro.py` + pytest).
- [x] Ningún token ni secreto en artefactos versionados.

---

*Última revisión alineada a [PREPRINT_ARTIFACTS.md](../../docs/PREPRINT_ARTIFACTS.md) y [ARXIV_TARGET_ALIGNMENT.md](../../docs/ARXIV_TARGET_ALIGNMENT.md).*
