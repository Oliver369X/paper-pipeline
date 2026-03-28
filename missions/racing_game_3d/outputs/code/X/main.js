import * as THREE from "three";
import {
  CAR,
  CAR_MESH,
  FINISH_U,
  GAME,
  HUD,
  LIGHTING,
  RENDERER,
  SCENE,
  VIEW,
} from "./config.js";
import {
  createInitialMotion,
  updateMotion,
  updateCamera,
} from "./motion.js";
import { setupTrackAndEnvironment } from "./track.js";
import {
  formatRaceTime,
  crossedFinishForward,
} from "./timing.js";
import {
  createDrivingKeyState,
  installDrivingKeyboardListeners,
  resetDrivingKeys,
} from "./driving-input.js";
import { showGameError } from "./error-overlay.js";

/** Intervalo mínimo entre actualizaciones de `aria-label` en el HUD (ms). */
const HUD_ARIA_INTERVAL_MS = 1000;

/**
 * Evita recalcular matrices locales en cada frame para hierba, asfalto, meta, etc.
 * (el coche y la cámara siguen con `matrixAutoUpdate` por defecto).
 * @param {THREE.Scene} scene
 */
function freezeStaticSceneRoots(scene) {
  const roots = scene.userData.staticSceneRoots;
  if (!roots) return;
  for (const root of roots) {
    root.traverse((child) => {
      if (child.isMesh || child.isLine) {
        child.matrixAutoUpdate = false;
        child.updateMatrix();
      }
    });
  }
}

/**
 * Si el coche cruza la línea de meta hacia delante con velocidad suficiente, fija el tiempo final y el HUD.
 * @param {{ finished: boolean, finishMs: number, t0: number }} race
 * @param {{ trackU: number, speed: number }} motion
 * @param {number} prevU
 * @param {number} newU
 * @param {HTMLElement | null} hudFinishEl
 * @param {number} now
 */
function recordFinishIfCrossed(race, motion, prevU, newU, hudFinishEl, now) {
  if (race.finished || motion.speed <= GAME.minSpeedForFinish) return;
  if (!crossedFinishForward(prevU, newU, FINISH_U)) return;
  race.finished = true;
  race.finishMs = now - race.t0;
  if (hudFinishEl) {
    hudFinishEl.hidden = false;
    hudFinishEl.textContent = `¡Meta! Tiempo: ${formatRaceTime(race.finishMs)}`;
  }
}

/**
 * Cronómetro y velocidad en pantalla; `aria-label` a baja frecuencia para lectores de pantalla.
 * @returns {number} último instante en que se actualizó `aria-label`
 */
function updateHudTelemetry(
  race,
  motion,
  now,
  hudTimeEl,
  hudSpeedEl,
  lastHudAriaMs
) {
  const displayMs = race.finished ? race.finishMs : now - race.t0;
  if (hudTimeEl) hudTimeEl.textContent = formatRaceTime(displayMs);
  const spd = Math.abs(motion.speed);
  const pct = Math.min(
    HUD.speedPercentMax,
    Math.round((spd / CAR.maxSpeed) * HUD.speedPercentMax)
  );
  if (hudSpeedEl) {
    hudSpeedEl.textContent = `Velocidad: ${pct} % (${spd.toFixed(1)} u/s)`;
  }

  let next = lastHudAriaMs;
  if (now - lastHudAriaMs < HUD_ARIA_INTERVAL_MS) return next;
  next = now;
  if (hudTimeEl) {
    hudTimeEl.setAttribute(
      "aria-label",
      `Tiempo de carrera: ${formatRaceTime(displayMs)}`
    );
  }
  if (hudSpeedEl) {
    hudSpeedEl.setAttribute(
      "aria-label",
      `Velocidad ${pct} por ciento, ${spd.toFixed(1)} unidades por segundo`
    );
  }
  return next;
}

/** Punto de entrada: arranque WebGL, construcción del circuito, bucle de juego y HUD. */

function main() {
  const container = document.getElementById("app");
  if (!container) {
    showGameError(
      "No se encontró el contenedor del juego (#app). Comprueba el HTML."
    );
    return;
  }

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance",
      stencil: RENDERER.stencil,
    });
  } catch (err) {
    console.error(err);
    showGameError(
      "No se pudo crear el renderizador WebGL. Prueba otro navegador o actualiza los controladores gráficos."
    );
    return;
  }

  if (!renderer.getContext()) {
    showGameError(
      "WebGL no está disponible. Actívalo en la configuración del navegador o prueba otro dispositivo."
    );
    return;
  }

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(SCENE.background);
  scene.fog = new THREE.Fog(SCENE.background, SCENE.fogNear, SCENE.fogFar);

  const w0 = Math.max(1, window.innerWidth);
  const h0 = Math.max(1, window.innerHeight);
  const camera = new THREE.PerspectiveCamera(
    VIEW.fov,
    w0 / h0,
    VIEW.near,
    VIEW.far
  );
  camera.position.set(VIEW.initialX, VIEW.initialY, VIEW.initialZ);

  renderer.setPixelRatio(
    Math.min(window.devicePixelRatio, VIEW.maxPixelRatio)
  );
  renderer.setSize(w0, h0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  /** Detiene el bucle y evita seguir renderizando tras pérdida irrecuperable del contexto WebGL. */
  let gameStopped = false;
  renderer.domElement.addEventListener(
    "webglcontextlost",
    (event) => {
      event.preventDefault();
      gameStopped = true;
      console.error("WebGL context lost");
      showGameError(
        "Se perdió el contexto gráfico (WebGL). Cierra otras pestañas pesadas o recarga la página."
      );
    },
    false
  );
  renderer.domElement.addEventListener(
    "webglcontextrestored",
    () => {
      window.location.reload();
    },
    false
  );

  const ambient = new THREE.AmbientLight(
    LIGHTING.ambientColor,
    LIGHTING.ambientIntensity
  );
  scene.add(ambient);
  const sun = new THREE.DirectionalLight(
    LIGHTING.sunColor,
    LIGHTING.sunIntensity
  );
  sun.position.set(LIGHTING.sunX, LIGHTING.sunY, LIGHTING.sunZ);
  sun.castShadow = false;
  scene.add(sun);

  let trackCenterline;
  try {
    trackCenterline = setupTrackAndEnvironment(scene);
  } catch (err) {
    console.error(err);
    showGameError(
      "Error al crear el circuito. Recarga la página o revisa la consola para más detalles."
    );
    renderer.dispose();
    return;
  }

  const carMesh = new THREE.Mesh(
    new THREE.BoxGeometry(CAR_MESH.width, CAR_MESH.height, CAR_MESH.depth),
    new THREE.MeshStandardMaterial({
      color: CAR_MESH.color,
      roughness: CAR_MESH.roughness,
      metalness: CAR_MESH.metalness,
    })
  );
  carMesh.position.y = CAR_MESH.floorY;
  scene.add(carMesh);

  freezeStaticSceneRoots(scene);
  try {
    renderer.compile(scene, camera);
  } catch {
    /* precompilación opcional; fallos en drivers raros no deben bloquear el juego */
  }

  const motion = createInitialMotion();

  const keys = createDrivingKeyState();

  window.addEventListener("click", () => {
    container.focus();
    acknowledgeFocus();
  });

  container.addEventListener("focusin", () => {
    acknowledgeFocus();
  });

  const hudTimeEl = document.getElementById("hud-time");
  const hudSpeedEl = document.getElementById("hud-speed");
  const hudFinishEl = document.getElementById("hud-finish");
  const focusBannerEl = document.getElementById("focus-banner");
  const readyToastEl = document.getElementById("ready-toast");

  if (hudTimeEl) {
    hudTimeEl.setAttribute("aria-label", "Tiempo de carrera: 0:00.00");
  }
  if (hudSpeedEl) {
    hudSpeedEl.setAttribute(
      "aria-label",
      "Velocidad 0 por ciento, 0.0 unidades por segundo"
    );
  }

  /** @type {{ t0: number, finished: boolean, finishMs: number }} */
  const race = {
    t0: performance.now(),
    finished: false,
    finishMs: 0,
  };

  let tabHiddenAt = 0;
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      tabHiddenAt = performance.now();
    } else if (tabHiddenAt > 0) {
      race.t0 += performance.now() - tabHiddenAt;
      tabHiddenAt = 0;
    }
  });

  let focusAcked = false;
  function acknowledgeFocus() {
    if (focusAcked) return;
    focusAcked = true;
    focusBannerEl?.classList.add("hidden");
    if (readyToastEl) {
      readyToastEl.hidden = false;
      readyToastEl.classList.add("show");
      setTimeout(() => {
        readyToastEl.classList.remove("show");
        readyToastEl.hidden = true;
      }, GAME.readyToastDurationMs);
    }
  }

  function resetRace() {
    race.t0 = performance.now();
    race.finished = false;
    race.finishMs = 0;
    if (hudFinishEl) {
      hudFinishEl.hidden = true;
      hudFinishEl.textContent = "";
    }
    Object.assign(motion, createInitialMotion());
  }

  installDrivingKeyboardListeners(window, container, keys, { onReset: resetRace });

  const clock = new THREE.Clock();

  function onResize() {
    try {
      const w = Math.max(1, window.innerWidth);
      const h = Math.max(1, window.innerHeight);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    } catch (err) {
      console.error("Error al redimensionar la vista:", err);
    }
  }
  window.addEventListener("resize", onResize);
  window.addEventListener("orientationchange", () => {
    requestAnimationFrame(onResize);
  });

  let renderErrorLogged = false;
  let lastHudAriaMs = 0;

  function tick() {
    if (gameStopped) return;
    requestAnimationFrame(tick);
    if (document.visibilityState === "hidden") {
      clock.getDelta();
      return;
    }
    const dt = Math.min(clock.getDelta(), GAME.maxDeltaSeconds);
    const prevU = motion.trackU;
    try {
      updateMotion(dt, trackCenterline, motion, keys, carMesh);
    } catch (err) {
      if (!renderErrorLogged) {
        console.error("Error en física del vehículo:", err);
        renderErrorLogged = true;
      }
      Object.assign(motion, createInitialMotion());
      resetDrivingKeys(keys);
      try {
        updateMotion(
          GAME.recoveryDtSeconds,
          trackCenterline,
          motion,
          keys,
          carMesh
        );
      } catch {
        /* si sigue fallando, el siguiente tick lo reintenta */
      }
    }
    const newU = motion.trackU;
    const now = performance.now();

    recordFinishIfCrossed(race, motion, prevU, newU, hudFinishEl, now);
    lastHudAriaMs = updateHudTelemetry(
      race,
      motion,
      now,
      hudTimeEl,
      hudSpeedEl,
      lastHudAriaMs
    );

    try {
      updateCamera(dt, carMesh, camera);
      renderer.render(scene, camera);
    } catch (err) {
      if (!renderErrorLogged) {
        console.error("Error al renderizar:", err);
        renderErrorLogged = true;
      }
    }
  }

  tick();
}

main();
