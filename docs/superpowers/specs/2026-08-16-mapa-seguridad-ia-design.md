# Spec de diseño — Mapa Maestro de Investigación en Seguridad en IA

- **Fecha:** 2026-08-16
- **Estado:** Diseño aprobado por el usuario (v2, con rama G y sub-proyecto futuro documentado)
- **Ubicación del trabajo:** `paper-pipeline/` dentro de `D:\oliver\Actividades\mcp_perplesity`

## 1. Problema y objetivo

No existe, en un solo lugar, un mapa actualizado y fundamentado en fuentes de **todo** el campo de Seguridad en IA: sus líneas de investigación (ramas), qué líneas nacen, cuáles avanzan, cuáles están en auge y cuáles se cierran; dónde se publica y verifica por pares ese trabajo; qué empresas y laboratorios lo hacen y con qué redes de colaboración; y qué vertientes alternativas (hackathons, CTFs, literatura gris) lo alimentan.

**Objetivo:** generar, con el sistema `paper-pipeline` existente, un mega survey tipo árbol — **"Mapa Maestro de Investigación en Seguridad en IA"** — en Markdown, en español, con citas a fuentes, clasificando cada línea por estado. El entregable es un documento (no una web visual).

**No-objetivos (fuera de alcance de este sub-proyecto):**
- Visualización web interactiva del árbol.
- Experimentos ejecutados o replicación empírica (modo narrativo del pipeline).
- La web/MCP de consulta (ver §8, sub-proyecto siguiente).

## 2. Decisiones tomadas con el usuario

| Decisión | Elección |
|---|---|
| Forma del entregable | Solo documento/survey en Markdown (state of the art del campo) |
| Alcance de "Seguridad en IA" | Espectro completo: AI Security ofensiva/defensiva + seguridad de sistemas ML + AI Safety/alignment + gobernanza |
| Arquitectura de recolección | 1 misión madre (tronco) + misiones paralelas por rama vía `paper-parallel batch` (worktrees) + consolidación |
| Idioma | Español (`language: es-ES`), terminología técnica en inglés, citas en idioma original |
| Proveedor LLM | Perplexity (búsqueda web); sin token, aborta con mensaje claro (fallback `mistral` solo si el usuario lo pide) |

## 3. Arquitectura general

```
FASE 1 (tronco)          FASE 2 (ramas, ~55 agentes)         FASE 3 (consolidación)
┌─────────────────┐      ┌──────────────────────────┐      ┌─────────────────────┐
│ Misión madre:   │─────▶│ Misión por sub-rama, en  │─────▶│ Consolidador une    │
│ taxonomía +     │      │ worktrees aislados       │      │ todo en UN doc con  │
│ marco unificado │      │ (paper-parallel batch)   │      │ árbol + tabla de    │
│                 │      │ → rama git exp/mapa-<id> │      │ estados + bibliografía│
└─────────────────┘      └──────────────────────────┘      └─────────────────────┘
```

Todo vive en un solo lugar: `missions/mapa-seguridad-ia/` (entradas) y `outputs/mapa-seguridad-ia/` (salida final). Monitoreo con la web existente (`paper-web`).

## 4. Taxonomía canónica (el árbol)

Fuente única de verdad: `missions/mapa-seguridad-ia/taxonomy.json`. Siete ramas troncales, ~55 sub-ramas. La Fase 1 puede corregir/agregar sub-ramas detectadas por la misión madre; los cambios se congelan en `taxonomy.json` antes de generar los specs.

Estados por línea de investigación: 🌱 emergente · 🔥 en auge · ✅ activa · 📉 en declive · ⚰️ cerrada/convergida (siempre con evidencia: años activos, papers o señales de cierre).

| Rama troncal | Sub-ramas |
|---|---|
| **A. Ataques y ofensiva** (~13) | jailbreaks LLM, prompt injection, ataques a agentes, adversarios en visión, envenenamiento/backdoors, extracción de modelos, ataques de privacidad, RAG poisoning, ataques multimodales, cadena de suministro ML, deepfakes ofensivos, side-channels, sistemas embebidos/edge |

> El conteo por rama es orientativo: el número exacto y la lista definitiva de sub-ramas salen de `taxonomy.json`, que es la fuente única de verdad y de donde el generador dimensiona el batch.
| **B. Defensas y robustez** (~12) | entrenamiento adversario, robustez certificada, guardarraíles LLM, defensas anti-prompt-injection, detección de jailbreaks, watermarking, procedencia de contenido (C2PA), privacidad diferencial, machine unlearning, sanitización de datos, sandboxing de agentes, MLSecOps/hardening |
| **C. AI Safety / alineamiento** (~11) | RLHF/DPO/Constitutional AI, scalable oversight, interpretabilidad mecanicista, dangerous evals, AI control, model organisms of misalignment, reward hacking/specification gaming, honestidad y epistemia, riesgos existenciales, cooperación multi-agente, alineamiento de agentes autónomos |
| **D. Evaluación y benchmarks** (~6) | HarmBench/JailbreakBench y afines, red teaming automatizado, evaluación de agentes (tau-bench...), métricas (ASR, refusal...), arenas/leaderboards, rigor estadístico y contaminación |
| **E. Gobernanza y ecosistema normativo** (~7) | regulación (EU AI Act, US, China), estándares (NIST AI RMF, ISO 42001, OWASP LLM Top 10), divulgación coordinada de vulnerabilidades, gobernanza de modelos de frontera, auditorías y certificación, dual-use/bioseguridad, economía de la seguridad (responsabilidad, seguros) |
| **F. Aplicaciones y dominios** (~5) | ciberseguridad con IA (ofensiva/defensiva), fraude y abuso criminal, seguridad de contenido, integridad electoral/desinformación, sistemas críticos (salud, vehículos, finanzas) |
| **G. Ecosistema, publicaciones y comunidad** (~5) | venues peer-reviewed (ver §4.1), literatura gris, hackathons y CTFs, empresas y laboratorios, redes de colaboración |

### 4.1 Requisitos específicos de la rama G

- **G1 Venues:** conferencias de seguridad (IEEE S&P, USENIX Security, ACM CCS, NDSS), de ML (NeurIPS, ICLR, ICML), de NLP (ACL, EMNLP) y especializadas (SaTML, AISec, SafeGenAI...); revistas (TIFS, TOPS, Nature Machine Intelligence...). Cada venue clasificada por: revisión por pares (sí/no), tipo (conferencia/revista/workshop/arXiv-only), ranking (CORE, cuartil) y qué sub-ramas del árbol publican ahí.
- **G2 Literatura gris:** blogs de labs, reports técnicos, preprints — clasificados por estatus de verificación vs. peer-review.
- **G3 Hackathons/CTFs (vertiente aparte de research):** DARPA AIxCC, DEF CON AI Village CTF, SaTML CTF, hackathones de seguridad IA — líneas de investigación surgidas de ahí y proyectos con artefactos públicos.
- **G4 Empresas y laboratorios:** big tech (safety/security teams), startups (Protect AI, HiddenLayer, Lakera, Prompt Security, Mindgard...), nonprofits (METR, Apollo Research, RAND...), organismos públicos — con enfoque, productos y publicaciones.
- **G5 Redes de colaboración:** co-autoría academia↔industria, flujos de financiamiento, consorcios — mapeo de "firmas con sus redes".

## 5. Componentes

1. **Misión madre** — `missions/mapa-seguridad-ia/mission.md`. Topic: "Mapa maestro de investigación en Seguridad en IA". Secciones del catálogo existente: `related_work`, `sota`, `gaps`, `discussion`. Provider `perplexity`. `output_dir: outputs/mapa-seguridad-ia/tronco` (el consolidador lee de ahí). Produce el tronco: visión del campo, marco unificado (incluye clasificación de áreas afines: criptografía aplicada a ML, verificación formal, seguridad de sistemas, HCI-seguridad, derecho), y metodología de clasificación de estados. `enable_quality_check: true` solo aquí y en consolidación.
2. **`taxonomy.json`** — árbol versionado: id, nombre, rama troncal, descripción, preguntas guía por sub-rama, estado inicial tentativo (a validar por su agente).
3. **Extensión del catálogo de secciones** (`paper_pipeline/templates.py`) — 5 claves nuevas (~30-40 líneas, aditivo, sin tocar claves existentes):
   - `research_lines_status`: clasificar líneas de {topic} por estado (emergente/auge/activa/declive/cerrada) con evidencia y años.
   - `key_actors`: empresas, laboratorios y grupos que trabajan en {topic}, con su enfoque y redes de colaboración del área.
   - `trends_timeline`: qué líneas nacen, cuáles mueren y por qué (2019–presente).
   - `venues_map`: dónde se publica y verifica por pares el trabajo de {topic} (conferencias, revistas, workshops), con rankings.
   - `hackathon_projects`: hackathons, CTFs y proyectos de comunidad en {topic} con artefactos públicos.
4. **Generador de specs** — `scripts/generar_specs_mapa.py`: lee `taxonomy.json` → escribe `specs.json` con un `AgentRunSpec` por sub-rama. Misión embebida por rama: topic descriptivo de la sub-rama (incluye el encuadre de estados), secciones `related_work`, `research_lines_status`, `trends_timeline`, `venues_map`, `key_actors`, `related_code` (la sub-rama G3 hackathons/CTFs añade `hackathon_projects`); `max_perplexity_calls: 8`; `language: es-ES`; `enable_quality_check: false`. Comando por agente: `python -m paper_pipeline mission.md` (prefijo `python` ya permitido). Salta sub-ramas cuya rama git ya tiene outputs (reanudable). `--only` para regenerar un subset.
5. **Retención de ramas (cambio en `paper-parallel`)** — el código actual (`agent_executor.py`) elimina la rama `exp/<id>` tras cada agente salvo tier-3, y el tier solo se calcula con `outputs/metrics.json`, que las misiones de research no generan: sin este cambio, el batch destruiría los outputs. Cambio mínimo y aditivo: campo `keep_all_branches: bool = False` en `WorktreeConfig` (`parallel/specs.py`), honrado en `agent_executor.py` (`keep = keep_all_branches or (tier_result == 3 and keep_breakthrough_branches)`), expuesto como flag `--keep-branches` en `paper-parallel batch` (`parallel_cli.py`). Para este proyecto el batch se lanza **siempre** con `--keep-branches`.
6. **Ejecución paralela** — `paper-parallel batch --repo . --specs specs.json --max-concurrent 5 --timeout 3600 --keep-branches`. Cada agente: worktree aislado → misión inyectada → secciones vía Perplexity → outputs → commit en rama `exp/mapa-<id>` → worktree eliminado, **rama y outputs preservados en git**.
7. **Consolidador** — `scripts/consolidar_mapa.py`: extrae los drafts/secciones de cada rama `exp/mapa-<id>` (vía `git show`), ensambla `outputs/mapa-seguridad-ia/MAPA_SEGURIDAD_IA.md` en orden del árbol: portada, índice, resumen ejecutivo, tronco (misión madre), ramas A–G con sus sub-ramas, tabla maestra (sub-rama × estado × venues × actores), glosario y bibliografía consolidada. Reporta sub-ramas fallidas como PENDIENTE. Incluye `--limpiar-ramas` para borrar las ramas `exp/mapa-*` tras una consolidación exitosa (opt-in, nunca por defecto).
8. **Verificación de calidad final** — un run de revisión (misión de consolidación con `peer_review` del catálogo existente) sobre el documento ensamblado.

## 6. Flujo de datos

```
taxonomy.json ──▶ generar_specs_mapa.py ──▶ specs.json
                                                │
                     paper-parallel batch (max 5 concurrentes)
                                                ▼
        [worktree exp/mapa-<id>] × ~55 ──▶ commit a rama exp/mapa-<id>
                                                │
                                                ▼
                     consolidar_mapa.py (git show por rama)
                                                ▼
        outputs/mapa-seguridad-ia/MAPA_SEGURIDAD_IA.md (+ reporte de faltantes)
```

## 7. Manejo de errores

- **Agente fallido/timeout:** queda registrado en `batch_summary.json`; el consolidador lo marca PENDIENTE; se relanza solo ese subset (`generar_specs_mapa.py --only <ids>`).
- **Pérdida de outputs:** imposible por diseño — el batch corre con `--keep-branches` (§5.5) y las ramas `exp/mapa-<id>` persisten hasta una consolidación exitosa con `--limpiar-ramas` explícito.
- **Perplexity sin token o saturado:** aborta con mensaje claro; rate limiter integrado del orquestador paralelo + `max_concurrent: 5` + `max_perplexity_calls: 6` por misión.
- **Sección inválida:** validación estricta del catálogo (error existente de `templates.py`); los tests lo cubren.
- **Reanudabilidad:** specs filtrados por ramas git ya completadas; ninguna rerun innecesaria.
- **Costo acotado:** calidad solo en tronco y consolidación (no 55 veces).

## 8. Sub-proyecto siguiente (fuera de este spec, registrado como visión)

Al terminar el mapa: **web que exponga la base de conocimiento para consulta por personas y agentes vía MCP/API** — servir `taxonomy.json`, el documento consolidado y las secciones por rama (FastAPI ya existente + servidor MCP estilo `perplexity-webui-scraper[mcp]`). Ese sub-proyecto tendrá su propio ciclo spec → plan → implementación.

## 9. Pruebas

- `--dry-run` de la misión madre y de una misión de rama (valida sin llamadas de red).
- Test unitario de `generar_specs_mapa.py` (taxonomía → specs válidos, filtro de reanudación, `--only`).
- Test de las 5 claves nuevas de `templates.py` (presentes en `prompt_for_section`, formato correcto).
- Test de retención de ramas: con `--keep-branches`, tras un batch la rama `exp/<id>` existe; sin el flag, comportamiento actual intacto.
- Test de `consolidar_mapa.py` con fixtures (2-3 ramas falsas en un repo temporal): orden del árbol, PENDIENTE en faltantes, bibliografía.
- **Piloto:** batch con 2-3 sub-ramas reales antes del batch completo de ~55.

## 10. Criterios de éxito

1. `MAPA_SEGURIDAD_IA.md` existe, en español, con las 7 ramas troncales y ~55 sub-ramas.
2. Cada sub-rama clasifica líneas por estado con evidencia y citas a fuentes.
3. La tabla maestra incluye venues (con estatus peer-review) y actores por sub-rama.
4. Las ramas G1-G5 cubren: venues, literatura gris, hackathons/CTFs, empresas/labs y redes.
5. El pipeline es reanudable y el reporte de faltantes está limpio (o los fallos son explícitos).
