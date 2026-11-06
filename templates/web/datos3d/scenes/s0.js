// Escena 0 — Intro: plató de concurso, el Profe Bambú presenta y cae un «5» gigante.
import { THREE, scene, add, shadows, phys, std, glowMat, glow, sky, points, contactShadow, text3d, cam, ev, bloom, fx,
  clamp, lerp, ease, sm, spring, outBack, bump, rng, W, H } from "../core.js";
import { makePanda, posePanda } from "../panda.js";
import { sticker, card, uiState } from "../overlay.js";

export async function build() {
  const R = rng(5);
  sky("#24125e", "#a8378f", "#24125e");
  scene.fog = new THREE.Fog("#a8378f", 16, 48);
  scene.environmentIntensity = .38;
  add(new THREE.HemisphereLight("#ffe3f6", "#4a1f8a", .65));
  const key = add(new THREE.DirectionalLight("#fff1dc", 2.1)); key.position.set(4, 9, 7); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8 }); key.shadow.bias = -.0004; key.shadow.normalBias = .03;
  const rimA = add(new THREE.SpotLight("#4de1ff", 140, 30, .45, .6)); rimA.position.set(-7, 7, -5);
  const rimB = add(new THREE.SpotLight("#ff4f9a", 140, 30, .45, .6)); rimB.position.set(7, 7, -5);
  // suelo de espejo y escenario redondo
  const floor = add(new THREE.Mesh(new THREE.CircleGeometry(60, 96), phys("#3d2a9c", { roughness: .18, metalness: .2, clearcoat: 1 })));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
  const stageProf = [[0, 0], [3.6, 0], [3.75, .06], [3.8, .2], [3.75, .34], [3.6, .4], [0, .4]].map(([x, y]) => new THREE.Vector2(x, y));
  const stage = add(new THREE.Mesh(new THREE.LatheGeometry(stageProf, 96), phys("#ffc7e6", { roughness: .35, clearcoat: .8 }))); stage.receiveShadow = true;
  const ring = add(new THREE.Mesh(new THREE.TorusGeometry(3.78, .05, 12, 160), glowMat("#ffe14d", 3))); ring.rotation.x = Math.PI / 2; ring.position.y = .2;
  // arco de bombillas
  const arch = add(new THREE.Group()); arch.position.set(0, 0, -3.2);
  add(new THREE.Mesh(new THREE.TorusGeometry(4.4, .32, 32, 120, Math.PI), phys("#ff4f9a", { roughness: .25 })), arch);
  const bulbs = []; for (let i = 0; i <= 26; i++) { const a = i / 26 * Math.PI;
    const b = add(new THREE.Mesh(new THREE.SphereGeometry(.11, 20, 14), glowMat("#fff3b0", 1.6)), arch); b.position.set(Math.cos(a) * 4.4, Math.sin(a) * 4.4, .3); bulbs.push(b); }
  // disco de rayos detrás del «5»
  const c = document.createElement("canvas"); c.width = c.height = 512; const x = c.getContext("2d");
  for (let i = 0; i < 24; i++) { x.fillStyle = i % 2 ? "#3dd6ff" : "#2a7bff"; x.beginPath(); x.moveTo(256, 256); x.arc(256, 256, 256, i / 24 * 6.283, (i + 1) / 24 * 6.283); x.fill(); }
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const burst = add(new THREE.Mesh(new THREE.CircleGeometry(3.2, 96), new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: .95, fog: false })));
  burst.position.set(1.4, 3.2, -2.6);
  // «5» de oro y signos «?» de caramelo orbitando
  const five = add(text3d("5", 2.3, phys("#ffc21a", { metalness: .55, roughness: .2, emissive: "#ff7a00", emissiveIntensity: .25 })));
  const qs = [0, 1, 2, 3, 4].map(i => add(text3d("?", .7, phys(["#4de1ff", "#ff4f9a", "#7dff6b", "#ffe14d", "#b388ff"][i], { roughness: .15 }))));
  // formas flotantes
  const toys = []; const geos = [new THREE.SphereGeometry(.35, 32, 24), new THREE.TorusGeometry(.32, .13, 20, 48), new THREE.CapsuleGeometry(.18, .4, 10, 20), new THREE.IcosahedronGeometry(.34, 4)];
  for (let i = 0; i < 18; i++) { const m = add(new THREE.Mesh(geos[i % 4], phys(["#4de1ff", "#ff4f9a", "#ffe14d", "#7dff6b", "#b388ff", "#ff8a1f"][i % 6], { roughness: .2 })));
    const a = R() * 6.28, r = 5 + R() * 9; toys.push({ m, x: Math.cos(a) * r, z: -Math.abs(Math.sin(a)) * r - 2, y: 1 + R() * 5, ph: R() * 6, s: .6 + R() * .8 }); shadows(m, true, false); }
  // panda
  const P = makePanda({ seed: 1.3 }); add(P.root); P.root.position.set(-1.7, .4, .4); P.root.rotation.y = .35;
  add(contactShadow(1.1, .5)).position.set(-1.7, .42, .4);
  // confeti redondo (discos) que estalla con el título
  const conf = new THREE.InstancedMesh(new THREE.CircleGeometry(.07, 16), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }), 260);
  const cols = ["#ff4f9a", "#ffe14d", "#4de1ff", "#7dff6b", "#ff8a1f", "#ffffff"]; const cd = [];
  for (let i = 0; i < 260; i++) { conf.setColorAt(i, new THREE.Color(cols[i % 6])); cd.push({ a: R() * 6.28, v: 3 + R() * 6, up: 5 + R() * 6, sp: R() * 10, ph: R() * 6 }); }
  add(conf); const M4 = new THREE.Matrix4(), q4 = new THREE.Quaternion(), e3 = new THREE.Euler();
  const sparks = add(points(160, "#fff6c8", .16, (i, T) => { const k = i / 160, a = k * 40, t = (T * .5 + k) % 1; return [Math.cos(a) * (2 + t * 6), .5 + t * 6, Math.sin(a) * (2 + t * 6) - 3]; }, { opacity: .7 }));

  // capa de edición
  const tS = ev("titleSlam");
  sticker({ t0: ev("heartsTeaser") - .1, t1: 3.4, html: "🐙", size: 120, x: 1010, y: 300, cls: "emo" });
  [0, 1, 2].forEach(i => sticker({ t0: ev("heartsTeaser") + .1 + i * .16, t1: 3.4, html: "❤️", size: 58, x: 1010 + Math.cos(i * 2.1 - 1) * 120, y: 300 + Math.sin(i * 2.1 - 1) * 95, cls: "emo" }));
  sticker({ t0: ev("planetTeaser") - .1, t1: 6.2, kind: "fly", from: [1500, 40], spin: -160, html: "🪐", size: 130, x: 1000, y: 280, cls: "emo" });
  card({ t0: ev("dayYearTeaser") + .3, t1: 6.2, html: "☀️ 1 día &gt; 1 año 🤔", x: 1000, y: 455 });
  sticker({ t0: tS + .15, t1: 11.5, kind: "stamp", html: "DATOS CURIOSOS", cls: "stamp", x: 790, y: 470, rot: -4, float: false,
    update: el => { el.style.background = "linear-gradient(180deg,#ff4f9a,#d9257a)"; } });
  sticker({ t0: ev("mindBlown") + .05, t1: 11.5, html: "🤯", size: 150, x: 230, y: 230, cls: "emo" });

  return (t, T) => {
    const u = fx.material.uniforms; bloom.strength = .38; bloom.threshold = 1.0;
    toys.forEach(o => { o.m.position.set(o.x + Math.sin(T * .5 * o.s + o.ph) * .4, o.y + Math.sin(T * o.s + o.ph) * .35, o.z); o.m.rotation.set(T * .4 * o.s, T * .6 * o.s + o.ph, 0); });
    bulbs.forEach((b, i) => { b.material.emissiveIntensity = 1.0 + 1.8 * (Math.sin(T * 8 - i * .7) > .2 ? 1 : 0); });
    rimA.intensity = 110 + 60 * Math.sin(T * 2); rimB.intensity = 110 + 60 * Math.sin(T * 2 + 2);
    // «5»: cae con rebote al decir «cinco»
    const k = spring(T - tS, 10, 5.2); five.position.set(1.4, lerp(10, 3.15, Math.min(1.15, k)), -1.2); five.rotation.y = Math.sin(T * 1.4) * .45; five.visible = T > tS - .4;
    burst.scale.setScalar(Math.max(.001, spring(T - tS - .05, 9, 6))); burst.rotation.z = -T * .35;
    qs.forEach((m, i) => { const a = T * .7 + i * 1.256; m.position.set(1.4 + Math.cos(a) * 3, 2.6 + Math.sin(T * 1.6 + i) * .45, -1.2 + Math.sin(a) * 2); m.rotation.y = -a + T; m.visible = T > tS; m.scale.setScalar(spring(T - tS - .2 - i * .06)); });
    // panda: saluda, se asombra, salta con el título
    const S = P.state; S.wave = T > .3 && T < 1.7 ? 1 : 0; S.mood = T > 1.6 && T < 3.2 ? "surprised" : "happy";
    const jt = T - tS + .15, jump = jt > 0 && jt < .55 ? Math.sin(jt / .55 * Math.PI) : 0, squash = bump(jt - .55, .04, .25);
    P.root.position.y = .4 + jump * .9; P.root.scale.set(1 + squash * .12, 1 - squash * .14 + jump * .06, 1 + squash * .12);
    if (jt > 0 && jt < 1.2) { S.armL = [0, -2.6]; S.armR = [0, 2.6]; } else { S.armL = S.armR = null; }
    S.look.set(T > tS ? .8 : 0, T > tS ? .5 : 0); posePanda(P, T);
    // confeti
    for (let i = 0; i < cd.length; i++) { const d = cd[i], tt = T - tS - .05;
      if (tt < 0) { M4.makeScale(0, 0, 0); conf.setMatrixAt(i, M4); continue; }
      const r = d.v * (1 - Math.exp(-tt * 2.2)), y = 3 + d.up * (1 - Math.exp(-tt * 2.5)) - tt * tt * 1.3;
      e3.set(tt * d.sp + d.ph, tt * d.sp * .7, d.ph); q4.setFromEuler(e3);
      M4.compose(new THREE.Vector3(1.4 + Math.cos(d.a) * r, Math.max(.05, y), -1 + Math.sin(d.a) * r * .6), q4, new THREE.Vector3(1, 1, 1)); conf.setMatrixAt(i, M4); }
    conf.instanceMatrix.needsUpdate = true; sparks.userData.update(T);
    // cámara: primer plano → plano general → órbita
    const a1 = ease(clamp((T - 2.4) / 4.6)), a2 = ease(clamp((T - 7.4) / 4));
    const ang = lerp(-.12, .22, a2), rad = lerp(lerp(4.3, 8.6, a1), 9.2, a2);
    const cx = lerp(-1.25, .4, a1), cy = lerp(2.35, 2.9, a1);
    cam.pos.set(cx + Math.sin(ang) * rad * .4, cy, Math.cos(ang) * rad + .4); cam.look.set(lerp(-1.65, .2, a1), lerp(2.05, 2.1, a1), 0);
    cam.fov = 36 - bump(T - tS, .05, .5) * 6 - bump(T - ev("mindBlown"), .05, .4) * 4;
    cam.shake = bump(T - tS - .05, .03, .5) * .6;
    u.uCA.value += bump(T - tS, .04, .4) * .02; u.uFlash.value = bump(T - tS, .02, .18) * .35;
    uiState.shake = bump(T - tS, .03, .4) * .6;
  };
}
