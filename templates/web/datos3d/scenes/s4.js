// Escena 4 — El rayo: unos 30.000 °C, cinco veces más caliente que la superficie del Sol.
import { THREE, scene, add, shadows, phys, std, glowMat, glow, sky, contactShadow, cam, ev, bloom, fx, clamp, lerp, ease, sm, bump, rng } from "../core.js";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { makePanda, posePanda } from "../panda.js";
import { sticker, counter, card, uiState } from "../overlay.js";

const V = (x, y, z) => new THREE.Vector3(x, y, z);
function windows(R, tint) { const c = document.createElement("canvas"); c.width = 256; c.height = 512; const x = c.getContext("2d");
  x.fillStyle = "#000"; x.fillRect(0, 0, 256, 512);
  for (let r = 0; r < 10; r++) for (let k = 0; k < 4; k++) { if (R() < .35) continue; x.fillStyle = R() < .8 ? tint : "#9fd8ff";
    const X = 18 + k * 60, Y = 18 + r * 50; x.beginPath(); x.roundRect(X, Y, 38, 30, 10); x.fill(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }

export async function build() {
  const R = rng(41);
  const sk = sky("#1d2a63", "#4f62a8", "#141a38"); scene.fog = new THREE.Fog("#27315f", 14, 55); scene.environmentIntensity = .3;
  const hemi = add(new THREE.HemisphereLight("#8fa6ff", "#20223a", .75));
  const moon = add(new THREE.DirectionalLight("#b9c6ff", 1.3)); moon.position.set(-6, 12, 6); moon.castShadow = true;
  moon.shadow.mapSize.set(2048, 2048); Object.assign(moon.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10 }); moon.shadow.bias = -.0004;
  const boltL = add(new THREE.DirectionalLight("#dbe6ff", 0)); boltL.position.set(4, 20, -18);
  // calle mojada con charcos
  const ground = add(new THREE.Mesh(new THREE.PlaneGeometry(80, 120), phys("#2a2e40", { roughness: .2, metalness: .25, clearcoat: 1, clearcoatRoughness: .1 }))); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true;
  for (let i = 0; i < 9; i++) { const p = add(new THREE.Mesh(new THREE.CircleGeometry(.6 + R() * 1.2, 48), phys("#1b2034", { roughness: .02, metalness: .6, clearcoat: 1 })));
    p.rotation.x = -Math.PI / 2; p.position.set((R() - .5) * 8, .01, -R() * 20 + 4); p.scale.y = .55; }
  const curb = std("#5b6078", { roughness: .7 });
  for (const s of [-1, 1]) { const c = add(new THREE.Mesh(new RoundedBoxGeometry(2.2, .25, 70, 4, .1), curb)); c.position.set(s * 5.2, .12, -20); c.receiveShadow = true; }
  // edificios redondeados de colores
  const COLS = ["#5fd3c6", "#b48cff", "#ff8fb8", "#ffb36b", "#6fb2ff", "#7ee08a"], TINTS = ["#ffd27a", "#ffe9a8", "#ffc46b"];
  const antennas = [];
  for (const s of [-1, 1]) for (let i = 0; i < 7; i++) { const w = 3 + R() * 1.6, h = 5 + R() * 11, d = 3.4;
    const b = add(new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 6, .45), std(COLS[(i * 2 + (s > 0 ? 1 : 0)) % 6], { roughness: .55, emissive: "#ffffff", emissiveMap: windows(R, TINTS[i % 3]), emissiveIntensity: .85 })));
    b.position.set(s * (8.2 + R() * .6), h / 2, 4 - i * 5.6); shadows(b);
    if (R() < .45) { const tw = add(new THREE.Group()); tw.position.set(b.position.x, h, b.position.z);
      add(new THREE.Mesh(new THREE.CylinderGeometry(.6, .6, 1.1, 32), std("#9b7652")), tw).position.y = 1.2;
      add(new THREE.Mesh(new THREE.ConeGeometry(.75, .6, 32), std("#7a5a3d")), tw).position.y = 2.05;
      for (let l = 0; l < 4; l++) { const g = add(new THREE.Mesh(new THREE.CylinderGeometry(.04, .04, .7, 8), std("#555")), tw); g.position.set(Math.cos(l * 1.57) * .45, .35, Math.sin(l * 1.57) * .45); } shadows(tw); }
    else { const an = add(new THREE.Mesh(new THREE.CylinderGeometry(.04, .06, 2.2, 8), std("#666"))); an.position.set(b.position.x, h + 1.1, b.position.z);
      const lamp = add(glow("#ff3b3b", .7)); lamp.position.set(b.position.x, h + 2.25, b.position.z); antennas.push(lamp); } }
  // neones redondos
  [["#ff4fa0", -7.0, 3.2, -2], ["#4de1ff", 7.0, 3.8, -7.5], ["#ffe14d", -7.0, 4.2, -13]].forEach(([c, x, y, z], i) => {
    const n = add(new THREE.Mesh(i === 1 ? new THREE.TorusGeometry(.7, .09, 16, 64) : new THREE.TorusKnotGeometry(.45, .08, 96, 12), glowMat(c, 3.2))); n.position.set(x, y, z); n.rotation.y = x < 0 ? Math.PI / 2 : -Math.PI / 2; });
  // farolas con charcos de luz
  for (let i = 0; i < 4; i++) for (const s of [-1, 1]) { const g = add(new THREE.Group()); g.position.set(s * 4.4, 0, 2 - i * 8);
    const curve = new THREE.CatmullRomCurve3([V(0, 0, 0), V(0, 3.6, 0), V(-s * .3, 4.3, 0), V(-s * 1.0, 4.35, 0)]);
    add(new THREE.Mesh(new THREE.TubeGeometry(curve, 32, .07, 10), std("#3a3f55", { roughness: .4, metalness: .6 })), g);
    const hd = add(glow("#ffd59a", 1.5), g); hd.position.set(-s * 1.0, 4.2, 0);
    add(new THREE.Mesh(new THREE.SphereGeometry(.16, 20, 14), glowMat("#ffe2b0", 3)), g).position.set(-s * 1.0, 4.22, 0);
    if (i < 3) { const l = add(new THREE.SpotLight("#ffcf8a", 70, 14, .7, .7, 1.5), g); l.position.set(-s * 1.0, 4.1, 0); l.target.position.set(-s * 1.2, 0, 0); g.add(l.target); } shadows(g, true, false); }
  // lluvia + salpicaduras
  const NR = 1600, rp = new Float32Array(NR * 6), rb = [...Array(NR)].map(() => [(R() - .5) * 30, R() * 18, -R() * 40 + 8]);
  const rg = new THREE.BufferGeometry(); rg.setAttribute("position", new THREE.BufferAttribute(rp, 3));
  add(new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: "#c9d6ff", transparent: true, opacity: .5 })));
  const NS = 60, spl = add(new THREE.InstancedMesh(new THREE.RingGeometry(.08, .12, 24), new THREE.MeshBasicMaterial({ color: "#dfe8ff", transparent: true, opacity: .5, side: THREE.DoubleSide }), NS));
  const sd = [...Array(NS)].map(() => ({ x: (R() - .5) * 10, z: -R() * 16 + 5, ph: R() })); const M4 = new THREE.Matrix4(), RX = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
  // rayo ramificado (HDR para el bloom)
  const boltM = new THREE.MeshBasicMaterial({ color: new THREE.Color("#e8f0ff").multiplyScalar(6), fog: false }); const bolt = add(new THREE.Group());
  function makeBolt(seed, x0, z0) { bolt.clear(); const r = rng(seed); const main = [V(x0, 30, z0)];
    for (let i = 1; i < 16; i++) { const p = main[i - 1]; main.push(V(p.x + (r() - .5) * 2.4, 30 - i * 2, p.z + (r() - .5) * 1.2)); }
    const tube = (pts, rad) => bolt.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, "catmullrom", .1), pts.length * 6, rad, 8), boltM));
    tube(main, .14); for (let b = 0; b < 5; b++) { const st = main[2 + b * 2]; const br = [st]; for (let i = 1; i < 5; i++) { const p = br[i - 1]; br.push(V(p.x + (r() - .3) * 2.2, p.y - 1.6, p.z + (r() - .5))); } tube(br, .05); }
    const g = glow("#9fc0ff", 40, .8); g.position.set(main[8].x, 14, z0); bolt.add(g); }
  const STR = [ev("strike1"), ev("strike2"), ev("x5"), ev("sunCmp") + .55];
  // termómetro de cristal
  const th = add(new THREE.Group()); th.position.set(-2.9, 0, 1.4);
  add(new THREE.Mesh(new THREE.CapsuleGeometry(.32, 4.2, 16, 32), new THREE.MeshPhysicalMaterial({ color: "#ffffff", transparent: true, opacity: .25, roughness: .05, clearcoat: 1, depthWrite: false })), th).position.y = 2.75;
  const bulb = add(new THREE.Mesh(new THREE.SphereGeometry(.55, 40, 28), glowMat("#ff2b4a", 1.4)), th); bulb.position.y = .55;
  const liq = add(new THREE.Mesh(new THREE.CapsuleGeometry(.17, 1, 10, 24), glowMat("#ff2b4a", 1.6)), th);
  for (let k = 0; k < 9; k++) { const m = add(new THREE.Mesh(new THREE.CapsuleGeometry(.025, .22, 4, 8), std("#ffffff")), th); m.rotation.z = Math.PI / 2; m.position.set(.42, 1.3 + k * .48, 0); }
  shadows(th, true, false);
  // panda con paraguas
  const P = makePanda({ umbrella: true, seed: 5.3, glasses: true }); add(P.root); P.root.scale.setScalar(.8); P.root.position.set(.9, 0, 1.8); P.root.rotation.y = -.3;
  add(contactShadow(1, .5)).position.set(.9, .01, 1.8);
  // capa de edición
  sticker({ t0: ev("strike1") + .02, t1: 48.6, kind: "stamp", html: "¡ZAS! ⚡", cls: "stamp", x: 1000, y: 180, rot: 8, float: false, update: el => { el.style.background = "linear-gradient(180deg,#6c7bff,#3a3fd8)"; } });
  counter({ t0: ev("deg") - .1, t1: 52.9, from: 0, to: 30000, dur: 1.3, suffix: " °C", size: 128, x: 760, y: 200 });
  card({ t0: ev("deg") + .3, t1: 51.1, html: "🌡️ temperatura de un rayo", x: 760, y: 305 });
  sticker({ t0: ev("x5") - .02, t1: 53.0, kind: "stamp", html: "×5", cls: "stamp", x: 1050, y: 330, rot: -8, float: false, update: el => { el.style.fontSize = "150px"; el.style.background = "linear-gradient(180deg,#ff8a1f,#ff3d3d)"; } });
  let bs, br;
  card({ t0: ev("sunCmp") - .15, t1: 55.5, x: 900, y: 430, float: false,
    html: `<div style="width:440px"><div>☀️ Superficie del Sol <b style="float:right">5.500 °C</b></div><div class="bar"><b class="bs" style="width:0;background:linear-gradient(90deg,#ffb300,#ffe14d)"></b></div>
      <div style="margin-top:12px">⚡ Rayo <b style="float:right">30.000 °C</b></div><div class="bar"><b class="br" style="width:0;background:linear-gradient(90deg,#6c7bff,#4de1ff)"></b></div></div>`,
    update: (el, t) => { bs = bs || el.querySelector(".bs"); br = br || el.querySelector(".br"); bs.style.width = (18.3 * ease(t / .6)).toFixed(1) + "%"; br.style.width = (100 * ease((t - .25) / .9)).toFixed(1) + "%"; } });

  let lastBolt = -1;
  return (t, T) => {
    const u = fx.material.uniforms; bloom.strength = .45; bloom.threshold = 1.0;
    rb.forEach(([x, y, z], i) => { const yy = ((y - T * 17) % 18 + 18) % 18; rp.set([x - yy * .04, yy, z, x - yy * .04 + .04, yy + .55, z], i * 6); }); rg.attributes.position.needsUpdate = true;
    for (let i = 0; i < NS; i++) { const d = sd[i], k = (T * 1.7 + d.ph) % 1; M4.makeScale(.4 + k * 2.2, .4 + k * 2.2, 1).premultiply(RX); M4.setPosition(d.x, .02, d.z); spl.setMatrixAt(i, M4); }
    spl.instanceMatrix.needsUpdate = true; spl.material.opacity = .45;
    antennas.forEach((a, i) => a.material.opacity = Math.sin(T * 4 + i) > 0 ? 1 : .15);
    // rayos: parpadeo de 0,45 s
    let f = 0, si = -1; STR.forEach((s, i) => { const d = T - s; if (d >= 0 && d < .45) { const v = (1 - d / .45) * (d < .07 || (d > .13 && d < .2) ? 1 : .3); if (v > f) { f = v; si = i; } } });
    if (si >= 0 && si !== lastBolt) { makeBolt(101 + si * 977, [4, -6, 6, -2][si], [-22, -26, -18, -24][si]); lastBolt = si; }
    bolt.visible = f > .25; boltL.intensity = f * 6; hemi.intensity = .75 + f * 1.4; sk.material.uniforms.uFlash.value = f * 1.6;
    u.uFlash.value = f * .2; u.uInvert.value = T - ev("strike2") > 0 && T - ev("strike2") < .05 ? 1 : 0; u.uCA.value += f * .02;
    // termómetro sube con «30.000 grados»
    const hk = ease(clamp((T - ev("deg") + .05) / 1.3)), hh = lerp(.2, 4.0, hk); liq.scale.y = hh; liq.position.y = .75 + hh / 2 + .1; bulb.material.emissiveIntensity = 1.4 + hk * 2.5;
    // panda asustado bajo el paraguas
    const fear = Math.max(...STR.map(s => bump(T - s, .03, .9)));
    P.state.mood = fear > .2 ? "scared" : "happy"; P.state.look.set(.4, .8); P.state.armR = [-.35 + Math.sin(T * 30) * fear * .08, .25]; posePanda(P, T);
    P.root.position.x = .9 + Math.sin(T * 40) * fear * .03;
    // cámara
    const a1 = ease(clamp((T - 45.9) / 1.4)), a2 = ease(clamp((T - ev("deg") + .3) / 1.0)), a3 = ease(clamp((T - ev("x5") - .2) / 1.6));
    let p = V(lerp(3.2, 2.4, a1), lerp(1.2, 1.9, a1), lerp(7.6, 6.6, a1)), l = V(.6, lerp(2.0, 3.2, a1), -2);
    p.lerp(V(-.6, 1.4, 6.2), a2); l.lerp(V(-2.9, 2.9, 1.2), a2); p.lerp(V(1.5, 3.2, 10.5), a3); l.lerp(V(0, 3.4, -6), a3);
    cam.pos.copy(p); cam.look.copy(l);
    cam.fov = 40 - bump(T - ev("x5"), .04, .45) * 7 - bump(T - ev("deg"), .05, .4) * 4; cam.shake = f * .9 + bump(T - ev("x5"), .03, .4) * .5;
    uiState.shake = f * .6 + bump(T - ev("x5"), .03, .4) * .6;
  };
}
