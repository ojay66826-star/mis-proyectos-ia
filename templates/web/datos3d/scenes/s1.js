// Escena 1 — El pulpo y sus 3 corazones (rayos X) · sangre azul.
import { THREE, scene, camera, add, shadows, phys, std, glowMat, glow, sky, points, shaft, bendTube, contactShadow, cam, ev, bloom, fx,
  clamp, lerp, ease, sm, spring, outBack, bump, rng } from "../core.js";
import { makePanda, posePanda } from "../panda.js";
import { sticker, card, uiState } from "../overlay.js";

const V = (x, y, z) => new THREE.Vector3(x, y, z), UP = V(0, 1, 0);
export function heart(size, mat) { const g = new THREE.Group();
  for (const s of [-1, 1]) { const b = add(new THREE.Mesh(new THREE.SphereGeometry(size * .55, 32, 24), mat), g); b.position.set(s * size * .42, size * .2, 0); }
  const c = add(new THREE.Mesh(new THREE.ConeGeometry(size * .82, size * 1.15, 32), mat), g); c.rotation.z = Math.PI; c.position.y = -size * .42; c.scale.z = .75;
  return g; }

export async function build() {
  const R = rng(17);
  sky("#8be8ff", "#1ba3c6", "#06536e");
  scene.fog = new THREE.FogExp2("#1689ab", .042); scene.environmentIntensity = .3;
  add(new THREE.HemisphereLight("#c9f6ff", "#0b5c73", .8));
  const key = add(new THREE.DirectionalLight("#effdff", 1.8)); key.position.set(2, 12, 4); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9 }); key.shadow.bias = -.0004; key.shadow.normalBias = .03;
  const fill = add(new THREE.PointLight("#ffd6a8", 18, 14, 1.5)); fill.position.set(2.5, 2.5, 4);
  // arena con dunas + cáusticas animadas encima
  const sand = add(new THREE.Mesh(new THREE.PlaneGeometry(90, 90, 120, 120), std("#d9bd84", { roughness: 1 }))); sand.rotation.x = -Math.PI / 2; sand.receiveShadow = true;
  const sp = sand.geometry.attributes.position; for (let i = 0; i < sp.count; i++) { const x = sp.getX(i), y = sp.getY(i); sp.setZ(i, Math.sin(x * .35) * .18 + Math.cos(y * .28 + x * .1) * .22); } sand.geometry.computeVertexNormals();
  const caus = add(new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uT: { value: 0 } }, vertexShader: "varying vec2 vP; void main(){ vP = position.xy; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
    fragmentShader: `uniform float uT; varying vec2 vP;
      float cst(vec2 uv, float t){ vec2 p = mod(uv * 6.2831, 6.2831) - 250.0; vec2 i = p; float c = 1.0; float k = .005;
        for (int n = 0; n < 4; n++) { float tt = t * (1.0 - (3.5 / float(n + 1))); i = p + vec2(cos(tt - i.x) + sin(tt + i.y), sin(tt - i.y) + cos(tt + i.x));
          c += 1.0 / length(vec2(p.x / (sin(i.x + tt) / k), p.y / (cos(i.y + tt) / k))); }
        c /= 4.0; c = 1.17 - pow(c, 1.4); return pow(abs(c), 8.0); }
      void main(){ float f = 1.0 - smoothstep(6.0, 19.0, length(vP)); gl_FragColor = vec4(vec3(.75, 1.0, .95) * cst(vP * .09, uT * .6) * .55 * f, 1.0); }` })));
  caus.rotation.x = -Math.PI / 2; caus.position.y = .25;
  const rays = [0, 1, 2, 3, 4, 5].map(i => { const s = add(shaft("#d9fbff", .5, 2.6 + i * .3, 18, .1)); s.position.set(-7 + i * 3 + R(), 16, -3 - R() * 5); s.rotation.z = .12; return s; });
  // rocas suaves, corales y algas
  for (let i = 0; i < 14; i++) { const g = new THREE.IcosahedronGeometry(.4 + R() * .7, 5), p = g.attributes.position;
    for (let k = 0; k < p.count; k++) { const v = V(p.getX(k), p.getY(k), p.getZ(k)); v.multiplyScalar(1 + Math.sin(v.x * 3 + i) * .08 + Math.cos(v.y * 4) * .06); p.setXYZ(k, v.x, v.y * .7, v.z); }
    g.computeVertexNormals(); const r = add(new THREE.Mesh(g, std(["#8295a8", "#6f7f93", "#9aa7b8"][i % 3], { roughness: .85 })));
    const a = R() * 6.28, d = 4 + R() * 9; r.position.set(Math.cos(a) * d, .1, -Math.abs(Math.sin(a)) * d + 1); shadows(r); }
  const corals = []; const CC = ["#ff6fa8", "#ff9e4f", "#b06bff", "#ffd24f", "#4fffd2"];
  for (let i = 0; i < 9; i++) { const g = add(new THREE.Group()); const col = CC[i % 5], m = phys(col, { roughness: .45, clearcoat: .3 });
    for (let b = 0; b < 7; b++) { const h = .5 + R() * .9; const c = add(new THREE.Mesh(new THREE.CapsuleGeometry(.07 + R() * .05, h, 8, 16), m), g);
      c.position.set((R() - .5) * .5, h / 2, (R() - .5) * .5); c.rotation.set((R() - .5) * .9, 0, (R() - .5) * .9);
      const tip = add(new THREE.Mesh(new THREE.SphereGeometry(.11, 20, 14), m), g); tip.position.copy(c.position).add(V(Math.sin(c.rotation.z) * -h / 2, h / 2, Math.sin(c.rotation.x) * h / 2)); }
    const side = i % 2 ? 1 : -1; g.position.set(side * (2.8 + R() * 5), 0, -1.5 - R() * 6); g.scale.setScalar(.8 + R() * .7); shadows(g); corals.push(g); }
  const weeds = []; for (let i = 0; i < 16; i++) { const L = 2 + R() * 3.5; const w = add(bendTube(L, .08, .02, 30, 10, std(["#2fae5c", "#58c24a", "#1e8a6b"][i % 3], { roughness: .6 })));
    const a = R() * 6.28, d = 3.5 + R() * 9; w.userData.base = V(Math.cos(a) * d, 0, -Math.abs(Math.sin(a)) * d - .5); w.userData.ph = R() * 6; w.castShadow = true; weeds.push(w); }
  // peces
  const fish = []; for (let i = 0; i < 7; i++) { const g = add(new THREE.Group()); const col = ["#ffd23f", "#ff6f3c", "#4dc9ff", "#ff5fa2"][i % 4];
    const b = add(new THREE.Mesh(new THREE.SphereGeometry(.26, 32, 20), phys(col)), g); b.scale.set(1, .62, .34);
    const tail = add(new THREE.Mesh(new THREE.ConeGeometry(.16, .26, 24), phys(col)), g); tail.rotation.z = Math.PI / 2; tail.position.x = -.3; tail.scale.z = .3;
    const e = add(new THREE.Mesh(new THREE.SphereGeometry(.05, 16, 12), phys("#111", { roughness: .1 })), g); e.position.set(.15, .05, .07);
    fish.push({ g, tail, r: 5 + R() * 6, y: 1.5 + R() * 3.5, s: (.25 + R() * .25) * (i % 2 ? 1 : -1), ph: R() * 6, z: -4 - R() * 5 }); shadows(g, true, false); }
  // burbujas (instancias redondas y brillantes)
  const NB = 90, bub = add(new THREE.InstancedMesh(new THREE.SphereGeometry(1, 20, 14), phys("#e8fdff", { transparent: true, opacity: .45, roughness: .05, clearcoat: 1 }), NB));
  const bd = [...Array(NB)].map(() => ({ x: (R() - .5) * 16, z: -R() * 10 + 2, s: .03 + R() * .07, v: .5 + R() * .9, ph: R() * 10 })); const M4 = new THREE.Matrix4();
  // ---------- el pulpo
  const oct = add(new THREE.Group()); const skinM = new THREE.MeshPhysicalMaterial({ color: "#ff7a59", roughness: .38, clearcoat: .55, clearcoatRoughness: .3, sheen: .4, sheenColor: new THREE.Color("#ffd0c0"), transparent: true, opacity: 1 });
  const prof = [V(0, 0, 0)]; for (let k = 0; k <= 32; k++) { const u = k / 32; prof.push(new THREE.Vector2(1.0 * Math.pow(Math.sin(Math.PI * (.14 + .86 * u)), .75) * (1 - .12 * u), .1 + u * 1.85)); }
  prof.push(new THREE.Vector2(0, 1.95));
  const mantle = add(new THREE.Mesh(new THREE.LatheGeometry(prof.map(p => new THREE.Vector2(p.x, p.y)), 64), skinM), oct); mantle.position.y = .55; mantle.castShadow = true;
  const eyes = [-1, 1].map(s => { const g = add(new THREE.Group(), oct); g.position.set(s * .42, 1.0, .78); g.rotation.y = s * .45;
    add(new THREE.Mesh(new THREE.SphereGeometry(.24, 32, 24), phys("#ffffff", { roughness: .1 })), g).scale.z = .6;
    const pu = add(new THREE.Mesh(new THREE.SphereGeometry(.14, 24, 16), phys("#141420", { roughness: .08 })), g); pu.position.z = .1; pu.scale.z = .5;
    const hl = add(new THREE.Mesh(new THREE.SphereGeometry(.045, 12, 8), new THREE.MeshBasicMaterial({ color: "#fff" })), g); hl.position.set(.05, .06, .17);
    return g; });
  const smile = add(new THREE.Mesh(new THREE.TorusGeometry(.12, .025, 8, 24, Math.PI), std("#7a1f2b")), oct); smile.rotation.z = Math.PI; smile.position.set(0, .82, .93);
  const heartM = [0, 1, 2].map(() => glowMat("#ff2d55", 2.2));
  const hearts = [[-.42, 1.0, .05, .17], [.42, 1.0, .05, .17], [0, 1.45, .05, .26]].map(([x, y, z, s], i) => { const h = add(heart(s, heartM[i]), oct); h.position.set(x, y, z); return h; });
  const tents = [...Array(8)].map((_, i) => ({ a: i / 8 * Math.PI * 2 + .2, m: add(bendTube(2.3, .15, .03, 44, 14, new THREE.MeshPhysicalMaterial({ color: "#ff8a66", roughness: .4, clearcoat: .5 })), oct) }));
  tents.forEach(o => { o.m.castShadow = true; o.samples = [...Array(45)].map(() => ({ p: V(0, 0, 0), n: V(0, 0, 0), b: V(0, 0, 0) })); });
  const blood = add(points(320, "#3d8bff", .13, () => [0, -50, 0]), oct);
  add(contactShadow(2.2, .4));
  // panda buzo
  const P = makePanda({ helmet: "diver", seed: 2.2 }); add(P.root); P.root.scale.setScalar(.72); P.root.position.set(-3.3, .3, -.2); P.root.rotation.y = .7;
  // capa de edición
  const hearts2D = [0, 1, 2].map(i => sticker({ t0: ev("xray") + .25 + i * .22, t1: 20.6, html: "❤️", size: 64, x: 0, y: 0, cls: "emo", float: false }));
  sticker({ t0: ev("xray") + .1, t1: 20.6, kind: "stamp", html: "RAYOS X", cls: "stamp", x: 1080, y: 170, rot: 6, float: false, update: el => { el.style.background = "linear-gradient(180deg,#2bd9ff,#1683ff)"; } });
  const lab1 = card({ t0: ev("gills") + .1, t1: 20.6, html: "2 × <b style='color:#ff2d55'>branquias</b> 🫧", x: 0, y: 0 });
  const lab2 = card({ t0: ev("third") + .05, t1: 20.6, html: "1 × <b style='color:#ff2d55'>cuerpo</b> 🐙", x: 0, y: 0 });
  sticker({ t0: ev("blue") - .02, t1: 23.5, kind: "stamp", html: "¡SANGRE AZUL!", cls: "stamp", x: 640, y: 300, rot: -5, float: false, update: el => { el.style.background = "linear-gradient(180deg,#4d9bff,#1d4fff)"; } });
  [0, 1, 2, 3].forEach(i => sticker({ t0: ev("blue") + .15 + i * .1, t1: 23.5, html: "💙", size: 70, x: 640 + Math.cos(i * 1.6 + .4) * 330, y: 300 + Math.sin(i * 1.6 + .4) * 150, cls: "emo" }));
  const tmp = V(0, 0, 0); const toScreen = (o, obj, dx = 0, dy = 0) => { obj.getWorldPosition(tmp); tmp.project(camera); o.x = (tmp.x * .5 + .5) * 1280 + dx; o.y = (-tmp.y * .5 + .5) * 720 + dy; };

  return (t, T) => {
    const u = fx.material.uniforms; bloom.strength = .38; bloom.threshold = 1.0;
    caus.material.uniforms.uT.value = T; rays.forEach((r, i) => { r.rotation.z = .12 + Math.sin(T * .4 + i) * .05; r.material.uniforms.a.value = .08 + .04 * Math.sin(T * .9 + i * 2); });
    weeds.forEach(w => { const b = w.userData.base, ph = w.userData.ph, L = w.userData.L;
      w.userData.bend(uu => { const sw = Math.sin(T * 1.2 + ph + uu * 2.2) * .5 * uu; const d = V(Math.sin(sw) * .9, Math.cos(sw), Math.sin(sw * .6) * .4).normalize();
        return { p: b.clone().add(V(Math.sin(T * 1.2 + ph) * .5 * uu * uu * L * .3, uu * L, Math.cos(T + ph) * .2 * uu * uu * L * .3)), n: V(d.y, -d.x, 0).normalize(), b: V(0, 0, 1) }; }); });
    fish.forEach(f => { const a = T * f.s + f.ph; f.g.position.set(Math.cos(a) * f.r, f.y + Math.sin(T * 1.3 + f.ph) * .3, f.z + Math.sin(a) * 2); f.g.rotation.y = -a + (f.s > 0 ? -Math.PI / 2 : Math.PI / 2); f.tail.rotation.y = Math.sin(T * 12 + f.ph) * .5; });
    for (let i = 0; i < NB; i++) { const b = bd[i], y = ((T * b.v + b.ph) % 9); M4.makeScale(b.s, b.s, b.s); M4.setPosition(b.x + Math.sin(T * 2 + b.ph) * .15, y, b.z); bub.setMatrixAt(i, M4); } bub.instanceMatrix.needsUpdate = true;
    // pulpo: sale de la arena, respira, rayos X y sangre azul
    const rv = spring(T - ev("octoReveal"), 9, 5); oct.position.set(.5, lerp(-3.6, .15, Math.min(1.08, rv)), .3); oct.rotation.y = Math.sin(T * .6) * .25;
    oct.scale.set(1.25 + Math.sin(T * 2.6) * .03, 1.25 - Math.sin(T * 2.6) * .03, 1.25);
    const xr = sm((T - ev("xray")) / .5) * (1 - sm((T - 20.3) / .5)) + sm((T - ev("blue")) / .3) * .85;
    skinM.opacity = 1 - xr * .68; skinM.depthWrite = xr < .2; skinM.color.set(xr > .02 ? "#ff9d83" : "#ff7a59");
    const isBlue = T > ev("blue");
    hearts.forEach((h, i) => { const beat = Math.pow(Math.max(0, Math.sin(T * 7.5 + i * 1.1)), 6); h.scale.setScalar((.4 + .6 * xr) * (1 + beat * .4) + .001);
      heartM[i].color.set(isBlue ? "#3d8bff" : "#ff2d55"); heartM[i].emissive.set(isBlue ? "#3d8bff" : "#ff2d55"); heartM[i].emissiveIntensity = (1.4 + beat * 2.5) * xr + .2;
      const g = i < 2 ? T > ev("gills") && T < ev("third") + .6 : T > ev("third"); h.children.forEach(c => c.material = heartM[i]); if (g) heartM[i].emissiveIntensity *= 1.6; });
    eyes.forEach((e, i) => { const bt = (T + i * .02) % 3.4; e.scale.y = bt < .15 ? Math.max(.1, 1 - Math.sin(bt / .15 * Math.PI)) : 1; });
    tents.forEach((o, i) => { const d = V(Math.cos(o.a), 0, Math.sin(o.a)), bn = d.clone().cross(UP).normalize(); let pos = V(Math.cos(o.a) * .55, .62, Math.sin(o.a) * .55);
      const L = 2.3, N = 44; for (let k = 0; k <= N; k++) { const uu = k / N, th = -.75 + 3.6 * uu * uu + Math.sin(T * 2.1 + i * 1.7 + uu * 4) * .35 * uu;
        const tv = d.clone().multiplyScalar(Math.cos(th)).addScaledVector(UP, Math.sin(th)); const s = o.samples[k];
        s.p.copy(pos); s.n.copy(d).multiplyScalar(-Math.sin(th)).addScaledVector(UP, Math.cos(th)); s.b.copy(bn); pos = pos.clone().addScaledVector(tv, L / N); }
      o.m.userData.bend(uu => o.samples[Math.min(N, Math.round(uu * N))]); });
    blood.userData.update = blood.userData.update; const bp = blood.geometry.attributes.position.array;
    for (let i = 0; i < 320; i++) { const tn = tents[i % 8], k = Math.floor(((T * .45 + i * .0137) % 1) * 44), s = tn.samples[k];
      if (isBlue) { bp[i * 3] = s.p.x; bp[i * 3 + 1] = s.p.y; bp[i * 3 + 2] = s.p.z; } else { bp[i * 3 + 1] = -50; } }
    blood.geometry.attributes.position.needsUpdate = true;
    // panda buzo flotando
    P.root.position.y = .45 + Math.sin(T * 1.4) * .12; P.state.mood = T > ev("xray") && T < 15 ? "surprised" : T > ev("blue") ? "surprised" : "happy";
    P.state.look.set(1, .2); posePanda(P, T);
    // cámara
    const a = ease(clamp((T - 13.2) / 6.5)), push = ease(clamp((T - ev("riser1")) / 2)), ang = lerp(-.55, .35, a);
    const rad = lerp(lerp(9.5, 7.4, ease(clamp((T - 11.3) / 1.8))), 4.9, push);
    cam.pos.set(Math.sin(ang) * rad - .9, lerp(2.6, 1.9, push), Math.cos(ang) * rad); cam.look.set(-.8, lerp(1.45, 1.5, push), 0);
    cam.fov = 38 - bump(T - ev("xray"), .05, .5) * 5 - bump(T - ev("blue"), .04, .6) * 8; cam.shake = push * (1 - sm((T - ev("blue")) / .2)) * .06 + bump(T - ev("blue"), .03, .4) * .5;
    u.uCA.value += bump(T - ev("blue"), .03, .5) * .03 + push * .004; u.uFlash.value = bump(T - ev("blue"), .02, .2) * .4; uiState.shake = bump(T - ev("blue"), .03, .4) * .5;
    // etiquetas pegadas a los corazones
    hearts2D.forEach((o, i) => toScreen(o, hearts[i], 0, -46)); toScreen(lab1, hearts[0], -170, 40); toScreen(lab2, hearts[2], 200, -60);
  };
}
