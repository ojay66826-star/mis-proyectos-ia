#!/usr/bin/env node
// Captura determinista de animaciones web (GSAP, CSS, SVG, Lottie, Three.js) a MP4.
// Cada plantilla expone window.__seek(t) y window.__duration; aquí se avanza el
// tiempo frame a frame (no en tiempo real), así que el resultado es perfecto
// aunque la máquina sea lenta.
//
// Uso: node scripts/capture.mjs <plantilla.html> <salida.mp4> [--duration 4] [--fps 30]
//      [--width 1280] [--height 720] [--query "text=Hola&color=%23ff0066"]
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(here, "..");
const require = createRequire(import.meta.url);

function loadPlaywright() {
  const candidates = ["playwright", "/opt/node22/lib/node_modules/playwright", "playwright-core"];
  for (const c of candidates) {
    try { return require(c); } catch { /* siguiente */ }
  }
  try {
    const { execSync } = require("node:child_process");
    const g = execSync("npm root -g").toString().trim();
    return require(path.join(g, "playwright"));
  } catch {
    console.error("No se encontró Playwright. Instala con: npm i -g playwright && npx playwright install chromium");
    process.exit(2);
  }
}

const args = process.argv.slice(2);
const opt = { duration: null, fps: 30, width: 1280, height: 720, query: "" };
const pos = [];
for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith("--")) { opt[args[i].slice(2)] = args[i + 1]; i++; } else pos.push(args[i]);
}
if (pos.length < 2) {
  console.error("Uso: node scripts/capture.mjs <plantilla.html> <salida.mp4> [--duration s] [--fps n] [--width w] [--height h] [--query q]");
  process.exit(1);
}
const [templateArg, outArg] = pos;
const templatePath = path.resolve(templateArg);
const rel = path.relative(ROOT, templatePath).split(path.sep).join("/");
const outPath = path.resolve(outArg);
const fps = Number(opt.fps), W = Number(opt.width), H = Number(opt.height);

const MIME = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json",
  ".css": "text/css", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".glb": "model/gltf-binary",
  ".wasm": "application/wasm", ".ttf": "font/ttf" };

const server = createServer(async (req, res) => {
  try {
    const url = decodeURIComponent(new URL(req.url, "http://x").pathname);
    let p = path.join(ROOT, url);
    if (!p.startsWith(ROOT)) throw new Error("ruta fuera del proyecto");
    if (url.startsWith("/@abs/")) p = url.slice(5);
    const st = await stat(p);
    if (st.isDirectory()) p = path.join(p, "index.html");
    res.writeHead(200, { "Content-Type": MIME[path.extname(p)] || "application/octet-stream" });
    res.end(await readFile(p));
  } catch {
    res.writeHead(404); res.end("not found");
  }
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const port = server.address().port;

const { chromium } = loadPlaywright();
const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on("console", (m) => { if (m.type() === "error") console.error("[página]", m.text()); });
const q = `?capture=1${opt.query ? "&" + opt.query : ""}`;
await page.goto(`http://127.0.0.1:${port}/${rel}${q}`, { waitUntil: "load" });
await page.waitForFunction(() => window.__ready === true || typeof window.__seek === "function", null, { timeout: 30000 });
await page.waitForFunction(() => window.__ready !== false, null, { timeout: 30000 });
const duration = Number(opt.duration || (await page.evaluate(() => window.__duration || 4)));
const n = Math.round(duration * fps);

const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-i", "-",
  "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", outPath], { stdio: ["pipe", "inherit", "inherit"] });
for (let i = 0; i < n; i++) {
  await page.evaluate(async (t) => { const r = window.__seek(t); if (r instanceof Promise) await r; }, i / fps);
  const buf = await page.screenshot({ type: "png" });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  if (i % 30 === 0) process.stdout.write(`frame ${i}/${n}\n`);
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await browser.close();
server.close();
console.log(`OK ${outPath} (${n} frames, ${duration}s @ ${fps}fps)`);
