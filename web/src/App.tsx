import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import { OnboardingShell } from '@/components/OnboardingShell'
import { RouteFallback } from '@/components/RouteFallback'
import { lazy, Suspense } from 'react'
import { useTranslation } from 'react-i18next'
import { Navigate, Route, Routes } from 'react-router-dom'

const Home = lazy(() => import('@/pages/Home').then((m) => ({ default: m.Home })))
const BrainPage = lazy(() => import('@/pages/BrainPage').then((m) => ({ default: m.BrainPage })))
const MissionEditor = lazy(() =>
  import('@/pages/MissionEditor').then((m) => ({ default: m.MissionEditor })),
)
const Runner = lazy(() => import('@/pages/Runner').then((m) => ({ default: m.Runner })))
const DraftEditor = lazy(() =>
  import('@/pages/DraftEditor').then((m) => ({ default: m.DraftEditor })),
)
const LoopControl = lazy(() =>
  import('@/pages/LoopControl').then((m) => ({ default: m.LoopControl })),
)
const LogsPage = lazy(() => import('@/pages/LogsPage').then((m) => ({ default: m.LogsPage })))
const LiveTerminalPage = lazy(() =>
  import('@/pages/LiveTerminalPage').then((m) => ({ default: m.LiveTerminalPage })),
)
const CockpitPage = lazy(() =>
  import('@/pages/CockpitPage').then((m) => ({ default: m.CockpitPage })),
)

function AppChrome() {
  const { t } = useTranslation()
  return (
    <div className="min-h-svh">
      <a href="#main-content" className="skip-link">
        {t('app.skipToContent')}
      </a>
      <LanguageSwitcher />
      <OnboardingShell />
      <Suspense fallback={<RouteFallback />}>
        <main id="main-content" tabIndex={-1}>
          <Routes>
            <Route path="/missions/:id/brain" element={<BrainPage />} />
            <Route path="/missions/:id/edit" element={<MissionEditor />} />
            <Route path="/missions/:id/run" element={<Runner />} />
            <Route path="/missions/:id/draft" element={<DraftEditor />} />
            <Route path="/missions/:id/loop" element={<LoopControl />} />
            <Route path="/missions/:id/logs" element={<LogsPage />} />
            <Route path="/missions/:id/live" element={<LiveTerminalPage />} />
            <Route path="/missions/:id/cockpit" element={<CockpitPage />} />
            <Route path="/" element={<Home />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </Suspense>
    </div>
  )
}

export default function App() {
  return <AppChrome />
}
