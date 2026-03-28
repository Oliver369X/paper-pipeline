import { MissionNav } from '@/components/MissionNav'
import { Button } from '@/components/ui/button'
import { Card, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { apiGet, apiPatch } from '@/lib/api'
import type { MissionCreateBody, MissionDetail, MissionHypothesis } from '@/types/mission'
import type { SectionKeysResponse } from '@/types/sectionKeys'
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState, type ReactNode } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { useParams } from 'react-router-dom'

const FALLBACK_SECTIONS = ['gaps', 'methodology', 'experiments']

function SortableRow({ id, children }: { id: string; children: ReactNode }) {
  const { t } = useTranslation()
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id,
  })
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.7 : 1,
  }
  return (
    <div
      ref={setNodeRef}
      style={style}
      className="mb-2 flex items-center gap-2 rounded-md border border-zinc-800 bg-zinc-900/80 px-2 py-1.5"
    >
      <button
        type="button"
        className="cursor-grab touch-none text-zinc-500 active:cursor-grabbing"
        {...attributes}
        {...listeners}
        aria-label={t('missionEditor.dragHandle')}
      >
        ⋮⋮
      </button>
      {children}
    </div>
  )
}

function toBody(d: MissionDetail): MissionCreateBody {
  const m = d.mission
  const qg = m.quality_gates
  return {
    title: d.meta.title,
    description: d.meta.description,
    topic: m.topic,
    paper_target: m.paper_target,
    sections_needed: [...m.sections_needed],
    max_perplexity_calls: m.max_perplexity_calls,
    code_needed: m.code_needed,
    enable_quality_check: m.enable_quality_check,
    enable_cursor_cli: m.enable_cursor_cli,
    cursor_cli_optional: m.cursor_cli_optional ?? true,
    enable_notion: m.enable_notion,
    notion_page_id: m.notion_page_id,
    model: m.model,
    language: m.language,
    single_thread_perplexity: m.single_thread_perplexity ?? false,
    save_perplexity_to_library: m.save_perplexity_to_library ?? true,
    enable_epistemic_injection: m.enable_epistemic_injection ?? false,
    enable_degradation_monitor: m.enable_degradation_monitor ?? false,
    enable_skill_orchestrator: m.enable_skill_orchestrator ?? false,
    enable_hypervisor_triage: m.enable_hypervisor_triage ?? false,
    quality_gates: {
      target_metric: qg?.target_metric ?? '',
      higher_is_better: qg?.higher_is_better ?? true,
      sota_baseline_value: qg?.sota_baseline_value ?? 0,
      breakthrough_margin: qg?.breakthrough_margin ?? 0.02,
      replication_tolerance: qg?.replication_tolerance ?? 0.01,
      require_statistical_significance: qg?.require_statistical_significance ?? true,
    },
    hypotheses: normalizeHypotheses(m.hypotheses),
  }
}

function normalizeHypotheses(raw: MissionHypothesis[] | undefined): MissionHypothesis[] {
  if (!raw?.length) return []
  return raw.map((h) => ({
    id: h.id,
    description: h.description ?? '',
    priority: h.priority ?? 'MEDIUM',
    expected_outcome: h.expected_outcome ?? '',
  }))
}

function newHypothesisRow(): MissionHypothesis {
  return {
    id: `h-${Date.now()}`,
    description: '',
    priority: 'MEDIUM',
    expected_outcome: '',
  }
}

function clampPerplexityCalls(n: number): number {
  if (Number.isNaN(n)) return 8
  return Math.min(64, Math.max(1, Math.floor(n)))
}

function sanitizeSections(sections: string[], allowed: string[]) {
  const set = new Set(allowed)
  const invalid = sections.filter((s) => !set.has(s))
  const cleaned = sections.filter((s) => set.has(s))
  const next = cleaned.length ? cleaned : [...FALLBACK_SECTIONS]
  return { next, invalid }
}

export function MissionEditor() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const qc = useQueryClient()
  const [form, setForm] = useState<MissionCreateBody | null>(null)
  const [addKey, setAddKey] = useState('')
  /** Claves de sección descartadas por no estar en el servidor; el texto se arma con t() al renderizar. */
  const [stripInvalid, setStripInvalid] = useState<string[] | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['mission', id],
    queryFn: () => apiGet<MissionDetail>(`/api/missions/${id}`),
    enabled: Boolean(id),
  })

  const { data: sectionKeys } = useQuery({
    queryKey: ['section-keys'],
    queryFn: () => apiGet<SectionKeysResponse>('/api/section-keys'),
  })

  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect -- reset local UI al cambiar misión */
    setForm(null)
    setStripInvalid(null)
    setAddKey('')
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [id])

  useEffect(() => {
    if (!data || !sectionKeys?.keys?.length || !id) return
    if (data.id !== id) return
    const body = toBody(data)
    const { next, invalid } = sanitizeSections(body.sections_needed, sectionKeys.keys)
    body.sections_needed = next
    body.max_perplexity_calls = clampPerplexityCalls(body.max_perplexity_calls)
    /* eslint-disable react-hooks/set-state-in-effect -- hidratar formulario desde respuesta API */
    if (invalid.length) {
      setStripInvalid(invalid)
    } else {
      setStripInvalid(null)
    }
    setForm(body)
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [data, sectionKeys, id])

  const { data: models } = useQuery({
    queryKey: ['models'],
    queryFn: () => apiGet<{ models: string[] }>('/api/models'),
  })

  const save = useMutation({
    mutationFn: (body: MissionCreateBody) =>
      apiPatch(`/api/missions/${id}`, {
        ...body,
        max_perplexity_calls: clampPerplexityCalls(body.max_perplexity_calls),
      }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['mission', id] }),
  })

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  if (!id) return <p className="p-6 text-zinc-500">{t('common.missingMissionId')}</p>
  if (isLoading || !form || !sectionKeys?.keys?.length) {
    return <p className="p-6 text-zinc-500">{t('common.loading')}</p>
  }

  const allowed = sectionKeys.keys
  const meta = sectionKeys.meta
  const availableToAdd = allowed.filter((k) => !form.sections_needed.includes(k))
  function onDragEnd(e: DragEndEvent) {
    if (!form) return
    const { active, over } = e
    if (!over || active.id === over.id) return
    const oldIndex = form.sections_needed.indexOf(String(active.id))
    const newIndex = form.sections_needed.indexOf(String(over.id))
    if (oldIndex < 0 || newIndex < 0) return
    setForm({
      ...form,
      sections_needed: arrayMove(form.sections_needed, oldIndex, newIndex),
    })
  }

  function addSectionFromSelect() {
    if (!form || !addKey) return
    if (form.sections_needed.includes(addKey)) return
    setForm({
      ...form,
      sections_needed: [...form.sections_needed, addKey],
    })
    setAddKey('')
  }

  function removeSection(s: string) {
    if (!form) return
    setForm({
      ...form,
      sections_needed: form.sections_needed.filter((x) => x !== s),
    })
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <MissionNav missionId={id} />
      <Card>
        <CardTitle>{t('missionEditor.title')}</CardTitle>
        <p className="mb-4 text-sm text-zinc-500">
          <Trans
            i18nKey="missionEditor.intro"
            components={{ code: <code className="text-zinc-300" /> }}
          />
        </p>

        {stripInvalid && stripInvalid.length > 0 && (
          <div className="mb-4 rounded-md border border-amber-800/60 bg-amber-950/40 px-3 py-2 text-sm text-amber-100">
            {t('missionEditor.stripNote', { invalid: stripInvalid.join(', ') })}
            <button
              type="button"
              className="ml-2 text-amber-300 underline"
              onClick={() => setStripInvalid(null)}
            >
              {t('missionEditor.close')}
            </button>
          </div>
        )}

        <Tabs defaultValue="general">
          <TabsList className="mb-2 flex h-auto min-h-10 w-full flex-wrap gap-1">
            <TabsTrigger value="general">{t('missionEditor.tabs.general')}</TabsTrigger>
            <TabsTrigger value="sections">{t('missionEditor.tabs.sections')}</TabsTrigger>
            <TabsTrigger value="integrations">{t('missionEditor.tabs.integrations')}</TabsTrigger>
            <TabsTrigger value="pipeline2">{t('missionEditor.tabs.pipeline2')}</TabsTrigger>
            <TabsTrigger value="advanced">{t('missionEditor.tabs.advanced')}</TabsTrigger>
          </TabsList>

          <TabsContent value="general" className="space-y-4">
            <fieldset className="space-y-4 rounded-md border border-zinc-800/80 p-4">
              <legend className="px-1 text-sm font-medium text-zinc-300">{t('missionEditor.metaLegend')}</legend>
              <div>
                <Label htmlFor="title">{t('missionEditor.titleLabel')}</Label>
                <Input
                  id="title"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="desc">{t('missionEditor.descLabel')}</Label>
                <Input
                  id="desc"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="topic">{t('missionEditor.topicLabel')}</Label>
                <Input
                  id="topic"
                  value={form.topic}
                  onChange={(e) => setForm({ ...form, topic: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="paper_target">{t('missionEditor.paperTargetLabel')}</Label>
                <Input
                  id="paper_target"
                  value={form.paper_target}
                  onChange={(e) => setForm({ ...form, paper_target: e.target.value })}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label htmlFor="model">{t('missionEditor.modelLabel')}</Label>
                  <select
                    id="model"
                    className="w-full rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm"
                    value={form.model}
                    onChange={(e) => setForm({ ...form, model: e.target.value })}
                  >
                    {(models?.models ?? [form.model]).map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="maxp">{t('missionEditor.maxPerplexity')}</Label>
                  <Input
                    id="maxp"
                    type="number"
                    min={1}
                    max={64}
                    value={form.max_perplexity_calls}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        max_perplexity_calls: clampPerplexityCalls(Number(e.target.value)),
                      })
                    }
                  />
                </div>
                <div className="sm:col-span-2">
                  <Label htmlFor="lang">{t('missionEditor.languageLabel')}</Label>
                  <Input
                    id="lang"
                    value={form.language}
                    onChange={(e) => setForm({ ...form, language: e.target.value })}
                  />
                </div>
              </div>
            </fieldset>

            <fieldset className="space-y-3 rounded-md border border-zinc-800/80 p-4">
              <legend className="px-1 text-sm font-medium text-zinc-300">{t('missionEditor.perpLegend')}</legend>
              <label className="flex items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={form.single_thread_perplexity}
                  onChange={(e) => setForm({ ...form, single_thread_perplexity: e.target.checked })}
                />
                <span>{t('missionEditor.singleThread')}</span>
              </label>
              <label className="flex items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={form.save_perplexity_to_library}
                  onChange={(e) => setForm({ ...form, save_perplexity_to_library: e.target.checked })}
                />
                <span>{t('missionEditor.saveThreads')}</span>
              </label>
            </fieldset>
          </TabsContent>

          <TabsContent value="sections" className="space-y-4">
            {sectionKeys.outputs_help && (
              <div className="rounded-md border border-zinc-800 bg-zinc-950/70 p-3 text-xs leading-relaxed text-zinc-400">
                <strong className="text-zinc-200">{t('missionEditor.outputsWhere')}</strong>
                <p className="mt-1">{sectionKeys.outputs_help}</p>
              </div>
            )}

            <div>
              <div className="mb-2 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <Label>{t('missionEditor.sectionsLabel')}</Label>
                  <p className="text-xs text-zinc-500">
                    <Trans
                      i18nKey="missionEditor.sectionsHint"
                      components={{
                        strong: <strong />,
                        span: <span className="font-mono text-zinc-400" />,
                      }}
                    />
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <select
                    className="min-w-[240px] max-w-full rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm"
                    value={addKey}
                    onChange={(e) => setAddKey(e.target.value)}
                    aria-label={t('missionEditor.addSectionAria')}
                  >
                    <option value="">{t('missionEditor.chooseSection')}</option>
                    {availableToAdd.map((k) => (
                      <option key={k} value={k}>
                        {k} — {meta[k]?.title ?? k}
                      </option>
                    ))}
                  </select>
                  <Button
                    type="button"
                    variant="outline"
                    className="text-xs"
                    disabled={!addKey}
                    onClick={addSectionFromSelect}
                  >
                    {t('missionEditor.add')}
                  </Button>
                </div>
              </div>
              {addKey && meta[addKey] && (
                <div className="mb-3 rounded-md border border-violet-900/40 bg-violet-950/20 px-3 py-2 text-xs text-zinc-300">
                  <p className="font-medium text-violet-200">{meta[addKey].title}</p>
                  <p className="mt-1 text-zinc-400">{meta[addKey].summary}</p>
                  <p className="mt-1 font-mono text-zinc-500">{meta[addKey].output}</p>
                </div>
              )}
              {availableToAdd.length === 0 && (
                <p className="mb-2 text-xs text-zinc-500">{t('missionEditor.allSectionsAdded')}</p>
              )}
              <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
                <SortableContext
                  items={form.sections_needed}
                  strategy={verticalListSortingStrategy}
                >
                  {form.sections_needed.map((sec) => (
                    <SortableRow key={sec} id={sec}>
                      <div className="min-w-0 flex-1">
                        <div className="font-mono text-sm text-zinc-100">{sec}</div>
                        {meta[sec] && (
                          <div className="text-xs text-zinc-500">
                            {meta[sec].title} ·{' '}
                            <span className="font-mono text-zinc-600">{meta[sec].output}</span>
                          </div>
                        )}
                      </div>
                      <Button type="button" variant="ghost" onClick={() => removeSection(sec)}>
                        {t('missionEditor.remove')}
                      </Button>
                    </SortableRow>
                  ))}
                </SortableContext>
              </DndContext>
            </div>
          </TabsContent>

          <TabsContent value="integrations" className="space-y-4">
            <fieldset className="flex flex-col gap-4 rounded-md border border-zinc-800/80 p-4">
              <legend className="px-1 text-sm font-medium text-zinc-300">{t('missionEditor.servicesLegend')}</legend>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.enable_notion}
                  onChange={(e) => setForm({ ...form, enable_notion: e.target.checked })}
                />
                {t('missionEditor.notionSync')}
              </label>
              <div>
                <Label htmlFor="notion">{t('missionEditor.notionPageId')}</Label>
                <Input
                  id="notion"
                  value={form.notion_page_id ?? ''}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      notion_page_id: e.target.value.trim() ? e.target.value : null,
                    })
                  }
                />
                <p className="mt-1 text-xs text-zinc-500">
                  <Trans
                    i18nKey="missionEditor.notionHint"
                    components={{ code: <code className="text-zinc-400" /> }}
                  />
                </p>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.enable_quality_check}
                  onChange={(e) => setForm({ ...form, enable_quality_check: e.target.checked })}
                />
                {t('missionEditor.qualityCheck')}
              </label>
              <label className="flex flex-col gap-0.5 text-sm sm:flex-row sm:items-center sm:gap-2">
                <span className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.code_needed}
                    onChange={(e) => setForm({ ...form, code_needed: e.target.checked })}
                  />
                  {t('missionEditor.codeFolder')}
                </span>
                <span className="text-xs font-normal text-zinc-500">
                  <Trans
                    i18nKey="missionEditor.codeFolderHint"
                    components={{ code: <code className="text-zinc-400" /> }}
                  />
                </span>
              </label>
              <label className="flex flex-col gap-0.5 text-sm sm:flex-row sm:items-center sm:gap-2">
                <span className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.enable_cursor_cli}
                    onChange={(e) => setForm({ ...form, enable_cursor_cli: e.target.checked })}
                  />
                  {t('missionEditor.cursorCli')}
                </span>
                <span className="text-xs font-normal text-zinc-500">
                  <Trans
                    i18nKey="missionEditor.cursorCliHint"
                    components={{ code: <code className="text-zinc-400" /> }}
                  />
                </span>
              </label>
              <label className="flex flex-col gap-0.5 text-sm sm:flex-row sm:items-center sm:gap-2">
                <span className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.cursor_cli_optional}
                    onChange={(e) => setForm({ ...form, cursor_cli_optional: e.target.checked })}
                  />
                  {t('missionEditor.cursorOptional')}
                </span>
                <span className="text-xs font-normal text-zinc-500">{t('missionEditor.cursorOptionalHint')}</span>
              </label>
            </fieldset>
          </TabsContent>

          <TabsContent value="pipeline2" className="space-y-4">
            <fieldset className="space-y-4 rounded-md border border-violet-900/30 bg-violet-950/10 p-4">
              <legend className="px-1 text-sm font-medium text-violet-200">{t('missionEditor.p2Legend')}</legend>
              <p className="text-xs text-zinc-500">{t('missionEditor.p2Intro')}</p>
              <label className="flex items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={form.enable_epistemic_injection}
                  onChange={(e) => setForm({ ...form, enable_epistemic_injection: e.target.checked })}
                />
                <span>{t('missionEditor.epistemic')}</span>
              </label>
              <label className="flex items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={form.enable_degradation_monitor}
                  onChange={(e) => setForm({ ...form, enable_degradation_monitor: e.target.checked })}
                />
                <span>{t('missionEditor.degradation')}</span>
              </label>
              <label className="flex items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={form.enable_skill_orchestrator}
                  onChange={(e) => setForm({ ...form, enable_skill_orchestrator: e.target.checked })}
                />
                <span>{t('missionEditor.skills')}</span>
              </label>
              <label className="flex items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={form.enable_hypervisor_triage}
                  onChange={(e) => setForm({ ...form, enable_hypervisor_triage: e.target.checked })}
                />
                <span>
                  <Trans
                    i18nKey="missionEditor.hypervisor"
                    components={{ code: <code className="text-zinc-400" /> }}
                  />
                </span>
              </label>
            </fieldset>
          </TabsContent>

          <TabsContent value="advanced" className="space-y-4">
            <p className="text-xs text-zinc-500">
              <Trans
                i18nKey="missionEditor.advancedBlurb"
                components={{ code: <code className="text-zinc-400" /> }}
              />
            </p>

            <fieldset className="space-y-3 rounded-md border border-zinc-800/80 p-4">
              <legend className="px-1 text-sm font-medium text-zinc-300">{t('missionEditor.qgLegend')}</legend>
              <p className="text-xs text-zinc-500">
                <Trans
                  i18nKey="missionEditor.qgIntro"
                  components={{ code: <code className="text-zinc-400" /> }}
                />
              </p>
              <div>
                <Label htmlFor="qg_metric">target_metric</Label>
                <Input
                  id="qg_metric"
                  value={form.quality_gates.target_metric}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      quality_gates: { ...form.quality_gates, target_metric: e.target.value },
                    })
                  }
                />
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.quality_gates.higher_is_better}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      quality_gates: { ...form.quality_gates, higher_is_better: e.target.checked },
                    })
                  }
                />
                higher_is_better
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <Label htmlFor="qg_sota">sota_baseline_value</Label>
                  <Input
                    id="qg_sota"
                    type="number"
                    step="any"
                    value={form.quality_gates.sota_baseline_value}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        quality_gates: {
                          ...form.quality_gates,
                          sota_baseline_value: Number(e.target.value) || 0,
                        },
                      })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="qg_break">breakthrough_margin</Label>
                  <Input
                    id="qg_break"
                    type="number"
                    step="any"
                    value={form.quality_gates.breakthrough_margin}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        quality_gates: {
                          ...form.quality_gates,
                          breakthrough_margin: Number(e.target.value) || 0,
                        },
                      })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="qg_rep">replication_tolerance</Label>
                  <Input
                    id="qg_rep"
                    type="number"
                    step="any"
                    value={form.quality_gates.replication_tolerance}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        quality_gates: {
                          ...form.quality_gates,
                          replication_tolerance: Number(e.target.value) || 0,
                        },
                      })
                    }
                  />
                </div>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.quality_gates.require_statistical_significance}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      quality_gates: {
                        ...form.quality_gates,
                        require_statistical_significance: e.target.checked,
                      },
                    })
                  }
                />
                require_statistical_significance
              </label>
            </fieldset>

            <fieldset className="space-y-3 rounded-md border border-zinc-800/80 p-4">
              <legend className="px-1 text-sm font-medium text-zinc-300">{t('missionEditor.hypothesesLegend')}</legend>
              <p className="text-xs text-zinc-500">
                <Trans
                  i18nKey="missionEditor.hypothesesIntro"
                  components={{ code: <code className="text-zinc-400" /> }}
                />
              </p>
              <Button
                type="button"
                variant="outline"
                className="text-xs"
                onClick={() =>
                  setForm({ ...form, hypotheses: [...form.hypotheses, newHypothesisRow()] })
                }
              >
                {t('missionEditor.addHypothesis')}
              </Button>
              <div className="space-y-4">
                {form.hypotheses.map((h, idx) => (
                  <div
                    key={`${h.id}-${idx}`}
                    className="rounded-md border border-zinc-800 bg-zinc-950/50 p-3"
                  >
                    <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                      <span className="text-xs font-medium text-zinc-400">
                        {t('missionEditor.hypothesisN', { n: idx + 1 })}
                      </span>
                      <Button
                        type="button"
                        variant="ghost"
                        className="h-8 text-xs text-red-400 hover:text-red-300"
                        onClick={() =>
                          setForm({
                            ...form,
                            hypotheses: form.hypotheses.filter((_, i) => i !== idx),
                          })
                        }
                      >
                        {t('missionEditor.remove')}
                      </Button>
                    </div>
                    <div className="grid gap-2 sm:grid-cols-2">
                      <div>
                        <Label htmlFor={`hyp-id-${idx}`}>id</Label>
                        <Input
                          id={`hyp-id-${idx}`}
                          value={h.id}
                          onChange={(e) => {
                            const next = [...form.hypotheses]
                            next[idx] = { ...next[idx], id: e.target.value }
                            setForm({ ...form, hypotheses: next })
                          }}
                        />
                      </div>
                      <div>
                        <Label htmlFor={`hyp-prio-${idx}`}>priority</Label>
                        <Input
                          id={`hyp-prio-${idx}`}
                          value={h.priority ?? 'MEDIUM'}
                          onChange={(e) => {
                            const next = [...form.hypotheses]
                            next[idx] = { ...next[idx], priority: e.target.value }
                            setForm({ ...form, hypotheses: next })
                          }}
                        />
                      </div>
                    </div>
                    <div className="mt-2">
                      <Label htmlFor={`hyp-desc-${idx}`}>description</Label>
                      <Input
                        id={`hyp-desc-${idx}`}
                        value={h.description}
                        onChange={(e) => {
                          const next = [...form.hypotheses]
                          next[idx] = { ...next[idx], description: e.target.value }
                          setForm({ ...form, hypotheses: next })
                        }}
                      />
                    </div>
                    <div className="mt-2">
                      <Label htmlFor={`hyp-exp-${idx}`}>expected_outcome</Label>
                      <Input
                        id={`hyp-exp-${idx}`}
                        value={h.expected_outcome ?? ''}
                        onChange={(e) => {
                          const next = [...form.hypotheses]
                          next[idx] = { ...next[idx], expected_outcome: e.target.value }
                          setForm({ ...form, hypotheses: next })
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </fieldset>
          </TabsContent>
        </Tabs>

        <div className="mt-6 flex flex-wrap items-center gap-2 border-t border-zinc-800 pt-4">
          <Button onClick={() => save.mutate(form)} disabled={save.isPending}>
            {save.isPending ? t('missionEditor.saving') : t('missionEditor.save')}
          </Button>
          {save.isSuccess && <span className="text-sm text-emerald-400">{t('missionEditor.saved')}</span>}
          {save.isError && (
            <span className="text-sm text-red-400">{(save.error as Error).message}</span>
          )}
        </div>
      </Card>
    </div>
  )
}
