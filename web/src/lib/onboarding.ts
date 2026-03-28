/** Clave de localStorage; subir versión si cambia el contenido del tour. */
export const ONBOARDING_STORAGE_KEY = 'paper-web-onboarding-dismissed-v2'

export function isOnboardingDismissed(): boolean {
  try {
    return localStorage.getItem(ONBOARDING_STORAGE_KEY) === '1'
  } catch {
    return true
  }
}

export function dismissOnboarding(): void {
  try {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, '1')
  } catch {
    /* private mode */
  }
}
