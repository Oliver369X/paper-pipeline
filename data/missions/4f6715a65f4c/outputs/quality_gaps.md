<!-- quality_check: assisted review via same Perplexity stack as sections; not independent empirical validation. See docs/technical/EVALUATION_LAYERS.md -->

This draft is a strong **method‑oriented design document** for a follow‑on paper targeting the *“From Memorization to Reasoning in the Spectrum of Loss Curvature”* (arXiv:2510.24256) line of work, but it reads more like an internal experiment plan than a finished arXiv‑style manuscript. Below are concrete gaps grouped by type: missing/wrong citations, weak methodology, unclear experiments, ethical/safety issues, and formatting issues for the target venue.

***

### 1. Missing or weak citations

- **Under‑connecting to recent curvature‑based safety / alignment work:**  
  - Missing explicit citation to **curvature‑aware safety‑restoration** (e.g., “Curvature‑Aware Safety Restoration In LLMs Fine‑Tuning”, arXiv:2511.18039v1) when you mention “safety‑aware curvature” or “curvature‑aware regularization”, which is a natural fit for arXiv:2510.24256‑style follow‑ups.[1](https://arxiv.org/html/2511.18039v1)
- **Shallow ties to prior memorization‑via‑curvature work:**  
  - You mention earlier work on “memorization via curvature” only generically; a **direct citation to Garg et al., *“Memorization Through the Lens of Curvature of Loss Function…”*** (MLR v235) would strengthen the related‑work narrative.[2](https://proceedings.mlr.press/v235/garg24a.html)[3](https://proceedings.mlr.press/v235/ravikumar24a.html)
- **Inconsistent citation style:**  
  - URLs are used inline as Markdown `[](https://…)` but many are **non‑archival** (blog posts, Reddit, social‑media, Medium‑style articles) and should either be **converted to standard bibliographic entries** or moved to an appendix with a brief note on “informal discussions”.

***

### 2. Weak / incomplete methodology

- **No explicit choice of base model or hyperparameters:**  
  - The text suggests OLMo‑2‑1B/2B or Llama‑style models, but **does not specify a concrete architecture / checkpoint** (e.g., “Llama‑2‑2B‑hf fine‑tuned on X”), nor key training / data‑split protocols; this leaves the replication exercise under‑specified for arXiv‑style reusability.  
- **Curvature‑estimation data left vague:**  
  - You describe “a representative slice of training / validation data” for the K‑FAC pass, but **no concrete subset** (e.g., “10k Dolma‑style sentences with memorizable patterns”) is fixed; this weakens the reproducibility claim for arXiv‑style computational work.  
- **Editing procedure is schematic, not executable:**  
  - The weight‑editing formula is given in closed‑form, but the **implementation details** (e.g., how to handle tied / repeated eigenvalues, numerical tolerances, handling of near‑zero curvature modes) are missing; this is a weak point for a venue that expects clear, reproducible methods.  

***

### 3. Unclear‑to‑invalid experiments

- **Results table is purely illustrative; no real numbers:**  
  - The Markdown table shows **made‑up percentages** (e.g., “‑92.1%”, “‑23.4%”) with no indication that these are placeholders; readers may mistake them for reported results unless you explicitly mark them as `TODO` or `Example values` near the table.  
- **No concrete experiment identifiers:**  
  - The draft does not define **experiment IDs** (e.g., “Experiment‑1: K‑FAC‑0.5 on LLM‑2B‑mem‑split‑A”), which makes it hard to refer back to “Fig.‑3 corresponds to Experiment‑4” in a paper‑style text.  
- **No randomness‑control section:**  
  - Although you mention 3–5 seeds, you **do not spell out a fixed random seed strategy** (e.g., “all runs use `seed=42`; only curvature‑estimation data is shuffled”); this is a small but real threat to validity for arXiv submissions.  

***

### 4. Ethical and safety‑related omissions

- **Privacy‑motivated unlearning angle is under‑grounded:**  
  - The draft positions curvature‑based editing as a privacy‑oriented unlearning tool, but **does not benchmark on any privacy‑relevant metric** (e.g., membership‑inference on sensitive data, PII‑memorization tests); for arXiv‑style transparency, it should either add such a benchmark or explicitly state that this is a conceptual link, not a tested one.  
- **Safety‑impact discussion is speculative:**  
  - The safety‑alignment discussion is appropriately cautious, but the manuscript would benefit from **a short “Limitations” subsection explicitly stating that hallucination / bias / jailbreak‑robustness were not measured** and that those claims are extrapolations.  

***

### 5. Formatting and “arXiv‑style” fit issues

- **Blob‑style Markdown instead of LaTeX‑style paper structure:**  
  - The draft is laid out as a **single long Markdown document** with interleaved sections, rather than a clean separation of `abstract`, `introduction`, `method`, `experiments`, `discussion`, `limitations`, and `reproducibility`. For arXiv‑style fit, it either needs to be converted to LaTeX (or `arxiv‑lwpaper`‑style Markdown) or explicitly framed as an **experimental design report**, not a paper.  
- **Equation rendering is inconsistent:**  
  - Some equations are given in LaTeX `$$...$$`, but the Markdown is not wrapped in a LaTeX‑aware environment; this looks fine in GH‑style Markdown but **will not render correctly on arXiv PDFs** unless the manuscript is actually compiled via LaTeX.  
- **“Replication status” / `outputs/*` artifacts are non‑arXiv‑appropriate:**  
  - The top‑of‑file block with `outputs/metrics.json`, `outputs/replication_status.md`, etc., is useful for internal tooling but **belongs in a separate repo report**, not in the main arXiv‑style draft.  
- **Section‑embedded LLM‑disclaimer is helpful but not enough:**  
  - The LLM‑assistant disclaimer is good, but for arXiv‑style transparency you should add a **short “Author contributions” sentence** (e.g., “All experiments and code were implemented by the authors; this text was drafted with LLM assistance and then manually verified.”).  

***

### 6. Reproducibility‑specific weak points

- **CPU‑only / small‑model reproducibility is asserted but not benchmarked:**  
  - The draft claims that the method is CPU‑friendly, but the text only describes it in abstract; a **minimal “reproducibility recipe”** (e.g., “Step 1: …; Step 2: …; hardware constraints”) would strengthen the fit with arXiv‑style expectations for reproducible ML research.  
- **No explicit “minimal runtime / memory budget” table:**  
  - Adding a tiny table (or paragraph) such as “K‑FAC‑estimation on 2B‑model takes ≈X hours on 1×A100‑40GB; editing step runs in ≈Y minutes on CPU” would make the paper‑oriented narrative more concrete for arXiv‑style readers.  

***

If you want, I can help you **refactor the current draft** into a 5–7‑section arXiv‑style outline (Abstract, Intro, Method, Experiments, Discussion, Limitations, Reproducibility) that addresses these gaps and explicitly targets arXiv:2510.24256‑style follow‑up work.
