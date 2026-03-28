import * as THREE from "three";
import { CAR, CAR_MESH, CHASE, MOTION, NUM_EPS } from "./config.js";
import { horizontalTangentAt } from "./curve-utils.js";
import { clampLateralToTrack } from "./track.js";

const CAR_FORWARD = new THREE.Vector3(0, 0, 1);

const _tan = new THREE.Vector3();
const _right = new THREE.Vector3();
const _base = new THREE.Vector3();
const _pos = new THREE.Vector3();
const _deltaP0 = new THREE.Vector3();
const _deltaP1 = new THREE.Vector3();
const _camTarget = new THREE.Vector3();
const _camDesired = new THREE.Vector3();
const _back = new THREE.Vector3();
const _facing = new THREE.Vector3();
const _camUpOffset = new THREE.Vector3(0, CHASE.heightOffset, 0);

/**
 * @param {THREE.CatmullRomCurve3} curve
 * @param {number} u
 * @param {number} speed
 * @param {number} dt
 */
export function deltaUFromSpeed(curve, u, speed, dt) {
  const eps = NUM_EPS.curveDu;
  const u1 = u + eps > 1 ? u + eps - 1 : u + eps;
  curve.getPointAt(u, _deltaP0);
  curve.getPointAt(u1, _deltaP1);
  const dsDu = Math.max(
    NUM_EPS.arcLengthDivisor,
    _deltaP0.distanceTo(_deltaP1) / eps
  );
  const du = (speed * dt) / dsDu;
  return Number.isFinite(du) ? du : 0;
}

/**
 * @returns {{ trackU: number, lateral: number, speed: number, lateralVel: number }}
 */
export function createInitialMotion() {
  return {
    trackU: MOTION.startTrackU,
    lateral: 0,
    speed: 0,
    lateralVel: 0,
  };
}

/**
 * @param {object} keys
 * @param {boolean} keys.up
 * @param {boolean} keys.down
 * @param {boolean} keys.left
 * @param {boolean} keys.right
 */
export function updateMotion(dt, curve, motion, keys, carMesh) {
  let throttle = 0;
  if (keys.up) throttle += 1;
  if (keys.down) throttle -= 1;

  if (throttle > 0) {
    motion.speed += CAR.accel * throttle * dt;
  } else if (throttle < 0) {
    if (motion.speed > CAR.brakeToReverseSpeed) {
      motion.speed -= CAR.brake * Math.abs(throttle) * dt;
    } else {
      motion.speed -=
        CAR.accel * CAR.reverseAccelFactor * Math.abs(throttle) * dt;
    }
  } else {
    motion.speed *= Math.exp(-CAR.drag * dt);
  }

  motion.speed = THREE.MathUtils.clamp(
    motion.speed,
    -CAR.reverseMax,
    CAR.maxSpeed
  );

  let steer = 0;
  if (keys.left) steer -= 1;
  if (keys.right) steer += 1;
  motion.lateralVel += steer * CAR.lateralAccel * dt;
  motion.lateralVel *= Math.exp(-CAR.lateralDrag * dt);
  motion.lateral += motion.lateralVel * dt;

  const du = deltaUFromSpeed(curve, motion.trackU, motion.speed, dt);
  motion.trackU += du;
  // Parámetro de curva cerrada: mantener u en [0, 1).
  motion.trackU = ((motion.trackU % 1) + 1) % 1;
  if (!Number.isFinite(motion.trackU)) motion.trackU = 0;
  if (!Number.isFinite(motion.lateral)) motion.lateral = 0;
  if (!Number.isFinite(motion.lateralVel)) motion.lateralVel = 0;
  if (!Number.isFinite(motion.speed)) motion.speed = 0;

  curve.getPointAt(motion.trackU, _base);
  horizontalTangentAt(curve, motion.trackU, _tan);
  _right.set(-_tan.z, 0, _tan.x);

  const clamped = clampLateralToTrack(motion.lateral, _base, _right);
  motion.lateral = clamped.lateral;
  if (clamped.hitBorder) {
    motion.lateralVel *= CAR.borderLateralDamping;
  }

  _pos.copy(_base).addScaledVector(_right, motion.lateral);
  _pos.y = CAR_MESH.floorY;
  carMesh.position.copy(_pos);

  _facing.copy(_tan);
  if (motion.speed < 0) _facing.negate();
  carMesh.quaternion.setFromUnitVectors(CAR_FORWARD, _facing);
}

/**
 * @param {THREE.PerspectiveCamera} camera
 */
export function updateCamera(dt, carMesh, camera) {
  const smooth = 1 - Math.exp(-CHASE.smoothness * dt);
  carMesh.getWorldPosition(_camTarget);
  _back.set(0, 0, -1).applyQuaternion(carMesh.quaternion);
  _camDesired
    .copy(_camTarget)
    .addScaledVector(_back, CHASE.distance)
    .add(_camUpOffset);
  camera.position.lerp(_camDesired, smooth);
  camera.lookAt(_camTarget);
}
