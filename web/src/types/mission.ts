/** Mirrors `paper_pipeline.server.schemas.MissionCreate` / `Mission` for API I/O. */

export interface MissionMeta {
  title: string
  description: string
}

export interface QualityGatesConfig {
  target_metric?: string
  higher_is_better?: boolean
  sota_baseline_value?: number
  breakthrough_margin?: number
  replication_tolerance?: number
  require_statistical_significance?: boolean
}

/** Editable block sent on PATCH (full object; server merges nested partials). */
export interface QualityGatesForm {
  target_metric: string
  higher_is_better: boolean
  sota_baseline_value: number
  breakthrough_margin: number
  replication_tolerance: number
  require_statistical_significance: boolean
}

export interface MissionHypothesis {
  id: string
  description: string
  priority?: string
  expected_outcome?: string
}

/** Full mission payload from `GET /api/missions/{id}` (`mission.model_dump()`). */
export interface MissionData {
  topic: string
  paper_target: string
  sections_needed: string[]
  max_perplexity_calls: number
  code_needed: boolean
  notion_page_id: string | null
  model: string
  language: string
  output_dir: string
  enable_notion: boolean
  enable_quality_check: boolean
  enable_cursor_cli: boolean
  /** Si true, un fallo del agente no aborta todo el run (default API). */
  cursor_cli_optional?: boolean
  cursor_cli_prompt_path: string | null
  cursor_cli_cwd: string | null
  single_thread_perplexity?: boolean
  save_perplexity_to_library?: boolean
  enable_epistemic_injection?: boolean
  enable_degradation_monitor?: boolean
  enable_skill_orchestrator?: boolean
  enable_hypervisor_triage?: boolean
  quality_gates?: QualityGatesConfig
  hypotheses?: MissionHypothesis[]
}

export interface MissionDetail {
  id: string
  meta: MissionMeta
  mission: MissionData
}

export interface MissionFlagsV2 {
  enable_epistemic_injection: boolean
  enable_degradation_monitor: boolean
  enable_skill_orchestrator: boolean
  enable_hypervisor_triage: boolean
}

export interface MissionListItem {
  id: string
  title: string
  description: string
  has_run_state: boolean
  last_error: string | null
  flags_v2?: MissionFlagsV2
}

/** Body for `POST /api/missions` and `PATCH` (full set of editable flat fields). */
export interface MissionCreateBody {
  title: string
  description: string
  topic: string
  paper_target: string
  sections_needed: string[]
  max_perplexity_calls: number
  code_needed: boolean
  enable_quality_check: boolean
  enable_cursor_cli: boolean
  cursor_cli_optional: boolean
  enable_notion: boolean
  notion_page_id: string | null
  model: string
  language: string
  single_thread_perplexity: boolean
  save_perplexity_to_library: boolean
  enable_epistemic_injection: boolean
  enable_degradation_monitor: boolean
  enable_skill_orchestrator: boolean
  enable_hypervisor_triage: boolean
  quality_gates: QualityGatesForm
  hypotheses: MissionHypothesis[]
}

export function defaultQualityGatesForm(): QualityGatesForm {
  return {
    target_metric: '',
    higher_is_better: true,
    sota_baseline_value: 0,
    breakthrough_margin: 0.02,
    replication_tolerance: 0.01,
    require_statistical_significance: true,
  }
}

export const defaultMissionCreateBody = (): MissionCreateBody => ({
  title: 'Nueva misión',
  description: '',
  topic: 'Research topic',
  paper_target: 'generic venue',
  sections_needed: ['gaps', 'methodology', 'experiments'],
  max_perplexity_calls: 8,
  code_needed: false,
  enable_quality_check: true,
  enable_cursor_cli: false,
  cursor_cli_optional: true,
  enable_notion: false,
  notion_page_id: null,
  model: 'best',
  language: 'en-US',
  single_thread_perplexity: false,
  save_perplexity_to_library: true,
  enable_epistemic_injection: false,
  enable_degradation_monitor: false,
  enable_skill_orchestrator: false,
  enable_hypervisor_triage: false,
  quality_gates: defaultQualityGatesForm(),
  hypotheses: [],
})

export interface LoopRequestBody {
  perplexity_section: string | null
  perplexity_extra: string
  include_notion: boolean
  cursor_prompt: string
  run_meta: boolean
}
