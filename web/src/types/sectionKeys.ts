export interface SectionMeta {
  title: string
  summary: string
  output: string
}

export interface SectionKeysResponse {
  keys: string[]
  meta: Record<string, SectionMeta>
  outputs_help: string
}
