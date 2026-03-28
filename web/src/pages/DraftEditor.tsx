import { MissionNav } from '@/components/MissionNav'
import { Card, CardTitle } from '@/components/ui/card'
import { apiGet, apiPut } from '@/lib/api'
import { Markdown } from '@tiptap/markdown'
import Placeholder from '@tiptap/extension-placeholder'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { useParams } from 'react-router-dom'

export function DraftEditor() {
  const { t, i18n } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['draft', id],
    queryFn: () => apiGet<{ content: string }>(`/api/missions/${id}/draft`),
    enabled: Boolean(id),
  })

  const editor = useEditor(
    {
      extensions: [
        StarterKit,
        Markdown,
        Placeholder.configure({ placeholder: t('draft.placeholder') }),
      ],
      content: '',
      contentType: 'markdown',
      editorProps: {
        attributes: {
          class:
            'max-w-none min-h-[320px] focus:outline-none px-3 py-2 rounded-md border border-zinc-800 bg-zinc-950 text-sm leading-relaxed',
        },
      },
    },
    [i18n.language, t],
  )

  useEffect(() => {
    if (!editor || data === undefined) return
    const cur = editor.getMarkdown()
    if (cur !== data.content) {
      editor.commands.setContent(data.content, { contentType: 'markdown' })
    }
  }, [editor, data])

  useEffect(() => {
    if (!editor || !id) return
    const save = () => {
      const md = editor.getMarkdown()
      void apiPut(`/api/missions/${id}/draft`, { content: md })
    }
    const onUpdate = () => {
      if (saveTimer.current) clearTimeout(saveTimer.current)
      saveTimer.current = setTimeout(save, 30_000)
    }
    editor.on('update', onUpdate)
    return () => {
      editor.off('update', onUpdate)
      if (saveTimer.current) clearTimeout(saveTimer.current)
    }
  }, [editor, id])

  if (!id) return <p className="p-6 text-zinc-500">{t('common.missingId')}</p>
  if (isLoading || !editor) return <p className="p-6 text-zinc-500">{t('common.loading')}</p>

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <MissionNav missionId={id} />
      <Card>
        <CardTitle>{t('draft.title')}</CardTitle>
        <p className="mb-2 text-sm text-zinc-500">
          <Trans i18nKey="draft.autosave" components={{ code: <code className="text-zinc-300" /> }} />
        </p>
        <EditorContent editor={editor} />
      </Card>
    </div>
  )
}
