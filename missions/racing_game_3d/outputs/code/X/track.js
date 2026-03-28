import * as THREE from "three";
import {
  TRACK,
  CAR,
  FINISH_U,
  FINISH_VISUAL,
  NUM_EPS,
  TRACK_LEVELS,
  TRACK_PALETTE,
} from "./config.js";
import { horizontalTangentAt } from "./curve-utils.js";

/** Resultado reutilizable de `clampLateralToTrack` (evita `{ }` nuevo cada frame). */
const _clampOut = { lateral: 0, hitBorder: false };

/**
 * @param {number} A
 * @param {number} B
 * @param {number} C
 * @returns {number[]}
 */
function quadraticRoots(A, B, C) {
  const eps = NUM_EPS.quadraticLinearA;
  if (Math.abs(A) < eps) {
    if (Math.abs(B) < eps) return [];
    return [-C / B];
  }
  const disc = B * B - 4 * A * C;
  if (disc < 0) return [];
  const s = Math.sqrt(disc);
  return [(-B - s) / (2 * A), (-B + s) / (2 * A)];
}

/**
 * Corona oval: radio normalizado √((x/sx)² + z²) entre rInnerEff y rOuterEff.
 * @param {number} lateral
 * @param {THREE.Vector3} P
 * @param {THREE.Vector3} right
 * @returns {{ lateral: number, hitBorder: boolean }}
 */
export function clampLateralToTrack(lateral, P, right) {
  const sx = TRACK.ovalScaleX;
  const rInnerEff = TRACK.innerRadius + CAR.trackMargin;
  const rOuterEff = TRACK.outerRadius - CAR.trackMargin;
  const px = P.x;
  const pz = P.z;
  const rx = right.x;
  const rz = right.z;

  function metricAt(lambda) {
    const x = px + lambda * rx;
    const z = pz + lambda * rz;
    return Math.sqrt((x / sx) * (x / sx) + z * z);
  }

  function rootsForCircleRadius(r) {
    const r2 = r * r;
    const A = (rx / sx) * (rx / sx) + rz * rz;
    const B = 2 * ((px / sx) * (rx / sx) + pz * rz);
    const C = (px / sx) * (px / sx) + pz * pz - r2;
    return quadraticRoots(A, B, C);
  }

  function pickClosestRoot(roots, ref) {
    let best = ref;
    let bestD = Infinity;
    for (const t of roots) {
      if (!Number.isFinite(t)) continue;
      const d = Math.abs(t - ref);
      if (d < bestD) {
        bestD = d;
        best = t;
      }
    }
    return best;
  }

  let lambda = lateral;
  let hitBorder = false;

  const rp = metricAt(lambda);
  if (rp < rInnerEff - NUM_EPS.trackBorderRadius) {
    const roots = rootsForCircleRadius(rInnerEff);
    if (roots.length > 0) {
      lambda = pickClosestRoot(roots, lateral);
      hitBorder = true;
    }
  } else if (rp > rOuterEff + NUM_EPS.trackBorderRadius) {
    const roots = rootsForCircleRadius(rOuterEff);
    if (roots.length > 0) {
      lambda = pickClosestRoot(roots, lateral);
      hitBorder = true;
    }
  }

  _clampOut.lateral = lambda;
  _clampOut.hitBorder = hitBorder;
  return _clampOut;
}

function makeCheckeredTexture() {
  const c = document.createElement("canvas");
  const sz = FINISH_VISUAL.canvasSize;
  c.width = sz;
  c.height = sz;
  const ctx = c.getContext("2d");
  if (!ctx) return null;
  const n = FINISH_VISUAL.cells;
  const s = sz / n;
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      ctx.fillStyle =
        (x + y) % 2 === 0
          ? FINISH_VISUAL.checkeredDark
          : FINISH_VISUAL.checkeredLight;
      ctx.fillRect(x * s, y * s, s, s);
    }
  }
  try {
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(FINISH_VISUAL.textureRepeatU, FINISH_VISUAL.textureRepeatV);
    return tex;
  } catch {
    return null;
  }
}

const _finTan = new THREE.Vector3();
const _finRight = new THREE.Vector3();
const _finPos = new THREE.Vector3();

/**
 * @param {THREE.Scene} scene
 * @param {THREE.CatmullRomCurve3} curve
 * @param {number} u
 * @param {THREE.Object3D[]} staticRoots
 */
function addFinishLineBanner(scene, curve, u, staticRoots) {
  curve.getPointAt(u, _finPos);
  horizontalTangentAt(curve, u, _finTan);
  _finRight.set(-_finTan.z, 0, _finTan.x);
  const trackW =
    TRACK.outerRadius - TRACK.innerRadius - 2 * CAR.trackMargin;
  const tex = makeCheckeredTexture();
  const mat = new THREE.MeshStandardMaterial({
    ...(tex ? { map: tex } : { color: TRACK_PALETTE.finishBannerFallback }),
    roughness: FINISH_VISUAL.bannerRoughness,
    metalness: FINISH_VISUAL.bannerMetalness,
    side: THREE.DoubleSide,
  });
  const banner = new THREE.Mesh(
    new THREE.PlaneGeometry(
      trackW * FINISH_VISUAL.bannerWidthScale,
      FINISH_VISUAL.bannerHeight
    ),
    mat
  );
  banner.position.copy(_finPos);
  banner.position.y = FINISH_VISUAL.bannerY;
  const up = new THREE.Vector3(0, 1, 0);
  const m = new THREE.Matrix4().makeBasis(_finRight, up, _finTan);
  banner.quaternion.setFromRotationMatrix(m);
  scene.add(banner);
  staticRoots.push(banner);

  const postMat = new THREE.MeshStandardMaterial({
    color: TRACK_PALETTE.finishPost,
    roughness: FINISH_VISUAL.postRoughness,
    metalness: FINISH_VISUAL.postMetalness,
  });
  const postGeom = new THREE.CylinderGeometry(
    FINISH_VISUAL.postRadiusTop,
    FINISH_VISUAL.postRadiusBottom,
    FINISH_VISUAL.postHeight,
    FINISH_VISUAL.postSegments
  );
  const leftPost = new THREE.Mesh(postGeom, postMat);
  const rightPost = new THREE.Mesh(postGeom, postMat);
  const half = trackW * FINISH_VISUAL.postHalfSpread;
  leftPost.position.copy(_finPos).addScaledVector(_finRight, -half);
  rightPost.position.copy(_finPos).addScaledVector(_finRight, half);
  leftPost.position.y = FINISH_VISUAL.postY;
  rightPost.position.y = FINISH_VISUAL.postY;
  scene.add(leftPost, rightPost);
  staticRoots.push(leftPost, rightPost);
}

/**
 * Crea suelo, pista oval, bordes, línea central y meta; rellena `scene.userData`.
 * @param {THREE.Scene} scene
 * @returns {THREE.CatmullRomCurve3}
 */
export function setupTrackAndEnvironment(scene) {
  /** Objetos que no se animan; se congelan en `main` para evitar trabajo de matriz por frame. */
  const staticSceneRoots = [];

  const grass = new THREE.Mesh(
    new THREE.PlaneGeometry(TRACK.grassPlaneSize, TRACK.grassPlaneSize),
    new THREE.MeshStandardMaterial({
      color: TRACK_PALETTE.grass,
      roughness: TRACK_PALETTE.grassRoughness,
      metalness: TRACK_PALETTE.grassMetalness,
    })
  );
  grass.rotation.x = -Math.PI / 2;
  grass.position.y = TRACK_LEVELS.grass;
  scene.add(grass);
  staticSceneRoots.push(grass);

  const asphaltMat = new THREE.MeshStandardMaterial({
    color: TRACK_PALETTE.asphalt,
    roughness: TRACK_PALETTE.asphaltRoughness,
    metalness: TRACK_PALETTE.asphaltMetalness,
  });
  const trackMesh = new THREE.Mesh(
    new THREE.RingGeometry(
      TRACK.innerRadius,
      TRACK.outerRadius,
      TRACK.ringSegments
    ),
    asphaltMat
  );
  trackMesh.rotation.x = -Math.PI / 2;
  trackMesh.scale.set(TRACK.ovalScaleX, 1, 1);
  trackMesh.position.y = TRACK_LEVELS.asphalt;
  scene.add(trackMesh);
  staticSceneRoots.push(trackMesh);

  const borderMat = new THREE.MeshStandardMaterial({
    color: TRACK_PALETTE.border,
    roughness: TRACK_PALETTE.borderRoughness,
    metalness: TRACK_PALETTE.borderMetalness,
  });
  const innerBorder = new THREE.Mesh(
    new THREE.RingGeometry(
      TRACK.innerRadius - TRACK.borderWidth,
      TRACK.innerRadius + TRACK.innerBorderOuterPad,
      TRACK.ringSegments
    ),
    borderMat
  );
  innerBorder.rotation.x = -Math.PI / 2;
  innerBorder.scale.set(TRACK.ovalScaleX, 1, 1);
  innerBorder.position.y = TRACK_LEVELS.border;
  scene.add(innerBorder);
  staticSceneRoots.push(innerBorder);

  const outerBorder = new THREE.Mesh(
    new THREE.RingGeometry(
      TRACK.outerRadius - TRACK.outerBorderInnerPad,
      TRACK.outerRadius + TRACK.borderWidth,
      TRACK.ringSegments
    ),
    borderMat
  );
  outerBorder.rotation.x = -Math.PI / 2;
  outerBorder.scale.set(TRACK.ovalScaleX, 1, 1);
  outerBorder.position.y = TRACK_LEVELS.border;
  scene.add(outerBorder);
  staticSceneRoots.push(outerBorder);

  const rMid = (TRACK.innerRadius + TRACK.outerRadius) / 2;
  const a = rMid * TRACK.ovalScaleX;
  const b = rMid;
  const centerPoints = [];
  for (let i = 0; i <= TRACK.centerlineSegments; i++) {
    const t = (i / TRACK.centerlineSegments) * Math.PI * 2;
    centerPoints.push(
      new THREE.Vector3(
        a * Math.cos(t),
        TRACK_LEVELS.centerline,
        b * Math.sin(t)
      )
    );
  }
  const trackCenterline = new THREE.CatmullRomCurve3(centerPoints, true);
  scene.userData.trackCenterline = trackCenterline;
  scene.userData.track = {
    innerRadius: TRACK.innerRadius,
    outerRadius: TRACK.outerRadius,
    ovalScaleX: TRACK.ovalScaleX,
    rMid,
  };

  const lineGeom = new THREE.BufferGeometry().setFromPoints(
    trackCenterline.getPoints(TRACK.centerlineLinePoints)
  );
  const lineMat = new THREE.LineBasicMaterial({
    color: TRACK_PALETTE.centerLine,
    transparent: true,
    opacity: TRACK_PALETTE.centerLineOpacity,
  });
  const centerLine = new THREE.Line(lineGeom, lineMat);
  scene.add(centerLine);
  staticSceneRoots.push(centerLine);

  addFinishLineBanner(scene, trackCenterline, FINISH_U, staticSceneRoots);
  scene.userData.finishU = FINISH_U;
  scene.userData.staticSceneRoots = staticSceneRoots;

  return trackCenterline;
}
