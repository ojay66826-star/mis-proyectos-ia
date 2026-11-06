// Profe Bambú: panda 3D de formas suaves con boca sincronizada a la voz, parpadeo, cejas y accesorios.
import { THREE, add, shadows, phys, std, clamp, lerp, envAt, wobble } from "./core.js";

const WHITE = () => new THREE.MeshPhysicalMaterial({ color: "#e9e4dc", roughness: .62, sheen: .5, sheenColor: new THREE.Color("#fff6ea"), sheenRoughness: .6 });
const BLACK = () => new THREE.MeshPhysicalMaterial({ color: "#1b1a21", roughness: .5, sheen: .3, sheenColor: new THREE.Color("#45455a"), sheenRoughness: .5 });
const GLOSS = () => phys("#0c0c12", { roughness: .12, clearcoat: 1 });
const sph = (r, m, ws = 48, hs = 32) => new THREE.Mesh(new THREE.SphereGeometry(r, ws, hs), m);

export function makePanda(opts = {}) {
  const P = { root: new THREE.Group(), opts };
  const white = WHITE(), black = BLACK(), gloss = GLOSS();
  const body = add(new THREE.Group(), P.root); P.body = body;
  // cuerpo en forma de pera (torno) + franja negra de hombros
  const prof = []; for (let k = 0; k <= 28; k++) { const u = k / 28; prof.push(new THREE.Vector2(.64 * Math.pow(Math.sin(Math.PI * (.04 + u * .96)), .7) * (1 - .3 * u), u * 1.2)); }
  prof.unshift(new THREE.Vector2(0, 0)); prof.push(new THREE.Vector2(0, 1.2));
  add(new THREE.Mesh(new THREE.LatheGeometry(prof, 64), white), body).position.y = .05;
  const band = add(new THREE.Mesh(new THREE.TorusGeometry(.4, .17, 24, 64), black), body); band.rotation.x = Math.PI / 2; band.position.y = 1.0; band.scale.set(1, 1, .75);
  const tail = add(sph(.1, white), body); tail.position.set(0, .3, -.55);
  // cabeza
  const head = add(new THREE.Group(), body); head.position.y = 1.66; P.head = head;
  const HS = new THREE.Vector3(.66, .57, .6);
  add(sph(1, white, 64, 48), head).scale.copy(HS);
  const onHead = (x, y, z, out = 0) => { const d = new THREE.Vector3(x, y, z).normalize(); return d.multiply(HS).multiplyScalar(1 + out); };
  const face = (m, x, y, z, out = 0) => { m.position.copy(onHead(x, y, z, out)); m.lookAt(m.position.clone().multiplyScalar(2)); return m; };
  for (const s of [-1, 1]) {
    const ear = add(sph(.2, black), head); ear.position.copy(onHead(s * .62, .74, -.12)); ear.scale.set(1, 1, .7);
    const patch = add(face(sph(.17, black), s * .36, .06, .93, -.06), head); patch.scale.set(.82, 1.18, .42); patch.rotateZ(s * .5);
  }
  P.eyes = [-1, 1].map(s => {
    const g = add(face(new THREE.Group(), s * .35, .08, .93, .04), head);
    const scl = add(sph(.088, phys("#ffffff", { roughness: .15 })), g); scl.scale.z = .55;
    const iris = add(sph(.064, phys("#3b2414", { roughness: .2 })), g); iris.position.z = .036; iris.scale.z = .5;
    const pup = add(sph(.042, gloss), g); pup.position.z = .05; pup.scale.z = .45;
    const h1 = add(sph(.019, new THREE.MeshBasicMaterial({ color: "#fff" })), g); h1.position.set(.022, .026, .07);
    const h2 = add(sph(.009, new THREE.MeshBasicMaterial({ color: "#fff" })), g); h2.position.set(-.02, -.018, .07);
    return { g, iris, pup };
  });
  P.brows = [-1, 1].map(s => { const b = add(new THREE.Mesh(new THREE.CapsuleGeometry(.022, .1, 6, 12), black), head);
    b.position.copy(onHead(s * .36, .36, .86, .02)); b.rotation.z = Math.PI / 2 + s * .12; b.userData.base = b.position.clone(); b.userData.s = s; return b; });
  const muz = add(face(sph(.25, white), 0, -.34, .94, -.12), head); muz.scale.set(1.05, .72, .62);
  const nose = add(face(sph(.075, gloss), 0, -.2, .98, .1), head); nose.scale.set(1.3, .78, .8);
  const mouth = add(new THREE.Group(), head); mouth.position.copy(onHead(0, -.46, .89, .04)); mouth.lookAt(mouth.position.clone().multiplyScalar(2)); P.mouth = mouth;
  P.mouthIn = add(sph(.075, std("#5c1424", { roughness: .7 })), mouth); P.mouthIn.scale.set(1.2, .2, .35);
  P.tongue = add(sph(.045, std("#ff7a8a")), mouth); P.tongue.position.set(0, -.02, .012); P.tongue.scale.set(1.1, .5, .4);
  P.smile = add(new THREE.Mesh(new THREE.TorusGeometry(.07, .011, 8, 32, Math.PI), black), mouth); P.smile.rotation.z = Math.PI; P.smile.position.y = .035;
  for (const s of [-1, 1]) { const c = add(face(sph(.075, new THREE.MeshStandardMaterial({ color: "#ff8fa8", transparent: true, opacity: .55, roughness: .9 })), s * .64, -.26, .72, -.02), head); c.scale.z = .3; }
  // brazos (pivote en el hombro) y piernas
  P.arms = [-1, 1].map(s => { const sh = add(new THREE.Group(), body); sh.position.set(s * .5, 1.02, .04);
    const a = add(new THREE.Mesh(new THREE.CapsuleGeometry(.14, .4, 10, 24), black), sh); a.position.y = -.27;
    const paw = add(sph(.155, black), sh); paw.position.y = -.55; const pad = add(sph(.065, std("#ff9fb5")), sh); pad.position.set(0, -.57, .13); pad.scale.z = .4;
    sh.userData.s = s; return sh; });
  P.legs = [-1, 1].map(s => { const l = add(new THREE.Group(), P.root); l.position.set(s * .29, .22, .1);
    add(new THREE.Mesh(new THREE.CapsuleGeometry(.18, .16, 10, 24), black), l);
    const pad = add(sph(.09, std("#ff9fb5")), l); pad.position.set(0, -.12, .16); pad.scale.set(1, .5, .4); return l; });
  // accesorios
  if (opts.glasses !== false) for (const s of [-1, 1]) {
    const fr = add(face(new THREE.Mesh(new THREE.TorusGeometry(.125, .017, 12, 48), phys("#ff8a1f", { metalness: .4, roughness: .25 })), s * .35, .08, .93, .1), head);
    const br = add(new THREE.Mesh(new THREE.CapsuleGeometry(.012, .1, 4, 8), phys("#ff8a1f", { metalness: .4 })), head); br.rotation.z = Math.PI / 2; br.position.copy(onHead(0, .1, 1, .1));
    void fr;
  }
  if (opts.bow !== false) { const bow = add(new THREE.Group(), body); bow.position.set(0, 1.2, .43);
    const m = phys("#ff3d6e"); for (const s of [-1, 1]) { const w = add(new THREE.Mesh(new THREE.ConeGeometry(.1, .2, 24), m), bow); w.rotation.z = s * Math.PI / 2; w.position.x = s * .1; w.scale.z = .5; }
    add(sph(.05, m), bow); }
  if (opts.helmet) { const hm = add(sph(.86, new THREE.MeshPhysicalMaterial({ color: "#e8fbff", transparent: true, opacity: .16, roughness: .04, clearcoat: 1, depthWrite: false })), head);
    hm.position.y = .02; const rim = add(new THREE.Mesh(new THREE.TorusGeometry(.5, .07, 16, 64), phys(opts.helmet === "space" ? "#f2f2f2" : "#ffb300", { metalness: .5 })), body);
    rim.rotation.x = Math.PI / 2; rim.position.y = 1.25; }
  if (opts.hat) { const hat = add(new THREE.Group(), head); hat.position.y = .42; hat.rotation.x = -.12;
    const dome = []; for (let k = 0; k <= 16; k++) { const a = k / 16 * Math.PI / 2; dome.push(new THREE.Vector2(Math.cos(a) * .5, Math.sin(a) * .36)); }
    add(new THREE.Mesh(new THREE.LatheGeometry(dome, 48), std("#d9b77a", { roughness: .8 })), hat);
    const brim = add(new THREE.Mesh(new THREE.TorusGeometry(.62, .05, 12, 64), std("#cfa866", { roughness: .8 })), hat); brim.rotation.x = Math.PI / 2; brim.scale.z = .5;
    add(new THREE.Mesh(new THREE.CylinderGeometry(.62, .62, .03, 64), std("#cfa866", { roughness: .8 })), hat);
    const bd = add(new THREE.Mesh(new THREE.TorusGeometry(.49, .035, 10, 64), std("#6d4c41")), hat); bd.rotation.x = Math.PI / 2; bd.position.y = .05; }
  if (opts.umbrella) { const u = add(new THREE.Group(), P.arms[1]); u.position.set(0, -.55, .05); P.umbrella = u;
    const st = add(new THREE.Mesh(new THREE.CylinderGeometry(.025, .025, 2.1, 12), phys("#333")), u); st.position.y = 1.0;
    const can = []; for (let k = 0; k <= 20; k++) { const a = k / 20 * Math.PI / 2; can.push(new THREE.Vector2(Math.sin(a) * 1.15, Math.cos(a) * .55)); }
    const cg = new THREE.LatheGeometry(can, 64); const cols = []; const pa = cg.attributes.position;
    for (let i = 0; i < pa.count; i++) { const ang = Math.atan2(pa.getZ(i), pa.getX(i)); const seg = Math.floor(((ang + Math.PI) / (Math.PI * 2)) * 8) % 2;
      const c = new THREE.Color(seg ? "#ffd23f" : "#ff3d6e"); cols.push(c.r, c.g, c.b); }
    cg.setAttribute("color", new THREE.Float32BufferAttribute(cols, 3));
    const cm = add(new THREE.Mesh(cg, phys("#ffffff", { vertexColors: true, side: THREE.DoubleSide })), u); cm.position.y = 1.55;
    const tip = add(sph(.05, phys("#333")), u); tip.position.y = 2.12; }
  shadows(P.root, true, false);
  P.state = { talk: 1, mood: "happy", wave: 0, dance: 0, look: new THREE.Vector2(0, 0), blinkSeed: opts.seed || 0, armL: null, armR: null };
  return P;
}

// pose por frame: respiración, parpadeo, labios con la voz, gestos y expresiones
export function posePanda(P, T) {
  const S = P.state, v = clamp(envAt(T) * S.talk, 0, 1.2);
  P.body.scale.set(1 + Math.sin(T * 2.4) * .012, 1 + Math.sin(T * 2.4 + 1) * .018, 1);
  P.head.rotation.set(-v * .1 + Math.sin(T * 1.9) * .04 + (S.headX || 0), Math.sin(T * .9) * .12 + (S.headY || 0), Math.sin(T * 1.3) * .06 + (S.headZ || 0));
  // boca: se abre con la amplitud de la voz
  const o = clamp(v * 1.15); P.mouthIn.scale.set(1.15 - o * .25, .16 + o * 1.05, .35); P.tongue.visible = o > .25; P.smile.visible = o < .18;
  // parpadeo cada ~3 s (doble a veces)
  const bt = (T + S.blinkSeed) % 3.1, bl = bt < .14 ? Math.sin(bt / .14 * Math.PI) : (bt > .3 && bt < .44 && Math.floor((T + S.blinkSeed) / 3.1) % 3 === 0 ? Math.sin((bt - .3) / .14 * Math.PI) : 0);
  const sur = S.mood === "surprised" || S.mood === "scared" ? 1 : 0;
  P.eyes.forEach((e, i) => { e.g.scale.set(1 + sur * .12, Math.max(.08, 1 - bl) * (1 + sur * .15), 1);
    const lx = S.mood === "dizzy" ? Math.cos(T * 9 + i * Math.PI) * .022 : S.look.x * .02, ly = S.mood === "dizzy" ? Math.sin(T * 9 + i * Math.PI) * .022 : S.look.y * .02;
    e.iris.position.x = e.pup.position.x = lx; e.iris.position.y = e.pup.position.y = ly;
    e.pup.scale.setScalar(S.mood === "scared" ? .7 : 1); e.pup.scale.z = .45; });
  P.brows.forEach(b => { const s = b.userData.s; b.position.copy(b.userData.base); b.position.y += sur * .06 + v * .02;
    b.rotation.z = Math.PI / 2 - s * (S.mood === "scared" ? .4 : .16); });   // extremo interior arriba = cara amable
  // brazos: gesto al hablar, saludo o baile
  P.arms.forEach(a => { const s = a.userData.s;
    let z = s * (.25 + v * .35 * (.5 + .5 * Math.sin(T * 3.1 + s))), x = -v * .4 * (.5 + .5 * Math.sin(T * 2.3 + s * 2));
    if (S.wave && s > 0) { z = 2.5 + Math.sin(T * 11) * .35; x = -.2; }
    if (S.dance) { z = s * (1.8 + Math.sin(T * S.dance + (s > 0 ? Math.PI : 0)) * .7); x = Math.sin(T * S.dance * .5) * .3; }
    const ov = s < 0 ? S.armL : S.armR; if (ov) { x = ov[0]; z = ov[1]; }
    a.rotation.set(x, 0, z); });
}
export { wobble, lerp };
