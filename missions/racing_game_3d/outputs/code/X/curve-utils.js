import * as THREE from "three";
import { NUM_EPS } from "./config.js";

/**
 * Tangente de la curva proyectada al plano XZ y normalizada (eje de avance en pista).
 * @param {THREE.Curve<THREE.Vector3>} curve
 * @param {number} u
 * @param {THREE.Vector3} out
 */
export function horizontalTangentAt(curve, u, out) {
  curve.getTangentAt(u, out);
  out.y = 0;
  if (out.lengthSq() < NUM_EPS.tangentMinSq) out.set(0, 0, 1);
  else out.normalize();
}
