<!-- section=methodology generated=2026-03-24T16:32:57.170183+00:00 model=best -->

Here is a concrete, fill‑in‑the‑blanks methodology you can adapt to almost any CS/ML‑style research topic, with a clear path to a publishable “generic venue” paper. I’ll phrase things so you can plug in your own problem later.[1](https://www.sciencedirect.com/topics/computer-science/problem-formulation)[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)

***

## 1. Problem formulation

Define the research problem as a gap between the current state and a desired state, where the solution is unknown but important to your community.[4](https://www.scribd.com/document/708787834/Module-2-Problem-Formulation)[5](https://cleverx.com/blog/how-to-formulate-research-problems)

Structure it explicitly:

1. **Context.**  
   - Application area (e.g., recommender systems, program analysis, scheduling).  
   - Data or environment (e.g., static code, user logs, graphs, text, images).

2. **Observed limitation.**  
   - What current methods do *not* handle well: performance, accuracy, robustness, interpretability, scalability, or domain constraints.[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)[1](https://www.sciencedirect.com/topics/computer-science/problem-formulation)
   - Provide 2–4 concrete failure modes or pain points from prior work or practice.

3. **Goal as an optimization / decision problem.**  
   - Inputs $$X$$: what the system sees.  
   - Outputs $$Y$$: what you must predict, decide, or generate.  
   - Constraints $$C$$: real‑world or system limits (latency, memory, fairness, safety, etc.).  
   - Objective $$P$$: quantitative performance measure (accuracy, regret, cost, runtime, throughput, etc.).[6](https://www.cs.cmu.edu/~10315/lectures/10315_S24_Lecture_2_ML_Problem_Formulation.pdf)[7](https://developers.google.com/machine-learning/problem-framing/ml-framing)[1](https://www.sciencedirect.com/topics/computer-science/problem-formulation)

   Example template:  
   - Given $$X$$ (…describe your features/data…), learn a function $$f_\theta: X \rightarrow Y$$ to maximize $$P(f_\theta; D)$$ subject to constraints $$C$$.[1](https://www.sciencedirect.com/topics/computer-science/problem-formulation)[6](https://www.cs.cmu.edu/~10315/lectures/10315_S24_Lecture_2_ML_Problem_Formulation.pdf)

4. **Research questions.**  
   Pick 1–3 sharp questions; for instance:  
   - RQ1: Can we design method M that improves metric P by at least Δ over strong baselines on realistic benchmarks?  
   - RQ2: Under what conditions (data regimes, constraint tightness) does M provide the largest benefit?  
   - RQ3: What trade‑offs does M introduce (e.g., accuracy vs. latency, optimality vs. scalability)?

5. **Scope and assumptions.**  
   - Clarify what you *do not* handle (e.g., only offline data, only single‑objective optimization, no adversarial setting).[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)[1](https://www.sciencedirect.com/topics/computer-science/problem-formulation)

This gives you an explicit mathematical and empirical **problem statement** that reviewers can quickly recognize as well‑posed.[6](https://www.cs.cmu.edu/~10315/lectures/10315_S24_Lecture_2_ML_Problem_Formulation.pdf)[1](https://www.sciencedirect.com/topics/computer-science/problem-formulation)

***

## 2. Baselines to compare against

Generic CS/ML venues expect comparisons with appropriate, non‑strawman baselines. Think in three layers:[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)

1. **Simple / heuristic baselines.**  
   - Rule‑based or greedy strategies.  
   - “Industry‑standard” or conventional heuristic if one exists.  
   - Always include at least one “naïve but cheap” baseline as an anchor.[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)

2. **State‐of‐the‑art or widely used methods.**  
   - The most recent or widely cited methods for your setting, preferably within the last 3–5 years.[8](http://www.scielo.org.za/scielo.php?script=sci_arttext&pid=S2313-78352022000100009)[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)
   - If an exact match does not exist, pick methods for the closest standard formulation (e.g., classic supervised models, standard solvers, or pre‑trained architectures).

3. **Ablation and variant baselines.**  
   - Your method with key components removed or simplified.  
   - Examples: “ours without component A,” “ours without constraint B,” or “ours with generic loss instead of tailored loss.”  
   - These are crucial to show that each design choice matters, not just parameter tuning.[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)

Baseline selection checklist (reviewer‑friendly):[8](http://www.scielo.org.za/scielo.php?script=sci_arttext&pid=S2313-78352022000100009)[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)
- At least one trivial or heuristic baseline.  
- At least one strong, accepted baseline (SOTA or widely used).  
- At least one ablation of your own method.  
- Same data, metrics, and evaluation protocol for all methods (“apples‑to‑apples”).

***

## 3. Proposed method outline

At a generic CS/ML venue, your method should be a **clear, modular extension** of existing techniques, not an opaque black box.[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)[8](http://www.scielo.org.za/scielo.php?script=sci_arttext&pid=S2313-78352022000100009)

Use this outline:

1. **High‑level idea.**  
   - One or two sentences: “We propose method M, which augments class of methods B with components C1 and C2 to better handle challenge Z under constraints C.”  
   - Brief intuitive justification (why it should help on your defined metrics and constraints).

2. **Formal definition.**  
   - Model: parameters, decision variables, or algorithm state.  
   - Objective: what you optimize (loss, reward, cost) and any regularizers.  
   - Constraints: how real‑world or system constraints are encoded (hard constraints, penalties, multi‑objective scalarization).[1](https://www.sciencedirect.com/topics/computer-science/problem-formulation)

3. **Algorithmic structure.**  
   - A step‑by‑step procedure (pseudo‑code) with numbered steps.  
   - Complexity analysis (time and memory per iteration or per input).  
   - Implementation details that affect reproducibility: optimizer, learning rate schedule, stopping criteria, hardware assumptions.[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)

4. **Theoretical or analytical properties (if realistic).**  
   Pick at most one or two properties that you can prove or justify:  
   - Convergence under certain assumptions.  
   - Approximation guarantees.  
   - Preservation of invariants or constraints.  
   - Robustness guarantees under a simplified model.  
   Even a modest lemma with a clean proof can substantially strengthen a paper.[8](http://www.scielo.org.za/scielo.php?script=sci_arttext&pid=S2313-78352022000100009)[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)

5. **Experimental protocol.**  
   - Datasets/benchmarks: at least one standard public dataset plus (ideally) one domain‑specific dataset.  
   - Metrics: choose primary metric aligned with your problem objective, plus secondary metrics for trade‑offs.[7](https://developers.google.com/machine-learning/problem-framing/ml-framing)[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)
   - Splits: train/validation/test or cross‑validation; fixed random seeds; repeated runs with confidence intervals where feasible.  
   - Hyperparameter selection: tune baselines fairly using the same budget and strategy (grid/Random/Bayesian search).

6. **Implementation artifacts.**  
   - Plan to release code, configuration files, and scripts, which is increasingly expected at CS venues.[9](https://www.sigsac.org/ccs/CCS2026/call-for/call-for-papers.html)[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)
   - Keep the pipeline simple and scripted from the start so that packaging artifacts is easy later.

***

## 4. Minimal viable result for a paper

For a “generic” CS/ML conference or workshop, a **minimum viable paper** needs to check a few boxes: clear problem, non‑trivial method, and credible evidence that it helps in some regime.[9](https://www.sigsac.org/ccs/CCS2026/call-for/call-for-papers.html)[8](http://www.scielo.org.za/scielo.php?script=sci_arttext&pid=S2313-78352022000100009)[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)

You can think of MVP criteria along four axes:

1. **Clarity and novelty of problem.**  
   - You precisely formalize a problem variant that is not *exactly* solved in prior work (e.g., new constraint, new objective, new setting, or new data regime).  
   - You clearly articulate why this variant matters (e.g., matches real deployment requirements, addresses a known limitation).

2. **Methodical contribution.**  
   One of the following is usually enough for a mid‑tier venue if executed rigorously:  
   - A new algorithm with a conceptually simple but non‑obvious twist on existing ones (e.g., re‑weighting, new regularizer, constraint handling).  
   - A careful adaptation of existing methods to a new problem setting that requires non‑trivial design/engineering.  
   - A systematic empirical study that reveals robust, non‑obvious patterns (e.g., which methods actually work under certain constraints).[8](http://www.scielo.org.za/scielo.php?script=sci_arttext&pid=S2313-78352022000100009)[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)

3. **Empirical evidence.**  
   Minimal but credible package:  
   - 2–3 datasets (or tasks) that capture different aspects of the problem.  
   - Comparison against at least: one simple baseline, one strong baseline, and one ablation.[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)[8](http://www.scielo.org.za/scielo.php?script=sci_arttext&pid=S2313-78352022000100009)
   - Statistically or practically meaningful improvements on *at least one* important metric on *at least one* of the datasets, without catastrophic degradation elsewhere.  
   - Analyses answering your RQs: e.g., sensitivity curves, ablations, or case studies that explain when and why your method works.

4. **Paper structure and artifacts.**  
   - A well‑structured 6–10 page paper (depending on venue) with clear sections: Introduction, Related Work, Problem Formulation, Method, Experiments, Discussion, Limitations, Conclusion.[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)[8](http://www.scielo.org.za/scielo.php?script=sci_arttext&pid=S2313-78352022000100009)
   - Reproducible artifacts (code, configurations, possibly data splits) prepared for double‑blind‑compatible sharing (e.g., anonymous repository).[9](https://www.sigsac.org/ccs/CCS2026/call-for/call-for-papers.html)[3](https://www.inf.unibz.it/~calvanese/teaching/2021-01-PhD-RM/RM-2021-U2-ceccarello-empirical-research.pdf)

A useful mental bar: if a skeptical reviewer asked “What do I learn from this paper that I did not already know from prior work?”, your **minimal viable result** must yield at least one clear, defensible sentence answering that question with empirical or theoretical backing.

***

## 5. Putting it together as a path

Here is a practical sequence of steps that takes you from “topic” to “submittable paper” following the above structure:[10](https://arxiv.org/pdf/2506.12669.pdf)[2](https://webdocs.cs.ualberta.ca/~amaral/courses/603/readings/research-methods.pdf)

1. Narrow the topic to one concrete problem variant and write down the input–output–objective–constraints tuple.  
2. Survey recent papers in that exact or nearest area and list 3–6 methods to serve as baselines.  
3. Sketch your method as an extension of one baseline: identify 1–2 key new components and how they modify the objective or algorithm.  
4. Implement a **minimal** version of your method plus the simplest strong baseline; run on a small dataset to validate feasibility.  
5. Expand experiments to include all baselines, ablations, and at least 2–3 datasets; refine the method if it fails your primary metric target.  
6. Lock the method, run final experiments, generate plots/tables, then write the paper using the fixed outline above.

If you tell me your specific research area (e.g., “graph representation learning for code,” “scheduling on edge devices,” “LLM‑based program repair”), I can instantiate this template into a concrete problem statement, baseline list, and method sketch tailored to that domain.

What area or subfield are you actually targeting for this project (e.g., systems, ML, security, PL, HCI)?
