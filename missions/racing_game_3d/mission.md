---
topic: "Juego web de carreras 3D Triple-A con Three.js + Cannon-ES — outputs/code/racing/"
paper_target: "demo público / portfolio / potencial publicación SIGGRAPH/CHI"
sections_needed:
  - graphics_pipeline
  - physics_engine
  - ai_opponents
  - audio_system
  - ui_ux
max_perplexity_calls: 2
code_needed: true
model: "best"
language: "es-ES"
output_dir: "outputs/code/racing"
enable_notion: true
enable_quality_check: true
enable_cursor_cli: true
save_perplexity_to_library: true

# ── ARQUITECTURA AAA ───────────────────────────────────────────────
architecture:
  renderer: "Three.js r169 + WebGPU (fallback WebGL2)"
  physics: "Cannon-ES 0.20 (WASM build)"
  audio: "Howler.js 2.2 + Web Audio API (positional 3D audio)"
  ui: "Vanilla TS + CSS custom properties (no framework = máx rendimiento)"
  bundler: "Vite 5 + Rollup (tree-shaking agresivo)"
  assets: "GLTF 2.0 + KTX2 (compresión GPU-native Basis Universal)"

# ── FEATURES GRÁFICAS ─────────────────────────────────────────────
graphics:
  post_processing:
    - "Bloom HDR (UnrealBloomPass)"
    - "Motion Blur (velocidad del vehículo)"
    - "Depth of Field (bokeh adaptativo al speed)"
    - "FXAA + TAA (anti-aliasing temporal)"
    - "Screen Space Reflections (pista mojada)"
    - "Lens Flare (sol dinámico)"
  lighting:
    - "IBL (Image Based Lighting) + HDRI sky"
    - "Sombras PCF Soft (cascaded shadow maps)"
    - "Luces de freno y faros volumétricos"
    - "Time of day dinámico (día → atardecer → noche)"
  environment:
    - "Skybox HDRI procedural"
    - "Niebla volumétrica en curvas"
    - "Partículas: chispas, polvo, lluvia, smoke del motor"
    - "Terreno con displacement map + tessellation"
    - "Multiples circuitos (3): Ciudad, Desierto, Montaña nevada"

# ── FÍSICA & VEHÍCULOS ────────────────────────────────────────────
physics:
  vehicle_model: "Raycast vehicle (Cannon-ES) — 4 ruedas independientes"
  features:
    - "Suspensión con parámetros ajustables por vehículo"
    - "Fuerza de frenado diferencial (ABS simulado)"
    - "Drift con friction slip realista"
    - "Colisiones mesh-to-mesh para obstáculos"
    - "Nitro boost con cooldown y partículas"
    - "Daño visual acumulativo (deformación mesh)"
  vehicles: 3  # Muscle car, Fórmula, Buggy off-road

# ── IA OPONENTES ──────────────────────────────────────────────────
ai:
  system: "Racing Line AI con Waypoints + PID controller"
  difficulty_levels: ["Rookie", "Pro", "Elite"]
  behaviors:
    - "Overtaking dinámico (cambio de línea)"
    - "Rubber-band inteligente (no tramposo, basado en errores)"
    - "Respuesta a colisiones del jugador"
  opponents: 5  # hasta 5 IA simultáneos

# ── AUDIO ─────────────────────────────────────────────────────────
audio:
  engine:
    - "Motor dinámico con pitch = f(RPM) usando OscillatorNode"
    - "Transición idle → acceleration → redline"
  sfx:
    - "Chirp de neumáticos en curvas"
    - "Impacto metálico en colisiones"
    - "Viento espacializado 3D"
    - "Cuenta atrás (3, 2, 1, GO!)"
  music:
    - "Soundtrack procedural adaptativo (BPM sube con velocidad)"
    - "3 temas por circuito"

# ── HUD & UI ──────────────────────────────────────────────────────
ui:
  hud:
    - "Velocímetro analógico animado (SVG)"
    - "RPM bar con zona de redline"
    - "Mapa del circuito en miniatura con posición live"
    - "Posición en carrera (1ro / 6to)"
    - "Lap counter + mejor vuelta"
    - "Nitro gauge"
  menus:
    - "Main menu con preview del circuito en background"
    - "Selector de vehículo con stats visuales"
    - "Opciones gráficas (Low / Medium / High / Ultra)"
    - "Pantalla de resultados con replay highlight"
  accessibility:
    - "Colorblind mode"
    - "Subtítulos en anuncios del locutor"

# ── ESTRUCTURA DE ARCHIVOS ────────────────────────────────────────
file_structure:
  outputs/code/racing/:
    - index.html           # entry point
    - src/:
        - main.ts          # bootstrap + game loop
        - renderer/        # Three.js setup, postFX, materials
        - physics/         # Cannon-ES wrapper, vehicle model
        - ai/              # Waypoint system, AI controller
        - audio/           # Howler + Web Audio engine sounds
        - ui/              # HUD components, menus
        - entities/        # Car, Track, Environment classes
        - utils/           # Math helpers, asset loader, debug
    - assets/:
        - models/          # GLTF cars + track segments
        - textures/        # KTX2 (albedo, normal, roughness, AO)
        - hdri/            # Environment maps
        - audio/           # SFX + music (OGG/OPUS)
    - vite.config.ts
    - tsconfig.json

# ── MÉTRICAS DE CALIDAD AAA ───────────────────────────────────────
quality_targets:
  performance:
    - "60 FPS estable en hardware mid-range (GTX 1060 / RX 580)"
    - "30 FPS en hardware integrado (Intel Iris Xe)"
    - "Bundle size < 2MB (sin assets)"
    - "Tiempo de carga inicial < 3s en red 4G"
  code:
    - "TypeScript strict mode — 0 errores"
    - "ESLint + Prettier pre-commit"
    - "Cobertura lógica de física > 70% (Vitest)"
  ux:
    - "Responsive: desktop 1080p/1440p + tablet landscape"
    - "Gamepad API (Xbox/DualSense) + teclado + touch"

# ── LOOP DE ITERACIÓN (Cursor) ─────────────────────────────────────
cursor_loop:
  phases:
    - id: P1
      name: "Foundation"
      tasks:
        - "Vite + TS + Three.js + Cannon-ES scaffolding"
        - "Pista básica (spline → mesh) + vehículo físico"
        - "Cámara chase con suavizado"
      exit_criteria: "Coche se mueve con física real, sin caerse"

    - id: P2
      name: "Core Gameplay"
      tasks:
        - "AI oponentes (3 waypoint-based)"
        - "Sistema de vueltas + posición en carrera"
        - "Nitro + daño visual básico"
        - "HUD mínimo (velocidad, posición, lap)"
      exit_criteria: "Carrera completa jugable de 3 vueltas"

    - id: P3
      name: "Polish Visual"
      tasks:
        - "Post-processing pipeline completo"
        - "Partículas: polvo, chispas, humo"
        - "Time of day + sombras suaves"
        - "3 circuitos con temática única"
      exit_criteria: "Capturas de pantalla parecen juego comercial"

    - id: P4
      name: "Audio & UI"
      tasks:
        - "Motor dinámico con Web Audio API"
        - "SFX posicional 3D"
        - "Menú principal + selector vehículo"
        - "Pantalla de resultados + replay parcial"
      exit_criteria: "Experiencia completa de inicio a fin"

    - id: P5
      name: "Optimization & Ship"
      tasks:
        - "LOD system (Level of Detail para assets lejanos)"
        - "Frustum culling agresivo"
        - "Web Worker para física (off main thread)"
        - "Progressive asset loading (KTX2 + GLTF lazy)"
        - "Deploy en GitHub Pages / Vercel"
      exit_criteria: "60 FPS en GTX 1060, bundle < 2MB, lighthouse score > 90"

  rules:
    - "Cada fase tiene su rama Git: feat/P1-foundation, etc."
    - "Commit por task completada, no por fase"
    - "Si un task bloquea > 2h → documentar blocker en BLOCKERS.md"
    - "No avanzar de fase sin cumplir exit_criteria"

# ── PROMPTS CURSOR SUGERIDOS ──────────────────────────────────────
cursor_prompts:
  P1_start: |
    Crea el scaffolding completo para un juego de carreras AAA en
    outputs/code/racing/ usando Vite 5 + TypeScript strict + Three.js r169
    + Cannon-ES. Implementa: pista circular como spline Catmull-Rom → mesh
    con normales correctas, vehículo Raycast con 4 ruedas y suspensión,
    cámara chase con SmoothDamp, y loop de física a 60Hz desacoplado del
    render. El vehículo debe poder driftar.

  P2_ai: |
    Añade sistema de AI racing para 5 oponentes usando waypoints extraídos
    de la curva de la pista. Cada AI usa PID controller para steering y
    throttle. Implementa: overtaking (lane shift al detectar oponente
    adelante), rubber-band suave (±5% velocidad según posición), y
    sistema de colisiones IA-IA sin tunneling.

  P3_postfx: |
    Implementa pipeline completo de post-processing con EffectComposer:
    UnrealBloomPass (threshold 0.8, strength 1.5), MotionBlurPass basado
    en velocidad del vehículo (max 8px), BokehPass adaptativo (foco en
    coche del jugador), FXAA final pass. Añadir sistema de partículas
    GPU-instanced para polvo (tierra) y chispas (metal). Todo debe
    mantenerse a 60fps en GTX 1060.
---