import { OnboardingModal } from '@/components/OnboardingModal'
import { isOnboardingDismissed } from '@/lib/onboarding'
import { useCallback, useState } from 'react'
import { useTranslation } from 'react-i18next'

export function OnboardingShell() {
  const { t } = useTranslation()
  const [open, setOpen] = useState(() => !isOnboardingDismissed())

  const handleClose = useCallback(() => {
    setOpen(false)
  }, [])

  return (
    <>
      <OnboardingModal open={open} onClose={handleClose} />
      <button
        type="button"
        className="no-print fixed bottom-5 right-5 z-50 flex h-11 w-11 items-center justify-center rounded-full border border-zinc-600 bg-zinc-800 text-lg font-semibold text-zinc-200 shadow-lg transition hover:bg-zinc-700 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-400 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950"
        title={t('onboardingShell.helpTitle')}
        aria-label={t('onboardingShell.helpAria')}
        onClick={() => setOpen(true)}
      >
        ?
      </button>
    </>
  )
}
