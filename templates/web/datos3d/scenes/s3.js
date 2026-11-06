// Escena 3 — Venus: un día (243 días terrestres) dura más que un año (225).
import { THREE, scene, add, shadows, phys, std, glowMat, glow, points, cam, ev, bloom, fx, clamp, lerp, ease, sm, spring, bump, rng } from "../core.js";
import { makePanda, posePanda } from "../panda.js";
import { sticker, card, uiState } from "../overlay.js";

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const NOISE = `float h3(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
  float n3(vec3 p){ vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(h3(i), h3(i + vec3(1,0,0)), f.x), mix(h3(i + vec3(0,1,0)), h3(i + vec3(1,1,0)), f.x), f.y),
               mix(mix(h3(i + vec3(0,0,1)), h3(i + vec3(1,0,1)), f.x), mix(h3(i + vec3(0,1,1)), h3(i + vec3(1,1,1)), f.x), f.y), f.z); }
  float fbm(vec3 p){ float v = 0.0, a = .5; for (int i = 0; i < 4; i++) { v += a * n3(p); p *= 2.03; a *= .5; } return v; }`;

export async function build() {
  const R = rng(31);
  // nebulosa de colores + estrellas
  const neb = add(new THREE.Mesh(new THREE.SphereGeometry(500, 48, 24), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { uT: { value: 0 } }, vertexShader: "varying vec3 vD; void main(){ vD = normalize(position); vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.0); gl_Position = p.xyww; }",
    fragmentShader: `uniform float uT; varying vec3 vD; ${NOISE}
      void main(){ vec3 d = vD; float n = fbm(d * 2.2 + vec3(uT * .01)), m = fbm(d * 4.0 - 3.0);
        vec3 c = mix(vec3(.03, .02, .09), vec3(.35, .08, .45), smoothstep(.35, .75, n)); c = mix(c, vec3(.05, .38, .55), smoothstep(.5, .85, m) * .7);
        c += vec3(.9, .35, .55) * pow(smoothstep(.55, .9, n * m * 1.6), 2.0) * .6;
        vec3 q = floor(d * 300.0); float s = h3(q); c += vec3(step(.9972, s)) * (.6 + .6 * h3(q + 2.0)); gl_FragColor = vec4(c, 1.0); }` })));
  neb.renderOrder = -10; neb.frustumCulled = false;
  add(new THREE.AmbientLight("#8a7bd6", .55)); scene.environmentIntensity = .35;
  // Sol con granulación animada y corona
  const sunM = new THREE.ShaderMaterial({ uniforms: { uT: { value: 0 } },
    vertexShader: "varying vec3 vP, vN, vV; void main(){ vP = position; vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position, 1.0); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }",
    fragmentShader: `uniform float uT; varying vec3 vP, vN, vV; ${NOISE}
      void main(){ float n = fbm(vP * 1.6 + vec3(uT * .25, -uT * .18, uT * .1)); float rim = pow(1.0 - max(dot(vN, vV), 0.0), 2.0);
        vec3 c = mix(vec3(1.7, .62, .1), vec3(2.4, 1.5, .45), n) + vec3(1.2, .4, .05) * rim; gl_FragColor = vec4(c, 1.0); }` });
  const sun = add(new THREE.Mesh(new THREE.SphereGeometry(2.4, 64, 48), sunM));
  const cor = [add(glow("#ffb347", 9.5, .5)), add(glow("#ff6a1f", 15, .3)), add(glow("#fff2c0", 6, .6))];
  const sunL = add(new THREE.PointLight("#fff2dc", 520, 0, 1.2));
  // órbita, Venus con nubes y atmósfera, baliza que delata su giro
  const ORB = 7.2; const ring = add(new THREE.Mesh(new THREE.TorusGeometry(ORB, .03, 8, 256), glowMat("#ffe08a", 1.6))); ring.rotation.x = Math.PI / 2;
  const trail = add(new THREE.Mesh(new THREE.TorusGeometry(ORB, .09, 10, 256, .01), glowMat("#4de1ff", 2.4))); trail.rotation.x = Math.PI / 2;
  const c = document.createElement("canvas"); c.width = 1024; c.height = 512; const x = c.getContext("2d");
  const gr = x.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, "#f3d9a0"); gr.addColorStop(.5, "#e8b36a"); gr.addColorStop(1, "#f0d29a"); x.fillStyle = gr; x.fillRect(0, 0, 1024, 512);
  for (let i = 0; i < 900; i++) { const y = R() * 512, w = 60 + R() * 260; x.strokeStyle = `rgba(${R() > .5 ? "255,246,220" : "196,128,62"},${.1 + R() * .18})`; x.lineWidth = 4 + R() * 14;
    x.beginPath(); x.moveTo(R() * 1024, y); x.bezierCurveTo(R() * 1024, y + (R() - .5) * 60, R() * 1024, y + (R() - .5) * 60, R() * 1024 + w, y + (R() - .5) * 40); x.stroke(); }
  const vt = new THREE.CanvasTexture(c); vt.colorSpace = THREE.SRGBColorSpace; vt.wrapS = THREE.RepeatWrapping;
  const venus = add(new THREE.Group()); const vball = add(new THREE.Mesh(new THREE.SphereGeometry(1.25, 64, 48), std("#ffffff", { map: vt, roughness: .85 })), venus); vball.castShadow = true;
  const atm = add(new THREE.Mesh(new THREE.SphereGeometry(1.42, 64, 48), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.BackSide,
    vertexShader: "varying vec3 vN, vV; void main(){ vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position, 1.0); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }",
    fragmentShader: "varying vec3 vN, vV; void main(){ float f = pow(1.0 - abs(dot(vN, vV)), 3.0); gl_FragColor = vec4(vec3(1.0, .78, .45) * f * 1.6, 1.0); }" })), venus);
  const pin = add(new THREE.Group(), vball); pin.position.set(0, 0, 1.24); pin.lookAt(0, 0, 3);
  add(new THREE.Mesh(new THREE.CylinderGeometry(.025, .025, .5, 12), phys("#ffffff")), pin).rotation.x = Math.PI / 2;
  const flag = add(new THREE.Mesh(new THREE.SphereGeometry(.12, 24, 16), glowMat("#4de1ff", 2.5)), pin); flag.position.z = .3;
  // asteroides redondeados en primer plano
  const rocks = []; for (let i = 0; i < 16; i++) { const g = new THREE.IcosahedronGeometry(.2 + R() * .5, 4), p = g.attributes.position;
    for (let k = 0; k < p.count; k++) { const v = V(p.getX(k), p.getY(k), p.getZ(k)); v.multiplyScalar(1 + Math.sin(v.x * 5 + i) * .1); p.setXYZ(k, v.x, v.y, v.z); } g.computeVertexNormals();
    const m = add(new THREE.Mesh(g, std("#8d7f9c", { roughness: .9 }))); rocks.push({ m, p: V((R() - .5) * 26, (R() - .5) * 10, (R() - .5) * 18), s: R() * 2 }); }
  const dust = add(points(500, "#cfd8ff", .08, (i, T) => { const a = i * 2.4 + T * .02, r = 4 + (i % 50) * .25; return [Math.cos(a) * r, Math.sin(i * 7.7) * .3, Math.sin(a) * r]; }, { opacity: .5 }));
  // panda astronauta
  const P = makePanda({ helmet: "space", seed: 4.2 }); add(P.root); P.root.scale.setScalar(.55);
  // capa de edición: marcador «día contra año»
  sticker({ t0: ev("venus") - .05, t1: 38.2, kind: "stamp", html: "VENUS", cls: "stamp", x: 1030, y: 170, rot: 5, float: false, update: el => { el.style.background = "linear-gradient(180deg,#ffb347,#e0761f)"; } });
  card({ t0: ev("dayGtYear") + .1, t1: 38.3, html: "1 DÍA <span style='color:#ff4f9a'>&gt;</span> 1 AÑO <span class='emo'>🤯</span>", x: 1030, y: 290 });
  let dEl, yEl, dNum, yNum, yOk;
  card({ t0: ev("day243") - .1, t1: 46.5, x: 1000, y: 395, float: false,
    html: `<div style="width:400px"><div>🔄 1 día en Venus <b class="dn" style="float:right;color:#ff4f9a">0</b></div><div class="bar"><b class="db" style="width:0;background:linear-gradient(90deg,#ff4f9a,#ff9ac6)"></b></div>
      <div class="yr" style="margin-top:14px;opacity:0">☀️ 1 año en Venus <b class="yn" style="float:right;color:#1aa3ff">0</b></div><div class="bar yr" style="opacity:0"><b class="yb" style="width:0;background:linear-gradient(90deg,#1aa3ff,#7de3ff)"></b></div>
      <small style="margin-top:8px">días terrestres <span class="ok" style="opacity:0;color:#1f9e44">· ¡el año termina primero! ✅</span></small></div>`,
    update: (el, t, T) => { if (!dEl) { dEl = el.querySelector(".db"); yEl = el.querySelector(".yb"); dNum = el.querySelector(".dn"); yNum = el.querySelector(".yn"); yOk = el.querySelector(".ok"); }
      const D = 243 * clamp((T - 38.6) / 6.2); dEl.style.width = (D / 243 * 100).toFixed(1) + "%"; dNum.textContent = Math.round(D);
      const yv = T > ev("year225") - .1 ? 1 : 0; el.querySelectorAll(".yr").forEach(e => e.style.opacity = String(yv)); yEl.style.width = (Math.min(1, D / 225) * 100).toFixed(1) + "%";
      yNum.textContent = Math.round(Math.min(225, D)); yOk.style.opacity = D >= 225 ? "1" : "0"; } });

  return (t, T) => {
    const u = fx.material.uniforms; bloom.strength = .42; bloom.threshold = 1.0; neb.material.uniforms.uT.value = T; sunM.uniforms.uT.value = T;
    cor.forEach((g, i) => { g.material.opacity = [.5, .3, .6][i] * (.9 + .1 * Math.sin(T * 2 + i)); g.material.rotation = T * .05 * (i + 1); });
    const D = 243 * clamp((T - 38.6) / 6.2), ang = -.7 + Math.PI * 2 * D / 225 + (T - 34) * .02;
    venus.position.set(Math.cos(ang) * ORB, 0, Math.sin(ang) * ORB); vball.rotation.y = -Math.PI * 2 * D / 243 * .999 + .6; vt.offset.x = T * .004;
    trail.geometry.dispose(); trail.geometry = new THREE.TorusGeometry(ORB, .09, 10, 256, Math.max(.01, ang + .7)); trail.rotation.set(Math.PI / 2, 0, -.7);
    flag.material.emissiveIntensity = 2 + Math.sin(T * 6) * 1.2;
    rocks.forEach((r, i) => { r.m.position.copy(r.p).add(V(Math.sin(T * .2 + i) * .6, Math.cos(T * .25 + i) * .4, 0)); r.m.rotation.set(T * .2 + r.s, T * .3 + r.s, 0); });
    dust.userData.update(T);
    const cp = cam.pos;
    P.root.rotation.set(Math.sin(T * .7) * .15, -1.0 + Math.sin(T * .4) * .3, Math.sin(T * .9) * .2);
    P.state.mood = T > ev("dayGtYear") && T < 38 ? "surprised" : T > 44.3 ? "dizzy" : "happy"; P.state.look.set(-1, 0); posePanda(P, T); void cp;
    // cámara: destello del Sol → Venus de cerca → vista de la órbita completa
    const a1 = ease(clamp((T - 34) / 1.6)), a2 = ease(clamp((T - 38.2) / 2.6));
    const vp = venus.position, close = V(vp.x * 1.42 + 1.5, 1.3, vp.z * 1.42 + 2.2), wide = V(2.5, 7.5, 15.5);
    const start = V(-1.5, .8, 7.5); const p1 = start.clone().lerp(close, a1), p2 = p1.clone().lerp(wide, a2);
    cam.pos.copy(p2); cam.look.copy(V(0, 0, 0).lerp(vp, a1).lerp(V(0, -.5, 0), a2)); cam.fov = 40 - bump(T - ev("venus"), .05, .5) * 6 - bump(T - ev("year225"), .05, .4) * 3;
    const fw = cam.look.clone().sub(cam.pos).normalize(), rt = fw.clone().cross(V(0, 1, 0)).normalize(), up = rt.clone().cross(fw);
    P.root.position.copy(cam.pos).addScaledVector(fw, 5.6).addScaledVector(rt, -2.5).addScaledVector(up, -.9 + Math.sin(T * 1.1) * .12);
    u.uCA.value += .002; uiState.leak = bump(T - 34.1, .1, 1.2) * .5;
  };
}
