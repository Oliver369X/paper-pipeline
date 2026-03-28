import { create } from 'zustand'

interface AppState {
  pipelineRunning: boolean
  setPipelineRunning: (v: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  pipelineRunning: false,
  setPipelineRunning: (v) => set({ pipelineRunning: v }),
}))
