// Interfaz del Estudio de Animación IA (JavaScript sin dependencias)
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const api = async (path, body, isForm) => {
  const opt = body ? { method: "POST", body: isForm ? body : JSON.stringify(body), headers: isForm ? {} : { "Content-Type": "application/json" } } : {};
  const r = await fetch(path, opt);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || j.detail || r.statusText);
  return j;
};
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const EXAMPLES = [
  "Crea una caricatura animada de una manzana que saluda en el parque",
  "Haz una animación estilo anime de una niña con magia en un castillo",
  "Crea un personaje 3D: un gato que baila en el escenario",
  "Haz una historia con frutas animadas en la cocina",
  "Crea una animación cinematográfica de un robot en la ciudad de noche",
  "Crea una animación para TikTok de un plátano que baila",
  "Un perro y un gato pelean en el dojo con explosiones",
  "Un fantasma asusta a un niño en un bosque embrujado",
  "Un conejo tierno camina en la nieve",
  "Clase educativa: un robot explica en el aula",
];
const STYLE_ICON = { cartoon: "🎨", anime: "🌸", pixel: "👾", minimalist: "◻️", cute: "🧁", cinematic: "🎥", horror: "👻", fantasy: "🪄",
  paper: "📄", clay: "🧱", stopmotion: "🎞️", realistic: "📷", comic: "💥", retro: "📼" };
const ACTION_ES = { idle: "reposo", walk: "camina", run: "corre", jump: "salta", dance: "baila", talk: "habla", wave: "saluda", punch: "golpea",
  kick: "patea", celebrate: "celebra", float: "flota", scared_shake: "tiembla", spin: "gira", think: "piensa", sit_bounce: "rebota" };

let OPT = null;
const state = { style: "", format: "", effects: new Set(), cast: [], plan: null, ivEffects: new Set() };

// ------------------------------------------------------------------ pestañas
$$("#tabs button").forEach((b) => b.onclick = () => {
  $$("#tabs button").forEach((x) => x.classList.toggle("active", x === b));
  $$(".tab").forEach((t) => t.classList.toggle("active", t.id === "tab-" + b.dataset.tab));
  if (b.dataset.tab === "proyectos") loadProjects();
  if (b.dataset.tab === "ajustes") loadStatus();
});

function fillSelect(sel, entries, first) {
  sel.innerHTML = (first ? `<option value="">${first}</option>` : "") + entries.map(([v, l]) => `<option value="${esc(v)}">${esc(l)}</option>`).join("");
}

async function init() {
  OPT = await api("/api/options");
  // ejemplos
  $("#examples").innerHTML = EXAMPLES.map((e) => `<span class="chip">${esc(e)}</span>`).join("");
  $$("#examples .chip").forEach((c) => c.onclick = () => { $("#prompt").value = c.textContent; });
  // estilos
  $("#styles").innerHTML = `<div class="style on" data-v=""><b>✨ Automático</b><span>Según tu descripción</span></div>` +
    Object.entries(OPT.styles).map(([k, v]) => `<div class="style" data-v="${k}"><b>${STYLE_ICON[k] || "•"} ${esc(v.label)}</b><span>${esc(v.desc)}</span></div>`).join("");
  $$("#styles .style").forEach((s) => s.onclick = () => { $$("#styles .style").forEach((x) => x.classList.toggle("on", x === s)); state.style = s.dataset.v; });
  // formatos
  const shapes = { "16:9": [44, 25], "9:16": [18, 32], "1:1": [28, 28], "4:5": [24, 30] };
  $("#formats").innerHTML = `<div class="fmt on" data-v=""><div class="shape" style="width:30px;height:24px"></div>Automático</div>` +
    Object.entries(OPT.formats).map(([k, v]) => `<div class="fmt" data-v="${k}"><div class="shape" style="width:${shapes[k][0]}px;height:${shapes[k][1]}px"></div><b>${k}</b><br>${esc(v)}</div>`).join("");
  $$("#formats .fmt").forEach((s) => s.onclick = () => { $$("#formats .fmt").forEach((x) => x.classList.toggle("on", x === s)); state.format = s.dataset.v; });
  $("#duration").oninput = (e) => $("#durLabel").textContent = +e.target.value ? `${e.target.value} s` : "Automática";
  // selects
  const sp = Object.entries(OPT.species);
  fillSelect($("#castSpecies"), sp);
  fillSelect($("#chSpecies"), sp);
  const acc = OPT.accessories.map((a) => [a, { none: "Sin accesorio", hat: "Sombrero de copa", bow: "Moño", glasses: "Gafas", crown: "Corona", cap: "Gorra", wizard: "Gorro de mago", scarf: "Bufanda" }[a] || a]);
  fillSelect($("#castAcc"), acc);
  fillSelect($("#chAcc"), acc);
  fillSelect($("#chStyle"), Object.entries(OPT.styles).map(([k, v]) => [k, v.label]));
  fillSelect($("#background"), Object.entries(OPT.backgrounds), "Automático (según el texto)");
  const moodsEs = { happy: "Alegre", cute: "Tierna", sad: "Triste", epic: "Épica", spooky: "Terror", dance: "Baile", action: "Acción", calm: "Tranquila", fantasy: "Fantasía" };
  fillSelect($("#mood"), OPT.moods.map((m) => [m, moodsEs[m] || m]), "Automática");
  fillSelect($("#ivMusic"), [["", "Sin música"], ...OPT.moods.map((m) => [m, moodsEs[m] || m])]);
  $("#ivMusic").value = "calm";
  fillSelect($("#ivMove"), OPT.moves.map((m) => [m, { zoom_in: "Acercar", zoom_out: "Alejar", pan_left: "Paneo izquierda", pan_right: "Paneo derecha", pan_up: "Subir", orbit: "Órbita suave", parallax: "Paralaje 2.5D", breathe: "Respiración" }[m] || m]));
  fillSelect($("#tplName"), OPT.templates.map((t) => [t, t]));
  const chip = (cont, set) => {
    cont.innerHTML = Object.entries(OPT.effects).map(([k, v]) => `<span class="chip" data-v="${k}">${esc(v)}</span>`).join("");
    cont.querySelectorAll(".chip").forEach((c) => c.onclick = () => { c.classList.toggle("on"); c.classList.contains("on") ? set.add(c.dataset.v) : set.delete(c.dataset.v); });
  };
  chip($("#effects"), state.effects);
  chip($("#ivEffects"), state.ivEffects);
}

// ------------------------------------------------------------------ reparto
function renderCast() {
  $("#castList").innerHTML = state.cast.map((c, i) =>
    `<span class="who"><span class="dot" style="background:${c.color}"></span>${esc(c.name || OPT.species[c.species])}<span class="x" data-i="${i}">✕</span></span>`).join("")
    || `<span class="muted">Sin personajes elegidos: se detectarán del texto.</span>`;
  $$("#castList .x").forEach((x) => x.onclick = () => { state.cast.splice(+x.dataset.i, 1); renderCast(); });
}
$("#castAdd").onclick = () => {
  state.cast.push({ species: $("#castSpecies").value, name: $("#castName").value.trim(), color: $("#castColor").value, accessory: $("#castAcc").value });
  $("#castName").value = "";
  renderCast();
};
$("#castSpecies").onchange = () => { /* color por defecto no disponible en options: se mantiene el elegido */ };

function formBody() {
  const d = +$("#duration").value;
  return {
    prompt: $("#prompt").value.trim(), style: state.style, format: state.format, background: $("#background").value,
    characters: state.cast, effects: [...state.effects], duration: d || null, mood: $("#mood").value, ai: $("#useAI").checked,
    three_d: $("#is3d").checked, voices: $("#voices").checked, music: $("#music").checked, transition: $("#transition").value,
  };
}

// ------------------------------------------------------------------ guion
$("#btnPlan").onclick = async () => {
  if (!$("#prompt").value.trim()) return alert("Escribe primero qué quieres crear.");
  $("#btnPlan").disabled = true;
  try { state.plan = await api("/api/plan", formBody()); showPlan(); } catch (e) { alert(e.message); }
  $("#btnPlan").disabled = false;
};
function showPlan() {
  const p = state.plan, names = Object.fromEntries(p.characters.map((c) => [c.id, c.name]));
  $("#planCard").hidden = false;
  $("#planView").innerHTML = `<p><b>${esc(p.title)}</b> · estilo <b>${esc(OPT.styles[p.style]?.label || p.style)}</b> · formato ${p.format} · música ${p.mood} · motor ${p.engine === "3d" ? "3D (Blender)" : "2D"}
    <br><span class="muted">Reparto: ${p.characters.map((c) => esc(c.name)).join(", ")}</span></p>` +
    p.scenes.map((s, si) => `<div class="scene"><h3>Escena ${si + 1}: ${esc(OPT.backgrounds[s.background] || s.background)} (${s.time_of_day}) · ${s.duration}s</h3>
      <div class="meta">Cámara: ${s.camera.type} · Acciones: ${s.actors.map((a) => `${esc(names[a.character])} ${ACTION_ES[a.action] || a.action} (${a.emotion})`).join(", ")}
      ${s.effects.length ? "· Efectos: " + s.effects.map((f) => esc(OPT.effects[f.type] || f.type)).join(", ") : ""}</div>
      ${s.dialogue.map((d, di) => `<div class="line"><b>${esc(names[d.character])}</b><input data-s="${si}" data-d="${di}" value="${esc(d.text)}"></div>`).join("")}
      </div>`).join("");
  $$("#planView input").forEach((inp) => inp.oninput = () => { state.plan.scenes[+inp.dataset.s].dialogue[+inp.dataset.d].text = inp.value; $("#planJson").value = JSON.stringify(state.plan, null, 2); });
  $("#planJson").value = JSON.stringify(p, null, 2);
  $("#planCard").scrollIntoView({ behavior: "smooth" });
}
$("#planJson").onchange = () => { try { state.plan = JSON.parse($("#planJson").value); showPlan(); } catch (e) { alert("JSON inválido: " + e.message); } };

// ------------------------------------------------------------------ trabajos
async function follow(job, outEl, onDone) {
  const bar = outEl.querySelector(".progress div") || $("#bar");
  const st = outEl.querySelector(".st") || $("#status");
  for (;;) {
    const j = await api(`/api/jobs/${job.id}`);
    bar.style.width = `${j.progress || 2}%`;
    st.textContent = `${j.stage || ""} · ${j.message || ""}`;
    if (j.status === "done") { onDone(j); return; }
    if (j.status === "error") { st.innerHTML = `<span class="bad">Error:</span> <pre style="white-space:pre-wrap">${esc(j.error)}</pre>`; return; }
    await new Promise((r) => setTimeout(r, 1200));
  }
}
function progressBox(el, title) {
  el.innerHTML = `<div style="width:100%"><h3>${esc(title)}</h3><div class="progress"><div></div></div><p class="st muted">En cola…</p><div class="res"></div></div>`;
  return el;
}
function filesHtml(files) {
  return `<div class="files">` + Object.entries(files).map(([n, u]) => `<a class="btn ghost" href="${u}" download>⬇ ${esc(n)}</a>`).join("") + `</div>`;
}
function qcHtml(qc) {
  if (!qc) return "";
  return `<div class="qc"><b>Control de calidad: ${qc.passed ? '<span class="ok">APROBADO</span>' : '<span class="bad">CON ERRORES</span>'}</b><ul>` +
    qc.checks.map((c) => `<li>${c.ok ? "✔" : c.severity === "warning" ? "⚠" : "✘"} ${esc(c.check)} — ${esc(c.detail)}</li>`).join("") + "</ul></div>";
}
function exportButtons(videoUrl) {
  const ops = [["export:youtube", "YouTube 1080p"], ["export:tiktok", "TikTok/Reels"], ["export:instagram", "Instagram"], ["export:web", "Web ligero"],
    ["export:whatsapp", "WhatsApp"], ["export:capcut", "Paquete CapCut"], ["upscale:", "Upscale ×2"], ["interpolate:", "60 fps"], ["loop:", "Bucle perfecto"]];
  return `<div class="files">` + ops.map(([k, l]) => `<button class="btn ghost exp" data-k="${k}" data-v="${videoUrl}">${l}</button>`).join("") + `</div><div class="expOut"></div>`;
}
function bindExports(root) {
  root.querySelectorAll(".exp").forEach((b) => b.onclick = async () => {
    const [op, preset] = b.dataset.k.split(":");
    const out = root.querySelector(".expOut");
    progressBox(out, "Exportando " + b.textContent);
    const job = await api("/api/export", { video: b.dataset.v, op, preset: preset || "youtube" });
    follow(job, out, (j) => { out.querySelector(".res").innerHTML = filesHtml(j.files); });
  });
}

async function make(body) {
  $("#resultCard").hidden = false;
  $("#resultTitle").textContent = "Creando tu animación…";
  $("#result").innerHTML = "";
  $("#bar").style.width = "2%";
  $("#resultCard").scrollIntoView({ behavior: "smooth" });
  try {
    const job = await api("/api/render", body);
    follow(job, $("#resultCard"), (j) => {
      $("#resultTitle").textContent = "¡Listo! 🎉";
      const f = j.files;
      $("#result").innerHTML = `<video src="${f["final.mp4"]}" controls autoplay playsinline></video>${qcHtml(j.qc)}
        <h3>Descargas</h3>${filesHtml(f)}<a class="btn" href="/api/projects/${j.dir.split("/").pop()}/zip">📦 Descargar proyecto completo (ZIP)</a>
        <h3>Exportar</h3>${exportButtons(f["final.mp4"])}
        ${f["storyboard.jpg"] ? `<h3>Storyboard</h3><img src="${f["storyboard.jpg"]}" style="width:100%;border-radius:12px">` : ""}`;
      bindExports($("#result"));
    });
  } catch (e) { $("#status").textContent = "Error: " + e.message; }
}
$("#btnMake").onclick = () => {
  if (!$("#prompt").value.trim() && !state.cast.length) return alert("Escribe qué quieres crear o añade un personaje.");
  make({ ...formBody(), quality: $("#quality").value });
};
$("#btnRenderPlan").onclick = () => make({ spec: state.plan, quality: $("#quality").value });

// ------------------------------------------------------------------ personajes
function chBody() {
  return { species: $("#chSpecies").value, name: $("#chName").value.trim(), color: $("#chColor").value, accessory: $("#chAcc").value, eyes: $("#chEyes").value, style: $("#chStyle").value };
}
$("#chGo").onclick = async () => {
  $("#chOut").textContent = "Dibujando…";
  const r = await api("/api/character/preview", chBody());
  $("#chOut").innerHTML = `<img src="${r.sheet}"><div class="files"><a class="btn ghost" href="${r.sheet}" download>⬇ Hoja PNG</a><a class="btn ghost" href="${r.sheet.replace(".png", ".json")}" download>⬇ Ficha JSON</a></div>`;
};
$("#ch3d").onclick = async () => {
  const b = chBody();
  const el = progressBox($("#chOut"), "Modelando y animando en Blender (puede tardar unos minutos)…");
  const job = await api("/api/character3d", { species: b.species, color: b.color, action: "dance", duration: 3 });
  follow(job, el, (j) => {
    const vid = Object.entries(j.files).find(([n]) => n.endsWith(".mp4"));
    el.querySelector(".res").innerHTML = (vid ? `<video src="${vid[1]}" controls autoplay loop></video>` : "") + filesHtml(j.files) +
      (Object.keys(j.files).some((n) => n.endsWith(".glb")) ? `<p class="muted">El archivo .glb se puede abrir en Blender, Three.js, Unity o Godot.</p>` : "");
  });
};
$("#chUse").onclick = () => {
  const b = chBody();
  state.cast.push({ species: b.species, name: b.name, color: b.color, accessory: b.accessory });
  renderCast();
  $$("#tabs button")[0].click();
};

// ------------------------------------------------------------------ imagen → video
$("#ivGo").onclick = async () => {
  const f = $("#ivFile").files[0];
  if (!f) return alert("Elige una imagen.");
  const fd = new FormData();
  fd.append("file", f);
  fd.append("move", $("#ivMove").value); fd.append("effects", [...state.ivEffects].join(","));
  fd.append("style", $("#ivStyle").value); fd.append("format", $("#ivFormat").value);
  fd.append("duration", $("#ivDur").value); fd.append("music", $("#ivMusic").value);
  fd.append("provider", $("#ivProvider").value); fd.append("prompt", $("#ivPrompt").value);
  const el = progressBox($("#ivOut"), "Animando la imagen…");
  try {
    const job = await api("/api/img2video", fd, true);
    follow(job, el, (j) => { el.querySelector(".res").innerHTML = `<video src="${j.files["video.mp4"]}" controls autoplay loop></video>${filesHtml(j.files)}${exportButtons(j.files["video.mp4"])}`; bindExports(el); });
  } catch (e) { el.querySelector(".st").textContent = e.message; }
};
$("#imgGo").onclick = async () => {
  if (!$("#imgPrompt").value.trim()) return;
  const el = progressBox($("#ivOut"), "Generando imagen…");
  const job = await api("/api/image", { prompt: $("#imgPrompt").value, provider: $("#imgProvider").value });
  follow(job, el, (j) => {
    const img = Object.values(j.files)[0];
    el.querySelector(".res").innerHTML = `<img src="${img}">${filesHtml(j.files)}<p class="muted">Descárgala y súbela arriba para convertirla en video.</p>` +
      (j.log_tail || []).filter((l) => l.includes("aviso") || l.includes("local")).map((l) => `<p class="muted">${esc(l)}</p>`).join("");
  });
};

// ------------------------------------------------------------------ motion
$$("[data-motion]").forEach((b) => b.onclick = async () => {
  const kind = b.dataset.motion;
  const body = { kind };
  if (kind === "text") Object.assign(body, { text: $("#mtText").value, mode: $("#mtMode").value, format: $("#mtFormat").value, palette: $("#mtPalette").value });
  if (kind === "logo") Object.assign(body, { text: $("#lgName").value, tagline: $("#lgTag").value, color: $("#lgColor").value });
  if (kind === "infographic") Object.assign(body, { title: $("#ifTitle").value, data: $("#ifData").value });
  if (kind === "background") Object.assign(body, { style: $("#bgKind").value });
  const el = progressBox($("#mtOut"), "Animando…");
  const job = await api("/api/motion", body);
  follow(job, el, (j) => { const v = Object.values(j.files)[0]; el.querySelector(".res").innerHTML = `<video src="${v}" controls autoplay loop style="max-height:70vh;object-fit:contain"></video>${filesHtml(j.files)}`; });
});

// ------------------------------------------------------------------ web / 3D
$("#tplOpen").onclick = () => {
  const q = $("#tplQuery").value;
  $("#webOut").innerHTML = `<iframe src="/templates/web/${$("#tplName").value}.html${q ? "?" + q : ""}" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px"></iframe>`;
};
$("#tplGo").onclick = async () => {
  const el = progressBox($("#webOut"), "Capturando frames con Chromium…");
  const job = await api("/api/web", { template: $("#tplName").value, query: $("#tplQuery").value, format: $("#tplFormat").value });
  follow(job, el, (j) => { const v = Object.values(j.files)[0]; el.querySelector(".res").innerHTML = `<video src="${v}" controls autoplay loop></video>${filesHtml(j.files)}`; });
};

// ------------------------------------------------------------------ proyectos / estado
async function loadProjects() {
  const items = await api("/api/projects");
  $("#projects").innerHTML = items.map((p) => `<div class="item">${p.thumb ? `<img src="${p.thumb}">` : `<video src="${p.video}" muted></video>`}
    <div><b>${esc(p.title)}</b><br><span class="muted">${esc(p.name)}</span><div class="files"><a class="btn ghost" href="${p.video}" target="_blank">▶ Ver</a>
    <a class="btn ghost" href="/api/projects/${encodeURIComponent(p.name)}/zip">📦 ZIP</a></div></div></div>`).join("") || `<p class="muted">Aún no hay proyectos.</p>`;
}
$("#refreshProjects").onclick = loadProjects;
async function loadStatus() {
  const s = await api("/api/status");
  $("#tools").innerHTML = Object.entries(s.tools).map(([k, v]) => `<div class="status-row"><span>${esc(k)}</span><span class="${v ? "ok" : "no"}">${v ? "✔ instalado" : "— no disponible"}</span></div>`).join("");
  $("#keys").innerHTML = Object.entries(s.keys).map(([k, v]) => `<div class="status-row"><span><code>${k}</code><br><span class="muted">${esc(s.key_descriptions[k])}</span></span><span class="${v ? "ok" : "no"}">${v ? "✔ configurada" : "sin clave"}</span></div>`).join("");
}

init().then(renderCast).catch((e) => alert("No se pudo conectar con el estudio: " + e.message));
