import { useTranslation } from 'react-i18next'

/** Carga diferida de rutas (React.lazy); mensaje con elipsis tipográfica (guías de interfaz). */

export function RouteFallback() {
  const { t } = useTranslation()
  return (
    <div
      className="flex min-h-svh items-center justify-center bg-zinc-950 text-zinc-400"
      role="status"
      aria-live="polite"
    >
      {t('routeFallback.loading')}
    </div>
  )
}
