/**
 * Cronómetro de carrera y detección de cruce de meta (curva cerrada u ∈ [0,1)).
 */

import { FINISH_CROSS_MAX_DELTA_U } from "./config.js";

const MS_PER_MINUTE = 60_000;
const MS_PER_SECOND = 1000;
const CENTISECONDS_PER_SECOND = 100;

/**
 * @param {number} ms
 * @returns {string}
 */
export function formatRaceTime(ms) {
  if (!Number.isFinite(ms)) return "—:--.--";
  const t = Math.max(0, ms);
  const m = Math.floor(t / MS_PER_MINUTE);
  const s = (t % MS_PER_MINUTE) / MS_PER_SECOND;
  const si = Math.floor(s);
  const cs = Math.floor((s - si) * CENTISECONDS_PER_SECOND);
  return `${m}:${String(si).padStart(2, "0")}.${String(cs).padStart(2, "0")}`;
}

/**
 * Cruce hacia delante de la línea u = finishU en una curva cerrada (u ∈ [0,1)).
 * Ignora el wrap inverso (marcha atrás) cuando prev < new pero el salto abarca > media vuelta.
 * @param {number} prevU
 * @param {number} newU
 * @param {number} finishU
 */
export function crossedFinishForward(prevU, newU, finishU) {
  if (
    !Number.isFinite(prevU) ||
    !Number.isFinite(newU) ||
    !Number.isFinite(finishU)
  ) {
    return false;
  }
  if (prevU < newU) {
    if (newU - prevU > FINISH_CROSS_MAX_DELTA_U) return false;
    return prevU < finishU && newU >= finishU;
  }
  if (prevU > newU) {
    return prevU < finishU || newU >= finishU;
  }
  return false;
}
