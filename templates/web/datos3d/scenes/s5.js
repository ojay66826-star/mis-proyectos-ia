// Escena 5 — El panda gigante: hasta 14 horas al día comiendo bambú.
import { THREE, scene, add, shadows, phys, std, glowMat, glow, sky, points, shaft, contactShadow, cam, ev, bloom, fx, clamp, lerp, ease, sm, spring, bump, rng } from "../core.js";
import { makePanda, posePanda } from "../panda.js";
import { sticker, counter, card, uiState } from "../overlay.js";

const V = (x, y, z) => new THREE.Vector3(x, y, z);
export async function build() {
  const R = rng(53);
  sky("#6cc8ff", "#e4f8ff", "#a5d97a"); scene.fog = new THREE.Fog("#d6f2c6", 10, 42); scene.environmentIntensity = .6;
  add(new THREE.HemisphereLight("#f4fff0", "#5b8a3a", 1.05));
  const sun = add(new THREE.DirectionalLight("#fff4d6", 2.7)); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9 }); sun.shadow.bias = -.0004; sun.shadow.normalBias = .03;
  const ground = add(new THREE.Mesh(new THREE.CircleGeometry(60, 96), std("#7cc35a", { roughness: .95 }))); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true;
  // hierba y flores (instancias)
  const NG = 2600, grass = add(new THREE.InstancedMesh(new THREE.ConeGeometry(.035, .42, 5), std("#5fb544", { roughness: .8 }), NG)); const M4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
  const gd = [...Array(NG)].map(() => { const a = R() * 6.28, r = Math.sqrt(R()) * 14; return { x: Math.cos(a) * r, z: Math.sin(a) * r * .8 - 2, s: .6 + R() * .9, ph: R() * 6 }; });
  gd.forEach((g, i) => grass.setColorAt(i, new THREE.Color().setHSL(.27 + R() * .06, .55, .38 + R() * .15)));
  const NF = 120, flw = add(new THREE.InstancedMesh(new THREE.SphereGeometry(.07, 12, 8), std("#ffffff", { roughness: .6 }), NF));
  for (let i = 0; i < NF; i++) { const a = R() * 6.28, r = 2 + R() * 11; M4.makeTranslation(Math.cos(a) * r, .3, Math.sin(a) * r * .8 - 2); flw.setMatrixAt(i, M4); flw.setColorAt(i, new THREE.Color(["#ffffff", "#ffe14d", "#ff9ac6", "#c79bff"][i % 4])); }
  // bambúes con nudos y hojas
  const stalkM = [phys("#8bc34a", { roughness: .4, clearcoat: .4 }), phys("#9ccc65", { roughness: .4, clearcoat: .4 }), phys("#7cb342", { roughness: .4, clearcoat: .4 })], nodeM = std("#558b2f");
  const leafG = new THREE.SphereGeometry(1, 16, 10); const NL = 900, leaves = add(new THREE.InstancedMesh(leafG, std("#43a047", { roughness: .6 }), NL)); let li = 0;
  const stalks = [];
  for (let i = 0; i < 46; i++) { let x, z; do { x = (R() - .5) * 26; z = -R() * 18 + 4; } while (Math.hypot(x, z - .5) < 3.4 || (z > 2 && Math.abs(x) < 4.5));
    const g = add(new THREE.Group()); g.position.set(x, 0, z); const h = 7 + R() * 7, m = stalkM[i % 3];
    for (let k = 0; k < h / 1.1; k++) { add(new THREE.Mesh(new THREE.CylinderGeometry(.12, .13, 1.08, 16), m), g).position.y = k * 1.1 + .54;
      const n = add(new THREE.Mesh(new THREE.TorusGeometry(.13, .03, 8, 24), nodeM), g); n.rotation.x = Math.PI / 2; n.position.y = k * 1.1 + 1.09; }
    for (let k = 0; k < 18 && li < NL; k++, li++) { const y = h * (.55 + R() * .45), a = R() * 6.28, r = .4 + R() * .9;
      q.setFromEuler(e.set((R() - .5) * .8, a, -.9 + (R() - .5) * .6)); M4.compose(V(x + Math.cos(a) * r, y, z + Math.sin(a) * r), q, V(.09, .02, .45 + R() * .2)); leaves.setMatrixAt(li, M4);
      leaves.setColorAt(li, new THREE.Color().setHSL(.3 + R() * .05, .6, .32 + R() * .14)); }
    shadows(g); stalks.push({ g, ph: R() * 6 }); }
  leaves.count = li; leaves.castShadow = true;
  const rays = [0, 1, 2, 3].map(i => { const s = add(shaft("#fffbe0", .5, 2.2, 16, .16)); s.position.set(-5 + i * 3.4, 15, -4 - i); s.rotation.z = .3; return s; });
  const pollen = add(points(300, "#fff8c2", .08, (i, T) => { const k = i * 3.7; return [Math.sin(k) * 9 + Math.sin(T * .3 + k) * .6, 1 + ((k * .7 + T * .2) % 5), Math.cos(k * 1.3) * 6 - 1]; }, { opacity: .6 }));
  // mariposas
  const flies = [0, 1, 2].map(i => { const g = add(new THREE.Group()); const m = new THREE.MeshStandardMaterial({ color: ["#ff7ab8", "#ffd23f", "#6fd3ff"][i], side: THREE.DoubleSide, roughness: .5 });
    const w = [-1, 1].map(s => { const p = add(new THREE.Group(), g); const wi = add(new THREE.Mesh(new THREE.CircleGeometry(.15, 24), m), p); wi.position.x = s * .15; wi.scale.y = .75; return p; });
    add(new THREE.Mesh(new THREE.CapsuleGeometry(.02, .14, 4, 8), std("#2b2118")), g).rotation.z = Math.PI / 2; return { g, w, ph: i * 2.1 }; });
  // panda sentado con su montón de bambú
  const P = makePanda({ seed: 6.1, glasses: true }); add(P.root); P.root.position.set(0, -.05, .5);
  P.legs.forEach((l, i) => { l.rotation.x = -1.35; l.position.set(i ? .33 : -.33, .2, .38); });
  add(contactShadow(1.4, .5)).position.set(0, .01, .5);
  const stick = add(new THREE.Group(), P.arms[1]); stick.position.set(-.1, -.6, .12);
  for (let k = 0; k < 2; k++) { add(new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, .8, 12), stalkM[0]), stick).position.y = .4 + k * .8 - .4;
    const n = add(new THREE.Mesh(new THREE.TorusGeometry(.065, .02, 6, 16), nodeM), stick); n.rotation.x = Math.PI / 2; n.position.y = .4 + k * .8; }
  for (let k = 0; k < 3; k++) { const lf = add(new THREE.Mesh(leafG, std("#4caf50")), stick); lf.scale.set(.07, .02, .3); lf.position.set(.12, 1.0 - k * .15, 0); lf.rotation.set(0, k, -.8); }
  stick.rotation.set(0, 0, .35);
  for (let i = 0; i < 10; i++) { const s = add(new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, 1.5, 12), stalkM[i % 3])); s.rotation.set(0, R() * 3, Math.PI / 2); s.position.set(1.6 + (R() - .5) * .7, .07 + (i % 3) * .12, .9 + (R() - .5) * .7); s.castShadow = true; }
  // reloj 3D redondo
  const clock = add(new THREE.Group()); clock.position.set(-2.7, 3.1, -.6);
  add(new THREE.Mesh(new THREE.CylinderGeometry(1, 1, .22, 64), phys("#fff8e8", { roughness: .3 })), clock).rotation.x = Math.PI / 2;
  add(new THREE.Mesh(new THREE.TorusGeometry(1, .11, 20, 64), phys("#ff8a1f", { roughness: .25 })), clock);
  for (let k = 0; k < 12; k++) { const d = add(new THREE.Mesh(new THREE.SphereGeometry(.05, 12, 8), std("#5d4037")), clock); d.position.set(Math.sin(k / 12 * 6.283) * .8, Math.cos(k / 12 * 6.283) * .8, .13); }
  const hH = add(new THREE.Mesh(new THREE.CapsuleGeometry(.045, .42, 6, 12), std("#3e2723")), clock), hM = add(new THREE.Mesh(new THREE.CapsuleGeometry(.03, .62, 6, 12), phys("#ff3d6e")), clock);
  hH.geometry.translate(0, .24, 0); hM.geometry.translate(0, .34, 0); hH.position.z = hM.position.z = .15;
  const arc = add(new THREE.Mesh(new THREE.RingGeometry(.15, .72, 64, 1, 0, .01), new THREE.MeshBasicMaterial({ color: "#66d36e", transparent: true, opacity: .75, side: THREE.DoubleSide })), clock); arc.position.z = .12;
  shadows(clock, true, false);
  // capa de edición
  sticker({ t0: ev("panda") - .05, t1: 58.3, kind: "stamp", html: "PANDA GIGANTE 🐼", cls: "stamp", x: 860, y: 170, rot: -4, float: false, update: el => { el.style.background = "linear-gradient(180deg,#3a3a48,#14121f)"; } });
  counter({ t0: ev("hours") - .1, t1: 63.3, from: 0, to: 14, dur: 1.6, suffix: " h", size: 140, x: 980, y: 215 });
  card({ t0: ev("hours") + .5, t1: 63.3, html: "<span class='emo'>⏩</span> comiendo al día", x: 980, y: 320 });
  [0, 1, 2].forEach(i => sticker({ t0: ev("bamboo") + i * .15, t1: 63.3, html: "🎋", size: 90, x: 820 + i * 120, y: 450 + (i % 2) * 30, cls: "emo" }));
  sticker({ t0: ev("eat") - .05, t1: 64.5, kind: "stamp", html: "¡ÑAM ÑAM!", cls: "stamp", x: 330, y: 220, rot: -8, float: false, update: el => { el.style.background = "linear-gradient(180deg,#ff8a1f,#ff4f9a)"; } });
  sticker({ t0: ev("eat") + .25, t1: 64.5, html: "😋", size: 120, x: 520, y: 150, cls: "emo" });

  return (t, T) => {
    const u = fx.material.uniforms; bloom.strength = .35; bloom.threshold = 1.0; u.uWarm.value = .15;
    // cámara rápida: el sol cruza el cielo mientras corren las 14 horas
    const tl = ease(clamp((T - ev("hours") + .1) / 1.9)), sa = lerp(-.9, .9, tl) + (T - 55) * .01;
    sun.position.set(Math.sin(sa) * 10, 9 + Math.cos(sa) * 2, 5); sun.intensity = 2.7 - Math.sin(tl * Math.PI) * .5;
    for (let i = 0; i < NG; i++) { const g = gd[i]; q.setFromEuler(e.set(Math.sin(T * 1.6 + g.ph + g.x * .2) * .12, g.ph, Math.cos(T * 1.3 + g.ph) * .08));
      M4.compose(V(g.x, .19 * g.s, g.z), q, V(g.s, g.s, g.s)); grass.setMatrixAt(i, M4); } grass.instanceMatrix.needsUpdate = true;
    stalks.forEach(s => { s.g.rotation.z = Math.sin(T * .8 + s.ph) * .025; s.g.rotation.x = Math.cos(T * .6 + s.ph) * .015; });
    rays.forEach((r, i) => { r.material.uniforms.a.value = .12 + .05 * Math.sin(T * .7 + i * 1.7); }); pollen.userData.update(T);
    flies.forEach((f, i) => { const a = T * .9 + f.ph; f.g.position.set(Math.sin(a) * 3.2 + (i - 1) * 1.5, 1.6 + Math.sin(a * 2.3) * .5 + i * .3, Math.cos(a) * 1.8 + .5); f.g.rotation.y = -a;
      f.w.forEach((w, s) => w.rotation.y = (s ? 1 : -1) * Math.abs(Math.sin(T * 14 + i)) * 1.1); });
    // panda: mastica, sostiene el bambú y se da palmaditas al decir «comer»
    const chew = Math.sin(T * 9), S = P.state; S.mood = "happy"; S.look.set(.3, -.1);
    S.armR = [-1.55 + chew * .12, .55]; S.armL = T > ev("eat") ? [-.9 + Math.sin(T * 12) * .25, -.25] : [-1.25 + chew * .1, -.45]; S.headX = .05 + chew * .03;
    posePanda(P, T); P.mouthIn.scale.y = Math.max(P.mouthIn.scale.y, .16 + Math.max(0, chew) * .5); P.body.position.y = Math.abs(Math.sin(T * 4.5)) * .03;
    const hk = ease(clamp((T - ev("hours") + .1) / 1.6)) * 14; hM.rotation.z = -hk * Math.PI * 2; hH.rotation.z = -hk / 12 * Math.PI * 2;
    arc.geometry.dispose(); arc.geometry = new THREE.RingGeometry(.15, .72, 64, 1, Math.PI / 2 - hk / 12 * Math.PI * 2, Math.max(.01, hk / 12 * Math.PI * 2));
    clock.scale.setScalar(Math.max(.001, spring(T - ev("hours") + .3, 10, 6)) * .85); clock.rotation.y = Math.sin(T) * .25;
    // cámara
    const a1 = ease(clamp((T - 54.8) / 2.2)), a2 = ease(clamp((T - ev("hours") + .2) / 2.0)), a3 = ease(clamp((T - ev("bamboo") + .1) / 1.6));
    let p = V(lerp(-3.5, 1.2, a1), lerp(2.6, 2.1, a1), lerp(12, 6.8, a1)), l = V(0, lerp(2.6, 1.7, a1), 0);
    p.lerp(V(2.6, 2.6, 6.4), a2); l.lerp(V(-1.0, 2.1, 0), a2); p.lerp(V(.6, 1.9, 4.3), a3); l.lerp(V(0, 1.75, .5), a3);
    cam.pos.copy(p); cam.look.copy(l); cam.fov = 40 - bump(T - ev("panda"), .05, .5) * 5 - bump(T - ev("eat"), .04, .4) * 5;
    u.uZoom.value += sm((T - ev("hours")) / .2) * (1 - sm((T - ev("hours") - 1.6) / .3)) * .25; uiState.shake = bump(T - ev("eat"), .03, .35) * .4;
  };
}
