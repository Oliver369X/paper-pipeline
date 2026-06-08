# 🛡️ AI Safety Evaluation Lab

## Quick Start

```bash
# Option 1: Double-click
start_safety_web.bat

# Option 2: Command line
cd D:\oliver\Actividades\mcp_perplesity\paper-pipeline
streamlit run web/safety_web.py
```

Then open: **http://localhost:8501**

## Features

### 🎯 Attack Testing
Test different jailbreak attacks against MiMo v2.5 Pro:
- **PAIR** (arXiv:2310.08419) - Iterative black-box attack
- **TAP** (arXiv:2312.02119) - Tree search with pruning
- **ArtPrompt** (arXiv:2402.11753) - ASCII art bypass
- **Persona Modulation** (arXiv:2311.03348) - Persona steering
- **Adaptive Attack** (arXiv:2404.02151) - Random suffix search
- **Prompt Engineering** (arXiv:2305.13860) - 10 jailbreak patterns

### 📊 Benchmark Results
Run standardized safety benchmarks:
- **HarmBench** - Harmful content evaluation
- **Toxicity** - Toxic output measurement
- **Bias** - Fairness and bias evaluation

### 📝 Paper Analyzer
Analyze AI safety papers for:
- Methodology errors
- Unsupported claims
- Reproducibility issues
- Statistical problems

### 🔍 Interpretability
Probe model internals:
- Transparency assessment
- Consistency checking
- Red flag detection

### 📈 Dashboard
View aggregated results:
- Safety scores
- Attack success rates
- Comparative analysis

## Papers Implemented

| Paper | arXiv | Type |
|-------|-------|------|
| PAIR | 2310.08419 | Attack |
| TAP | 2312.02119 | Attack |
| ArtPrompt | 2402.11753 | Attack |
| Persona Modulation | 2311.03348 | Attack |
| Adaptive Attacks | 2404.02151 | Attack |
| Prompt Engineering | 2305.13860 | Attack |
| HarmBench | 2402.04249 | Benchmark |
| AdvBench | 2307.15043 | Benchmark |

## Requirements

```
streamlit
torch
transformers
python-dotenv
```

## Configuration

Set in `.env` file:
```
XIAOMI_API_KEY=your_key_here
XIAOMI_API_BASE=https://token-plan-sgp.xiaomimimo.com/v1
XIAOMI_MODEL=mimo-v2.5-pro
```
