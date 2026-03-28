/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** URL absoluta del backend FastAPI (sin slash final). Vacío = mismo origen (proxy en dev). */
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
