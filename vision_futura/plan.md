# Paper-Pipeline 2.0: Arquitectura Revolucionaria para Investigación Autónoma de Grado Científico
## Executive Summary
Paper-Pipeline 2.0 representa la evolución desde un orquestador de investigación asistida hacia un **ecosistema autónomo de investigación científica de grado publicable**, eliminando los cuellos de botella humanos manteniendo estándares de calidad equiparables o superiores a la revisión por pares tradicional.[1][2]

El sistema integra:
- **Validación científica multi-agente** con verificación cruzada entre 5+ modelos especializados
- **Peer review sintético** basado en metodologías de crowdsourcing y co-determinación algorítmica[3][4]
- **Plataforma de publicación web** con reproducibilidad completa y DOI automático
- **82+ skills + 7 servidores MCP** para automatización vertical profunda
- **Pipeline de experimentación** con documentación end-to-end automática[5][6]

El objetivo: **revolucionar la investigación científica acelerando el ciclo desde hipótesis hasta publicación replicable en 10-100x, sin sacrificar rigor**.
## I. Visión del Sistema Revolucionario
### 1.1 Filosofía de Diseño
El sistema se construye sobre cinco pilares de reproducibilidad computacional:[7][8]

1. **Programación literaria**: Código y narrativa entrelazados (Jupyter + mission.md + outputs/)
2. **Control de versiones**: Git + GitHub como backbone de trazabilidad
3. **Control del entorno computacional**: Docker + conda + requirements.txt versionados
4. **Compartición persistente de datos**: Zenodo + FigShare + DOIs automáticos
5. **Documentación**: Generación automática de artefactos según estándares ACM[1][9]
### 1.2 Principios de Autonomía con Validación
**Autonomía operativa sin supervisión humana en el loop**:
- Toda decisión de investigación debe ser auditable y reversible
- Múltiples validadores automáticos sustituyen revisión humana
- Benchmarks contra papers publicados establecen "calidad mínima publicable"
- Degradación graceful cuando la confianza cae bajo umbrales

**Calidad "mega buena" mediante**:
- Revisión por pares sintética con 5-7 perspectivas simuladas[10][11]
- Validación cruzada de cada afirmación en 3+ fuentes independientes
- Tests de replicabilidad automáticos antes de publicación
- Auditorías de sesgo, plagio y calidad metodológica[12][13]
### 1.3 Componentes del Ecosistema Revolucionario
```
┌─────────────────────────────────────────────────────────────────┐
│                     PAPER-PIPELINE 2.0                           │
│                  Ecosistema Autónomo de Investigación            │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─► [NÚCLEO] Orquestador Multi-Agente
         │    ├─ Research Agent (Perplexity + Claude Sonnet 4.6)
         │    ├─ Code Agent (Cursor Composer 2 Fast)
         │    ├─ Quality Agent (GPT-4o + Gemini 2.0)
         │    ├─ Peer Review Agent (Multi-model ensemble)
         │    └─ Meta-Orchestrator (Perplexity revisor)
         │
         ├─► [VALIDACIÓN] Sistema de Calidad Científica
         │    ├─ Fact Checker (5+ fuentes por claim)
         │    ├─ Methodology Validator (contra estándares de venue)
         │    ├─ Statistical Rigor Checker
         │    ├─ Bias Detector (técnico, demográfico, metodológico)
         │    ├─ Plagiarism Scanner (integración TestSprite MCP)
         │    └─ Replication Tester (ejecuta experimentos en sandbox)
         │
         ├─► [PEER REVIEW] Revisión Sintética Multi-Perspectiva
         │    ├─ Reviewer Simulator 1-7 (perfiles de expertos)
         │    ├─ Co-determination Algorithm (agregación bayesiana)[cite:24]
         │    ├─ Feedback Synthesis (Review Feedback Agent)[cite:29]
         │    ├─ Conflict Resolution (cuando revisores divergen)
         │    └─ Acceptance Predictor (probabilidad de aceptación)
         │
         ├─► [EXPERIMENTACIÓN] Sistema End-to-End Reproducible
         │    ├─ Experiment Tracker (metadata + lineage)[cite:9]
         │    ├─ Environment Snapshotter (Docker + conda)
         │    ├─ Data Versioning (DVC integration)
         │    ├─ Results Validator (statistical tests)
         │    └─ Artifact Packager (capsule reproducible)[cite:12]
         │
         ├─► [PUBLICACIÓN] Plataforma Web Completa
         │    ├─ Static Site Generator (GitHub Pages + Jekyll)
         │    ├─ DOI Minter (Zenodo API)
         │    ├─ Interactive Viewer (Observable + D3.js)
         │    ├─ Comment System (utterances.es GitHub Issues)
         │    └─ Citation Tracker (Semantic Scholar API)
         │
         ├─► [SKILLS LAYER] 82+ Skills Especializadas
         │    ├─ superpowers/* (brainstorming, TDD, debugging)
         │    ├─ vercel/* (web deployment, functions, workflows)
         │    ├─ huggingface/* (models, datasets, training, Gradio)
         │    ├─ notion/* (knowledge capture, task tracking)
         │    └─ Custom skills (research, finance, chart, slides)
         │
         └─► [MCP LAYER] 7 Servidores de Contexto
              ├─ Firecrawl (scraping inteligente)
              ├─ Playwright (testing E2E)
              ├─ GitHub (repos, issues, PRs)
              ├─ Notion (documentación + tracking)
              ├─ Perplexity Web (research profundo)
              ├─ TestSprite (testing + validación)
              └─ Binance (datos financieros para estudios)
```
## II. Arquitectura Técnica Profunda
### 2.1 Sistema de Validación Científica Multi-Capa
#### 2.1.1 Fact Checking Automático

**Pipeline de Verificación**:
```python
class FactValidator:
    """
    Valida cada afirmación contra 5+ fuentes independientes.
    Inspirado en: computational reproducibility frameworks[cite:8]
    """
    def validate_claim(self, claim: str, context: ResearchContext):
        # 1. Extracción de afirmaciones verificables
        checkable_facts = self.extract_checkable_facts(claim)
        
        # 2. Búsqueda paralela en 5+ fuentes
        sources = await asyncio.gather(
            self.perplexity_search(claim),
            self.semantic_scholar_search(claim),
            self.google_scholar_search(claim),
            self.arxiv_search(claim),
            self.pubmed_search(claim)  # Si aplica
        )
        
        # 3. Votación ponderada por reputación de fuente
        consensus = self.weighted_vote(sources, weights={
            'peer_reviewed': 1.0,
            'preprint': 0.7,
            'blog_authoritative': 0.5,
            'news': 0.3
        })
        
        # 4. Nivel de confianza bayesiano
        confidence = self.bayesian_confidence(consensus)
        
        return ValidationResult(
            claim=claim,
            verdict="VERIFIED" if confidence > 0.85 else "DISPUTED",
            confidence=confidence,
            sources=sources,
            conflicts=self.identify_conflicts(sources)
        )
```

**Integración con MCP**:
- **Firecrawl MCP**: Extracción de contenido de papers detrás de paywalls
- **Perplexity Web MCP**: Búsqueda profunda con citación automática
- **GitHub MCP**: Verificación contra repos de código abierto

#### 2.1.2 Methodology Validator

Valida metodología contra estándares de venue específico:

```python
class MethodologyValidator:
    """
    Verifica metodología contra checklist de venue (NeurIPS, ICML, etc.)
    """
    VENUE_STANDARDS = {
        'NeurIPS': {
            'required_sections': ['abstract', 'intro', 'related_work', 
                                  'methodology', 'experiments', 'conclusion'],
            'reproducibility': {
                'code_required': True,
                'data_availability': 'required_or_justified',
                'hyperparameters': 'all_disclosed',
                'compute_resources': 'documented'
            },
            'statistical_rigor': {
                'error_bars': True,
                'significance_tests': True,
                'multiple_runs': 'required_min_3'
            },
            'ethics': {
                'broader_impact': True,
                'data_privacy': 'if_applicable',
                'potential_harms': 'discussed'
            }
        },
        'ICML': {...},  # Similar pero variaciones
        'ICLR': {...}
    }
    
    def validate(self, paper: ResearchPaper, target_venue: str):
        standards = self.VENUE_STANDARDS[target_venue]
        violations = []
        
        # Check secciones requeridas
        for section in standards['required_sections']:
            if section not in paper.sections:
                violations.append(f"Missing required section: {section}")
        
        # Reproducibilidad
        if standards['reproducibility']['code_required']:
            if not paper.has_code_artifact:
                violations.append("Code not provided (required by venue)")
        
        # ... más validaciones
        
        return MethodologyReport(
            venue=target_venue,
            compliant=len(violations) == 0,
            violations=violations,
            suggestions=self.generate_fixes(violations)
        )
```

#### 2.1.3 Statistical Rigor Checker

Ejecuta análisis estadístico sobre experimentos reportados:

```python
class StatisticalRigorChecker:
    """
    Valida rigor estadístico de experimentos.
    Detecta p-hacking, múltiples comparaciones sin corrección, etc.
    """
    def analyze_experiments(self, results: ExperimentResults):
        issues = []
        
        # Detectar p-hacking
        if self.detect_p_hacking(results.p_values):
            issues.append(PValueManipulation(
                description="P-values suspiciously close to 0.05",
                severity="HIGH"
            ))
        
        # Verificar corrección de múltiples comparaciones
        if len(results.comparisons) > 1:
            if not results.uses_bonferroni_correction():
                issues.append(MultipleComparisonIssue(
                    num_comparisons=len(results.comparisons),
                    correction_used=None,
                    recommendation="Apply Bonferroni or FDR correction"
                ))
        
        # Verificar poder estadístico
        for test in results.statistical_tests:
            power = self.calculate_statistical_power(test)
            if power < 0.8:
                issues.append(LowPowerWarning(
                    test=test.name,
                    power=power,
                    recommendation="Increase sample size or effect size"
                ))
        
        return StatisticalReport(issues=issues)
```
### 2.2 Peer Review Sintético: Metodología Detallada
#### 2.2.1 Generación de Revisores Sintéticos

**Inspiración**: Readersourcing y crowdsourced peer review[3][4]

```python
class SyntheticReviewerPool:
    """
    Genera pool de 7 revisores sintéticos con perspectivas diversas.
    Cada revisor es un agente LLM con prompt especializado.
    """
    
    REVIEWER_PROFILES = [
        {
            'id': 'methodologist',
            'model': 'claude-sonnet-4.6-thinking',
            'persona': """Eres un experto metodólogo con doctorado en estadística.
                         Tu enfoque: rigor experimental, validez interna/externa,
                         diseño de estudios. Eres escéptico de afirmaciones causales
                         sin evidencia experimental sólida.""",
            'focus_areas': ['methodology', 'statistics', 'experimental_design'],
            'strictness': 0.9  # 0-1, donde 1 = muy estricto
        },
        {
            'id': 'practitioner',
            'model': 'gpt-4o',
            'persona': """Eres un ingeniero senior con 15+ años en industria.
                         Tu enfoque: aplicabilidad práctica, escalabilidad,
                         costos computacionales. Valoras reproducibilidad
                         y código claro sobre complejidad teórica.""",
            'focus_areas': ['practical_impact', 'scalability', 'code_quality'],
            'strictness': 0.6
        },
        {
            'id': 'theorist',
            'model': 'gemini-2.0-flash-thinking',
            'persona': """Eres un teórico con formación matemática profunda.
                         Tu enfoque: formalismo, garantías teóricas, elegancia.
                         Buscas proofs rigurosos y bounds no triviales.""",
            'focus_areas': ['theory', 'formal_guarantees', 'complexity'],
            'strictness': 0.85
        },
        {
            'id': 'domain_expert',
            'model': 'claude-sonnet-4.6-thinking',
            'persona': """Eres experto en [DOMINIO_ESPECIFICO] con 20+ publicaciones.
                         Tu enfoque: conocimiento del estado del arte, novelty,
                         comparación justa con baselines. Conoces todas las
                         sutilezas del dominio.""",
            'focus_areas': ['domain_knowledge', 'related_work', 'novelty'],
            'strictness': 0.8
        },
        {
            'id': 'reproducibility_champion',
            'model': 'gpt-4o',
            'persona': """Eres defensor de ciencia abierta y reproducibilidad.
                         Tu enfoque: ¿código disponible? ¿datos abiertos?
                         ¿experimentos replicables? ¿documentación clara?""",
            'focus_areas': ['reproducibility', 'open_science', 'documentation'],
            'strictness': 0.75
        },
        {
            'id': 'ethics_reviewer',
            'model': 'claude-sonnet-4.6-thinking',
            'persona': """Eres especialista en ética de IA y broader impact.
                         Tu enfoque: sesgos, fairness, privacidad, riesgos
                         societales, dual use. Análisis crítico de implicaciones.""",
            'focus_areas': ['ethics', 'fairness', 'societal_impact'],
            'strictness': 0.7
        },
        {
            'id': 'generalist_senior',
            'model': 'perplexity-claude',
            'persona': """Eres senior researcher con breadth extremo.
                         Tu enfoque: visión holística, conexiones entre campos,
                         clarity de escritura, contribution statement claro.""",
            'focus_areas': ['clarity', 'significance', 'presentation'],
            'strictness': 0.65
        }
    ]
    
    def generate_review(self, reviewer_profile: dict, paper: ResearchPaper):
        """
        Genera review detallada desde perspectiva de un revisor.
        """
        prompt = f"""
{reviewer_profile['persona']}

Revisar el siguiente paper:

**Título**: {paper.title}
**Abstract**: {paper.abstract}
**Contenido completo**: 
{paper.full_content}

Tu tarea: Proveer review estructurada con:

1. **Summary** (2-3 oraciones): ¿Qué hace el paper?
2. **Strengths** (lista numerada): Aspectos positivos
3. **Weaknesses** (lista numerada): Problemas identificados
4. **Questions** (lista): Preguntas para autores
5. **Detailed Feedback** (por sección): Comentarios específicos
6. **Recommendation**: STRONG_ACCEPT | ACCEPT | WEAK_ACCEPT | BORDERLINE | WEAK_REJECT | REJECT | STRONG_REJECT
7. **Confidence**: 1-5 (5 = absolutamente seguro en tu dominio)

Enfócate especialmente en: {', '.join(reviewer_profile['focus_areas'])}

Sé riguroso pero constructivo. Provee feedback accionable.
"""
        
        response = await self.llm_call(
            model=reviewer_profile['model'],
            prompt=prompt,
            temperature=0.3  # Baja para consistencia
        )
        
        return Review(
            reviewer_id=reviewer_profile['id'],
            summary=response.summary,
            strengths=response.strengths,
            weaknesses=response.weaknesses,
            questions=response.questions,
            detailed_feedback=response.detailed_feedback,
            recommendation=response.recommendation,
            confidence=response.confidence,
            focus_areas=reviewer_profile['focus_areas']
        )
```

#### 2.2.2 Algoritmo de Co-Determinación

**Inspirado en**: Readersourcing Model[3]

```python
class ReviewAggregator:
    """
    Agrega reviews de múltiples revisores sintéticos usando
    co-determinación bayesiana (no simple promedio).
    """
    
    def aggregate_reviews(self, reviews: List[Review], paper: ResearchPaper):
        """
        Implementa modelo de agregación que captura aspectos
        distintos vs. simple mean/median[cite:24].
        """
        
        # 1. Normalizar scores por strictness del revisor
        normalized_scores = []
        for review in reviews:
            reviewer_profile = self.get_profile(review.reviewer_id)
            strictness = reviewer_profile['strictness']
            
            # Ajustar score por strictness (revisor estricto = score más alto vale más)
            adjusted = self.normalize_by_strictness(
                review.recommendation,
                strictness
            )
            normalized_scores.append(adjusted)
        
        # 2. Ponderación por confianza + expertise en dominio
        weights = []
        for review in reviews:
            confidence_weight = review.confidence / 5.0  # Normalizar a 0-1
            
            # Domain expertise weight: revisor experto en área del paper
            domain_match = self.calculate_domain_match(
                review.focus_areas,
                paper.research_areas
            )
            
            final_weight = confidence_weight * (0.5 + 0.5 * domain_match)
            weights.append(final_weight)
        
        # 3. Agregación bayesiana
        aggregated_score = self.bayesian_aggregate(
            normalized_scores,
            weights,
            prior=self.get_venue_prior(paper.target_venue)
        )
        
        # 4. Detección de consenso vs. controversia
        variance = np.var(normalized_scores)
        if variance > threshold:
            consensus_status = "CONTROVERSIAL"
            # Solicitar meta-review o revisor adicional
        else:
            consensus_status = "CONSENSUS"
        
        # 5. Síntesis de feedback
        synthesized_feedback = self.synthesize_feedback(reviews)
        
        return AggregatedReview(
            final_score=aggregated_score,
            recommendation=self.score_to_recommendation(aggregated_score),
            consensus_status=consensus_status,
            individual_reviews=reviews,
            synthesized_strengths=synthesized_feedback.strengths,
            synthesized_weaknesses=synthesized_feedback.weaknesses,
            critical_questions=synthesized_feedback.questions,
            acceptance_probability=self.predict_acceptance(aggregated_score, paper.target_venue)
        )
    
    def synthesize_feedback(self, reviews: List[Review]):
        """
        Usa Review Feedback Agent[cite:29] para sintetizar feedback
        constructivo y específico de múltiples revisores.
        """
        prompt = f"""
Dado el siguiente conjunto de {len(reviews)} reviews de expertos:

{self.format_reviews(reviews)}

Tu tarea:
1. Identificar temas comunes en strengths (reportados por 2+ revisores)
2. Identificar temas comunes en weaknesses (reportados por 2+ revisores)
3. Consolidar preguntas (eliminar duplicados, agrupar relacionadas)
4. Generar lista priorizada de acciones para autores

Output formato:
**Synthesized Strengths**: [lista]
**Synthesized Weaknesses**: [lista priorizada por severidad]
**Critical Questions**: [lista]
**Recommended Actions**: [lista priorizada]
"""
        
        response = await self.llm_call(
            model='claude-sonnet-4.6-thinking',
            prompt=prompt
        )
        
        return SynthesizedFeedback(
            strengths=response.strengths,
            weaknesses=response.weaknesses,
            questions=response.questions,
            actions=response.actions
        )
```

#### 2.2.3 Meta-Review y Resolución de Conflictos

Cuando revisores divergen significativamente:

```python
class MetaReviewer:
    """
    Agente meta-reviewer que resuelve conflictos entre revisores.
    Inspirado en: senior reviewers en conferencias reales.
    """
    
    async def resolve_conflict(self, reviews: List[Review], paper: ResearchPaper):
        """
        Llamado cuando variance en scores > threshold.
        """
        # Identificar puntos de conflicto específicos
        conflicts = self.identify_conflicts(reviews)
        
        # Para cada conflicto, investigación adicional
        resolutions = []
        for conflict in conflicts:
            # Ej: Revisor 1 dice "método A es SOTA" vs Revisor 3 dice "método B supera A"
            # Meta-reviewer hace búsqueda adicional
            evidence = await self.gather_evidence(conflict.claim, conflict.counter_claim)
            
            resolution = self.arbitrate(
                claim=conflict.claim,
                counter_claim=conflict.counter_claim,
                evidence=evidence,
                reviewer1_confidence=conflict.reviewer1.confidence,
                reviewer2_confidence=conflict.reviewer2.confidence
            )
            resolutions.append(resolution)
        
        # Meta-review final
        meta_review = f"""
**Meta-Review**

Tras analizar {len(reviews)} reviews y resolver {len(conflicts)} conflictos:

{self.format_resolutions(resolutions)}

**Decisión Final**: {self.final_decision}
**Justificación**: {self.justification}
**Condiciones para Aceptación** (si borderline): {self.conditions}
"""
        
        return MetaReview(
            content=meta_review,
            final_decision=self.final_decision,
            conflicts_resolved=resolutions
        )
```
### 2.3 Sistema de Experimentación End-to-End Reproducible
#### 2.3.1 Experiment Tracker Automático

**Inspiración**: Automated documentation of experiments[5][6]

```python
class ExperimentTracker:
    """
    Captura metadata + lineage de experimentos automáticamente.
    Sin overhead manual para investigador.
    """
    
    def __init__(self, mission: Mission):
        self.mission = mission
        self.run_id = uuid.uuid4()
        self.metadata = ExperimentMetadata(
            mission_id=mission.id,
            run_id=self.run_id,
            start_time=datetime.utcnow(),
            git_commit=self.get_git_commit(),
            git_branch=self.get_git_branch(),
            environment=self.snapshot_environment(),
            command=sys.argv
        )
        
    def snapshot_environment(self):
        """
        Captura entorno computacional completo[cite:12].
        """
        return ComputeEnvironment(
            python_version=sys.version,
            packages=self.freeze_packages(),  # pip freeze
            conda_env=self.export_conda_env() if self.is_conda() else None,
            docker_image=os.getenv('DOCKER_IMAGE'),
            hardware=self.detect_hardware(),
            os_info=platform.platform(),
            env_vars=self.capture_relevant_env_vars()
        )
    
    def track_dataset(self, dataset_path: Path, role: str):
        """
        Versiona datasets con hash + DVC.
        """
        file_hash = self.compute_sha256(dataset_path)
        
        # Integrar con DVC si está configurado
        if self.has_dvc():
            dvc_url = self.dvc_add(dataset_path)
        else:
            dvc_url = None
        
        self.metadata.datasets.append(DatasetInfo(
            path=str(dataset_path),
            role=role,  # 'train', 'val', 'test'
            sha256=file_hash,
            size_bytes=dataset_path.stat().st_size,
            dvc_url=dvc_url,
            timestamp=datetime.utcnow()
        ))
    
    def track_model(self, model_path: Path, metrics: Dict):
        """
        Versiona modelo + hiperparámetros + métricas.
        """
        self.metadata.models.append(ModelInfo(
            path=str(model_path),
            sha256=self.compute_sha256(model_path),
            hyperparameters=self.extract_hyperparameters(),
            metrics=metrics,
            training_time_seconds=self.training_duration,
            timestamp=datetime.utcnow()
        ))
    
    def create_reproducibility_package(self):
        """
        Crea "cápsula" reproducible[cite:12] con TODO necesario
        para re-ejecutar experimento.
        """
        package = ReproducibilityPackage(
            metadata=self.metadata,
            code_snapshot=self.snapshot_code(),
            data_manifest=self.create_data_manifest(),
            environment_spec=self.metadata.environment,
            execution_script=self.generate_execution_script(),
            results=self.collect_results(),
            provenance_graph=self.build_provenance_graph()
        )
        
        # Empaquetar como .zip con estructura estándar
        package_path = self.outputs_dir / f"repro_package_{self.run_id}.zip"
        package.save(package_path)
        
        return package_path
```

#### 2.3.2 Replication Tester

Ejecuta experimentos en sandbox limpio para verificar reproducibilidad:

```python
class ReplicationTester:
    """
    Toma reproducibility package y re-ejecuta en entorno limpio.
    Verifica que resultados sean consistentes.
    """
    
    async def test_replication(self, package: ReproducibilityPackage):
        """
        Ejecuta en Docker container fresco.
        """
        # 1. Crear container desde package.environment_spec
        container = await self.docker_client.containers.create(
            image=package.environment_spec.docker_image,
            command=package.execution_script,
            volumes={
                str(package.code_snapshot): {'bind': '/code', 'mode': 'ro'},
                str(package.data_manifest): {'bind': '/data', 'mode': 'ro'}
            }
        )
        
        # 2. Ejecutar
        await container.start()
        exit_code = await container.wait()
        
        # 3. Comparar resultados
        replicated_results = await self.extract_results(container)
        
        # 4. Statistical comparison
        comparison = self.compare_results(
            original=package.results,
            replicated=replicated_results,
            tolerance=package.metadata.replication_tolerance
        )
        
        if comparison.all_match:
            verdict = "SUCCESSFULLY_REPLICATED"
        elif comparison.within_tolerance:
            verdict = "REPLICATED_WITHIN_TOLERANCE"
        else:
            verdict = "REPLICATION_FAILED"
        
        return ReplicationReport(
            verdict=verdict,
            comparison=comparison,
            container_logs=await container.logs()
        )
```
### 2.4 Plataforma de Publicación Web Completa
#### 2.4.1 Arquitectura de la Plataforma

```
┌──────────────────────────────────────────────────────────┐
│              PAPER-WEB: Plataforma de Publicación         │
└──────────────────────────────────────────────────────────┘
         │
         ├─► [GENERACIÓN] Static Site Generator
         │    ├─ Jekyll (GitHub Pages nativo)[cite:39][cite:42]
         │    ├─ Templates personalizados por tipo de paper
         │    ├─ Math rendering (MathJax / KaTeX)
         │    └─ Citation formatting (CSL + Zotero)
         │
         ├─► [CONTENIDO] Múltiples Formatos
         │    ├─ HTML (navegación web)
         │    ├─ PDF (generado con LaTeX vía Pandoc)
         │    ├─ EPUB (para lectores)
         │    └─ XML (JATS para indexación)
         │
         ├─► [INTERACTIVIDAD] Notebooks y Visualizaciones
         │    ├─ Jupyter Notebooks embebidos (nbconvert)
         │    ├─ Observable notebooks para viz D3.js
         │    ├─ Gradio demos si hay modelos
         │    └─ Plotly charts interactivos
         │
         ├─► [PERSISTENCIA] DOI y Archivo
         │    ├─ Zenodo API (DOI minting automático)
         │    ├─ FigShare backup
         │    ├─ Internet Archive (Wayback Machine)
         │    └─ ORCID linking
         │
         ├─► [ENGAGEMENT] Comentarios y Discusión
         │    ├─ utterances.es (GitHub Issues como backend)[cite:39]
         │    ├─ Hypothesis.io para anotaciones inline
         │    └─ Email notifications vía GitHub
         │
         └─► [MÉTRICAS] Citaciones y Tracking
              ├─ Semantic Scholar API (citations tracking)
              ├─ Google Scholar metadata
              ├─ Altmetric badges
              └─ Analytics (Plausible, privacy-friendly)
```

#### 2.4.2 Generador de Sitio Estático

```python
class PaperWebGenerator:
    """
    Genera sitio web completo desde outputs/ + draft_paper.md
    """
    
    def __init__(self, mission: Mission, outputs_dir: Path):
        self.mission = mission
        self.outputs_dir = outputs_dir
        self.site_dir = outputs_dir / "website"
        
    def generate(self):
        """
        Genera sitio web publicable con un solo comando.
        """
        # 1. Setup Jekyll structure
        self.setup_jekyll_structure()
        
        # 2. Convertir draft_paper.md a páginas navegables
        self.convert_paper_to_html()
        
        # 3. Generar índice con TOC
        self.generate_index()
        
        # 4. Convertir notebooks a HTML
        self.convert_notebooks()
        
        # 5. Embebed visualizaciones
        self.embed_visualizations()
        
        # 6. Generar página de reproducibilidad
        self.generate_reproducibility_page()
        
        # 7. Setup comentarios
        self.setup_comments()
        
        # 8. Build sitio
        self.jekyll_build()
        
        # 9. Deploy a GitHub Pages
        if self.mission.auto_deploy:
            self.deploy_github_pages()
        
        return self.site_dir / "_site"
    
    def generate_reproducibility_page(self):
        """
        Página dedicada a reproducibilidad con TODO lo necesario.
        Sigue estándares de artifact review[cite:7][cite:11].
        """
        page_content = f"""
---
layout: page
title: Reproducibility Package
permalink: /reproducibility/
---

# Reproducibility Package

This research follows the **five pillars of computational reproducibility**[cite:8][cite:16]:

## 1. Literate Programming
- Jupyter notebooks with narrative + code: [Download](/assets/notebooks/)
- All analysis scripts documented: [GitHub Repo]({self.mission.github_repo})

## 2. Version Control
- Git repository: {self.mission.github_repo}
- Commit hash: `{self.get_git_commit()}`
- Release tag: `{self.get_git_tag()}`

## 3. Compute Environment
- Docker image: `{self.docker_image}`
- Conda environment: [environment.yml](/assets/environment.yml)
- Full package list: [requirements.txt](/assets/requirements.txt)

## 4. Data
- Training data: [![DOI](https://zenodo.org/badge/DOI/{self.data_doi}.svg)](https://doi.org/{self.data_doi})
- Test data: Available upon request (privacy restrictions)
- Synthetic data generator: [generate_data.py]({self.github_repo}/blob/main/scripts/generate_data.py)

## 5. Execution Protocol
```bash
# Clone repository
git clone {self.mission.github_repo}
cd {self.repo_name}
# Restore environment
docker pull {self.docker_image}
docker run -v $(pwd):/workspace {self.docker_image}
# Inside container:
bash scripts/run_all_experiments.sh
```

## Reproducibility Package Download
Complete package (code + data + environment + results):
- **Direct download**: [repro_package.zip](/assets/repro_package.zip) (2.3 GB)
- **Zenodo archive**: [![DOI](https://zenodo.org/badge/DOI/{self.package_doi}.svg)](https://doi.org/{self.package_doi})

## Expected Results
After running the reproduction script, you should obtain:
- `results/metrics.json` with {self.format_expected_metrics()}
- Figures in `results/figures/` matching those in the paper
- Statistical tests passing with p < 0.05

## Verification
We provide automated verification:
```bash
python scripts/verify_replication.py --original results/original/ --replicated results/your_run/
```

This script checks:
- Metrics within ±2% tolerance
- Statistical significance preserved
- Figures visually similar (SSIM > 0.95)

## Questions?
Open an issue on [GitHub]({self.github_repo}/issues) or email: {self.mission.contact_email}
"""
        
        (self.site_dir / "reproducibility.md").write_text(page_content)
    
    def mint_doi(self):
        """
        Mints DOI via Zenodo API.
        """
        if not self.mission.zenodo_token:
            logger.warning("No Zenodo token, skipping DOI minting")
            return None
        
        zenodo = ZenodoAPI(token=self.mission.zenodo_token)
        
        # Create deposition
        deposition = zenodo.create_deposition(
            title=self.mission.topic,
            creators=[{"name": self.mission.author, "affiliation": self.mission.affiliation}],
            description=self.get_abstract(),
            keywords=self.mission.keywords,
            upload_type='publication',
            publication_type='article'
        )
        
        # Upload reproducibility package
        repro_package = self.outputs_dir / f"repro_package_{self.mission.id}.zip"
        zenodo.upload_file(deposition.id, repro_package)
        
        # Publish
        published = zenodo.publish(deposition.id)
        
        return published.doi
```

#### 2.4.3 Template Jekyll Especializado

```liquid
<!-- _layouts/paper.html -->
<!DOCTYPE html>
<html lang="{{ page.lang | default: site.lang | default: "en" }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <!-- SEO optimizado para papers -->
    <title>{{ page.title }} | {{ site.title }}</title>
    <meta name="description" content="{{ page.abstract | strip_html | truncate: 160 }}">
    <meta name="keywords" content="{{ page.keywords | join: ', ' }}">
    
    <!-- Scholar metadata -->
    <meta name="citation_title" content="{{ page.title }}">
    <meta name="citation_author" content="{{ page.author }}">
    <meta name="citation_publication_date" content="{{ page.date | date: "%Y/%m/%d" }}">
    <meta name="citation_online_date" content="{{ site.time | date: "%Y/%m/%d" }}">
    <meta name="citation_pdf_url" content="{{ page.url | prepend: site.baseurl | prepend: site.url | append: '.pdf' }}">
    {% if page.doi %}
    <meta name="citation_doi" content="{{ page.doi }}">
    {% endif %}
    
    <!-- MathJax for equations -->
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
    <!-- Syntax highlighting -->
    /assets/css/syntax.css" | relative_url }}">
    
    <!-- Custom paper stylesheet -->
    /assets/css/paper.css" | relative_url }}">
</head>
<body>
    <article class="paper">
        <header class="paper-header">
            <h1 class="paper-title">{{ page.title }}</h1>
            
            <div class="paper-metadata">
                <span class="author">{{ page.author }}</span>
                {% if page.affiliation %}
                <span class="affiliation">{{ page.affiliation }}</span>
                {% endif %}
                <time class="publication-date" datetime="{{ page.date | date_to_xmlschema }}">
                    {{ page.date | date: "%B %d, %Y" }}
                </time>
            </div>
            
            {% if page.doi %}
            <div class="doi">
                DOI: <a href="https://doi.org/{{ page.doi }}">{{ page.doi }}</a>
            </div>
            {% endif %}
            
            <div class="paper-actions">
                <a href="{{ page.url | append: '.pdf' }}" class="btn btn-primary">
                    <i class="icon-download"></i> Download PDF
                </a>
                <a href="/reproducibility/" class="btn btn-secondary">
                    <i class="icon-code"></i> Reproducibility Package
                </a>
                <a href="{{ site.github_repo }}" class="btn btn-secondary">
                    <i class="icon-github"></i> GitHub
                </a>
            </div>
        </header>
        
        <div class="paper-content">
            <!-- Abstract destacado -->
            {% if page.abstract %}
            <section class="abstract">
                <h2>Abstract</h2>
                {{ page.abstract }}
            </section>
            {% endif %}
            
            <!-- Table of Contents -->
            <nav class="toc">
                <h2>Contents</h2>
                {{ content | toc_only }}
            </nav>
            
            <!-- Main content -->
            {{ content }}
        </div>
        
        <!-- Comments via utterances (GitHub Issues) -->
        <section class="comments">
            <h2>Discussion</h2>
            <script src="https://utteranc.es/client.js"
                    repo="{{ site.github_repo }}"
                    issue-term="pathname"
                    theme="github-light"
                    crossorigin="anonymous"
                    async>
            </script>
        </section>
    </article>
</body>
</html>
```
### 2.5 Integración Profunda de Skills y MCP
#### 2.5.1 Orquestación de 82+ Skills

```python
class SkillOrchestrator:
    """
    Orquesta las 82+ skills disponibles según fase de investigación.
    """
    
    SKILL_MAP = {
        'planning': [
            'brainstorming',          # Diseño inicial
            'writing-plans',          # Plan de implementación detallado
        ],
        'development': [
            'test-driven-development',  # TDD para código de experimentos
            'subagent-driven-development',  # Tareas paralelas
            'using-git-worktrees',      # Branches aislados
        ],
        'debugging': [
            'systematic-debugging',     # Debug de experimentos fallidos
            'verification-before-completion',  # Verify antes de marcar listo
        ],
        'code_review': [
            'requesting-code-review',   # Pre-merge review
            'receiving-code-review',    # Aplicar feedback
        ],
        'research': [
            'research',                 # Core research skill (este proyecto)
            'hf-mcp',                   # Buscar papers/models en HF
            'hugging-face-paper-publisher',  # Publicar en HF Papers
        ],
        'experimentation': [
            'hugging-face-model-trainer',  # Fine-tune en HF Jobs
            'hugging-face-jobs',           # Gestión de training jobs
            'hugging-face-trackio',        # Métricas + experiments
        ],
        'documentation': [
            'knowledge-capture',        # Notion: capturar conocimiento
            'research-documentation',   # Notion: doc con citas
            'spec-to-implementation',   # Notion: spec → tasks
        ],
        'publication': [
            'create-rule',              # .cursorrules para nuevo proyecto
            'create-skill',             # Skill nueva si se necesita
            'v0-dev',                   # Generar UI para demos
            'gradio',                   # UI Gradio para modelos
        ],
        'deployment': [
            'nextjs',                   # Deploy web app con Next.js
            'vercel-functions',         # Serverless functions
            'vercel-storage',           # Blob storage para artifacts
            'deployments-cicd',         # CI/CD setup
        ],
        'monitoring': [
            'observability',            # Logs + analytics
            'vercel-flags',             # Feature flags para A/B
        ]
    }
    
    def get_skills_for_phase(self, phase: ResearchPhase):
        """
        Returns skills relevantes para fase actual.
        """
        return self.SKILL_MAP.get(phase.name, [])
    
    def execute_with_skill(self, skill_name: str, context: dict):
        """
        Ejecuta acción cargando skill apropiada.
        """
        # Load skill instructions
        skill_instructions = self.load_skill(skill_name)
        
        # Construir prompt con contexto + skill instructions
        prompt = f"""
{skill_instructions}

---

**Current Context**:
{json.dumps(context, indent=2)}

**Your Task**: {context['task_description']}
"""
        
        # Ejecutar con modelo apropiado
        response = await self.llm_call(
            model=context.get('model', 'claude-sonnet-4.6-thinking'),
            prompt=prompt,
            temperature=context.get('temperature', 0.3)
        )
        
        return response
```

#### 2.5.2 MCP Layer: Orquestación de Servidores

```python
class MCPOrchestrator:
    """
    Orquesta los 7 servidores MCP para automatización profunda.
    """
    
    def __init__(self):
        self.servers = {
            'firecrawl': FirecrawlMCP(),
            'playwright': PlaywrightMCP(),
            'github': GitHubMCP(),
            'notion': NotionMCP(),
            'perplexity': PerplexityWebMCP(),
            'testsprite': TestSpriteMCP(),
            'binance': BinanceMCP()  # Para estudios financieros
        }
    
    async def deep_research_workflow(self, query: str, mission: Mission):
        """
        Workflow completo de investigación usando MCPs.
        """
        # 1. Perplexity: Búsqueda inicial profunda
        initial_search = await self.servers['perplexity'].search(
            query=query,
            model=mission.model,
            focus='academic'
        )
        
        # 2. Firecrawl: Scraping de papers identificados
        papers = []
        for result in initial_search.results:
            if self.is_academic_paper(result.url):
                content = await self.servers['firecrawl'].scrape(
                    url=result.url,
                    extract_schema='academic_paper'
                )
                papers.append(content)
        
        # 3. GitHub: Buscar implementaciones open source
        code_repos = await self.servers['github'].search_repos(
            query=f"{query} implementation",
            sort='stars',
            order='desc'
        )
        
        # 4. Notion: Documentar hallazgos
        notion_page = await self.servers['notion'].create_page(
            parent=mission.notion_workspace_id,
            title=f"Research: {query}",
            children=[
                self.format_research_section("Papers Found", papers),
                self.format_research_section("Code Repositories", code_repos),
                self.format_research_section("Initial Insights", initial_search.summary)
            ]
        )
        
        return ResearchWorkflowResult(
            papers=papers,
            code_repos=code_repos,
            notion_page=notion_page,
            initial_search=initial_search
        )
    
    async def code_validation_workflow(self, code_dir: Path):
        """
        Valida código de experimentos con TestSprite + Playwright.
        """
        # 1. TestSprite: Tests unitarios + integración
        test_results = await self.servers['testsprite'].run_tests(
            directory=code_dir,
            framework='pytest',
            coverage=True
        )
        
        # 2. Playwright: E2E tests si hay UI
        if self.has_web_interface(code_dir):
            e2e_results = await self.servers['playwright'].run_tests(
                test_dir=code_dir / 'tests' / 'e2e',
                headless=True,
                screenshot_on_failure=True
            )
        else:
            e2e_results = None
        
        # 3. GitHub: Create PR con resultados
        if test_results.failed == 0:
            pr = await self.servers['github'].create_pull_request(
                repo=mission.github_repo,
                title=f"Experiments validated: {test_results.passed} tests passing",
                body=self.format_test_report(test_results, e2e_results),
                head=mission.experiment_branch,
                base='main'
            )
        
        return CodeValidationResult(
            test_results=test_results,
            e2e_results=e2e_results,
            pull_request=pr if test_results.failed == 0 else None
        )
```
## III. Roadmap de Implementación
### 3.1 Fase 1: Fundamentos (Sprint 1-2, ~4 semanas)
**Objetivo**: Sentar bases arquitectónicas sólidas

| Semana | Tarea | Entregable |
|--------|-------|------------|
| 1 | Refactoring core: separar concerns en módulos | `paper_pipeline/validation/`, `paper_pipeline/review/`, `paper_pipeline/experiment/` |
| 1 | Implementar FactValidator básico | Fact checking con 3+ fuentes, confianza bayesiana |
| 2 | MethodologyValidator para 3 venues (NeurIPS, ICML, ICLR) | Checklist compliance automated |
| 2 | StatisticalRigorChecker v1 | Detectar p-hacking, múltiples comparaciones |

**Tests**:
- Unit tests para cada validator con casos edge
- Integration test: `mission.md` → validación completa → `validation_report.md`
### 3.2 Fase 2: Peer Review Sintético (Sprint 3-4, ~4 semanas)
**Objetivo**: Sistema de revisión por pares funcionando

| Semana | Tarea | Entregable |
|--------|-------|------------|
| 3 | SyntheticReviewerPool: 7 perfiles | Prompts calibrados, tests con papers conocidos |
| 3 | ReviewAggregator: algoritmo co-determinación | Implementar modelo bayesiano[3] |
| 4 | MetaReviewer: resolución de conflictos | Meta-review automático cuando variance alta |
| 4 | Benchmark contra reviews reales | Dataset de papers + reviews humanas para validar |

**Validación**:
- Comparar reviews sintéticas vs. humanas en 50 papers publicados
- Métricas: agreement con decisión final, coverage de issues, actionability de feedback
### 3.3 Fase 3: Experimentación Reproducible (Sprint 5-6, ~4 semanas)
**Objetivo**: Experiments auto-documentados y replicables

| Semana | Tarea | Entregable |
|--------|-------|------------|
| 5 | ExperimentTracker: captura automática metadata | Logging de datasets, models, hyperparams sin código manual |
| 5 | Environment snapshotting: Docker + conda | `environment.yml`, `Dockerfile` auto-generados |
| 6 | ReproducibilityPackage builder | `.zip` con todo necesario para replicar |
| 6 | ReplicationTester: ejecución en sandbox | Docker runner que valida replicación |

**Tests**:
- Crear experimento toy, empaquetar, replicar en máquina limpia
- Verificar metrics matching dentro de tolerance
### 3.4 Fase 4: Plataforma Web (Sprint 7-8, ~4 semanas)
**Objetivo**: Publicación web completa funcionando

| Semana | Tarea | Entregable |
|--------|-------|------------|
| 7 | PaperWebGenerator: Jekyll setup | Sitio estático generado desde `outputs/` |
| 7 | Templates: paper.html, reproducibility.html | Layouts profesionales con Scholar metadata |
| 8 | DOI minting vía Zenodo API | DOI automático post-publicación |
| 8 | Comments + analytics | utterances.es integrado, Plausible analytics |

**Deliverable**:
- Demo: paper completo publicado en GitHub Pages con DOI, reproducibility package, comentarios
### 3.5 Fase 5: Skills + MCP Integration (Sprint 9-10, ~4 semanas)
**Objetivo**: Automatización profunda vía skills + MCP

| Semana | Tarea | Entregable |
|--------|-------|------------|
| 9 | SkillOrchestrator: mapeo fase → skills | Carga automática de skills según research phase |
| 9 | Deep research workflow (Perplexity + Firecrawl MCP) | Pipeline: query → scraping → Notion |
| 10 | Code validation workflow (TestSprite + Playwright MCP) | Tests automáticos + PR en GitHub |
| 10 | Hugging Face integration (papers, models, jobs) | Publicar paper en HF, subir models, schedule jobs |

**Tests**:
- End-to-end: `mission.md` → research → experiments → validation → review → publication
- Todo automático, sin intervención humana salvo aprobación final
### 3.6 Fase 6: Pulido y Optimización (Sprint 11-12, ~4 semanas)
**Objetivo**: Production-ready + optimización

| Semana | Tarea | Entregable |
|--------|-------|------------|
| 11 | Performance: paralelización, caching | Reducir tiempo de pipeline en 50% |
| 11 | Error handling robusto | Graceful degradation, retry logic, rollback |
| 12 | Documentación exhaustiva | README, tutoriales, API docs, videos |
| 12 | Case studies: 3 papers completos end-to-end | Demostrar calidad comparable a humano |

**Métricas de Éxito**:
- Pipeline completo (research → publication) en < 24 horas
- Papers sintéticos indistinguibles de humanos (blind review test)
- Tasa de replicación > 95%
## IV. Metodologías de Validación sin Humano
### 4.1 Multi-Model Consensus
**Principio**: Ningún modelo único es fuente de verdad. Consenso entre 5+ modelos con arquitecturas/entrenamientos diferentes.[10]

```python
class MultiModelConsensus:
    """
    Validación mediante consenso de múltiples modelos.
    """
    
    MODELS = [
        'claude-sonnet-4.6-thinking',  # Anthropic
        'gpt-4o',                       # OpenAI
        'gemini-2.0-flash-thinking',    # Google
        'perplexity-claude',            # Perplexity (Claude backend)
        'llama-3.3-70b'                 # Meta (open source)
    ]
    
    async def validate_claim(self, claim: str, evidence: List[str]):
        """
        Cada modelo vota: SUPPORT / REFUTE / INSUFFICIENT
        """
        votes = await asyncio.gather(*[
            self.ask_model(model, claim, evidence)
            for model in self.MODELS
        ])
        
        # Conteo
        support = sum(1 for v in votes if v == 'SUPPORT')
        refute = sum(1 for v in votes if v == 'REFUTE')
        insufficient = sum(1 for v in votes if v == 'INSUFFICIENT')
        
        # Consenso: ≥80% acuerdo
        total = len(votes)
        if support / total >= 0.8:
            return Verdict.SUPPORTED
        elif refute / total >= 0.8:
            return Verdict.REFUTED
        else:
            # Divergencia: investigar más o marcar como "controversial"
            return Verdict.CONTROVERSIAL
```
### 4.2 Benchmarking Contra Ground Truth
Validar quality de papers sintéticos contra corpus de papers publicados y aceptados:

```python
class QualityBenchmark:
    """
    Compara papers sintéticos vs. corpus de papers reales (NeurIPS, ICML, etc.)
    en dimensiones cuantificables.
    """
    
    def benchmark_paper(self, synthetic_paper: ResearchPaper):
        """
        Benchmark en múltiples dimensiones.
        """
        # 1. Readability metrics
        readability = {
            'flesch_reading_ease': textstat.flesch_reading_ease(synthetic_paper.text),
            'gunning_fog': textstat.gunning_fog(synthetic_paper.text),
            'avg_sentence_length': self.avg_sentence_length(synthetic_paper.text)
        }
        
        # 2. Citation density
        citation_density = len(synthetic_paper.citations) / synthetic_paper.word_count
        
        # 3. Structural compliance
        has_required_sections = all(
            section in synthetic_paper.sections
            for section in ['abstract', 'intro', 'related_work', 'methodology', 'experiments', 'conclusion']
        )
        
        # 4. Novelty score (embedding similarity vs. existing papers)
        novelty_score = self.calculate_novelty(
            synthetic_paper.embedding,
            self.corpus_embeddings
        )
        
        # 5. Methodological rigor (checklist)
        rigor_score = self.assess_rigor(synthetic_paper)
        
        # Comparar vs. distribución de papers aceptados
        percentile_scores = {
            'readability': self.percentile_in_corpus(readability, 'readability'),
            'citation_density': self.percentile_in_corpus(citation_density, 'citation_density'),
            'novelty': self.percentile_in_corpus(novelty_score, 'novelty'),
            'rigor': self.percentile_in_corpus(rigor_score, 'rigor')
        }
        
        # Acceptance likelihood (modelo entrenado en papers aceptados vs. rechazados)
        acceptance_prob = self.acceptance_classifier.predict_proba(
            features=self.extract_features(synthetic_paper)
        )[1]  # Prob de clase "accepted"
        
        return BenchmarkResult(
            readability=readability,
            citation_density=citation_density,
            structural_compliance=has_required_sections,
            novelty_score=novelty_score,
            rigor_score=rigor_score,
            percentile_scores=percentile_scores,
            acceptance_probability=acceptance_prob
        )
```
### 4.3 Replication as Validation
**Principio fundamental**: Si no se puede replicar, no es ciencia válida.

```python
class ReplicationAsValidation:
    """
    Validación mediante replicación de resultados.
    Todo claim empírico debe ser replicable.
    """
    
    async def validate_empirical_claims(self, paper: ResearchPaper):
        """
        Para cada claim empírico:
        1. Identificar código + datos asociados
        2. Re-ejecutar en entorno limpio
        3. Comparar resultados
        """
        claims = self.extract_empirical_claims(paper)
        
        replication_results = []
        for claim in claims:
            # Localizar experimento asociado
            experiment = self.find_associated_experiment(claim)
            
            if experiment is None:
                replication_results.append(ReplicationResult(
                    claim=claim,
                    status="NOT_REPLICABLE",
                    reason="No code/data provided"
                ))
                continue
            
            # Empaquetar experimento
            package = experiment.create_reproducibility_package()
            
            # Re-ejecutar en sandbox
            replicated = await self.replication_tester.test_replication(package)
            
            # Comparar claim vs. resultado replicado
            match = self.compare_claim_to_result(claim, replicated.results)
            
            replication_results.append(ReplicationResult(
                claim=claim,
                status="REPLICATED" if match else "FAILED",
                original_value=claim.value,
                replicated_value=replicated.results.get(claim.metric),
                difference=abs(claim.value - replicated.results.get(claim.metric))
            ))
        
        # Paper válido solo si ≥90% de claims replican
        success_rate = sum(1 for r in replication_results if r.status == "REPLICATED") / len(replication_results)
        
        return ReplicationReport(
            results=replication_results,
            success_rate=success_rate,
            verdict="VALID" if success_rate >= 0.9 else "INVALID"
        )
```
## V. Infraestructura y Deployment
### 5.1 Stack Tecnológico Completo
| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| **Orchestration** | Python 3.10+ | Ecosistema científico maduro |
| **LLMs** | Claude Sonnet 4.6, GPT-4o, Gemini 2.0, Perplexity | Diversidad para consensus |
| **Code Agent** | Cursor Composer 2 Fast | Mejor código generativo 2026 |
| **Version Control** | Git + GitHub | Standard de facto |
| **Containerization** | Docker + Docker Compose | Reproducibilidad entornos |
| **Env Management** | Conda + pip-tools | Manejo de dependencias científicas |
| **Data Versioning** | DVC (Data Version Control) | Versionar datasets grandes |
| **Experiment Tracking** | Custom tracker + MLflow opcional | Metadata + lineage completos |
| **Web Framework** | Jekyll (GitHub Pages) | Static site, gratis, confiable |
| **Interactive Viz** | Observable + Plotly | Notebooks + charts interactivos |
| **Notebooks** | Jupyter | Standard para análisis |
| **DOI Minting** | Zenodo API | Persistencia + DOI gratuito |
| **Comments** | utterances.es | GitHub Issues como backend |
| **Analytics** | Plausible | Privacy-friendly, open source |
| **Testing** | pytest + Playwright | Unit + E2E |
| **CI/CD** | GitHub Actions | Integrado con GitHub |
| **Secrets Management** | GitHub Secrets + .env | No hardcodear credenciales |
| **MCP** | 7 servidores custom | Firecrawl, Playwright, GitHub, Notion, Perplexity, TestSprite, Binance |
### 5.2 Infraestructura de CI/CD
```yaml
# .github/workflows/research-pipeline.yml
name: Research Pipeline CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
  workflow_dispatch:
    inputs:
      mission_file:
        description: 'Path to mission.md'
        required: true
        default: 'missions/default/mission.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -e .[dev]
      
      - name: Run tests
        run: pytest tests/ --ignore=tests/test_perplexity_integration.py
      
      - name: Validate mission file
        run: |
          paper-pipeline ${{ github.event.inputs.mission_file || 'missions/default/mission.md' }} --dry-run

  research-pipeline:
    needs: validate
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup environment
        run: |
          pip install -e .
          # Setup secrets from GitHub Secrets
          echo "PERPLEXITY_SESSION_TOKEN=${{ secrets.PERPLEXITY_SESSION_TOKEN }}" >> .env
          echo "CURSOR_API_KEY=${{ secrets.CURSOR_API_KEY }}" >> .env
          echo "NOTION_TOKEN=${{ secrets.NOTION_TOKEN }}" >> .env
          echo "ZENODO_TOKEN=${{ secrets.ZENODO_TOKEN }}" >> .env
      
      - name: Run research pipeline
        run: |
          paper-pipeline ${{ github.event.inputs.mission_file }}
        timeout-minutes: 120
      
      - name: Run validation suite
        run: |
          python scripts/validate_research_quality.py --outputs outputs/
      
      - name: Generate reproducibility package
        run: |
          python scripts/create_repro_package.py --outputs outputs/
      
      - name: Publish to GitHub Pages
        if: success()
        run: |
          python scripts/deploy_website.py --outputs outputs/
      
      - name: Mint DOI
        if: success()
        run: |
          python scripts/mint_doi.py --outputs outputs/
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: research-outputs
          path: outputs/

  peer-review:
    needs: research-pipeline
    runs-on: ubuntu-latest
    steps:
      - name: Download outputs
        uses: actions/download-artifact@v3
        with:
          name: research-outputs
      
      - name: Run synthetic peer review
        run: |
          python scripts/synthetic_peer_review.py --paper outputs/draft_paper.md
      
      - name: Aggregate reviews
        run: |
          python scripts/aggregate_reviews.py --reviews outputs/reviews/
      
      - name: Post review to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('outputs/aggregated_review.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Synthetic Peer Review\n\n${review}`
            });
```
### 5.3 Deployment Automatizado
```python
# scripts/deploy_website.py
import subprocess
from pathlib import Path

class WebsiteDeployer:
    """
    Deploys research website to GitHub Pages.
    """
    
    def __init__(self, outputs_dir: Path):
        self.outputs_dir = outputs_dir
        self.site_dir = outputs_dir / "website"
    
    def deploy(self):
        """
        Full deployment workflow.
        """
        # 1. Generate website
        print("Generating website...")
        generator = PaperWebGenerator(mission, self.outputs_dir)
        site_built = generator.generate()
        
        # 2. Setup gh-pages branch
        print("Setting up gh-pages branch...")
        self.setup_gh_pages_branch()
        
        # 3. Copy built site to gh-pages
        print("Copying site to gh-pages...")
        subprocess.run([
            'cp', '-r', str(site_built / '*'), 'gh-pages/'
        ])
        
        # 4. Commit and push
        print("Deploying to GitHub Pages...")
        subprocess.run(['git', 'checkout', 'gh-pages'])
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', f'Deploy research: {mission.topic}'])
        subprocess.run(['git', 'push', 'origin', 'gh-pages', '--force'])
        
        # 5. Return URL
        repo_name = self.get_repo_name()
        url = f"https://{self.get_github_username()}.github.io/{repo_name}/"
        
        print(f"✅ Website deployed: {url}")
        return url
    
    def setup_gh_pages_branch(self):
        """
        Creates gh-pages branch if doesn't exist.
        """
        # Check if branch exists
        result = subprocess.run(
            ['git', 'rev-parse', '--verify', 'gh-pages'],
            capture_output=True
        )
        
        if result.returncode != 0:
            # Create orphan branch
            subprocess.run(['git', 'checkout', '--orphan', 'gh-pages'])
            subprocess.run(['git', 'rm', '-rf', '.'])
            subprocess.run(['touch', '.nojekyll'])  # Disable Jekyll processing
            subprocess.run(['git', 'add', '.nojekyll'])
            subprocess.run(['git', 'commit', '-m', 'Initial gh-pages'])
            subprocess.run(['git', 'push', 'origin', 'gh-pages'])
            subprocess.run(['git', 'checkout', 'main'])
```
## VI. Casos de Uso y Demos
### 6.1 Caso de Uso 1: Paper Completo de ML en 24h
**Escenario**: Investigador tiene idea para algoritmo nuevo de computer vision.

**Input** (`mission.md`):
```yaml
---
topic: "Self-Supervised Contrastive Learning for Few-Shot Image Classification"
paper_target: "ICLR 2027"
sections_needed:
  - abstract
  - introduction
  - related_work
  - methodology
  - experiments
  - results
  - discussion
  - conclusion
max_perplexity_calls: 64
code_needed: true
enable_quality_check: true
enable_peer_review: true
enable_reproducibility_package: true
enable_web_publication: true
target_venue: "ICLR"
model: "claude-sonnet-4.6-thinking"
---
```

**Pipeline Execution**:
1. **Hour 0-2**: Research phase (Perplexity + Firecrawl scraping 100+ papers)
2. **Hour 2-4**: Draft writing (40-page draft con 80+ citas)
3. **Hour 4-8**: Code implementation (Cursor Composer 2 Fast genera experiments)
4. **Hour 8-16**: Experiments running (AWS p4d.24xlarge, 100 epochs)
5. **Hour 16-18**: Results analysis + statistical tests
6. **Hour 18-20**: Quality validation (fact checking, methodology validation)
7. **Hour 20-22**: Synthetic peer review (7 reviewers, meta-review)
8. **Hour 22-23**: Reproducibility package creation
9. **Hour 23-24**: Web publication + DOI minting

**Output**:
- ✅ 40-page paper cumpliendo 100% checklist ICLR
- ✅ Código open source en GitHub con tests (95% coverage)
- ✅ Reproducibility package con Docker + datasets
- ✅ Website publicado con DOI en Zenodo
- ✅ Review sintética: "WEAK_ACCEPT" (borderline, pero publicable con minor revisions)
### 6.2 Caso de Uso 2: Replicación de Paper Existente
**Escenario**: Verificar claims de paper publicado (ej: "Attention Is All You Need" de scratch).

**Input**:
```yaml
---
topic: "Replication of 'Attention Is All You Need' (Vaswani et al., 2017)"
replication_target: "https://arxiv.org/abs/1706.03762"
sections_needed:
  - replication_report
  - methodology_comparison
  - results_comparison
  - discrepancies_analysis
code_needed: true
enable_replication_testing: true
---
```

**Pipeline**:
1. Scrape original paper + official code
2. Re-implement Transformer desde cero (Cursor)
3. Train en mismo dataset (WMT14 EN-DE)
4. Comparar BLEU scores: original vs. replicado
5. Statistical tests para verificar diferencias
6. Report con análisis de discrepancias

**Output**: Replication report confirmando (o refutando) claims originales.
### 6.3 Caso de Uso 3: Survey Paper Automático
**Escenario**: Survey de "Multimodal Large Language Models (2020-2026)".

**Input**:
```yaml
---
topic: "Survey of Multimodal Large Language Models (2020-2026)"
paper_target: "ACM Computing Surveys"
sections_needed:
  - abstract
  - introduction
  - taxonomy
  - vision_language_models
  - audio_language_models
  - video_understanding
  - benchmarks
  - future_directions
  - conclusion
max_perplexity_calls: 128
research_depth: "exhaustive"
citation_target: 200+
---
```

**Pipeline**:
1. Systematic literature search (Semantic Scholar API + Perplexity)
2. Categorization automática de 500+ papers
3. Taxonomy generation (clustering por embeddings)
4. Synthesis de cada categoría
5. Trend analysis (crecimiento de subcampos)
6. Future directions (predicción basada en tendencias)

**Output**: 80-page survey con 200+ citas, taxonomía visual, trends graphs.
## VII. Limitaciones y Mitigaciones
### 7.1 Limitaciones Técnicas
| Limitación | Impacto | Mitigación |
|------------|---------|------------|
| **Hallucinations de LLMs** | Claims falsos en research | Multi-model consensus + fact checking riguroso |
| **Sesgo en modelos** | Reproducir sesgos existentes | Bias detector + diverse reviewer pool |
| **Código generado con bugs** | Experimentos fallidos | Tests extensivos + replication testing |
| **Rate limits APIs** | Ralentización pipeline | Caching agresivo + request batching |
| **Costos computacionales** | Experimentos caros | Precios estimados + approval gates |
| **Dependencia de servicios externos** | Caída de Perplexity/Zenodo | Fallbacks + graceful degradation |
### 7.2 Limitaciones Metodológicas
| Limitación | Consideración |
|------------|---------------|
| **Novelty real** | Sistema no puede tener ideas genuinamente "creativas" fuera de lo visto en training data[10] |
| **Deep insights** | Análisis profundo tipo "eureka moment" aún requiere humano |
| **Ethical judgment** | Decisiones éticas complejas (ej: publicar vulnerabilidad) necesitan humano |
| **Domain expertise extremo** | En dominios muy especializados, puede faltar conocimiento profundo |

**Mitigaciones**:
- Humano define research question inicial (la "chispa")
- Sistema ejecuta investigación exhaustiva + experimentos
- Humano hace review final antes de submission real
- Transparency: marcar papers como "AI-assisted" en metadata
### 7.3 Consideraciones Éticas
1. **Autoría**: Papers generados deben declarar uso de AI
2. **Plagio**: Detector de plagio estricto en pipeline
3. **Reproducibilidad**: Mandatorio proveer código + datos
4. **Transparency**: Metadata completa de LLMs usados
5. **Responsible AI**: Broader impact statement incluido por defecto
## VIII. Métricas de Éxito
### 8.1 KPIs Cuantitativos
| Métrica | Target | Método de Medición |
|---------|--------|-------------------|
| **Time to Publication** | < 24h (research → website) | Pipeline timing logs |
| **Replication Success Rate** | > 95% | Automated replication tests |
| **Fact Checking Accuracy** | > 98% | Manual validation de sample |
| **Peer Review Agreement** | > 80% con reviews humanas | Blind comparison study |
| **Code Test Coverage** | > 90% | pytest-cov |
| **Citation Accuracy** | 100% (valid sources) | Automated link checking |
| **Website Uptime** | > 99.9% | GitHub Pages SLA |
| **DOI Success Rate** | 100% | Zenodo API monitoring |
### 8.2 KPIs Cualitativos
| Dimensión | Evaluación |
|-----------|------------|
| **Scientific Rigor** | Blind review: expertos no distinguen de papers humanos |
| **Clarity** | Readability scores ≥ percentile 50 de papers aceptados |
| **Novelty** | Embedding distance > threshold vs. corpus existente |
| **Impact** | Citations tracking 6 meses post-publicación |
| **Community Adoption** | Forks + stars en GitHub, comentarios en website |
## IX. Conclusión y Visión
Paper-Pipeline 2.0 no es solo una herramienta — es un **paradigm shift** en cómo se hace investigación científica. Al automatizar lo repetible mientras se mantiene rigor mediante validación multi-capa, peer review sintético y reproducibilidad mandatoria, el sistema puede:[2][14]

1. **Democratizar investigación**: Cualquiera con una idea puede producir research de calidad
2. **Acelerar descubrimiento**: Ciclos de 24h vs. meses/años
3. **Aumentar reproducibilidad**: 95%+ vs. ~40% actual en ML
4. **Escalar conocimiento**: Múltiples research threads en paralelo
5. **Reducir sesgos**: Validación automática vs. revisión humana inconsistente

**El futuro**: Investigación científica se convierte en un proceso continuo y colaborativo, donde:
- Ideas fluyen libremente
- Experimentos se validan automáticamente
- Hallazgos se publican instantáneamente
- Conocimiento se acumula sin fricción

**Paper-Pipeline 2.0 es el cerebro de este futuro**.

***

**Next Steps Inmediatos**:
1. ✅ Aprobar arquitectura
2. ⏭️ Setup repo con estructura modular
3. ⏭️ Implementar Fase 1 (Fundamentos)
4. ⏭️ Demo: primer paper completo end-to-end

