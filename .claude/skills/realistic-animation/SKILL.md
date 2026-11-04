---
name: realistic-animation
description: Busca realismo: sombreado suave, profundidad de campo, iluminación física, Cycles en 3D, y para fotorrealismo real, generación de video/imagen IA. Úsala para 'realista', 'fotorrealista', 'que parezca real', 'hiperrealista'.
---

# Animación realista

**Categoría:** Estilos especiales · **Skills relacionadas:** `ai-video-generation`, `animation-lighting`, `cinematic-effects`

Honestidad técnica: el motor 2D ofrece `style: realistic` (sombreado suave con desenfoque, contraste y grano leve) y el 3D puede usar Cycles (path tracing). El **fotorrealismo** de personas/animales reales requiere modelos generativos (Skill `ai-video-generation`, claves de Replicate/OpenAI/Stability o conector ElevenLabs) o assets escaneados.

## Cuándo usar esta Skill

- El usuario pide realismo; explicar opciones y coste.

## Principios profesionales

- La luz hace el realismo: GI, sombras suaves, rim light.
- Materiales físicos (roughness/metallic correctos).
- Movimiento con peso e inercia.
- Imperfección: grano, motion blur, DOF.

## Procedimiento paso a paso

1. Pregunta implícita: ¿estilizado-realista (local) o foto-real (IA)?
2. Local 3D: `--3d --engine cycles` y `samples` 128+ (lento en CPU).
3. Foto-real: genera imagen con `image --provider openai|stability|huggingface` y anímala con `img2video --provider replicate`.
4. Une y pasa QC.

## Comandos del estudio

```bash
python -m studio make "Un robot camina por la ciudad de noche" --3d --engine cycles --quality preview
python -m studio image "photorealistic red fox in a snowy forest, golden hour, 85mm" --provider auto -o zorro.png
python -m studio img2video zorro.png --provider replicate --prompt "the fox turns its head, snow falling, slow push in"
```

## Fragmento de proyecto (project.json)

```json
{"engine": "3d", "render_engine": "cycles", "samples": 128}
```

## Ejemplo completo

«Un león realista caminando»: sin claves → explicar que el motor produce estilizado; ofrecer 3D Cycles o `img2video --move parallax` sobre una foto del usuario; con clave → Replicate imagen→video.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender Cycles | path tracing | ✅ instalado y probado |
| style realistic | aproximación 2D | ✅ motor propio del estudio |
| Replicate / OpenAI / Stability | fotorrealismo generativo | 🔑 requiere clave API |
| Poly Haven | HDRI y texturas reales | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Iluminación coherente con el entorno.
- [ ] Sin artefactos de IA (manos, ojos).
- [ ] Coste/tiempo comunicado.

## Errores comunes y cómo evitarlos

- Cycles sin denoiser en CPU necesita muchas muestras: tiempos largos.
- Prometer fotorrealismo sin proveedor IA.

## Cómo encaja en el estudio (trabajo en equipo entre Skills)

El estudio sigue un único pipeline y **todas las Skills comparten el mismo proyecto JSON** (`project.json`), así que se combinan sin conversiones:

```
idea → animation-scripting → character-design → animation-storyboarding → scene-composition
     → (animación 2D/3D + personajes + efectos) → animation-sound-design → video-editing
     → animation-rendering → animation-quality-control → animation-optimization / exportación
```

- Orquestador general: Skill `animation-workflow` (decide qué Skills intervienen y en qué orden).
- Motor: `python -m studio …` (ver `docs/CLI.md`). Interfaz: `python -m studio serve` → http://127.0.0.1:8765
- Salida estándar de un proyecto: `projects/<fecha>-<titulo>/` con `final.mp4`, `storyboard.jpg`, `miniatura.jpg`,
  `vista_previa.gif`, `subtitulos.srt`, `characters/*_sheet.png`, `audio/*.wav`, `project.json`, `qc_report.json`.

## Reglas del estudio

1. **Primero lo local y gratuito** (motor 2D, Blender, FFmpeg, espeak-ng, Three.js, GSAP, Lottie, Remotion). Usa APIs de pago
   solo si el usuario lo pide o si la calidad exigida lo requiere, y avisa antes de gastar créditos.
2. **Nunca inventes resultados**: ejecuta el comando, revisa el archivo generado (abre un frame o el storyboard) y reporta
   rutas reales. Si algo requiere una clave que no existe (`python -m studio doctor`), dilo y ofrece la alternativa local.
3. **Consistencia de personajes**: reutiliza siempre la ficha JSON del personaje (mismo `id`, `color`, `species`, `accessory`).
4. **No subas secretos**: las claves viven en `.env` (ignorado por git).
5. Termina con `python -m studio qc <video>` y comunica qué pasó y qué no.
