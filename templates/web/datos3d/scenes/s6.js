// Escena 6 — Final: el panda baila; resumen de los 5 datos, comentarios y botón de suscribirse.
import { THREE, scene, add, shadows, phys, std, glowMat, glow, sky, shaft, contactShadow, text3d, cam, ev, bloom, fx, DATA,
  clamp, lerp, ease, sm, spring, bump, rng, beatPhase } from "../core.js";
import { makePanda, posePanda } from "../panda.js";
import { sticker, card, uiState } from "../overlay.js";

const V = (x, y, z) => new THREE.Vector3(x, y, z);
export async function build() {
  const R = rng(67);
  sky("#1a0b3d", "#6a2a9e", "#1a0b3d"); scene.fog = new THREE.Fog("#4a1f7a", 14, 50); scene.environmentIntensity = .5;
  add(new THREE.HemisphereLight("#e8d6ff", "#2a1050", .7));
  const key = add(new THREE.DirectionalLight("#fff0e0", 2.0)); key.position.set(3, 9, 7); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7 }); key.shadow.bias = -.0004; key.shadow.normalBias = .03;
  const floor = add(new THREE.Mesh(new THREE.CircleGeometry(50, 96), phys("#2b1a5e", { roughness: .15, metalness: .3, clearcoat: 1 }))); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
  const prof = [[0, 0], [3.2, 0], [3.35, .08], [3.4, .25], [3.35, .42], [3.2, .5], [0, .5]].map(([x, y]) => new THREE.Vector2(x, y));
  add(new THREE.Mesh(new THREE.LatheGeometry(prof, 96), phys("#ffb84d", { roughness: .45 }))).receiveShadow = true;
  const ring = add(new THREE.Mesh(new THREE.TorusGeometry(3.38, .06, 12, 160), glowMat("#ff4fa0", 3))); ring.rotation.x = Math.PI / 2; ring.position.y = .25;
  // haces de foco que barren + luces de color
  const COL = ["#ff4fa0", "#4de1ff", "#ffe14d", "#7dff6b"];
  const beams = COL.map((c, i) => { const b = add(shaft(c, .25, 2.6, 13, .28)); b.position.set(Math.cos(i * 1.57 + .7) * 6, 12.5, Math.sin(i * 1.57 + .7) * 4 - 2); return b; });
  const spots = COL.map((c, i) => { const s = add(new THREE.SpotLight(c, 60, 30, .38, .5)); s.position.set(Math.cos(i * 1.57) * 6, 10, Math.sin(i * 1.57) * 6); return s; });
  // globos (forma de gota) con cuerda
  const balloons = []; for (let i = 0; i < 14; i++) { const g = add(new THREE.Group()); const pts = []; for (let k = 0; k <= 24; k++) { const a = k / 24 * Math.PI; pts.push(new THREE.Vector2(Math.sin(a) * .45 * (1 - .25 * Math.cos(a) ** 3) * (k < 2 ? .3 : 1), -Math.cos(a) * .58)); }
    add(new THREE.Mesh(new THREE.LatheGeometry(pts, 48), phys(["#ff4fa0", "#4de1ff", "#ffe14d", "#b388ff", "#7dff6b", "#ff8a1f"][i % 6], { roughness: .15, clearcoat: 1 })), g);
    const str = add(new THREE.Mesh(new THREE.CylinderGeometry(.008, .008, 1.6, 6), std("#ffffff")), g); str.position.y = -1.4;
    const side = i % 2 ? 1 : -1; balloons.push({ g, x: side * (3.5 + R() * 4), z: -2 - R() * 6, y: 2.5 + R() * 3, ph: R() * 6 }); shadows(g, true, false); }
  // confeti redondo y serpentinas
  const NC = 320, conf = add(new THREE.InstancedMesh(new THREE.CircleGeometry(.06, 16), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }), NC));
  const cd = [...Array(NC)].map((_, i) => { conf.setColorAt(i, new THREE.Color(["#ff4fa0", "#ffe14d", "#4de1ff", "#7dff6b", "#ffffff", "#ff8a1f"][i % 6])); return { x: (R() - .5) * 14, z: (R() - .5) * 10, y: R() * 12, v: .8 + R() * 1.2, sp: R() * 8 }; });
  const M4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
  const qm = add(text3d("?", 1.5, phys("#ffe14d", { metalness: .4, roughness: .2, emissive: "#ff8a1f", emissiveIntensity: .3 }))); qm.position.set(0, 3.5, -1.6);
  const P = makePanda({ seed: 7.7 }); add(P.root); P.root.position.y = .5; add(contactShadow(1.1, .5)).position.y = .51;
  // capa de edición: resumen, comentarios y suscripción
  ["🐙", "🍯", "🪐", "⚡", "🐼"].forEach((em, i) => card({ t0: ev("recap") + .1 + i * .17, t1: 66.4, x: 330 + i * 155, y: 170, float: true,
    html: `<div style="text-align:center;width:90px"><div class="emo" style="font-size:62px">${em}</div><small>#${i + 1}</small></div>` }));
  card({ t0: ev("comment") - .1, t1: 71.8, html: "<span class='emo'>💬</span> ¡Cuéntamelo en los comentarios!", x: 640, y: 175 });
  let btn, cur, bell;
  sticker({ t0: ev("subscribe") - .15, t1: 71.8, x: 640, y: 300, float: false, cls: "",
    html: `<div style="position:relative"><div class="sb" style="font:400 56px 'Lucky',sans-serif;color:#fff;padding:18px 40px 10px;border-radius:18px;background:#ff1f3d;box-shadow:0 10px 0 #b3001b,0 18px 30px rgba(0,0,0,.4)">SUSCRÍBETE</div>
      <div class="bl emo" style="position:absolute;right:-110px;top:2px;font-size:76px">🔔</div><div class="cu emo" style="position:absolute;left:0;top:0;font-size:70px">👆</div></div>`,
    update: (el, t) => { btn = btn || el.querySelector(".sb"); cur = cur || el.querySelector(".cu"); bell = bell || el.querySelector(".bl");
      const click = .75, mv = ease(clamp((t - .15) / .55)), press = bump(t - click, .04, .2);
      cur.style.transform = `translate(${lerp(420, 210, mv)}px, ${lerp(260, 40, mv) + press * 10}px) scale(${1 - press * .15})`; cur.style.opacity = t > 2.2 ? "0" : "1";
      const done = t > click; btn.textContent = done ? "SUSCRITO ✔" : "SUSCRÍBETE"; btn.style.background = done ? "#6b6b7a" : "#ff1f3d"; btn.style.boxShadow = done ? "0 6px 0 #3d3d48,0 14px 26px rgba(0,0,0,.4)" : "0 10px 0 #b3001b,0 18px 30px rgba(0,0,0,.4)";
      btn.style.transform = `translateY(${press * 8}px) scale(${1 - press * .05})`;
      bell.style.transform = `rotate(${done ? Math.sin(t * 30) * 22 * Math.exp(-(t - click) * 2.5) : 0}deg) scale(${done ? 1 : .001})`; } });
  sticker({ t0: ev("subscribe") + 1.1, t1: 71.8, html: "👍", size: 110, x: 330, y: 300, cls: "emo" });

  return (t, T) => {
    const u = fx.material.uniforms; bloom.strength = .42; bloom.threshold = 1.0;
    const bp = beatPhase(T), hit = Math.exp(-bp.x * 4);
    beams.forEach((b, i) => { b.rotation.set(Math.sin(T * .9 + i * 1.3) * .5, 0, Math.cos(T * .7 + i) * .45); b.material.uniforms.a.value = .16 + hit * .14; });
    spots.forEach((s, i) => { const a = T * (.8 + i * .2) + i * 1.57; s.position.set(Math.cos(a) * 6, 10, Math.sin(a) * 6); s.intensity = 40 + hit * 45; });
    ring.material.emissiveIntensity = 1.8 + hit * 2.5;
    balloons.forEach(b => { b.g.position.set(b.x + Math.sin(T * .6 + b.ph) * .3, b.y + Math.sin(T * .9 + b.ph) * .35, b.z); b.g.rotation.z = Math.sin(T * .8 + b.ph) * .12; });
    for (let i = 0; i < NC; i++) { const d = cd[i], y = 12 - ((d.y + (T - 63) * d.v) % 12); q.setFromEuler(e.set(T * d.sp, T * d.sp * .7, d.sp));
      M4.compose(V(d.x + Math.sin(T * 1.5 + d.sp) * .4, y, d.z), q, V(1, 1, 1)); conf.setMatrixAt(i, M4); } conf.instanceMatrix.needsUpdate = true;
    qm.rotation.y = T * 1.6; qm.position.y = 3.5 + Math.sin(T * 2.5) * .2; qm.scale.setScalar(Math.max(.001, spring(T - ev("recap"), 10, 6)));
    // baile al ritmo (rebote en cada beat)
    const S = P.state; S.dance = Math.PI * DATA.bpm / 60; S.mood = "happy"; S.look.set(0, .2);
    if (T > ev("subscribe") + .6) { S.dance = 0; S.wave = 1; }
    posePanda(P, T); P.root.position.y = .5 + Math.abs(Math.sin(Math.PI * (bp.k + bp.x))) * .28; P.root.rotation.y = Math.sin(T * 1.4) * .5;
    P.body.rotation.z = Math.sin(Math.PI * (bp.k + bp.x)) * .1;
    // cámara en órbita lenta con empujón final
    const a = (T - 63.6) * .22 - .4, rad = lerp(8.5, 6.4, ease(clamp((T - 63.6) / 6)));
    cam.pos.set(Math.sin(a) * rad, lerp(2.6, 2.3, ease(clamp((T - 63.6) / 6))), Math.cos(a) * rad); cam.look.set(0, 2.0, 0);
    cam.fov = 40 - hit * .6 - bump(T - ev("subscribe") - .75, .03, .35) * 4; uiState.leak = bump(T - ev("recap"), .1, 1) * .35;
  };
}
