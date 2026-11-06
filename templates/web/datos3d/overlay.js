// Capa de edición (HTML encima del 3D): subtítulos, chip de dato, golpe de número, stickers, contadores y tarjetas.
import { DATA, SC, W, H, clamp, lerp, spring, outBack, outCubic, ease, bump } from "./core.js";
const $ = s => document.querySelector(s);
const layer = $("#layer"), capEl = $("#cap"), badge = $("#badge"), slam = $("#slam"), prog = $("#prog b"), leak = $("#leak");

// ---------- subtítulos: grupos de 1-3 palabras, palabra activa resaltada
let CH = [];
export function buildCaptions() {
  const ws = DATA.words; let cur = [];
  const flush = () => { if (cur.length) CH.push(cur); cur = []; };
  ws.forEach((w, i) => {
    cur.push(w); const nx = ws[i + 1], len = cur.map(x => x.w).join(" ").length;
    if (!nx || /[.,?!]$/.test(w.w) || cur.length >= 3 || len > 13 || nx.s - w.e > .3) flush();
  });
  CH = CH.map((g, i) => ({ g, s: g[0].s - .04, e: Math.min(CH[i + 1] ? CH[i + 1][0].s - .04 : 1e9, g[g.length - 1].e + .45) }));
}
let lastChunk = -1;
function captions(T, hide) {
  const i = CH.findIndex(c => T >= c.s && T < c.e);
  if (i < 0 || hide) { capEl.style.opacity = "0"; return; }
  const c = CH[i];
  if (i !== lastChunk) { capEl.innerHTML = c.g.map(w => `<span class="${w.k ? "k" : ""}">${w.w.replace(/[.,]$/, "")}</span>`).join(""); lastChunk = i; }
  const k = spring(T - c.s, 16, 9), sp = capEl.children;
  capEl.style.opacity = "1"; capEl.style.transform = `translateY(${(1 - k) * 30}px) scale(${.75 + .25 * k})`;
  c.g.forEach((w, j) => { const on = T >= w.s - .02 && T < w.e + .05, a = bump(T - w.s, .05, .3);
    sp[j].classList.toggle("on", on); sp[j].style.transform = `translateY(${-a * 10}px) scale(${1 + a * .14})`; });
}

// ---------- chip «DATO n/5» + barra de progreso del video
function chip(T, t) {
  if (SC < 1 || SC > 5) { badge.style.opacity = "0"; return; }
  const k = spring(t - 1.15, 12, 7);
  badge.querySelector(".n").textContent = SC;
  badge.querySelectorAll(".dots i").forEach((d, i) => d.classList.toggle("f", i < SC));
  badge.style.opacity = String(clamp(k * 3)); badge.style.transform = `translateX(${(1 - k) * -260}px) scale(${.8 + .2 * k})`;
}

// ---------- golpe de número al empezar cada dato
const SLAM = ["", "EL PULPO", "LA MIEL", "VENUS", "EL RAYO", "EL PANDA"];
function slamCard(t) {
  if (SC < 1 || SC > 5 || t > 1.4) { slam.style.display = "none"; return; }
  slam.style.display = "block";
  const a = clamp((t - .12) / .16), out = clamp((t - 1.05) / .3);
  const sc = lerp(2.4, 1, outCubic(a)) * (1 - out * .7) * (1 + bump(t - .28, .03, .25) * .08);
  slam.querySelector(".big").textContent = "#" + SC; slam.querySelector(".sub").textContent = SLAM[SC];
  slam.style.opacity = String(a * (1 - out));
  slam.style.transform = `translate(${-out * 520}px, ${-out * 260}px) scale(${sc}) rotate(${(1 - a) * -12 + Math.sin(t * 40) * bump(t - .28, .02, .2) * 3}deg)`;
  slam.querySelector(".burst").style.transform = `rotate(${t * 60}deg) scale(${.6 + .4 * outBack(a)})`;
}

// ---------- elementos temporizados
const items = [];
function el(html, cls = "") { const d = document.createElement("div"); d.className = "stk " + cls; d.innerHTML = html; layer.appendChild(d); return d; }
// kind: pop (rebote elástico) · stamp (sello que golpea) · fly (entra volando desde from)
export function sticker(o) { o.el = el(o.html, o.cls || ""); o.el.style.fontSize = (o.size || 90) + "px"; o.type = "stk"; items.push(o); return o; }
export function counter(o) { o.el = el("", "count " + (o.cls || "")); if (o.size) o.el.style.fontSize = o.size + "px"; o.type = "cnt"; o.kind = o.kind || "pop"; items.push(o); return o; }
export function card(o) { o.el = el(o.html, "card " + (o.cls || "")); o.el.style.position = "absolute"; o.type = "card"; o.kind = o.kind || "pop"; items.push(o); return o; }
const fmt = (v, d = 0) => v.toLocaleString("es-ES", { minimumFractionDigits: d, maximumFractionDigits: d, useGrouping: "always" });
function place(o, T) {
  const t = T - o.t0, t1 = (o.t1 ?? 1e9) - T;
  if (t < 0 || t1 < -.01) { o.el.style.display = "none"; return; }
  o.el.style.display = "block";
  let s = 1, x = o.x, y = o.y, r = o.rot || 0, op = 1;
  if (o.kind === "stamp") { const a = clamp(t / .14); s = lerp(2.8, 1, a * a) * (1 + bump(t - .14, .02, .25) * .1); op = a; r += (1 - a) * 18; }
  else if (o.kind === "fly") { const a = outBack(clamp(t / .55), 1.4); x = lerp(o.from[0], o.x, a); y = lerp(o.from[1], o.y, a); r += (1 - a) * (o.spin ?? -40); }
  else { s = spring(t, 13, 6.5); r += (1 - Math.min(1, s)) * 25; }
  if (o.float !== false) { y += Math.sin(T * 2.2 + o.x) * 6; r += Math.sin(T * 1.7 + o.y) * 3; }
  const out = clamp(1 - t1 / .22); s *= 1 - outCubic(out); op *= 1 - out;
  if (o.type === "cnt") { const k = outCubic(clamp((t - (o.delay || 0)) / (o.dur || 1)));
    o.el.innerHTML = (o.prefix || "") + fmt(lerp(o.from || 0, o.to, k), o.dec || 0) + (o.suffix || "");
    s *= 1 + bump(t - (o.delay || 0) - (o.dur || 1), .04, .35) * .18; }
  if (o.pulse) s *= 1 + Math.max(0, Math.sin(T * o.pulse)) * .06;
  o.el.style.opacity = String(op);
  o.el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) rotate(${r}deg) scale(${Math.max(0, s)})`;
  if (o.update) o.update(o.el, t, T);
}

// ---------- fotograma de la capa
export const uiState = { hideCaps: false, leak: 0, shake: 0 };
export function overlay(T, t) {
  captions(T, uiState.hideCaps); chip(T, t); slamCard(t);
  items.forEach(o => place(o, T));
  prog.style.width = (T / DATA.total * 100).toFixed(2) + "%";
  leak.style.opacity = String(uiState.leak);
  const s = uiState.shake; document.getElementById("ui").style.transform = s ? `translate(${Math.sin(T * 71) * s * 14}px, ${Math.cos(T * 63) * s * 10}px)` : "";
}
export { W, H };
