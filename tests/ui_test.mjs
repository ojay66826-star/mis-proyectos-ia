// Prueba end-to-end de la interfaz: abre el estudio, escribe una instrucción,
// pulsa "Crear animación" y espera el video terminado.
// Uso: node tests/ui_test.mjs [url] [carpeta_capturas]
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
let pw;
for (const c of ["playwright", "/opt/node22/lib/node_modules/playwright"]) { try { pw = require(c); break; } catch { /* */ } }
const url = process.argv[2] || "http://127.0.0.1:8765";
const shots = process.argv[3] || ".";
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
page.on("pageerror", (e) => { console.error("ERROR JS:", e.message); process.exitCode = 1; });
await page.goto(url);
await page.waitForSelector("#styles .style");
await page.screenshot({ path: `${shots}/ui_inicio.png`, fullPage: true });
await page.fill("#prompt", "Crea una caricatura animada de una manzana que saluda en el parque");
await page.click('#styles .style[data-v="cute"]');
await page.selectOption("#quality", "preview");
await page.click("#btnPlan");
await page.waitForSelector("#planView .scene");
console.log("guion OK:", await page.locator("#planView .scene").count(), "escenas");
await page.click("#btnRenderPlan");
await page.waitForSelector("#result video", { timeout: 300000 });
console.log("video OK:", await page.getAttribute("#result video", "src"));
await page.waitForTimeout(1500);
await page.screenshot({ path: `${shots}/ui_resultado.png`, fullPage: false });
await page.click('#tabs button[data-tab="personajes"]');
await page.click("#chGo");
await page.waitForSelector("#chOut img");
await page.screenshot({ path: `${shots}/ui_personajes.png` });
await page.click('#tabs button[data-tab="ajustes"]');
await page.waitForSelector("#tools .status-row");
await page.screenshot({ path: `${shots}/ui_estado.png` });
console.log("UI OK");
await browser.close();
