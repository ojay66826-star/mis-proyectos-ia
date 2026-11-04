# Skills de terceros (procedencia)

Instaladas el 2026-11-04 a partir de un carrusel de imágenes guardado en Google Drive (TikTok @steven_aristizabal).
Cada una se revisó (SKILL.md, referencias y scripts) antes de copiarla. Se conserva la licencia original en cada carpeta.
No las regenera `scripts/skills/build.py`; para actualizarlas, vuelve a copiar desde el repositorio de origen y revisa el diff.

| Skill | Imagen de origen | Repositorio | Commit | Licencia | Cambios locales |
|---|---|---|---|---|---|
| hyperframes | "CSS Animations (HyperFrames)" | github.com/heygen-com/hyperframes (`skills/hyperframes`) — oficial de HeyGen; la antigua skill `css-animations` está fusionada aquí | af0c815 | Apache-2.0 | se quitaron `*.test.mjs` |
| hyperframes-cli | (dependencia de la anterior) | heygen-com/hyperframes (`skills/hyperframes-cli`) | af0c815 | Apache-2.0 | ninguno |
| hyperframes-registry | (dependencia de la anterior) | heygen-com/hyperframes (`skills/hyperframes-registry`) | af0c815 | Apache-2.0 | ninguno |
| threejs-animation-api | "Three.js 3D Animation" | github.com/cloudai-x/threejs-skills (`skills/threejs-animation`) | 0e18186 | MIT | renombrada (antes `threejs-animation`) para no chocar con la Skill propia del estudio |
| ui-animation | "UI-Animation" | github.com/travisjneuman/.claude (`skills/ui-animation`) | ae7c24d | MIT | ninguno |
| flutter-animations | "Flutter Animations" | github.com/MADTeacher/mad-agents-skills (`flutter-animations`) — el repo oficial `flutter/skills` ya no incluye skill de animación | 2fb67e3 | MIT | ninguno |

Requisitos de HyperFrames: Node.js ≥ 22, FFmpeg y Chrome/Chromium; usa `npx hyperframes …` (paquete npm `hyperframes`).
Recomendado: `HYPERFRAMES_NO_TELEMETRY=1`. El render en la nube y los avatares usan cuenta/créditos de HeyGen (de pago): no son necesarios para render local.

No instalada: "Aura.js Web Motion Toolkit" — no existe ninguna Skill ni librería con ese nombre en fuentes verificables.

## Verificación de HyperFrames (2026-11-04)

Render local de prueba correcto con `hyperframes@0.9.13` (5 s, 1920×1080, 30 fps, H.264, 8,5 s de render),
`check` sin errores. Nota para este entorno: el Chromium del renderizador no usa el proxy de salida, así que
los `<script>` desde CDN fallan (`sub_timeline_script_failure`). Solución: guardar GSAP en el proyecto
(`npm pack gsap@<versión>` → `assets/vendor/gsap.min.js`) y referenciarlo como `assets/vendor/gsap.min.js`.
Exporta `HYPERFRAMES_NO_TELEMETRY=1` antes de usar la CLI.
