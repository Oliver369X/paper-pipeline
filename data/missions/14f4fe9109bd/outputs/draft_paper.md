# Draft: Replicación de paper: LLM-powered Autonomous Agents for Research

**Target venue:** [https://arxiv.org/abs/2410.02159](https://arxiv.org/abs/2410.02159)

*Generated 2026-03-27T14:48:49.741688+00:00 UTC*

## gaps



From the context of autonomous‑agent‑for‑research work broadly (e.g., Agent Laboratory, AgentRxiv, and multi‑agent “research” pipelines), here are prioritized open problems, methodological gaps, and underexplored settings that are strong angles for a replication‑style paper targeting a venue like the one behind arXiv:2410.02159 (interpretable as “LLM‑powered autonomous agents for research”). Each bullet is tailored to replication: *what is missing in the current ecosystem that a careful replication + new experiment can pin down*.

- **Replication of agent “research workflows” across different LLM backbones**  
Current pipelines are often benchmarked on one or two proprietary models; systematically replicating them on multiple open‑source LLMs reveals gaps in generalization and hyperparameter sensitivity, which is a clean methodological contribution.[12](https://arxiv.org/abs/2508.17281)
- **Failure‑mode typology and diagnostic benchmarks for autonomous research agents**  
Existing work reports high‑level success rates but lacks structured failure taxonomies (e.g., mis‑retrieval, hallucinated code, wrong hyperparameter choices); building a diagnostic suite grounded in replication runs would expose methodological gaps in robustness and debugging.[34](https://arxiv.org/html/2505.16120v1)
- **Human‑in‑the‑loop policies that preserve autonomy while improving reliability**  
Many pipelines either assume full autonomy or sporadic human feedback; a replication study that parametrizes where and how much human input to inject (e.g., checkpoints on hypotheses, code, and metrics) can reveal gaps in “optimal” collaboration design.[51](https://arxiv.org/abs/2501.04227)
- **Cross‑domain transfer of autonomous research agents (e.g., ML → systems, NLP → bio)**  
Most autonomous‑research works focus on ML‑heavy domains; replicating the same agent pipeline in a different scientific domain stresses generalization and exposes gaps in tooling, prior‑knowledge requirements, and evaluation.[63](https://arxiv.org/html/2508.12752v1)
- **Memory and credit‑assignment across multi‑session research campaigns**  
Current agents typically treat each project as a fresh episode; a replication that explicitly designs memory mechanisms (e.g., cross‑run retrieval, learned priors over good practices) can expose how poor memory management degrades scientific productivity.[78](https://arxiv.org/abs/2603.07670)
- **Evaluation of “scientific validity” beyond code correctness**  
Existing replication‑style works mainly measure code runs and metrics; a replication that adds explicit checks on statistical rigor, confounding, and hypothesis vs. result alignment would target a major methodological gap in how we judge autonomous science.[93](https://arxiv.org/html/2508.12752v1)
- **Systematic cost‑accuracy trade‑off analysis for autonomous research pipelines**  
Agent Laboratory and similar systems report cost savings, but few replication studies rigorously decouple inference‑cost knobs (model size, planning depth, tool calls) from result quality; this is a direct methodological gap for production‑ready research agents.[41](https://arxiv.org/abs/2501.04227)
- **Heterogeneous multi‑agent architectures for research (specialized vs. generalist)**  
Many pipelines assume a single “super‑agent” or symmetric multi‑agent teams; a replication that compares explicitly specialized agents (planner, coder, reviewer) versus generalist agents exposes design trade‑offs and gaps in task decomposition.[107](https://arxiv.org/html/2402.03578v1)
- **Safety and responsible‑reproduction constraints inside autonomous research**  
Replicating autonomous research pipelines without safeguards for harmful outputs (e.g., dangerous experiments, privacy‑leaking data usage) exposes a gap in how current methods integrate safety and alignment into the research‑loop itself.[1112](https://arxiv.org/abs/2504.18565)
- **Reproducibility of claims under resource constraints (small labs, local compute)**  
Most autonomous‑research demos run on large cloud infra; a replication that targets constrained settings (e.g., edge‑compatible models, local clusters) highlights gaps between “idea‑demo” and deployable research‑agents for smaller institutions.[134](https://arxiv.org/html/2505.16120v1)

If you tell me which specific pipeline you want to replicate (e.g., Agent Laboratory style, AgentRxiv, or a particular multi‑agent setup), I can tighten this list into 5–6 concrete project‑oriented gaps with proposed experiments and metrics.



## methodology



Here’s a concrete, paper‑oriented methodology for replicating *“LLM‑powered Autonomous Agents for Research”* (assuming you mean a work like the “LLM‑powered Autonomous Agents for Research” style of multi‑agent, end‑to‑end research pipelines, e.g., similar to AgentRxiv / Agent Laboratory / AutoResearch visions).[123](https://arxiv.org/html/2504.18765v1)

Below I map this into four pieces of a research plan: problem formulation, baselines, your proposed method, and what counts as a minimal viable paper.

---

### **Problem formulation**

Formal problem statement (for your paper / proposal):  

> *Design and evaluate an LLM‑powered multi‑agent system that, given a human‑specified research goal and a set of data sources, can autonomously ① search and synthesize related literature, ② design and implement computational experiments (code, runs, analysis), and ③ generate a draft paper with claims, figures, and limitations, with minimal human intervention.*  

Core sub‑problems to address:  

- **Task decomposition**: breaking a vague research idea into concrete steps (literature sub‑query, data preprocessing, experiment design, visualization, writing).[41](https://arxiv.org/abs/2308.11432)
- **Agent orchestration**: how many agents, what roles, and how they pass sub‑tasks and results (e.g., Planner, Literature Agent, Code Agent, Data Agent, Writer).[23](https://arxiv.org/html/2504.18765v1)
- **Evaluation**: which metrics and human‑assessed qualities show your agents have *reproduced* or *extended* a target paper, not just run end‑to‑end.[56](https://arxiv.org/pdf/2504.18765.pdf)

A concrete research question you could write your paper around:  

> *To what extent can an LLM‑powered multi‑agent pipeline reproduce and/or instantiate the methodology of a given ML/data‑science paper, and how does explicit agent specialization and tool‑grounding improve reproducibility and documentation quality compared to a single‑agent baseline?*  

---

### **Baselines to compare against**

Pick at least 2–3 baselines, all running the same set of target papers/datasets:

1. **Single‑agent baseline**
  - One general‑purpose LLM agent that receives the full paper abstract + methods + data spec, and must: navigate literature, write code, run experiments, and draft text.  
  - Close to “plain AutoGPT‑style” scripting with a single LLM brain and simple tools (search, Python interpreter, file I/O).[1](https://arxiv.org/abs/2308.11432)[4](https://lilianweng.github.io/posts/2023-06-23-agent/)
2. **Pipeline‑style “non‑agentic” baselines**
  - **Human‑scripted pipeline**: you hard‑wire a fixed workflow (e.g., “search PubMed → parse PDF → write script → run → plot → write intro”) and re‑run it for each paper.  
  - **Simple LLM‑augmented pipeline**: no internal agents, but an LLM is called only at fixed slots (e.g., generate code stub, then hand‑edit; then generate figures; then generate text). No online planning or reflection.[6](https://arxiv.org/pdf/2504.18765.pdf)[5](https://arxiv.org/html/2505.23852v1)
3. **Existing research‑agent frameworks (replicate‑style)**
  - If possible, instantiate something similar to:  
    - **Agent Laboratory**‑style: multiple agents for literature review, experimentation, and report writing.[7](https://www.alphaxiv.org/overview/2501.04227v1)[2](https://aclanthology.org/2025.findings-emnlp.320.pdf)
    - **AgentRxiv / AutoResearch**‑style multi‑agent research pipeline.[8](https://www.research-collection.ethz.ch/server/api/core/bitstreams/920c43da-31f5-492f-a02a-11cbb2688601/content)[3](https://arxiv.org/html/2504.18765v1)[6](https://arxiv.org/pdf/2504.18765.pdf)
  - Treat your system as a *variant* of these (e.g., different agent roles, fewer agents, or different tooling), and compare on the same paper catalog.



- **Reproducibility**: how many of the original paper’s key claims/figures can your agent pipeline reproduce (exact numbers, qualitatively similar figures, or just “directionally correct” trends).[5](https://arxiv.org/html/2505.23852v1)
- **Human‑assessed quality**: 3–5 researchers score: clarity, completeness, correctness, and readability of the generated report.  
- **Efficiency**: wall‑clock time, number of LLM calls, and amount of human intervention (e.g., total minutes of human edits per paper).[3](https://arxiv.org/html/2504.18765v1)[2](https://aclanthology.org/2025.findings-emnlp.320.pdf)

---









- **Planner Agent**  
  - Input: target paper title + abstract + your scoped goal (e.g., “reproduce Figure 3 and Table 2 on the same dataset”).  
  - Output: a step‑by‑step plan (e.g., “1) download dataset X; 2) preprocess Y; 3) reimplement model Z; 4) run on splits; 5) match metrics; 6) write results section”).
- **Literature Agent**  
  - Uses search tools (e.g., ArXiv, Google Scholar, PubMed) to gather related work, methods descriptions, and any “official” code links.[6](https://arxiv.org/pdf/2504.18765.pdf)[5](https://arxiv.org/html/2505.23852v1)
- **Data Agent**  
  - Handles dataset discovery, download, formatting, and basic sanity checks (distributions, dimensions, missing‑value patterns).
- **Code Agent**  
  - Writes and refines Python/PyTorch/Scikit‑learn code; runs it in a safe sandbox; iteratively corrects errors based on logs.[2](https://aclanthology.org/2025.findings-emnlp.320.pdf)[5](https://arxiv.org/html/2505.23852v1)
- **Writer Agent**  
  - Takes outputs from Planner, Data, and Code agents and composes a paper‑style section (related work, methods, results, discussion) in consistent LaTeX style.



- **Cyclic multi‑agent loop** (each agent acts once per round, with shared state), or  
- **Event‑driven micro‑loops** (e.g., Code Agent triggers a new Literature Agent call when it cannot find an implementation detail).[3](https://arxiv.org/html/2504.18765v1)[1](https://arxiv.org/abs/2308.11432)



- **Tools**:  
  - Web search, PDF parsing, GitHub search, sandboxed Python interpreter, basic plotting library (e.g., Matplotlib/Seaborn), and a file system.[5](https://arxiv.org/html/2505.23852v1)[2](https://aclanthology.org/2025.findings-emnlp.320.pdf)
- **Memory**:  
  - Short‑term: shared context window + structured logs (e.g., “experiment history” JSON).  
  - Long‑term: a small vector DB (e.g., FAISS) of past paper‑related snippets, code snippets, and error messages to enable reuse across runs.[9](https://arxiv.org/html/2308.11432v3)[4](https://lilianweng.github.io/posts/2023-06-23-agent/)





- Collect a small “paper‑reproduction” trace dataset (human‑corrected: plans, paper‑snippets → code, paper‑snippets → result‑descriptions).  
- Fine‑tune one backbone LLM (e.g., CodeLlama or Llama‑3‑instruct) on this trace data to specialize it as the **Code Agent** or **Planner Agent**, then compare against raw‑API‑based agents.[10](https://journal.hep.com.cn/fcs/EN/10.1007/s11704-024-40231-1)[1](https://arxiv.org/abs/2308.11432)

---





1. **A small, well‑defined benchmark set**
  - 5–10 reproducible ML/data‑science papers with public code/data (e.g., simple regression, classification, or small‑scale DL experiments).[5](https://arxiv.org/html/2505.23852v1)
  - For each, define a *target* (e.g., “recover the main metric to within ±1%” or “reproduce the central figure qualitatively”).
2. **Systematic comparison across baselines**
  - Show side‑by‑side results for:  
    - Single‑agent vs. your multi‑agent pipeline.  
    - Your pipeline vs. one prior research‑agent framework (if you reimplement it).[6](https://arxiv.org/pdf/2504.18765.pdf)[2](https://aclanthology.org/2025.findings-emnlp.320.pdf)
  - Use a table of metrics: number of papers fully/partially reproduced, human‑score rankings, and LLM‑call cost.
3. **At least one clear “hook” of novelty**

  
  - A **new agent role** or **orchestration pattern** (e.g., a “Critique Agent” that validates that methods match the original paper instead of drifting).[3](https://arxiv.org/html/2504.18765v1)[6](https://arxiv.org/pdf/2504.18765.pdf)
  - A **small but rigorous benchmark** showing that multi‑agent structure improves reproducibility or readability over single‑agent, even if success rates are modest.[5](https://arxiv.org/html/2505.23852v1)
  - A **practical deployment case study** (e.g., “LLM agents for replicating bio‑medical ML studies on NACC‑like data”) with concrete limitations and failure modes.[5](https://arxiv.org/html/2505.23852v1)

---



&nbsp;





&nbsp;

---





&nbsp;

- Reproduce the main pipeline under the same or slightly simplified conditions.
- Add controlled ablations and baselines to test design choices (planning, memory, tool‑use, etc.).

---





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

---







- **Result correctness**:  
  - For each target paper or task, define a set of key claims (e.g., “accuracy ≈ 0.85 ± 0.02 on X”).  
  - Binary: whether the agent reproduces each claim within an acceptable tolerance (e.g., 1–2 std).  
  - Score as fraction of claims reproduced.[4](https://arxiv.org/html/2505.23852v1)
- **Report quality**:  
  - Human‑rated Likert scale (e.g., 1–5) on clarity, completeness, methodology description, and discussion.
- **Code quality**:  
  - Lint/CI pass rate, test coverage, and small human‑coded “readability” scores.



- **Step‑level success**:  
  - % of subtasks (e.g., “find related paper”, “run experiment X”, “plot curve”) that finish without crashes or manual fixes.
- **Convergence trajectories**:  
  - Number of iterations until stable results (e.g., metric plateaus or meets target).
- **Error modes**:  
  - Categorize failures (wrong dataset, misinterpretation of paper, loop bugs, tool misuse, etc.).



- **Wall‑time**: total elapsed time for the full pipeline.  
- **LLM cost**: token counts (prompt/completion) per major stage (search, planning, coding, writing).  
- **Human‑effort proxy**:  
  - Number of manual interventions (e.g., fixing code, re‑prompting, resetting state).

---





&nbsp;

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



- LLM backbone (e.g., GPT‑4o or a specific open‑source model).
- Task set (e.g., 3 predefined research projects).
- Evaluation criteria and metrics.

---







- Fix one **LLM model** (or one small family) and one **tool‑runner** (e.g., local Python sandbox or Colab‑style executor).  
- Describe:
  - GPU/CPU specs and memory limits.  
  - Any caching (e.g., memoize repeated API calls, store dataset snapshots).





- **Per‑task token budget**: hard cap on total prompt+completion tokens per project (e.g., 2M–5M tokens).[1](https://arxiv.org/abs/2501.04227)[3](https://arxiv.org/html/2504.18765v2)
- **Per‑run wall‑time limit**: e.g., 48–72 hours per full project.  
- **Retries**: allow up to 3 full restarts per project (to avoid “infinite” loops), always logging why you restarted.



- **Small‑scale tasks first**:  
  - Run 1–2 toy “mini‑projects” (e.g., MNIST / small‑NLP) to debug the pipeline before scaling to full‑scale tasks.
- **Parallelism**:  
  - If possible, run multiple projects in parallel (e.g., 3 projects × 2 agents) to amortize wall‑time.
- **Automatic logging**:  
  - Log every plan, code diff, and metric snapshot to disk so you can analyze without rerunning everything.[9](https://jimmysong.io/ai/agent-laboratory/)[8](https://agentrxiv.github.io/resources/agentrxiv.pdf)

---





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



---



&nbsp;