<!-- section=experiments generated=2026-03-27T14:48:49.717925+00:00 model=best -->

To replicate a paper on **LLM‑powered autonomous agents for research**, you want an experiment plan that mirrors the original methodology while making explicit your baselines, metrics, ablations, and compute constraints. Below is a concrete, modular design you can adapt to your specific target paper.

***

### 1. High‑level goal and scope

Assume the paper studies an **autonomous research‑agent system** that, given a research idea or dataset, performs literature‑review → experimentation → reporting (e.g., Agent Laboratory–style).[1](https://arxiv.org/abs/2501.04227)[2](https://arxiv.org/html/2508.12752v1)

Your replication goal:
- Reproduce the main pipeline under the same or slightly simplified conditions.
- Add controlled ablations and baselines to test design choices (planning, memory, tool‑use, etc.).

***

### 2. Baselines to include

Pick 2–4 clear baselines, depending on the original paper’s setup.[2](https://arxiv.org/html/2508.12752v1)[3](https://arxiv.org/html/2504.18765v2)[1](https://arxiv.org/abs/2501.04227)

- **Zero‑agent baseline**:  
  - Human‑in‑the‑loop only (you manually execute each step: search, code, eval, write).  
  - Controls for “does any automation help at all?”  
- **LLM‑as‑assistant (non‑autonomous)**:  
  - Same LLM, but only as a chatbot (e.g., copy‑paste prompts, manual code runs, no automated loop).  
  - Tests autonomy vs. one‑off LLM use.  
- **Simplified agent baseline**:  
  - Removes one key component (e.g., no long‑term memory, no planning loop, no self‑reflection).  
  - Serves as partial‑agent ablation.  
- **Original‑paper agents (if available)**:  
  - If the paper releases configs or prompts, include them as a reference.

***

### 3. Metrics to track

Design metrics that capture **research quality**, **autonomy**, and **cost**.[4](https://arxiv.org/html/2505.23852v1)[5](https://fugumt.com/fugumt/paper_check/2506.19724v1)[1](https://arxiv.org/abs/2501.04227)

#### 3.1 Research‑quality metrics

- **Result correctness**:  
  - For each target paper or task, define a set of key claims (e.g., “accuracy ≈ 0.85 ± 0.02 on X”).  
  - Binary: whether the agent reproduces each claim within an acceptable tolerance (e.g., 1–2 std).  
  - Score as fraction of claims reproduced.[4](https://arxiv.org/html/2505.23852v1)
- **Report quality**:  
  - Human‑rated Likert scale (e.g., 1–5) on clarity, completeness, methodology description, and discussion.  
- **Code quality**:  
  - Lint/CI pass rate, test coverage, and small human‑coded “readability” scores.  

#### 3.2 Agent‑behavior metrics

- **Step‑level success**:  
  - % of subtasks (e.g., “find related paper”, “run experiment X”, “plot curve”) that finish without crashes or manual fixes.  
- **Convergence trajectories**:  
  - Number of iterations until stable results (e.g., metric plateaus or meets target).  
- **Error modes**:  
  - Categorize failures (wrong dataset, misinterpretation of paper, loop bugs, tool misuse, etc.).  

#### 3.3 Efficiency / cost metrics

- **Wall‑time**: total elapsed time for the full pipeline.  
- **LLM cost**: token counts (prompt/completion) per major stage (search, planning, coding, writing).  
- **Human‑effort proxy**:  
  - Number of manual interventions (e.g., fixing code, re‑prompting, resetting state).  

***

### 4. Ablation design

Fix the core task (e.g., 3–5 seed research‑idea prompts) and vary one component at a time.[6](https://bohrium.dp.tech/paper/arxiv/2404.04442)[3](https://arxiv.org/html/2504.18765v2)[2](https://arxiv.org/html/2508.12752v1)

Typical ablations to run:

- **Planning style**:  
  - No planning (single‑step agent) vs. Chain‑of‑Thought (CoT) vs. Tree‑of‑Thought (ToT) or iterative planning.  
- **Memory**:  
  - No long‑term memory vs. vector‑store memory vs. explicit memory bookkeeping.  
- **Tool‑use**:  
  - No external tools (just LLM) vs. file‑system + code‑interpreter vs. web search + code‑runner.  
- **Self‑reflection**:  
  - No self‑critique vs. reflection after each experiment vs. LLM‑as‑judge on intermediate outputs.[7](https://developers.openai.com/cookbook/examples/partners/self_evolving_agents/autonomous_agent_retraining/)
- **Human‑in‑the‑loop frequency**:  
  - 0 (fully autonomous), few check‑points (e.g., after each major phase), vs. human‑guided at each step.[8](https://agentrxiv.github.io/resources/agentrxiv.pdf)[1](https://arxiv.org/abs/2501.04227)

Each ablation should share the same:
- LLM backbone (e.g., GPT‑4o or a specific open‑source model).
- Task set (e.g., 3 predefined research projects).
- Evaluation criteria and metrics.

***

### 5. Computational budget considerations

To keep replication feasible, especially if you’re running on modest hardware, structure the budget explicitly.[3](https://arxiv.org/html/2504.18765v2)[1](https://arxiv.org/abs/2501.04227)

#### 5.1 Hardware and environment

- Fix one **LLM model** (or one small family) and one **tool‑runner** (e.g., local Python sandbox or Colab‑style executor).  
- Describe:
  - GPU/CPU specs and memory limits.  
  - Any caching (e.g., memoize repeated API calls, store dataset snapshots).  

#### 5.2 Token‑ and time‑based caps

For each experiment run:

- **Per‑task token budget**: hard cap on total prompt+completion tokens per project (e.g., 2M–5M tokens).[1](https://arxiv.org/abs/2501.04227)[3](https://arxiv.org/html/2504.18765v2)
- **Per‑run wall‑time limit**: e.g., 48–72 hours per full project.  
- **Retries**: allow up to 3 full restarts per project (to avoid “infinite” loops), always logging why you restarted.

#### 5.3 Resource‑efficient design choices

- **Small‑scale tasks first**:  
  - Run 1–2 toy “mini‑projects” (e.g., MNIST / small‑NLP) to debug the pipeline before scaling to full‑scale tasks.  
- **Parallelism**:  
  - If possible, run multiple projects in parallel (e.g., 3 projects × 2 agents) to amortize wall‑time.  
- **Automatic logging**:  
  - Log every plan, code diff, and metric snapshot to disk so you can analyze without rerunning everything.[9](https://jimmysong.io/ai/agent-laboratory/)[8](https://agentrxiv.github.io/resources/agentrxiv.pdf)

***

### 6. Table outline for results (Markdown)

Here’s a compact table structure you can adapt; each row corresponds to one agent configuration × project, and scores can be averaged across projects.

```markdown
| Config ID | System variant | Planning | Memory | Tools | Self‑reflection | Human‑loop | Claims repro. (%) | Report quality (avg) | Steps solved (%) | LLM cost (tokens) | Time (hours) | Notes |
|-----------|----------------|----------|--------|-------|-----------------|------------|-------------------|-----------------------|-------------------|-------------------|-------------|-------|
| 1         | Human baseline | Manual   | None   | None  | None            | Full       | 100.0             | 4.8                   | 100.0             | 0 (non‑LLM)       | 168.0       | Ideal upper bound |
| 2         | LLM chatbot    | None     | None   | Code interpreter | None | Mixed      | 60.0              | 3.5                   | 75.0              | 2.1M              | 120.0       | Many prompts |
| 3         | No‑plan agent  | None     | Short  | Code, search | None      | Low        | 55.0              | 3.2                   | 70.0              | 1.8M              | 90.0        | Tends to loop |
| 4         | CoT agent      | CoT      | Short  | Code, search | None      | Low        | 68.0              | 3.9                   | 82.0              | 2.4M              | 108.0       | Uses step‑wise plans |
| 5         | CoT + memory   | CoT      | Long   | Code, search | None      | Low        | 72.0              | 4.1                   | 85.0              | 2.7M              | 112.0       | Caches findings |
| 6         | CoT + ref.     | CoT      | Long   | Code, search | Yes (LLM‑judge) | Low  | 78.0              | 4.3                   | 88.0              | 3.2M              | 120.0       | Self‑critique helps |
| 7         | Full‑original* | [As‑per‑paper] | [As‑per‑paper] | [As‑per‑paper] | [As‑per‑paper] | [As‑per‑paper] | 85.0              | 4.5                   | 92.0              | 3.8M              | 144.0       | From paper |
```

You can also add a **per‑project breakdown** in an appendix (average over projects, then per‑project details).

***

If you share the **exact title or arXiv ID** of the paper you’re replicating, I can tailor the baselines, metrics, and ablations even more tightly to that specific system.
