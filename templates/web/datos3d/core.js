// Núcleo: render, posproceso, utilidades deterministas y transiciones. Todo es función del tiempo (seek).
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { TTFLoader } from "three/addons/loaders/TTFLoader.js";
import { Font } from "three/addons/loaders/FontLoader.js";
import { TextGeometry } from "three/addons/geometries/TextGeometry.js";
export { THREE };

export const Q = new URLSearchParams(location.search);
export const W = innerWidth, H = innerHeight;
export const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
document.getElementById("stage").appendChild(renderer.domElement);

export const scene = new THREE.Scene();
export const camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 900);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.55;

// ---------- posproceso: bloom en HDR, luego tono y una pasada de «edición» en espacio de pantalla
const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
export const composer = new EffectComposer(renderer, rt);
composer.addPass(new RenderPass(scene, camera));
export const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.4, 0.45, 1.0);
composer.addPass(bloom);
composer.addPass(new OutputPass());
export const fx = new ShaderPass({
  uniforms: {
    tDiffuse: { value: null }, uTime: { value: 0 }, uRes: { value: new THREE.Vector2(W, H) },
    uCA: { value: 0.002 }, uGrain: { value: 0.035 }, uVig: { value: 0.35 }, uZoom: { value: 0 }, uZoomC: { value: new THREE.Vector2(.5, .5) },
    uWhip: { value: 0 }, uWhipDir: { value: new THREE.Vector2(1, 0) }, uGlitch: { value: 0 }, uFlash: { value: 0 }, uInvert: { value: 0 },
    uSat: { value: 1.12 }, uContrast: { value: 1.06 }, uBright: { value: 0.0 }, uWarm: { value: 0.0 }, uSepia: { value: 0 },
  },
  vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform vec2 uRes, uZoomC, uWhipDir;
    uniform float uTime,uCA,uGrain,uVig,uZoom,uWhip,uGlitch,uFlash,uInvert,uSat,uContrast,uBright,uWarm,uSepia; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    vec3 samp(vec2 uv){ vec2 d = uv - 0.5; float ca = uCA * (0.5 + dot(d, d) * 2.5);
      return vec3(texture2D(tDiffuse, uv + d * ca).r, texture2D(tDiffuse, uv).g, texture2D(tDiffuse, uv - d * ca).b); }
    void main(){
      vec2 uv = vUv;
      if (uGlitch > 0.001) { float band = floor(uv.y * 22.0); float r = hash(vec2(band, floor(uTime * 30.0)));
        if (r < uGlitch * 0.7) uv.x += (hash(vec2(band, floor(uTime * 30.0) + 3.1)) - 0.5) * 0.16 * uGlitch; }
      vec3 c;
      if (uZoom > 0.001 || uWhip > 0.001) { c = vec3(0.0); float tot = 0.0;
        for (int i = 0; i < 14; i++) { float k = float(i) / 13.0;
          vec2 off = (uv - uZoomC) * (-uZoom * 0.22 * k) + uWhipDir * (uWhip * 0.16 * (k - 0.5));
          float w = 1.0 - k * 0.45; c += samp(uv + off) * w; tot += w; }
        c /= tot; } else c = samp(uv);
      if (uGlitch > 0.001) { c.r = mix(c.r, texture2D(tDiffuse, uv + vec2(0.018 * uGlitch, 0.0)).r, 0.85);
        c.b = mix(c.b, texture2D(tDiffuse, uv - vec2(0.018 * uGlitch, 0.0)).b, 0.85); }
      c = (c - 0.5) * uContrast + 0.5 + uBright;
      float l = dot(c, vec3(0.299, 0.587, 0.114)); c = mix(vec3(l), c, uSat);
      c *= vec3(1.0 + uWarm * 0.07, 1.0 + uWarm * 0.01, 1.0 - uWarm * 0.07);
      c = mix(c, vec3(l * 1.08 + 0.06, l * 0.94 + 0.03, l * 0.7), uSepia);
      vec2 q = (vUv - 0.5) * vec2(uRes.x / uRes.y, 1.0); c *= 1.0 - uVig * smoothstep(0.45, 1.15, length(q));
      c += (hash(vUv * uRes + fract(uTime * 7.31) * 113.0) - 0.5) * uGrain;
      c = mix(c, vec3(1.0), clamp(uFlash, 0.0, 1.0)); c = mix(c, 1.0 - c, uInvert);
      gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
    }`,
});
composer.addPass(fx);

// ---------- datos y tiempo
export let DATA = null, SC = Number(Q.get("scene") || 0), T0 = 0, DUR = 8;
export async function loadData() {
  DATA = await (await fetch("../../../" + (Q.get("data") || "projects/datos-curiosos-3d/v2/datos.json"))).json();
  T0 = DATA.scenes[SC].start; DUR = DATA.scenes[SC].dur; return DATA;
}
export const ev = k => DATA.events[k];
export function envAt(T) { const f = T * DATA.fps, i = Math.floor(f), a = DATA.env[i] || 0, b = DATA.env[i + 1] || 0; return a + (b - a) * (f - i); }
export function beatPhase(T) { const b = DATA.beats; let k = 0; while (k < b.length - 1 && b[k + 1] <= T) k++; return { k, x: (T - b[k]) / (60 / DATA.bpm) }; }

// ---------- matemáticas de animación
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, k) => a + (b - a) * k;
export const sm = x => { x = clamp(x); return x * x * (3 - 2 * x); };
export const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
export const outCubic = x => 1 - Math.pow(1 - clamp(x), 3);
export const outBack = (x, s = 1.9) => { x = clamp(x); return 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); };
export const spring = (x, f = 11, d = 6) => x <= 0 ? 0 : 1 - Math.exp(-d * x) * Math.cos(f * x);   // rebote elástico
export const bump = (x, a = .06, r = .45) => x < 0 ? 0 : x < a ? x / a : Math.max(0, 1 - (x - a) / r) ** 2; // golpe rápido
export const wobble = (T, s = 1) => Math.sin(T * 1.7 * s) * .6 + Math.sin(T * 2.9 * s + 1.3) * .3 + Math.sin(T * 5.3 * s + 2.1) * .1;
export function rng(seed) { let s = seed % 2147483647 || 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

// ---------- materiales y piezas suaves
export const std = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: .5, ...o });
export const phys = (c, o = {}) => new THREE.MeshPhysicalMaterial({ color: c, roughness: .35, clearcoat: .6, clearcoatRoughness: .25, ...o });
export const glowMat = (c, i = 2) => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: i, roughness: .4 });
export function add(o, p = scene) { p.add(o); return o; }
export function shadows(o, cast = true, recv = true) { o.traverse(m => { if (m.isMesh) { m.castShadow = cast; m.receiveShadow = recv; } }); return o; }
function canvasTex(size, draw) { const c = document.createElement("canvas"); c.width = c.height = size; draw(c.getContext("2d"), size);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
export const dotTex = canvasTex(64, (x, s) => { const g = x.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(.45, "rgba(255,255,255,.85)"); g.addColorStop(1, "rgba(255,255,255,0)"); x.fillStyle = g; x.fillRect(0, 0, s, s); });
export function glow(color, size, opacity = 1) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: dotTex, color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
  s.scale.set(size, size, 1); return s;
}
export function contactShadow(r = 1, o = .45) {
  const m = new THREE.Mesh(new THREE.CircleGeometry(r, 48), new THREE.MeshBasicMaterial({ map: dotTex, color: "#000", transparent: true, opacity: o, depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.position.y = .012; return m;
}
// partículas redondas (nunca cuadradas): fn(i, T) -> [x, y, z]
export function points(n, color, size, fn, opts = {}) {
  const g = new THREE.BufferGeometry(), pos = new Float32Array(n * 3);
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const p = new THREE.Points(g, new THREE.PointsMaterial({ color, size, map: dotTex, transparent: true, opacity: opts.opacity ?? .9,
    depthWrite: false, blending: opts.normal ? THREE.NormalBlending : THREE.AdditiveBlending, sizeAttenuation: true }));
  p.frustumCulled = false;
  p.userData.update = T => { for (let i = 0; i < n; i++) { const v = fn(i, T); pos[i * 3] = v[0]; pos[i * 3 + 1] = v[1]; pos[i * 3 + 2] = v[2]; } g.attributes.position.needsUpdate = true; };
  return p;
}
// cielo degradado en cúpula (se mueve con la cámara de forma natural)
export function sky(top, mid, bot, opts = {}) {
  const m = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { cT: { value: new THREE.Color(top) }, cM: { value: new THREE.Color(mid) }, cB: { value: new THREE.Color(bot) }, uStars: { value: opts.stars || 0 }, uFlash: { value: 0 } },
    vertexShader: "varying vec3 vD; void main(){ vD = normalize(position); vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.0); gl_Position = p.xyww; }",
    fragmentShader: `uniform vec3 cT, cM, cB; uniform float uStars, uFlash; varying vec3 vD;
      float h(vec3 p){ return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453); }
      void main(){ float y = vD.y; vec3 c = y > 0.0 ? mix(cM, cT, pow(clamp(y, 0.0, 1.0), 0.7)) : mix(cM, cB, pow(clamp(-y, 0.0, 1.0), 0.5));
        if (uStars > 0.0) { vec3 q = floor(vD * 260.0); float s = h(q); c += vec3(step(0.9965, s) * uStars * (0.6 + 0.4 * h(q + 1.0))); }
        gl_FragColor = vec4(c * (1.0 + uFlash), 1.0); }` });
  const s = new THREE.Mesh(new THREE.SphereGeometry(500, 48, 24), m); s.renderOrder = -10; s.frustumCulled = false; return add(s);
}
// haz de luz volumétrico (cono aditivo con bordes suaves)
export function shaft(color, rTop, rBot, h, alpha = .35) {
  const g = new THREE.CylinderGeometry(rTop, rBot, h, 48, 1, true); g.translate(0, -h / 2, 0);
  const m = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending,
    uniforms: { c: { value: new THREE.Color(color) }, a: { value: alpha } },
    vertexShader: "varying float vY; varying vec3 vN, vV; void main(){ vY = uv.y; vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position, 1.0); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }",
    fragmentShader: "uniform vec3 c; uniform float a; varying float vY; varying vec3 vN, vV; void main(){ float e = pow(abs(dot(normalize(vN), normalize(vV))), 1.6); gl_FragColor = vec4(c * a * e * pow(vY, 1.4), 1.0); }" });
  return new THREE.Mesh(g, m);
}
// texto 3D redondeado (Baloo 2, con tildes y Ñ)
let FONT = null;
export async function loadFont() {
  const json = await new Promise((ok, ko) => new TTFLoader().load("../../../node_modules/@expo-google-fonts/baloo-2/800ExtraBold/Baloo2_800ExtraBold.ttf", ok, undefined, ko));
  FONT = new Font(json);
}
export function text3d(str, size, mat) {
  const g = new TextGeometry(str, { font: FONT, size, depth: size * .32, curveSegments: 10, bevelEnabled: true,
    bevelThickness: size * .07, bevelSize: size * .045, bevelSegments: 5 });
  g.center(); g.computeVertexNormals();
  return shadows(new THREE.Mesh(g, mat), true, false);
}
// tubo deformable (tentáculos, algas): eje de longitud L, se curva cada frame sin recrear la geometría
export function bendTube(L, r0, r1, seg = 40, rad = 14, mat) {
  const g = new THREE.CylinderGeometry(1, 1, 1, rad, seg, false); const base = g.attributes.position.array.slice();
  const m = new THREE.Mesh(g, mat);
  m.userData.bend = (curve) => { // curve(u) -> {p:Vector3, n:Vector3, b:Vector3}; radio con conicidad
    const pos = g.attributes.position.array;
    for (let i = 0; i < pos.length; i += 3) {
      const u = clamp(base[i + 1] + .5), r = lerp(r0, r1, Math.pow(u, .9)) * (u > .985 ? .6 : 1);
      const f = curve(u); const x = base[i] * r, z = base[i + 2] * r;
      pos[i] = f.p.x + f.n.x * x + f.b.x * z; pos[i + 1] = f.p.y + f.n.y * x + f.b.y * z; pos[i + 2] = f.p.z + f.n.z * x + f.b.z * z;
    }
    g.attributes.position.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere();
  };
  m.userData.L = L; return m;
}

// ---------- cámara: guion de planos + vibración de mano + golpes de zoom
export const cam = { pos: new THREE.Vector3(), look: new THREE.Vector3(), fov: 38, roll: 0, shake: 0, hand: 1 };
export function applyCamera(T) {
  const s = cam.shake, h = cam.hand * .025;
  camera.position.set(cam.pos.x + wobble(T, 1.1) * h + Math.sin(T * 61) * s * .2, cam.pos.y + wobble(T + 9, .9) * h + Math.cos(T * 53) * s * .2, cam.pos.z);
  camera.lookAt(cam.look);
  camera.rotateZ(cam.roll + wobble(T + 3, .7) * h * .15);
  camera.fov = cam.fov; camera.updateProjectionMatrix();
}

// ---------- transiciones entre escenas (mitad al final de una, mitad al principio de la siguiente)
const TR = ["glitch", "stripes", "whip", "zoom", "glitch", "flash", "stripes"];
const HALF = .32;
const stripes = [...document.querySelectorAll("#stripes i")];
export function transitions(t) {
  const tin = TR[SC], tout = SC + 1 < TR.length ? TR[SC + 1] : "fade";
  let p = 0, type = null, dir = 0;
  if (t < HALF) { p = 1 - t / HALF; type = tin; dir = -1; }
  if (t > DUR - HALF) { p = (t - (DUR - HALF)) / HALF; type = tout; dir = 1; }
  if (SC === 0 && dir === -1) type = "glitchIn";
  p = clamp(p); const u = fx.material.uniforms;
  stripes.forEach(s => { s.style.display = "none"; });
  document.getElementById("flash").style.opacity = "0"; document.getElementById("fade").style.opacity = "0";
  if (!type || p <= 0) return { p: 0, type: null, dir: 0 };
  const e = p * p;
  if (type === "stripes") stripes.forEach((s, i) => { const c = clamp(p * 1.35 - (dir > 0 ? i : 2 - i) * .17);
    s.style.display = "block"; s.style.left = `${i * 33 - 10}%`; s.style.transform = `translateX(${(dir > 0 ? -1 : 1) * 190 * (1 - outCubic(c))}%) skewX(-14deg)`; });
  if (type === "whip") { u.uWhip.value += e * 1.2; u.uWhipDir.value.set(1, 0); }
  if (type === "zoom") { u.uZoom.value += e * 1.3; }
  if (type === "glitch" || type === "glitchIn") { u.uGlitch.value += type === "glitchIn" ? p * .8 : p; u.uCA.value += p * .03; }
  if (type === "flash") { u.uFlash.value = Math.max(u.uFlash.value, Math.pow(p, .8)); }
  if (type === "fade") document.getElementById("fade").style.opacity = String(ease(p));
  return { p, type, dir, e };
}
// efecto de transición sobre la cámara (llamar después de fijar cam.*)
export function transitionCamera(tr) {
  if (!tr.type) return;
  if (tr.type === "whip") { const yaw = tr.dir * tr.e * .9; const d = cam.look.clone().sub(cam.pos);
    d.applyAxisAngle(new THREE.Vector3(0, 1, 0), -yaw); cam.look.copy(cam.pos).add(d); }
  if (tr.type === "zoom") cam.fov *= 1 - .42 * tr.e;
  if (tr.type === "glitch") cam.shake += tr.p * .3;
}
