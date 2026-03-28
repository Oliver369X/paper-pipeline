/**
 * Minijuego 3D con físicas: Three.js + cannon-es
 */

import * as THREE from "three";
import * as CANNON from "cannon-es";

const canvas = document.getElementById("c");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f1419);
scene.fog = new THREE.Fog(0x0f1419, 20, 55);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  200,
);
camera.position.set(0, 12, 18);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;

const hemi = new THREE.HemisphereLight(0x7aa0ff, 0x1a1a1a, 0.55);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 0.85);
sun.position.set(10, 24, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 80;
sun.shadow.camera.left = -25;
sun.shadow.camera.right = 25;
sun.shadow.camera.top = 25;
sun.shadow.camera.bottom = -25;
scene.add(sun);

const world = new CANNON.World();
world.gravity.set(0, -22, 0);
world.defaultContactMaterial.friction = 0.35;
world.defaultContactMaterial.restitution = 0.25;

const groundSize = 40;
const groundGeo = new THREE.PlaneGeometry(groundSize, groundSize);
const groundMat = new THREE.MeshStandardMaterial({
  color: 0x1e2a3d,
  roughness: 0.85,
  metalness: 0.05,
});
const groundMesh = new THREE.Mesh(groundGeo, groundMat);
groundMesh.rotation.x = -Math.PI / 2;
groundMesh.receiveShadow = true;
scene.add(groundMesh);

const groundBody = new CANNON.Body({ mass: 0 });
groundBody.addShape(new CANNON.Plane());
groundBody.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
world.addBody(groundBody);

const wallMat = new THREE.MeshStandardMaterial({
  color: 0x243044,
  roughness: 0.7,
  metalness: 0.1,
});
const wallH = 4;
const t = groundSize / 2;

function addWall(x, z, rotY) {
  const geo = new THREE.BoxGeometry(groundSize, wallH, 0.6);
  const mesh = new THREE.Mesh(geo, wallMat);
  mesh.position.set(x, wallH / 2, z);
  mesh.rotation.y = rotY;
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  scene.add(mesh);

  const shape = new CANNON.Box(
    new CANNON.Vec3(groundSize / 2, wallH / 2, 0.3),
  );
  const body = new CANNON.Body({ mass: 0 });
  body.addShape(shape);
  body.position.set(x, wallH / 2, z);
  body.quaternion.setFromEuler(0, rotY, 0);
  world.addBody(body);
}

addWall(0, -t, 0);
addWall(0, t, 0);
addWall(-t, 0, Math.PI / 2);
addWall(t, 0, Math.PI / 2);

const meshes = [];
const bodies = [];

function addBox(x, y, z, sx, sy, sz, color) {
  const geo = new THREE.BoxGeometry(sx, sy, sz);
  const mat = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.55,
    metalness: 0.15,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  scene.add(mesh);
  meshes.push(mesh);

  const shape = new CANNON.Box(new CANNON.Vec3(sx / 2, sy / 2, sz / 2));
  const body = new CANNON.Body({ mass: 2.5 });
  body.addShape(shape);
  body.position.set(x, y, z);
  world.addBody(body);
  bodies.push(body);
}

const rng = () => 0.4 + Math.random() * 0.6;
for (let i = 0; i < 14; i++) {
  const x = (Math.random() - 0.5) * 14;
  const z = (Math.random() - 0.5) * 14;
  const s = 0.7 + Math.random() * 0.9;
  const c = new THREE.Color().setHSL(rng(), 0.45, 0.45);
  addBox(x, 3 + i * 0.05, z, s, s, s, c.getHex());
}

const ballR = 0.65;
const ballGeo = new THREE.SphereGeometry(ballR, 32, 24);
const ballMat = new THREE.MeshStandardMaterial({
  color: 0x3ecf8e,
  roughness: 0.35,
  metalness: 0.25,
});
const ballMesh = new THREE.Mesh(ballGeo, ballMat);
ballMesh.castShadow = true;
scene.add(ballMesh);

const ballShape = new CANNON.Sphere(ballR);
const ballBody = new CANNON.Body({ mass: 4 });
ballBody.addShape(ballShape);
ballBody.position.set(0, 4, 0);
ballBody.linearDamping = 0.25;
ballBody.angularDamping = 0.2;
world.addBody(ballBody);

const keys = new Set();
window.addEventListener("keydown", (e) => {
  keys.add(e.code);
  if (e.code === "Space") e.preventDefault();
});
window.addEventListener("keyup", (e) => keys.delete(e.code));

function jump() {
  if (ballBody.velocity.y > 4) return;
  const from = ballBody.position;
  const to = new CANNON.Vec3(from.x, from.y - 2.5, from.z);
  const result = new CANNON.RaycastResult();
  const hit = world.raycastClosest(
    from,
    to,
    {
      collisionFilterMask: -1,
      skipBodies: [ballBody],
    },
    result,
  );
  if (hit && result.hasHit && result.distance < ballR + 0.35) {
    ballBody.velocity.y = 11;
  }
}

const force = 55;
function applyInput(dt) {
  const v = new THREE.Vector3();
  if (keys.has("KeyW")) v.z -= 1;
  if (keys.has("KeyS")) v.z += 1;
  if (keys.has("KeyA")) v.x -= 1;
  if (keys.has("KeyD")) v.x += 1;
  if (v.lengthSq() > 0) {
    v.normalize().multiplyScalar(force * dt);
    ballBody.applyForce(new CANNON.Vec3(v.x, 0, v.z), ballBody.position);
  }
  if (keys.has("Space")) jump();
  if (keys.has("KeyR")) {
    ballBody.position.set(0, 6, 0);
    ballBody.velocity.set(0, 0, 0);
    ballBody.angularVelocity.set(0, 0, 0);
  }
}

const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();

window.addEventListener("click", (e) => {
  ndc.x = (e.clientX / window.innerWidth) * 2 - 1;
  ndc.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(ndc, camera);
  const hits = raycaster.intersectObjects(meshes, false);
  if (hits.length === 0) return;
  const mesh = hits[0].object;
  const i = meshes.indexOf(mesh);
  if (i < 0) return;
  const body = bodies[i];
  const dir = hits[0].point.clone().sub(ballBody.position);
  dir.y = 0.3;
  dir.normalize();
  body.applyImpulse(
    new CANNON.Vec3(dir.x * 18, 6, dir.z * 18),
    body.position,
  );
});

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

const clock = new THREE.Clock();
const tmpV = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  applyInput(dt);
  world.step(1 / 60, dt, 5);

  ballMesh.position.copy(ballBody.position);
  ballMesh.quaternion.copy(ballBody.quaternion);

  for (let i = 0; i < meshes.length; i++) {
    meshes[i].position.copy(bodies[i].position);
    meshes[i].quaternion.copy(bodies[i].quaternion);
  }

  tmpV.copy(ballBody.position);
  tmpV.y += 5;
  tmpV.z += 11;
  camera.position.lerp(tmpV, 0.08);
  camera.lookAt(ballBody.position.x, ballBody.position.y + 0.5, ballBody.position.z);

  renderer.render(scene, camera);
}

animate();
