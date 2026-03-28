/**
 * Parámetros globales de pista, vehículo, escena y gameplay.
 * Un solo lugar para tunear sin repartir números mágicos por los módulos.
 */

/** Corona oval escalada en X; centerlineSegments define suavidad de la curva Catmull-Rom. */
export const TRACK = {
  innerRadius: 8,
  outerRadius: 11,
  ovalScaleX: 1.55,
  borderWidth: 0.22,
  centerlineSegments: 128,
  /** Plano de hierba (tamaño del Mesh `PlaneGeometry`). */
  grassPlaneSize: 90,
  /** Segmentos del anillo de asfalto y bordes. */
  ringSegments: 72,
  /** Puntos para la línea visual sobre la centerline (menos vértices = menos trabajo GPU). */
  centerlineLinePoints: 256,
  /** Grosor del borde interior en geometría (anillo interior). */
  innerBorderOuterPad: 0.02,
  /** Hueco entre borde exterior y asfalto. */
  outerBorderInnerPad: 0.02,
};

/** Niebla y color de fondo (mismo tono para continuidad visual). */
export const SCENE = {
  background: 0x1a1a24,
  fogNear: 28,
  fogFar: 95,
};

/** Cámara de juego (vista inicial antes del chase). */
export const VIEW = {
  fov: 50,
  near: 0.1,
  far: 1000,
  initialX: 0,
  initialY: 18,
  initialZ: 26,
  /** Tope de `devicePixelRatio` para equilibrio nitidez / rendimiento. */
  maxPixelRatio: 2,
};

/** Opciones del WebGLRenderer (MVP no usa stencil). */
export const RENDERER = {
  stencil: false,
};

export const LIGHTING = {
  ambientColor: 0xffffff,
  ambientIntensity: 0.55,
  sunColor: 0xffffff,
  sunIntensity: 0.95,
  sunX: 6,
  sunY: 18,
  sunZ: 10,
};

/** Mesh del vehículo (caja) hasta que haya GLTF. */
export const CAR_MESH = {
  width: 1.2,
  height: 0.6,
  depth: 2.4,
  color: 0x3d7cff,
  roughness: 0.45,
  metalness: 0.25,
  floorY: 0.35,
};

/** Cámara chase detrás del coche. */
export const CHASE = {
  smoothness: 6,
  distance: 10,
  heightOffset: 5.2,
};

/** Bucle de simulación y HUD. */
export const GAME = {
  /** Paso máximo por frame (evita tunel tras lag). */
  maxDeltaSeconds: 0.05,
  /** Velocidad mínima (|speed|) para aceptar cruce de meta. */
  minSpeedForFinish: 0.4,
  readyToastDurationMs: 1400,
  /** Paso de tiempo mínimo al recuperar física tras error en `main` (evita división por cero). */
  recoveryDtSeconds: 1e-6,
};

export const CAR = {
  halfWidth: 0.55,
  trackMargin: 0.08,
  maxSpeed: 22,
  accel: 28,
  brake: 35,
  reverseMax: 8,
  /** Por debajo de esto se usa aceleración de marcha atrás en lugar de freno. */
  brakeToReverseSpeed: 0.5,
  /** Factor sobre `accel` al dar marcha atrás desde parado. */
  reverseAccelFactor: 0.5,
  lateralAccel: 42,
  lateralDrag: 3.2,
  drag: 2.15,
  /** Amortiguación de velocidad lateral al rozar bordes (0–1). */
  borderLateralDamping: 0.28,
};

/** Estado inicial sobre la pista (u en curva cerrada). */
export const MOTION = {
  startTrackU: 0.42,
};

/** Textura a cuadros de la meta (canvas). */
export const FINISH_VISUAL = {
  canvasSize: 128,
  cells: 8,
  bannerHeight: 1.35,
  bannerWidthScale: 1.02,
  bannerY: 0.72,
  postRadiusTop: 0.08,
  postRadiusBottom: 0.1,
  postHeight: 1.1,
  postSegments: 8,
  postY: 0.55,
  postHalfSpread: 0.52,
  /** Colores del lienzo a cuadros (canvas 2D). */
  checkeredDark: "#1a1a22",
  checkeredLight: "#f2f0ea",
  textureRepeatU: 2,
  textureRepeatV: 1,
  bannerRoughness: 0.65,
  bannerMetalness: 0.05,
  postRoughness: 0.7,
  postMetalness: 0.15,
};

/**
 * Progreso longitudinal u ∈ [0,1) de la línea de meta en la curva cerrada.
 */
export const FINISH_U = 0.25;

/**
 * En `crossedFinishForward`, un salto u que supere este delta se considera vuelta completa
 * (no cuenta como cruce “hacia delante” por la línea de meta).
 */
export const FINISH_CROSS_MAX_DELTA_U = 0.5;

/**
 * Tolerancias numéricas compartidas (derivadas en curva, raíces cuadráticas, clamp en pista).
 * Centralizadas para mantener el mismo criterio en `motion`, `track` y `curve-utils`.
 */
export const NUM_EPS = {
  curveDu: 1e-4,
  arcLengthDivisor: 1e-6,
  tangentMinSq: 1e-8,
  quadraticLinearA: 1e-9,
  trackBorderRadius: 1e-5,
};

/** Alturas Y de meshes estáticos (orden visual: hierba < asfalto ≈ bordes < línea central). */
export const TRACK_LEVELS = {
  grass: -0.02,
  asphalt: 0.001,
  border: 0.002,
  centerline: 0.03,
};

/** Colores y PBR básico de materiales de entorno (hex Three.js donde aplica). */
export const TRACK_PALETTE = {
  grass: 0x1c4d32,
  grassRoughness: 0.92,
  grassMetalness: 0.05,
  asphalt: 0x2a2a32,
  asphaltRoughness: 0.88,
  asphaltMetalness: 0.08,
  border: 0xd8d4c8,
  borderRoughness: 0.75,
  borderMetalness: 0.12,
  centerLine: 0xf5f0e6,
  centerLineOpacity: 0.55,
  finishBannerFallback: 0xe8e4dc,
  finishPost: 0xc8c4b8,
};

/** HUD: límites de presentación (no afectan simulación). */
export const HUD = {
  speedPercentMax: 100,
};
