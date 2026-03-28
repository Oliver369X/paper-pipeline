import { MissionNav } from '@/components/MissionNav'
import { Button } from '@/components/ui/button'
import { Card, CardTitle } from '@/components/ui/card'
import { apiDelete, apiGet, apiPost } from '@/lib/api'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { Link, useParams } from 'react-router-dom'

const zincCode = <code className="text-zinc-300" />
const amberCode = <code className="text-amber-100" />

type ChatMsg = { role: 'user' | 'assistant'; content: string }

type BrainChatResponse = {
  reply: string
  brief_markdown: string
  meta: { title: string; description: string }
  suggested_patch: Record<string, unknown>
  suggested_code_files?: Record<string, string>
  cursor_checklist_markdown?: string
  followup_questions?: string[]
}

type BrainApplyResponse = { ok: boolean; run_id?: string | null }

type BrainExportResponse = { ok: boolean; path?: string; absolute?: string }

type BrainVariantItem = {
  label: string
  short_rationale: string
  brief_markdown: string
  suggested_patch: Record<string, unknown>
}

export function BrainPage() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const qc = useQueryClient()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMsg[]>([])
  const [last, setLast] = useState<BrainChatResponse | null>(null)
  const [variantN, setVariantN] = useState(5)
  const [variants, setVariants] = useState<BrainVariantItem[] | null>(null)
  /** Por defecto ejecutar pipeline tras aplicar (mismo efecto que Run; se puede desmarcar). */
  const [runAfterApply, setRunAfterApply] = useState(true)
  const [dryRunPipeline, setDryRunPipeline] = useState(false)
  const [lastApplyRunId, setLastApplyRunId] = useState<string | null>(null)
  const [lastExportPath, setLastExportPath] = useState<string | null>(null)
  const hydratedRef = useRef(false)

  const health = useQuery({
    queryKey: ['health'],
    queryFn: () =>
      apiGet<{ brain_gemini?: 'missing' | 'missing_sdk' | 'configured' }>('/api/health'),
  })

  const historyQuery = useQuery({
    queryKey: ['brain-history', id],
    queryFn: () =>
      apiGet<{ messages: { ts: string; role: string; content: string }[] }>(
        `/api/missions/${id}/brain/history`,
      ),
    enabled: !!id,
  })

  useEffect(() => {
    hydratedRef.current = false
  }, [id])

  useEffect(() => {
    if (!id || historyQuery.isLoading || historyQuery.isError) return
    if (hydratedRef.current) return
    hydratedRef.current = true
    const rows = historyQuery.data?.messages ?? []
    if (rows.length === 0) return
    /* eslint-disable react-hooks/set-state-in-effect -- hidratar chat desde historial API una vez por misión */
    setMessages(
      rows.map((m) => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      })),
    )
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [id, historyQuery.isLoading, historyQuery.isError, historyQuery.data])

  const chat = useMutation({
    mutationFn: async ({ text, history }: { text: string; history: ChatMsg[] }) => {
      const next: ChatMsg[] = [...history, { role: 'user', content: text }]
      const body = {
        messages: next.map((m) => ({ role: m.role, content: m.content })),
      }
      return apiPost<BrainChatResponse>(`/api/missions/${id}/brain/chat`, body)
    },
    onSuccess: (data, { text, history }) => {
      setMessages([
        ...history,
        { role: 'user', content: text },
        { role: 'assistant', content: data.reply },
      ])
      setInput('')
      setLast(data)
      void qc.invalidateQueries({ queryKey: ['mission', id] })
    },
  })

  const fetchVariants = useMutation({
    mutationFn: async () => {
      const n = Math.min(10, Math.max(1, Math.floor(variantN)))
      const body = {
        n,
        messages: messages.map((m) => ({ role: m.role, content: m.content })),
      }
      return apiPost<{ variants: BrainVariantItem[] }>(
        `/api/missions/${id}/brain/variants`,
        body,
      )
    },
    onSuccess: (data) => {
      setVariants(data.variants ?? [])
    },
  })

  const applyAll = useMutation({
    mutationFn: () => {
      if (!last) throw new Error(t('brain.errNoBrain'))
      return apiPost<BrainApplyResponse>(`/api/missions/${id}/brain/apply`, {
        brief_markdown: last.brief_markdown,
        patch: last.suggested_patch,
        suggested_code_files: last.suggested_code_files ?? {},
        run_pipeline: runAfterApply,
        dry_run: dryRunPipeline,
      })
    },
    onSuccess: (data) => {
      setLastApplyRunId(data.run_id ?? null)
      void qc.invalidateQueries({ queryKey: ['mission', id] })
      void qc.invalidateQueries({ queryKey: ['missions'] })
    },
  })

  const applyBriefOnly = useMutation({
    mutationFn: () => {
      if (!last?.brief_markdown) throw new Error(t('brain.errNoBrief'))
      return apiPost<BrainApplyResponse>(`/api/missions/${id}/brain/apply`, {
        brief_markdown: last.brief_markdown,
        patch: {},
        run_pipeline: runAfterApply,
        dry_run: dryRunPipeline,
      })
    },
    onSuccess: (data) => {
      setLastApplyRunId(data.run_id ?? null)
      void qc.invalidateQueries({ queryKey: ['mission', id] })
    },
  })

  const applyVariant = useMutation({
    mutationFn: (v: BrainVariantItem) =>
      apiPost<BrainApplyResponse>(`/api/missions/${id}/brain/apply`, {
        brief_markdown: v.brief_markdown,
        patch: v.suggested_patch,
        run_pipeline: runAfterApply,
        dry_run: dryRunPipeline,
      }),
    onSuccess: (data) => {
      setLastApplyRunId(data.run_id ?? null)
      void qc.invalidateQueries({ queryKey: ['mission', id] })
      void qc.invalidateQueries({ queryKey: ['missions'] })
    },
  })

  const exportChat = useMutation({
    mutationFn: () => apiPost<BrainExportResponse>(`/api/missions/${id}/brain/export`, {}),
    onSuccess: (data) => {
      setLastExportPath(data.path ?? data.absolute ?? null)
    },
  })

  const clearChat = useCallback(async () => {
    if (!id) return
    try {
      await apiDelete(`/api/missions/${id}/brain/history`)
    } catch {
      /* ignore */
    }
    setMessages([])
    setLast(null)
    setVariants(null)
    setLastApplyRunId(null)
    setLastExportPath(null)
    hydratedRef.current = true
    void qc.invalidateQueries({ queryKey: ['brain-history', id] })
  }, [id, qc])

  if (!id) return <p className="p-6 text-zinc-500">{t('common.missingId')}</p>

  const brainState = health.data?.brain_gemini
  const brainOk = brainState === 'configured'

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <MissionNav missionId={id} />

      <Card className="mb-6">
        <CardTitle>{t('brain.title')}</CardTitle>
        <p className="mt-1 text-sm text-zinc-400">
          <Trans
            i18nKey="brain.introFull"
            components={{
              code: zincCode,
              cockpitLink: (
                <Link to={`/missions/${id}/cockpit`} className="text-violet-400 hover:underline" />
              ),
            }}
          />
        </p>
        {brainState === 'missing' && (
          <p className="mt-2 rounded border border-amber-900/50 bg-amber-950/30 p-2 text-sm text-amber-200">
            <Trans i18nKey="brain.missingKey" components={{ code: amberCode }} />
          </p>
        )}
        {brainState === 'missing_sdk' && (
          <p className="mt-2 rounded border border-amber-900/50 bg-amber-950/30 p-2 text-sm text-amber-200">
            <Trans i18nKey="brain.missingSdk" components={{ code: amberCode }} />
          </p>
        )}
      </Card>

      {lastApplyRunId && (
        <p className="mb-4 rounded border border-emerald-900/50 bg-emerald-950/20 px-3 py-2 text-sm text-emerald-200">
          {t('brain.pipelineStarted')} <code className="text-emerald-100">{lastApplyRunId}</code>{' '}
          <Link
            to={`/missions/${id}/live?run_id=${encodeURIComponent(lastApplyRunId)}&autoconnect=1`}
            className="text-violet-400 hover:underline"
          >
            {t('brain.openLive')}
          </Link>
        </p>
      )}

      <div className="mb-3 flex flex-wrap gap-4 text-sm text-zinc-400">
        <label className="flex cursor-pointer items-center gap-2">
          <input
            type="checkbox"
            checked={runAfterApply}
            onChange={(e) => setRunAfterApply(e.target.checked)}
          />
          {t('brain.runAfterApply')}
        </label>
        <label className="flex cursor-pointer items-center gap-2">
          <input
            type="checkbox"
            checked={dryRunPipeline}
            onChange={(e) => setDryRunPipeline(e.target.checked)}
            disabled={!runAfterApply}
          />
          {t('brain.dryRun')}
        </label>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <Button type="button" variant="outline" className="text-xs py-1.5 px-2" onClick={() => void clearChat()}>
          {t('brain.clearChat')}
        </Button>
        <Button
          type="button"
          variant="outline"
          className="text-xs py-1.5 px-2"
          disabled={!id || exportChat.isPending || messages.length === 0}
          onClick={() => exportChat.mutate()}
        >
          {exportChat.isPending ? '…' : t('brain.saveConversation')}
        </Button>
        <Button
          type="button"
          className="text-xs py-1.5 px-2"
          disabled={!last || applyAll.isPending}
          onClick={() => applyAll.mutate()}
        >
          {t('brain.applyAll')}
        </Button>
        <Button
          type="button"
          variant="outline"
          className="text-xs py-1.5 px-2"
          disabled={!last?.brief_markdown || applyBriefOnly.isPending}
          onClick={() => applyBriefOnly.mutate()}
        >
          {t('brain.saveBriefOnly')}
        </Button>
        <span className="text-xs text-zinc-500">{t('brain.variantsLabel')}</span>
        <input
          type="number"
          min={1}
          max={10}
          className="w-14 rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-xs"
          value={variantN}
          onChange={(e) => setVariantN(Number(e.target.value))}
        />
        <Button
          type="button"
          variant="outline"
          className="text-xs py-1.5 px-2"
          disabled={!brainOk || fetchVariants.isPending || messages.length === 0}
          onClick={() => fetchVariants.mutate()}
        >
          {fetchVariants.isPending ? '…' : t('brain.generateVariants')}
        </Button>
      </div>

      {lastExportPath && (
        <p className="mb-2 text-xs text-emerald-400">
          {t('brain.exportSaved')} <code className="text-emerald-200">{lastExportPath}</code> (y{' '}
          <code className="text-emerald-200">outputs/brain_latest_export.md</code>)
        </p>
      )}

      <div className="mb-4 max-h-[min(28rem,70vh)] space-y-2 overflow-auto rounded border border-zinc-800 bg-zinc-950 p-3 text-sm">
        {historyQuery.isLoading && <p className="text-zinc-500">{t('brain.loadingHistory')}</p>}
        {!historyQuery.isLoading && messages.length === 0 && (
          <p className="text-zinc-500">{t('brain.emptyChat')}</p>
        )}
        {messages.map((m, i) => (
          <div
            key={`${i}-${m.role}`}
            className={m.role === 'user' ? 'text-zinc-200' : 'text-zinc-400'}
          >
            <span className="font-semibold text-violet-400">
              {m.role === 'user' ? t('brain.you') : t('brain.brain')}
            </span>
            : {m.content}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <textarea
          className="min-h-[100px] flex-1 rounded-md border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
          placeholder={t('brain.placeholder')}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={chat.isPending || !brainOk}
        />
        <Button
          type="button"
          disabled={!input.trim() || chat.isPending || !brainOk}
          onClick={() => {
            const text = input.trim()
            if (!text) return
            chat.mutate({ text, history: messages })
          }}
        >
          {chat.isPending ? '…' : t('brain.send')}
        </Button>
      </div>

      {last?.followup_questions && last.followup_questions.length > 0 && (
        <div className="mt-3">
          <p className="mb-2 text-xs font-medium text-zinc-500">{t('brain.followupTitle')}</p>
          <div className="flex flex-wrap gap-2">
            {last.followup_questions.map((q) => (
              <button
                key={q.slice(0, 80)}
                type="button"
                className="max-w-full rounded-full border border-violet-800/80 bg-violet-950/40 px-3 py-1.5 text-left text-xs text-violet-200 hover:bg-violet-900/50"
                onClick={() => {
                  chat.mutate({ text: q, history: messages })
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {chat.isError && (
        <p className="mt-2 text-sm text-red-400">{(chat.error as Error).message}</p>
      )}
      {fetchVariants.isError && (
        <p className="mt-2 text-sm text-red-400">{(fetchVariants.error as Error).message}</p>
      )}
      {applyAll.isError && (
        <p className="mt-2 text-sm text-red-400">{(applyAll.error as Error).message}</p>
      )}

      {variants && variants.length > 0 && (
        <div className="mt-8 space-y-3">
          <CardTitle className="text-base">{t('brain.variantsTitle')}</CardTitle>
          {variants.map((v, i) => (
            <Card key={`${v.label}-${i}`} className="p-3">
              <p className="font-medium text-zinc-200">
                {v.label || t('brain.variantFallback', { n: i + 1 })}
              </p>
              <p className="mt-1 text-xs text-zinc-500">{v.short_rationale}</p>
              <Button
                type="button"
                className="mt-2 text-xs py-1.5 px-2"
                disabled={applyVariant.isPending}
                onClick={() => applyVariant.mutate(v)}
              >
                {t('brain.applyVariant')}
              </Button>
            </Card>
          ))}
        </div>
      )}

      {last && (
        <div className="mt-8 space-y-4">
          <Card>
            <CardTitle className="text-base">{t('brain.briefTitle')}</CardTitle>
            <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap rounded border border-zinc-800 bg-black p-2 text-xs text-zinc-300">
              {last.brief_markdown || t('brain.dash')}
            </pre>
          </Card>
          {last.cursor_checklist_markdown?.trim() ? (
            <Card>
              <CardTitle className="text-base">{t('brain.checklistTitle')}</CardTitle>
              <p className="mt-1 text-xs text-zinc-500">
                <Trans i18nKey="brain.checklistHint" components={{ code: <code className="text-zinc-400" /> }} />
              </p>
              <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap rounded border border-zinc-800 bg-black p-2 text-xs text-zinc-300">
                {last.cursor_checklist_markdown}
              </pre>
              <Button
                type="button"
                variant="outline"
                className="mt-2 text-xs"
                onClick={() =>
                  void navigator.clipboard.writeText(last.cursor_checklist_markdown ?? '')
                }
              >
                {t('brain.copyChecklist')}
              </Button>
            </Card>
          ) : null}
          {last.suggested_code_files && Object.keys(last.suggested_code_files).length > 0 ? (
            <Card>
              <CardTitle className="text-base">{t('brain.codeSuggestedTitle')}</CardTitle>
              <p className="mt-1 text-xs text-zinc-500">
                <Trans i18nKey="brain.codeSuggestedHint" components={{ code: <code className="text-zinc-400" /> }} />
              </p>
              {Object.entries(last.suggested_code_files).map(([path, src]) => (
                <div key={path} className="mt-2">
                  <p className="text-xs font-mono text-violet-300">{path}</p>
                  <pre className="mt-1 max-h-40 overflow-auto whitespace-pre-wrap rounded border border-zinc-800 bg-black p-2 text-xs text-zinc-300">
                    {src}
                  </pre>
                </div>
              ))}
            </Card>
          ) : null}
          <Card>
            <CardTitle className="text-base">{t('brain.patchTitle')}</CardTitle>
            <pre className="mt-2 max-h-64 overflow-auto rounded border border-zinc-800 bg-black p-2 text-xs text-zinc-400">
              {JSON.stringify(last.suggested_patch, null, 2)}
            </pre>
          </Card>
        </div>
      )}
    </div>
  )
}
