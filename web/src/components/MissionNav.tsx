import { cn } from '@/lib/utils'
import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'

export function MissionNav({ missionId }: { missionId: string }) {
  const { t } = useTranslation()
  const links = [
    { to: 'brain', labelKey: 'nav.brain' as const },
    { to: 'edit', labelKey: 'nav.editor' as const },
    { to: 'run', labelKey: 'nav.pipeline' as const },
    { to: 'draft', labelKey: 'nav.draft' as const },
    { to: 'loop', labelKey: 'nav.loop' as const },
    { to: 'logs', labelKey: 'nav.logs' as const },
    { to: 'live', labelKey: 'nav.live' as const },
    { to: 'cockpit', labelKey: 'nav.cockpit' as const },
  ] as const

  return (
    <nav className="no-print mb-6 flex flex-wrap gap-2 border-b border-zinc-800 pb-3">
      <NavLink
        to="/"
        end
        className={({ isActive }) =>
          cn(
            'rounded-md px-3 py-1.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950',
            isActive ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-500 hover:text-zinc-200',
          )
        }
      >
        {t('nav.home')}
      </NavLink>
      {links.map(({ to, labelKey }) => (
        <NavLink
          key={to}
          to={`/missions/${missionId}/${to}`}
          className={({ isActive }) =>
            cn(
              'rounded-md px-3 py-1.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950',
              isActive
                ? 'bg-violet-600/30 text-violet-200'
                : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200',
            )
          }
        >
          {t(labelKey)}
        </NavLink>
      ))}
    </nav>
  )
}
