/**
 * HTTP helpers for the FastAPI server.
 *
 * En producción (p. ej. SPA en Vercel), definí `VITE_API_BASE_URL` al host del API (https://…).
 * En desarrollo, vacío + proxy de Vite (`/api` → 127.0.0.1:8000).
 *
 * PATCH: callers send a JSON object whose keys match `MissionPatch` (only set fields are
 * sent; the backend uses `exclude_unset=True`). The mission editor currently sends the full
 * flat body from the form so every controlled field is persisted.
 */
export const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

/** URL absoluta para fetch / EventSource (path debe empezar con `/`). */
export function apiUrl(path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`
  return API_BASE ? `${API_BASE}${p}` : p
}

async function handle<T>(r: Response): Promise<T> {
  if (!r.ok) {
    const t = await r.text()
    throw new Error(t || `${r.status}`)
  }
  if (r.status === 204) return undefined as T
  return r.json() as Promise<T>
}

export async function apiGet<T>(path: string): Promise<T> {
  return handle<T>(await fetch(apiUrl(path)))
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return handle<T>(
    await fetch(apiUrl(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  )
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  return handle<T>(
    await fetch(apiUrl(path), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  )
}

export async function apiPut<T>(path: string, body: unknown): Promise<T> {
  return handle<T>(
    await fetch(apiUrl(path), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  )
}

export async function apiDelete<T>(path: string): Promise<T> {
  return handle<T>(
    await fetch(apiUrl(path), {
      method: 'DELETE',
    }),
  )
}
