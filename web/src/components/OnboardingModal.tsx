import { Button } from '@/components/ui/button'
import { API_BASE } from '@/lib/api'
import { dismissOnboarding } from '@/lib/onboarding'
import type { TFunction } from 'i18next'
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { Trans, useTranslation } from 'react-i18next'

const violetCode = <code className="text-violet-300" />

function buildSteps(t: TFunction, remote: boolean): { title: string; body: ReactNode }[] {
  return [
    {
      title: t('onboarding.steps.welcomeTitle'),
      body: (
        <>
          <p>
            <Trans i18nKey="onboarding.welcomeP1" components={{ strong: <strong /> }} />
          </p>
          {remote ? (
            <p className="mt-2 text-zinc-400">
              <Trans
                i18nKey="onboarding.welcomeRemote"
                components={{ code: violetCode }}
              />
            </p>
          ) : (
            <p className="mt-2 text-zinc-400">
              <Trans i18nKey="onboarding.welcomeLocal" components={{ strong: <strong /> }} />
            </p>
          )}
        </>
      ),
    },
    {
      title: t('onboarding.steps.flowTitle'),
      body: (
        <ol className="list-decimal space-y-2 pl-5 text-zinc-300">
          {(['flow1', 'flow2', 'flow3', 'flow4', 'flow5', 'flow6'] as const).map((k) => (
            <li key={k}>
              <Trans i18nKey={`onboarding.${k}`} components={{ strong: <strong /> }} />
            </li>
          ))}
        </ol>
      ),
    },
    {
      title: t('onboarding.steps.beforeTitle'),
      body: remote ? (
        <>
          <p>{t('onboarding.beforeRemoteP1')}</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-zinc-400">
            {(['beforeRemoteLi1', 'beforeRemoteLi2', 'beforeRemoteLi3', 'beforeRemoteLi4'] as const).map(
              (k) => (
                <li key={k}>
                  <Trans
                    i18nKey={`onboarding.${k}`}
                    components={{ code: violetCode, strong: <strong /> }}
                  />
                </li>
              ),
            )}
          </ul>
        </>
      ) : (
        <>
          <p>{t('onboarding.beforeLocalP1')}</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-zinc-400">
            {(
              [
                'beforeLocalLi1',
                'beforeLocalLi2',
                'beforeLocalLi3',
                'beforeLocalLi4',
                'beforeLocalLi5',
              ] as const
            ).map((k) => (
              <li key={k}>
                <Trans
                  i18nKey={`onboarding.${k}`}
                  components={{ code: violetCode, strong: <strong /> }}
                />
              </li>
            ))}
          </ul>
        </>
      ),
    },
    {
      title: t('onboarding.steps.navTitle'),
      body: (
        <>
          <p>
            <Trans
              i18nKey="onboarding.navP1"
              components={{
                strong: <strong />,
              }}
            />
          </p>
          <p className="mt-2 text-zinc-400">
            <Trans
              i18nKey="onboarding.navP2"
              components={{ span: <span className="text-white" /> }}
            />
          </p>
        </>
      ),
    },
  ]
}

type Props = {
  open: boolean
  onClose: () => void
}

export function OnboardingModal({ open, onClose }: Props) {
  if (!open) return null
  return <OnboardingModalInner onClose={onClose} />
}

function OnboardingModalInner({ onClose }: { onClose: () => void }) {
  const { t } = useTranslation()
  const [step, setStep] = useState(0)
  const remote = Boolean(API_BASE)
  const steps = useMemo(() => buildSteps(t, remote), [t, remote])

  const finish = useCallback(() => {
    dismissOnboarding()
    onClose()
  }, [onClose])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const last = step >= steps.length - 1
  const content = steps[step]

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center overflow-y-auto overscroll-contain p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-title"
    >
      <button
        type="button"
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        aria-label={t('onboarding.closeBackdrop')}
        onClick={onClose}
      />
      <div className="relative z-[101] max-h-[min(90vh,32rem)] w-full max-w-lg overflow-y-auto overscroll-contain rounded-xl border border-zinc-700 bg-zinc-900 p-6 shadow-2xl">
        <p className="text-xs font-medium uppercase tracking-wide text-violet-400">
          {t('onboarding.stepOf', { current: step + 1, total: steps.length })}
        </p>
        <h2 id="onboarding-title" className="mt-1 text-xl font-semibold text-white">
          {content.title}
        </h2>
        <div className="mt-4 text-sm leading-relaxed text-zinc-300">{content.body}</div>

        <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex gap-2">
            {steps.map((_, i) => (
              <span
                key={i}
                className={`h-2 w-2 rounded-full ${i === step ? 'bg-violet-500' : 'bg-zinc-600'}`}
                aria-hidden="true"
              />
            ))}
          </div>
          <div className="flex gap-2">
            {step > 0 && (
              <Button type="button" variant="outline" onClick={() => setStep((s) => s - 1)}>
                {t('onboarding.back')}
              </Button>
            )}
            {!last && (
              <Button type="button" onClick={() => setStep((s) => s + 1)}>
                {t('onboarding.next')}
              </Button>
            )}
            {last && (
              <Button type="button" onClick={finish}>
                {t('onboarding.done')}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
