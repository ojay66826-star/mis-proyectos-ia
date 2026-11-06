// Arranque: datos → fuentes → escena; __seek(t) pinta el frame t (s) de la escena de forma determinista.
import { Q, SC, loadData, loadFont, composer, fx, applyCamera, transitions, transitionCamera, cam, bloom } from "./core.js";
import * as core from "./core.js";
import { buildCaptions, overlay, uiState } from "./overlay.js";

window.__ready = false;
await loadData(); await loadFont();
await Promise.all([document.fonts.load('66px "Lucky"'), document.fonts.load('800 30px "Baloo"'), document.fonts.load('600 24px "Baloo"'),
  document.fonts.load('40px "Noto Color Emoji"', "🐙")]);
await document.fonts.ready;
buildCaptions();
const update = await (await import(`./scenes/s${SC}.js`)).build();
window.__duration = core.DUR;
const u = fx.material.uniforms;
window.__seek = (t) => {
  const T = core.T0 + t;
  Object.assign(cam, { shake: 0, roll: 0, hand: 1 });
  u.uTime.value = T; u.uCA.value = .0025; u.uInvert.value = 0; u.uSepia.value = 0; u.uBright.value = 0; u.uWarm.value = 0;
  u.uZoom.value = 0; u.uWhip.value = 0; u.uGlitch.value = 0; u.uFlash.value = 0; u.uSat.value = 1.2; u.uContrast.value = 1.12; u.uVig.value = .32; u.uGrain.value = .03;
  Object.assign(uiState, { leak: 0, shake: 0, hideCaps: false });
  update(t, T);
  const tr = transitions(t);
  transitionCamera(tr);
  applyCamera(T);
  overlay(T, t);
  composer.render();
};
window.__seek(0); window.__ready = true;
if (!Q.has("capture")) { const t0 = performance.now(); const loop = () => { window.__seek(((performance.now() - t0) / 1000) % core.DUR); requestAnimationFrame(loop); }; loop(); }
export { bloom };
