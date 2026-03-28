import { useTranslation } from 'react-i18next'

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation()
  const value = i18n.language.startsWith('en') ? 'en' : 'es'

  return (
    <div className="fixed right-4 top-4 z-[199]">
      <label className="sr-only" htmlFor="app-language">
        {t('language.label')}
      </label>
      <select
        id="app-language"
        className="rounded-md border border-zinc-600 bg-zinc-900 px-2 py-1.5 text-xs text-zinc-200 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950"
        value={value}
        onChange={(e) => void i18n.changeLanguage(e.target.value)}
      >
        <option value="es">{t('language.es')}</option>
        <option value="en">{t('language.en')}</option>
      </select>
    </div>
  )
}
