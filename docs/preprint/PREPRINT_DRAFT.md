# paper-pipeline: Auditable Infrastructure for AI-Assisted Research — Draft preprint (Markdown)

**Status:** Working draft for internal review. Not submitted to arXiv. Numbers below reflect the repository snapshot and one reference mission unless noted.

**Authors:** *[To be filled]*

**Keywords:** reproducible research, research infrastructure, AI safety, agent evaluation, audit trail, triage

---

## Mentor briefing (read this first — feedback-oriented)

**Purpose.** This file is a **working draft** meant for **mentor or colleague review** on positioning, defensible claims, and what (if any) minimal evaluation would increase credibility. It is **not** a camera-ready submission.

**What the codebase already supports.** (1) **Architecture:** mission-centric runs, `run_ledger.json`, triage and publish signals, appendix export without tokens (`case_study_trace.json`, `benchmark_bundle.json`, `benchmark_table.md`). (2) **Deterministic `agent_eval`:** 12 bundled scenarios, versioned baseline (`examples/baselines/agent_eval_baseline.json`)—this is **governance / policy regression in CI**, not a measure of LLM capability. (3) **Reference mission** `data/missions/4f6715a65f4c/` on arXiv:2510.24256: **tier 2**, **planning_only** when optional scientific dependencies were absent—documented **honesty** about partial replication, not a claim of reproducing all paper numbers. (4) **CI fixture** `examples/safety_usecase/`: claim extraction path without Perplexity.

**What we explicitly do *not* claim.** A new interpretability method; SOTA on an external benchmark; measured productivity (Claim A); full numerical replication of Merullo et al. from the snapshot alone; that heuristic `claims.json` rows are verified scientific facts.

**Concrete questions for your feedback**

1. **Venue / audience:** Where would you place this work—systems / MLSys / workshops on reproducibility, HCI, or a technical report—**without** new ML accuracy numbers?
2. **Claims:** Is the hybrid **B+C** framing (reusable architecture + safety-oriented case study with explicit limits) tight enough, or should we narrow further?
3. **Case study:** Does **tier 2 + planning_only** read as **integrity** (we surface weak empirical evidence) or as a **liability** to cut from the main story?
4. **Evaluation gap:** What **single** addition would most improve credibility for you—e.g., one GPU-backed metric in `metrics.json`, a small user study, or stronger related-work positioning only?
5. **Missing comparisons:** Which tool or paper (e.g., DSPy, LangChain, PaperBench) must be cited or contrasted in one paragraph?

**Handy artifacts for reviewers.** See `docs/PREPRINT_ARTIFACTS.md`; regenerate supplementary tables with `paper-export-appendix` or `scripts/generate_preprint_figures.py`.

---

## Abstract

Reproducible research in AI safety and mechanistic interpretability still lacks shared infrastructure for the repeatable parts of the research cycle—drafting, instruction loops, metric hooks, and publication gates—while keeping auditability first-class. We present **paper-pipeline**, an open-source system that records execution in a **ledger**, triages mission metrics, runs a **deterministic agent_eval harness** (no LLM API in continuous integration), and exports **supplementary bundles** suitable for preprints. We report a **reference mission** on arXiv:2510.24256 with wall-clock runtime **approximately 281 seconds** (**snapshot:** ledger `run_id` 2026-03-29; **see reproducibility notes**), **21** heuristic claim candidates extracted from the assembled draft, triage tier **2** (insufficient empirical metrics for a breakthrough claim), and experiment capability **planning_only** when optional heavy dependencies are absent. We **contrast** this run against a **CI-only fixture** (`examples/safety_usecase`) with **no** full mission ledger but **2** deterministic claim rows (no Perplexity). A **second** reference mission with comparable tables is **pending**; until then, generalization claims remain **N=1 mission** for the full pipeline. The bundled governance harness passes **12 of 12** scenarios at rate **1.0** against a versioned baseline (**exact**, reproducible without network). We do **not** claim end-to-end numerical replication of the target paper’s experiments in this artifact snapshot.

---

## 1. Introduction

Empirical papers in mechanistic interpretability often combine large-scale experiments, careful statistical reporting, and narrative synthesis. Replication efforts such as PaperBench (OpenAI, 2025) and community initiatives (e.g., Mechanistic Interpretability Benchmark) highlight both the value and the cost of faithful reproduction. Yet most labs still assemble ad hoc scripts, chat logs, and spreadsheets. That fragmentation makes it hard to answer basic questions: *What ran? What failed? What evidence supports each sentence in the draft?*

**paper-pipeline** targets the **infrastructure layer**: a mission-centric workflow with explicit phases, persisted outputs, and triage that separates *narrative completeness* from *empirical sufficiency*. The goal is not to replace human judgment or GPU work, but to make the **repeatable skeleton**—ledger, metrics hooks, deterministic checks, and export—first-class so that audits and preprints can point to concrete artifacts.

**Contributions** (claims we defend in this draft):

1. **Architecture:** A modular pipeline (ingest → assembly → experiments → quality → optional integrations) with **run ledger** and **publish signals** suitable for preprint appendices.
2. **Governance harness:** A **deterministic** `agent_eval` suite with **12** bundled scenarios and a **versioned JSON baseline** for regression testing without network calls.
3. **Case study:** A **reference mission** on arXiv:2510.24256 (Merullo et al.) with **honest reporting** of triage tier **2**, **planning_only** replication capability under missing optional dependencies, and **21** extracted claim rows for inspection—not as proof of correctness, but as **traceable evidence objects**.
4. **Replication bundle export:** Automated export of appendix-friendly JSON (including `case_study_trace.json`) without embedding secrets.

**Non-goals:** We do not present a new interpretability method, a new benchmark ranking pipelines, or user studies measuring productivity.

---

## 2. Related Work

**Paper replication and evaluation.** PaperBench and similar efforts structure replication as a measurable task with rubrics and tooling. paper-pipeline is **complementary**: it focuses on **per-mission audit trails** and **triage** rather than competing on leaderboard scores.

**Mechanistic interpretability tooling.** Libraries and benchmarks (e.g., MIB) provide task definitions and reference implementations. paper-pipeline does not implement Merullo’s method; it provides **scaffolding** to attach experiments, metrics, and narrative assembly around a chosen paper.

**Agent evaluation.** Many frameworks evaluate LLM agents online. Our `agent_eval` is intentionally **offline and deterministic** so CI can enforce **policy-shaped** scenarios (e.g., blocked writes, manifest invariants) without API keys.

---

## 3. System Overview

### 3.1 Mission model

A **mission** is a root directory containing configuration, inputs, and an `outputs/` tree. Each run appends to **`run_ledger.json`**: phase names, timestamps, and completion status. This supports after-the-fact audits (“did the experiment runner execute?”) distinct from qualitative draft review.

### 3.2 Phases (conceptual)

Typical phases include: source acquisition, assembly of a working draft, optional **Perplexity**-assisted enrichment, experiment planning or execution, quality gates, and optional integrations (e.g., Notion, Cursor CLI hooks). The exact set depends on configuration; the **ledger** is the source of truth for what actually ran.

### 3.3 Triage and publish signals

**Triage** consumes mission metrics (coverage, replication tier, dependency signals) and assigns a **tier**. Tier 2 in our reference mission indicates **insufficient empirical metrics** for a strong empirical claim—an explicit guardrail against overstating results.

**Publish decision** records whether the mission is suitable for external publication of *claims*, separate from whether the infrastructure worked.

### 3.4 Figures (architecture)

High-level diagrams live under `docs/assets/` (Mermaid sources). A **case study replication flow** figure links mission outputs to appendix export, including `case_study_trace.json`.

---

## 4. Deterministic Agent Evaluation

We ship a bundled **`agent_eval`** harness that exercises governance scenarios: blocked paths, manifest invariants, ledger consistency, and related checks. The harness is **deterministic** and intended for **CI**.

**Baseline.** `examples/baselines/agent_eval_baseline.json` defines expected pass counts and scenario rates. The CLI can **compare** current results against this baseline (`--check-baseline`), supporting **regression detection** when scenarios or weights change intentionally.

**Empirical snapshot (this repo).** As of the current baseline artifact, the bundled suite reports **12** scenarios at rate **1.0** (full pass). This number is **not** a claim about LLM quality; it is a claim about **our offline harness** and its fixtures.

---

## 5. Case Study: arXiv:2510.24256 (Reference Mission)

We highlight one **real mission folder** (`data/missions/4f6715a65f4c/`) as a **traceable example** of the pipeline end-to-end *as instrumented*, not as a claim of faithful numerical replication.

**Observed facts from artifacts (not cherry-picked beyond selecting this mission):**

- **Wall clock (single run window):** approximately **281 seconds** between ledger start and end timestamps.
- **Claim extraction:** **21** rows in `evidence/claims.json` (heuristic candidates for human review).
- **Triage tier:** **2**, with reason consistent with **insufficient metrics** for stronger publication claims.
- **Replication capability path:** **planning_only**, with signals that optional scientific stack pieces (e.g., Hugging Face stack, NumPy availability in the experiment environment) were **not** satisfied in that run—so empirical replication was **not** achieved in the artifact snapshot.

**Interpretation.** This case study is valuable precisely because it is **not** a success story on empirical metrics. It demonstrates that the pipeline can **record** a mission where narrative and planning progress while empirical gates remain open—matching how real research proceeds.

### 5.1 Cursor and “agent in the loop”

The reference ledger includes phases such as **cursor_cli**, reflecting optional integration with editor-side automation. We treat these as **instrumentation hooks**, not as proof that a particular agent policy is safe in general. The reproducibility story is: **the ledger tells you what ran**.

### 5.2 Comparative observations (full pipeline vs CI-only)

We summarize **what appears only when the full stack runs** (mission `4f6715a65f4c`) versus the **CI fixture** `examples/safety_usecase` (no Perplexity, deterministic claim extraction). See **[`COMPARATIVE_TABLES.md`](COMPARATIVE_TABLES.md) Table 1** in the repository: the full pipeline records **9** ledger phases, triage **tier 2**, **21** claim candidates, and `planning_only` in `metrics.json`; the fixture has **no** mission `run_ledger.json`, **no** triage tier from a live mission, **2** claim candidates, and **~1 s** wall time for `scripts/safety_usecase_repro.py` (machine-dependent). This is **not** an ML benchmark; it is a **structured comparison of observable artifacts** produced by each condition.

### 5.3 Second reference mission (pending)

**Table 2** in [`COMPARATIVE_TABLES.md`](COMPARATIVE_TABLES.md) is reserved for a **second** mission (different paper anchor) to move from a single anecdote to **N=2** full-pipeline runs. **No second mission outputs are committed** in the current snapshot; the placeholder and runbook live under `data/missions/` (see `README_ADDING_MISSION_V3.md`). Any future row must be filled **honestly** from `outputs/` artifacts.

---

## 6. CI Fixture Without External APIs

The **`examples/safety_usecase`** path provides a **minimal** mission demonstrating claim-oriented outputs **without** Perplexity or other network credentials. This supports the claim that parts of the pipeline are **testable in CI** without external services.

---

## 7. Limitations

1. **Narrative vs empirical modes.** The system can produce strong narrative artifacts while empirical metrics remain weak; triage is designed to surface that tension.
2. **Heuristic claims.** `claims.json` entries are **candidates** for review, not verified scientific assertions.
3. **Optional dependencies.** Experiment execution may degrade to planning-only when environments omit scientific packages; this is **explicitly recorded** in metrics.
4. **No user study.** We do not measure time savings with human participants; any efficiency discussion is qualitative.
5. **Snapshot numbers vs guarantees.** Wall-clock duration, claim counts, and triage tier for **mission `4f6715a65f4c`** are **execution snapshots** (see `docs/REPRODUCIBILITY_NOTES.md`); they are **not** guaranteed to repeat without identical credentials, models, and environment. Only **agent_eval** and the CI fixture claim path are **deterministic** in the sense of bit-reproducible CI tests.
6. **N=2 missions** (for full-pipeline case studies) **not yet achieved** in this repository snapshot; **N=1** for the full mission plus **N=1** CI fixture is insufficient for statistical generalization—sufficient only for an **initial pattern** worth further study.
7. **Variance in wall clock and claim counts** is **not** characterized statistically (no repeated runs).
8. **No head-to-head comparison** with alternative tools (e.g., DSPy, LangChain) in this draft—future work.

---

## 8. Conclusion and Future Work

paper-pipeline contributes **audit-first research infrastructure**: ledgers, deterministic governance tests, triage, and appendix exports—including **case study traces**—for missions that combine AI assistance with empirical hooks. Future work includes tighter integration with GPU experiment runners, richer metric schemas, and expanded case studies where empirical replication is fully realized.

---

## Figures and benchmark bundle

The repository includes `scripts/generate_preprint_figures.py`, which writes **`benchmark_bundle.json`** (aggregated `agent_eval` per-scenario outcomes, `case_study_trace` fields, and ledger phase durations in seconds) plus PNG figures: per-scenario pass/fail bars, governance-axis stacked counts, radar-style aggregate rates, **phase-duration** bars for the reference mission, and improved claim-type distributions. This **does not** substitute for an ML accuracy benchmark on a downstream task; it is a **reproducible snapshot** of governance regression and audit-relevant metrics suitable for supplementary material.

---

## Appendix A (conceptual): Supplementary bundle

The export tool bundles JSON artifacts for reviewers: metrics, triage, publish decision, manifest, and **`case_study_trace.json`** summarizing a mission’s outputs directory without secrets. See `PREPRINT_ARTIFACTS.md` for the canonical list. Generated **`benchmark_bundle.json`** and **`benchmark_table.md`** (Markdown table for supplementary PDFs) complement this with a single machine-readable table for the deterministic harness and phase timing.

## Appendix B (conceptual): Agent eval baseline

The versioned baseline JSON and comparison CLI document expected harness behavior for regression testing.

---

## Data and code availability

Repository: *[link when public]*. Mission outputs referenced here are under `data/missions/` in the developer workspace; redacted bundles can be exported for external sharing.

## Acknowledgments

*[To be filled]*

---

## References (placeholder list — expand for submission)

1. OpenAI, “PaperBench,” 2025.  
2. Merullo et al., “Mechanistic Interpretability for Scientific Discovery,” arXiv:2510.24256, 2025.  
3. Mechanistic Interpretability Benchmark (MIB) — *[cite official resource]*.
