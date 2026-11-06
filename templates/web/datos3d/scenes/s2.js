// Escena 2 — La miel de las tumbas egipcias: 3.000 años y en buen estado.
import { THREE, scene, add, shadows, phys, std, glowMat, glow, sky, points, shaft, contactShadow, cam, ev, bloom, fx,
  clamp, lerp, ease, sm, spring, bump, rng } from "../core.js";
import { makePanda, posePanda } from "../panda.js";
import { sticker, counter, card, uiState } from "../overlay.js";

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const lathe = (pts, mat, seg = 64) => new THREE.Mesh(new THREE.LatheGeometry(pts.map(([x, y]) => new THREE.Vector2(x, y)), seg), mat);

function glyphTexture(R) {
  const c = document.createElement("canvas"); c.width = 2048; c.height = 768; const x = c.getContext("2d");
  x.fillStyle = "#e7bf7a"; x.fillRect(0, 0, 2048, 768);
  for (let i = 0; i < 2600; i++) { x.fillStyle = `rgba(${120 + R() * 60},${80 + R() * 40},${40},${R() * .08})`; x.beginPath(); x.arc(R() * 2048, R() * 768, 2 + R() * 14, 0, 7); x.fill(); }
  const C = ["#1f4e8c", "#b33a2b", "#2b2118", "#3f7d4e", "#c98a1b"]; x.lineCap = "round"; x.lineJoin = "round";
  for (let row = 0; row < 3; row++) { const y0 = 70 + row * 230; x.fillStyle = "#b33a2b"; x.fillRect(0, y0 - 40, 2048, 10); x.fillStyle = "#1f4e8c"; x.fillRect(0, y0 + 168, 2048, 8);
    for (let k = 0; k < 18; k++) { const cx = 60 + k * 112 + R() * 20, cy = y0 + 70, col = C[Math.floor(R() * 5)], g = Math.floor(R() * 6);
      x.strokeStyle = col; x.fillStyle = col; x.lineWidth = 9; x.beginPath();
      if (g === 0) { x.ellipse(cx, cy, 34, 18, 0, 0, 7); x.stroke(); x.beginPath(); x.arc(cx, cy, 9, 0, 7); x.fill(); x.beginPath(); x.moveTo(cx - 10, cy + 18); x.quadraticCurveTo(cx - 14, cy + 50, cx + 12, cy + 52); x.stroke(); }
      else if (g === 1) { x.ellipse(cx, cy - 24, 15, 22, 0, 0, 7); x.stroke(); x.beginPath(); x.moveTo(cx, cy); x.lineTo(cx, cy + 60); x.moveTo(cx - 28, cy + 10); x.lineTo(cx + 28, cy + 10); x.stroke(); }
      else if (g === 2) { x.ellipse(cx, cy + 10, 30, 18, -.2, 0, 7); x.fill(); x.beginPath(); x.arc(cx + 30, cy - 14, 12, 0, 7); x.fill(); x.beginPath(); x.moveTo(cx + 40, cy - 14); x.lineTo(cx + 58, cy - 8); x.stroke(); x.beginPath(); x.moveTo(cx - 6, cy + 26); x.lineTo(cx - 10, cy + 56); x.moveTo(cx + 8, cy + 26); x.lineTo(cx + 10, cy + 56); x.stroke(); }
      else if (g === 3) { x.fillStyle = "#b33a2b"; x.beginPath(); x.arc(cx, cy + 10, 28, 0, 7); x.fill(); x.strokeStyle = "#c98a1b"; x.lineWidth = 6; x.beginPath(); x.arc(cx, cy + 10, 36, 0, 7); x.stroke(); }
      else if (g === 4) { for (let w = 0; w < 3; w++) { x.beginPath(); for (let s = 0; s <= 8; s++) x.lineTo(cx - 40 + s * 10, cy - 10 + w * 22 + (s % 2 ? -8 : 8)); x.stroke(); } }
      else { x.ellipse(cx, cy + 12, 22, 30, 0, 0, 7); x.fill(); x.lineWidth = 6; for (const s of [-1, 1]) for (let l = 0; l < 3; l++) { x.beginPath(); x.moveTo(cx + s * 20, cy + l * 16); x.lineTo(cx + s * 40, cy + l * 16 - 8); x.stroke(); } } } }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}

export async function build() {
  const R = rng(23);
  sky("#3a2412", "#8a5a2b", "#2a180a"); scene.fog = new THREE.Fog("#6b4422", 14, 34); scene.environmentIntensity = .32;
  add(new THREE.HemisphereLight("#ffe2b0", "#5a3a1f", .6));
  const sun = add(new THREE.DirectionalLight("#fff0c8", 2.3)); sun.position.set(-5, 10, 4); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8 }); sun.shadow.bias = -.0004; sun.shadow.normalBias = .03;
  const floor = add(new THREE.Mesh(new THREE.CircleGeometry(30, 96), std("#c4925a", { roughness: .9 }))); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
  // muro curvo de jeroglíficos
  const wall = add(new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 7, 96, 1, true, Math.PI * .62, Math.PI * .76), std("#ffffff", { map: glyphTexture(R), roughness: .85, side: THREE.BackSide })));
  wall.position.set(0, 3.5, 1); wall.receiveShadow = true;
  // columnas con capitel de loto
  const colM = std("#e9c98e", { roughness: .8 }), bandM = std("#1f4e8c", { roughness: .7 }), redM = std("#b33a2b", { roughness: .7 });
  [[-4.6, -3.2], [4.6, -3.2], [-6.6, 0], [6.6, 0]].forEach(([x, z]) => { const g = add(new THREE.Group()); g.position.set(x, 0, z);
    add(lathe([[0, 0], [.75, 0], [.75, .25], [.55, .35], [.5, 4.6], [.62, 4.9], [.95, 5.4], [1.0, 5.6], [0, 5.6]], colM), g);
    [1.2, 3.6, 4.7].forEach((y, i) => { const b = add(new THREE.Mesh(new THREE.TorusGeometry(.53, .07, 12, 48), i === 1 ? redM : bandM), g); b.rotation.x = Math.PI / 2; b.position.y = y; });
    shadows(g); });
  // haz de sol con polvo y antorchas
  const beam = add(shaft("#fff1c9", .9, 2.4, 11, .22)); beam.position.set(-2.2, 10.5, 1); beam.rotation.z = -.38;
  const dust = add(points(420, "#fff3d6", .07, (i, T) => { const k = i * 7.13, y = ((k * 1.3 + T * .25) % 8); return [-2.2 + 3.4 * Math.sin(-.38) * -(y / 8) * 1.3 + Math.sin(k + T * .3) * .9, y, 1 + Math.cos(k * 1.7 + T * .2) * .9]; }, { opacity: .55 }));
  const torches = [[-3.4, -2.6], [3.4, -2.6]].map(([x, z]) => { const g = add(new THREE.Group()); g.position.set(x, 0, z);
    add(lathe([[0, 0], [.08, 0], [.06, 2.1], [.22, 2.3], [.2, 2.5], [0, 2.5]], std("#6d4c41")), g);
    const f1 = add(glow("#ffb347", 1.6), g), f2 = add(glow("#ffe08a", .8), g); f1.position.y = 2.75; f2.position.y = 2.7;
    const l = add(new THREE.PointLight("#ff9a3c", 22, 12, 1.6), g); l.position.y = 2.8; shadows(g); return { f1, f2, l }; });
  // tesoros dorados
  const gold = phys("#ffc23a", { metalness: 1, roughness: .22 });
  [[2.7, -1.2, .9], [3.3, -.2, .7], [-2.9, -1.4, .8]].forEach(([x, z, s]) => { const v = add(lathe([[0, 0], [.22, 0], [.34, .25], [.36, .55], [.2, .82], [.16, 1.0], [.26, 1.08], [0, 1.08]], gold), scene); v.position.set(x, 0, z); v.scale.setScalar(s); shadows(v); });
  const coins = add(new THREE.InstancedMesh(new THREE.CylinderGeometry(.12, .12, .03, 32), gold, 60)); const M4 = new THREE.Matrix4(), q = new THREE.Quaternion();
  for (let i = 0; i < 60; i++) { const a = R() * 6.28, r = R() * .7; q.setFromEuler(new THREE.Euler((R() - .5) * .6, R() * 3, (R() - .5) * .6));
    M4.compose(V(2.6 + Math.cos(a) * r, .02 + (1 - r) * .25 * R(), .6 + Math.sin(a) * r), q, V(1, 1, 1)); coins.setMatrixAt(i, M4); } shadows(coins);
  // pedestal y tarro de miel
  add(lathe([[0, 0], [1.1, 0], [1.1, .15], [.85, .3], [.7, 1.0], [.95, 1.12], [.95, 1.25], [0, 1.25]], std("#c9a06a", { roughness: .75 }))).castShadow = true;
  const pot = add(new THREE.Group()); pot.position.y = 1.25;
  const potM = phys("#c96a3b", { roughness: .45, clearcoat: .5 });
  add(lathe([[0, 0], [.42, 0], [.62, .3], [.68, .62], [.55, .95], [.36, 1.08], [.38, 1.2], [.3, 1.22], [.28, 1.1], [0, 1.1]], potM), pot).castShadow = true;
  const band = add(new THREE.Mesh(new THREE.TorusGeometry(.66, .05, 12, 64), std("#1f4e8c")), pot); band.rotation.x = Math.PI / 2; band.position.y = .6; band.scale.z = .6;
  const honeyM = new THREE.MeshPhysicalMaterial({ color: "#ffb320", emissive: "#ff9800", emissiveIntensity: .55, roughness: .12, clearcoat: 1, transmission: 0 });
  const honey = add(new THREE.Mesh(new THREE.CylinderGeometry(.29, .29, .06, 48), honeyM), pot); honey.position.y = 1.12;
  const lid = add(lathe([[0, 0], [.4, 0], [.4, .06], [.3, .14], [.08, .2], [.1, .3], [0, .32]], std("#8d5a3b")), pot); lid.position.y = 1.2;
  const potGlow = add(glow("#ffcc4d", 3.5, 0), pot); potGlow.position.y = 1.4;
  const dipper = add(new THREE.Group()); const wood = std("#a8743a", { roughness: .6 });
  add(lathe([[0, 0], [.04, 0], [.04, 1.0], [0, 1.0]], wood), dipper).position.y = .25;
  for (let k = 0; k < 4; k++) add(new THREE.Mesh(new THREE.TorusGeometry(.12 - k * .012, .035, 12, 32), wood), dipper).position.y = .06 + k * .07;
  const drips = [0, 1, 2].map(() => add(new THREE.Mesh(new THREE.SphereGeometry(.045, 20, 14), honeyM)));
  // abejas
  const bees = [0, 1, 2, 3].map(i => { const g = add(new THREE.Group()); const yb = phys("#ffd23f"), bk = std("#2b2118");
    add(new THREE.Mesh(new THREE.SphereGeometry(.12, 24, 16), yb), g).scale.set(1.35, 1, 1);
    for (const x of [-.04, .06]) { const s = add(new THREE.Mesh(new THREE.TorusGeometry(.105, .025, 8, 24), bk), g); s.rotation.y = Math.PI / 2; s.position.x = x; }
    const wings = [-1, 1].map(s => { const w = add(new THREE.Mesh(new THREE.CircleGeometry(.11, 24), new THREE.MeshPhysicalMaterial({ color: "#eaffff", transparent: true, opacity: .55, side: THREE.DoubleSide, roughness: .1 })), g);
      w.position.set(0, .1, s * .07); w.rotation.x = -Math.PI / 2; return w; });
    return { g, wings, ph: i * 1.6 }; });
  // panda explorador
  const P = makePanda({ hat: true, seed: 3.1 }); add(P.root); P.root.scale.setScalar(.82); P.root.position.set(-2.3, 0, 1.6); P.root.rotation.y = .55;
  add(contactShadow(1, .45)).position.set(-2.3, 0, 1.6);
  // capa de edición
  sticker({ t0: ev("honey") + .1, t1: 27.6, html: "🍯", size: 120, x: 1060, y: 240, cls: "emo" });
  card({ t0: ev("honey") + 1.0, t1: 27.6, html: "¡Casi nunca caduca! <span class='emo'>♾️</span>", x: 1010, y: 380 });
  sticker({ t0: ev("egypt") + .2, t1: 30.0, kind: "stamp", html: "ANTIGUO EGIPTO 🏺", cls: "stamp", x: 640, y: 190, rot: -3, float: false, update: el => { el.style.background = "linear-gradient(180deg,#d9a441,#9c6a1e)"; } });
  counter({ t0: ev("years") - .05, t1: 32.4, from: 0, to: 3000, dur: 1.0, suffix: "+", size: 150, x: 640, y: 210, kind: "pop" });
  card({ t0: ev("years") + .4, t1: 32.4, html: "AÑOS 🕰️", x: 640, y: 320 });
  sticker({ t0: ev("good") - .05, t1: 34.5, kind: "stamp", html: "¡EN BUEN ESTADO! ✅", cls: "stamp", x: 700, y: 200, rot: 4, float: false, update: el => { el.style.background = "linear-gradient(180deg,#4fd16b,#1f9e44)"; } });
  sticker({ t0: ev("good") + .35, t1: 34.5, html: "😋", size: 130, x: 300, y: 260, cls: "emo" });

  return (t, T) => {
    const u = fx.material.uniforms; bloom.strength = .38; bloom.threshold = 1.0; u.uWarm.value = .2;
    dust.userData.update(T);
    torches.forEach((o, i) => { const f = .85 + .15 * Math.sin(T * 17 + i) * Math.sin(T * 7.3 + i * 2); o.f1.scale.setScalar(1.6 * f); o.f2.scale.setScalar(.8 * (2 - f)); o.l.intensity = 22 * f; });
    // tapa que salta y miel que brilla
    const la = clamp((T - ev("honey")) / .6), land = bump(T - ev("honey") - .6, .02, .3);
    lid.position.set(lerp(0, .78, la), 1.2 + Math.sin(la * Math.PI) * .95 - la * 1.17, lerp(0, .35, la));
    lid.rotation.set(0, la * 2.5, -Math.sin(la * Math.PI) * 1.3 - la * .15); lid.scale.set(1 + land * .12, 1 - land * .2, 1 + land * .12);
    potGlow.material.opacity = sm((T - ev("honey")) / .4) * (.75 + .25 * Math.sin(T * 3)); honeyM.emissiveIntensity = .4 + .35 * sm((T - ev("honey")) / .4);
    pot.rotation.y = Math.sin(T * .5) * .15;
    dipper.position.set(0, 1.25 + 1.0 + Math.sin(T * 1.3) * .05, 0); dipper.visible = T > ev("honey") + .3; dipper.rotation.z = Math.sin(T * 1.1) * .08;
    drips.forEach((d, i) => { const ph = ((T * .7 + i / 3) % 1); d.visible = dipper.visible; d.position.set(0, 2.25 - ph * .95, 0); d.scale.set(1, 1 + ph * 1.6, 1); });
    bees.forEach((b, i) => { const a = T * 1.6 + b.ph; b.g.position.set(Math.sin(a) * 1.3, 2.2 + Math.sin(a * 2) * .35 + i * .1, Math.cos(a) * .9 + .3); b.g.rotation.y = -a;
      b.g.visible = T > ev("honey") + .5; b.wings.forEach((w, s) => { w.rotation.x = -Math.PI / 2 + Math.sin(T * 60 + s * Math.PI) * .6; }); });
    // panda: prueba la miel al decir «buen estado»
    const S = P.state; S.mood = T > ev("egypt") && T < ev("years") ? "surprised" : "happy"; S.look.set(1, .1);
    const taste = sm((T - ev("good")) / .35); S.armR = taste > .01 ? [lerp(0, -1.9, taste), lerp(.3, .9, taste)] : null; posePanda(P, T);
    // flashback sepia en «antiguo Egipto»
    const fb = sm((T - ev("egypt")) / .35) * (1 - sm((T - ev("years") - .3) / .5));
    u.uSepia.value = fb * .85; u.uGrain.value = .03 + fb * .09; u.uVig.value = .32 + fb * .45; uiState.leak = fb * .5 + bump(T - ev("honey"), .05, .8) * .3;
    // cámara
    const a1 = ease(clamp((T - 22.9) / 1.8)), a2 = ease(clamp((T - ev("egypt") + .2) / 1.5)), a3 = ease(clamp((T - ev("years") - .1) / 1.4)), a4 = ease(clamp((T - ev("good") + .2) / 1.2));
    let px = lerp(4.5, 1.6, a1), py = lerp(3.2, 2.5, a1), pz = lerp(9.5, 5.4, a1), lx = 0, ly = 1.8, lz = 0;
    px = lerp(px, -.6, a2); py = lerp(py, 3.6, a2); pz = lerp(pz, 6.8, a2); ly = lerp(ly, 3.2, a2); lz = lerp(lz, -4, a2);
    px = lerp(px, 1.1, a3); py = lerp(py, 2.3, a3); pz = lerp(pz, 4.6, a3); ly = lerp(ly, 2.0, a3); lz = lerp(lz, 0, a3);
    px = lerp(px, -.4, a4); pz = lerp(pz, 5.0, a4); lx = lerp(lx, -1.1, a4); ly = lerp(ly, 1.9, a4);
    cam.pos.set(px, py, pz); cam.look.set(lx, ly, lz);
    cam.fov = 40 - bump(T - ev("honey"), .05, .5) * 5 - bump(T - ev("years"), .05, .5) * 4 - bump(T - ev("good"), .05, .5) * 5;
    u.uCA.value += bump(T - ev("good"), .03, .4) * .015; uiState.shake = bump(T - ev("good"), .03, .35) * .4;
  };
}
