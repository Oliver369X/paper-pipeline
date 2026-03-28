import { MissionNav } from '@/components/MissionNav'
import { Button } from '@/components/ui/button'
import { Card, CardTitle } from '@/components/ui/card'
import { apiGet } from '@/lib/api'
import { DiffEditor } from '@monaco-editor/react'
import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { useParams } from 'react-router-dom'

export function LogsPage() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const [filter, setFilter] = useState('')
  const [left, setLeft] = useState<string | null>(null)
  const [right, setRight] = useState<string | null>(null)

  const logs = useQuery({
    queryKey: ['run-log', id],
    queryFn: () => apiGet<Record<string, unknown>[]>(`/api/missions/${id}/run-log`),
    enabled: Boolean(id),
  })

  const directives = useQuery({
    queryKey: ['directive-history', id],
    queryFn: () => apiGet<Record<string, unknown>[]>(`/api/missions/${id}/directive-history`),
    enabled: Boolean(id),
  })

  const snaps = useQuery({
    queryKey: ['snapshots', id],
    queryFn: () => apiGet<{ snapshots: string[] }>(`/api/missions/${id}/snapshots`),
    enabled: Boolean(id),
  })

  const pipelineEvents = useQuery({
    queryKey: ['events-log', id],
    queryFn: () => apiGet<Record<string, unknown>[]>(`/api/missions/${id}/events-log`),
    enabled: Boolean(id),
  })

  const leftContent = useQuery({
    queryKey: ['snap', id, left],
    queryFn: () => apiGet<{ content: string }>(`/api/missions/${id}/snapshots/${left}`),
    enabled: Boolean(id && left),
  })

  const rightContent = useQuery({
    queryKey: ['snap', id, right],
    queryFn: () => apiGet<{ content: string }>(`/api/missions/${id}/snapshots/${right}`),
    enabled: Boolean(id && right),
  })

  const filtered = useMemo(() => {
    const rows = logs.data ?? []
    if (!filter.trim()) return rows
    const q = filter.toLowerCase()
    return rows.filter((r) => JSON.stringify(r).toLowerCase().includes(q))
  }, [logs.data, filter])

  if (!id) return <p className="p-6 text-zinc-500">{t('common.missingId')}</p>

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 print:max-w-none">
      <div className="no-print">
        <MissionNav missionId={id} />
      </div>

      <div className="mb-4 flex justify-end no-print">
        <Button type="button" variant="outline" onClick={() => window.print()}>
          {t('logs.printPdf')}
        </Button>
      </div>

      <Card className="mb-6">
        <CardTitle>{t('logs.pipelineEventsTitle')}</CardTitle>
        <p className="mb-2 text-xs text-zinc-500">{t('logs.pipelineEventsHint')}</p>
        <div className="max-h-48 overflow-auto rounded border border-zinc-800 font-mono text-xs">
          <ul className="divide-y divide-zinc-800">
            {(pipelineEvents.data ?? []).map((row, i) => (
              <li key={i} className="p-2 text-zinc-300">
                <span className="text-emerald-400">{String(row.event ?? row.ts ?? '')}</span>{' '}
                {JSON.stringify(row)}
              </li>
            ))}
          </ul>
        </div>
        {pipelineEvents.isLoading && <p className="text-sm text-zinc-500">{t('common.loading')}</p>}
      </Card>

      <Card className="mb-6">
        <CardTitle>{t('logs.runLogTitle')}</CardTitle>
        <InputLikeFilter
          value={filter}
          onChange={setFilter}
          placeholder={t('logs.filterPlaceholder')}
        />
        <div className="mt-2 max-h-64 overflow-auto rounded border border-zinc-800">
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 bg-zinc-900">
              <tr>
                <th className="p-2">{t('logs.colNum')}</th>
                <th className="p-2">{t('logs.colEvent')}</th>
                <th className="p-2">{t('logs.colDetail')}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row, i) => (
                <tr key={i} className="border-t border-zinc-800">
                  <td className="p-2 text-zinc-500">{i + 1}</td>
                  <td className="p-2 font-mono">{String(row.event ?? '')}</td>
                  <td className="p-2 font-mono text-zinc-400">
                    {JSON.stringify(row).slice(0, 200)}
                    {JSON.stringify(row).length > 200 ? '…' : ''}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {logs.isLoading && <p className="text-sm text-zinc-500">{t('common.loading')}</p>}
      </Card>

      <Card className="mb-6">
        <CardTitle>{t('logs.directivesTitle')}</CardTitle>
        <ul className="mt-2 max-h-48 space-y-1 overflow-auto font-mono text-xs text-zinc-300">
          {(directives.data ?? []).map((row, i) => (
            <li key={i}>{JSON.stringify(row)}</li>
          ))}
        </ul>
      </Card>

      <Card className="no-print">
        <CardTitle>{t('logs.diffTitle')}</CardTitle>
        <p className="mb-2 text-sm text-zinc-500">
          <Trans i18nKey="logs.diffHint" components={{ code: <code className="text-zinc-300" /> }} />
        </p>
        <div className="mb-2 flex flex-wrap gap-2">
          <select
            className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1 text-sm"
            value={left ?? ''}
            onChange={(e) => setLeft(e.target.value || null)}
          >
            <option value="">{t('logs.left')}</option>
            {(snaps.data?.snapshots ?? []).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <select
            className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1 text-sm"
            value={right ?? ''}
            onChange={(e) => setRight(e.target.value || null)}
          >
            <option value="">{t('logs.right')}</option>
            {(snaps.data?.snapshots ?? []).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        {left && right && leftContent.data && rightContent.data && (
          <DiffEditor
            height="420px"
            language="markdown"
            original={leftContent.data.content}
            modified={rightContent.data.content}
            options={{ readOnly: true }}
          />
        )}
      </Card>
    </div>
  )
}

function InputLikeFilter({
  value,
  onChange,
  placeholder,
}: {
  value: string
  onChange: (v: string) => void
  placeholder: string
}) {
  return (
    <input
      className="mt-2 w-full max-w-md rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm"
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}
