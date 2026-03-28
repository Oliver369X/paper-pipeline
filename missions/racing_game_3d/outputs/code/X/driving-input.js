/**
 * Estado de teclas para conducción (WASD / flechas) y reinicio (R).
 */

/**
 * @returns {{ up: boolean, down: boolean, left: boolean, right: boolean }}
 */
export function createDrivingKeyState() {
  return {
    up: false,
    down: false,
    left: false,
    right: false,
  };
}

/** @param {{ up: boolean, down: boolean, left: boolean, right: boolean }} keys */
export function resetDrivingKeys(keys) {
  keys.up = false;
  keys.down = false;
  keys.left = false;
  keys.right = false;
}

/**
 * @param {KeyboardEvent} e
 * @param {boolean} down
 * @param {{ up: boolean, down: boolean, left: boolean, right: boolean }} keys
 * @param {{ onReset: () => void }} handlers
 */
function applyDrivingKeyEvent(e, down, keys, { onReset }) {
  switch (e.code) {
    case "ArrowUp":
    case "KeyW":
      keys.up = down;
      e.preventDefault();
      break;
    case "ArrowDown":
    case "KeyS":
      keys.down = down;
      e.preventDefault();
      break;
    case "ArrowLeft":
    case "KeyA":
      keys.left = down;
      e.preventDefault();
      break;
    case "ArrowRight":
    case "KeyD":
      keys.right = down;
      e.preventDefault();
      break;
    case "KeyR":
      if (down) {
        if (e.repeat) break;
        onReset();
        e.preventDefault();
      }
      break;
    default:
      break;
  }
}

/**
 * @param {Window} win
 * @param {HTMLElement} container
 * @param {{ up: boolean, down: boolean, left: boolean, right: boolean }} keys
 * @param {{ onReset: () => void }} handlers
 * @returns {() => void} cleanup
 */
export function installDrivingKeyboardListeners(win, container, keys, handlers) {
  function gameHasKeyboardFocus() {
    return document.activeElement === container;
  }

  function keyFromEvent(e, down) {
    if (!gameHasKeyboardFocus()) return;
    applyDrivingKeyEvent(e, down, keys, handlers);
  }

  const onDown = (e) => keyFromEvent(e, true);
  const onUp = (e) => keyFromEvent(e, false);

  /** Evita teclas “pegadas” al cambiar de pestaña o perder foco del sistema. */
  function releaseAllDrivingKeys() {
    resetDrivingKeys(keys);
  }

  const onWindowBlur = () => releaseAllDrivingKeys();
  const onVisibilityChange = () => {
    if (document.hidden) releaseAllDrivingKeys();
  };

  win.addEventListener("keydown", onDown);
  win.addEventListener("keyup", onUp);
  win.addEventListener("blur", onWindowBlur);
  document.addEventListener("visibilitychange", onVisibilityChange);
  return () => {
    win.removeEventListener("keydown", onDown);
    win.removeEventListener("keyup", onUp);
    win.removeEventListener("blur", onWindowBlur);
    document.removeEventListener("visibilitychange", onVisibilityChange);
  };
}
