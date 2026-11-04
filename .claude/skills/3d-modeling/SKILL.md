---
name: 3d-modeling
description: Modela personajes, props y escenarios 3D estilizados de forma procedural con Blender (primitivas, modificadores Bevel/Subdivision/SimpleDeform, materiales PBR) y exporta GLB/FBX/OBJ. Úsala para 'modela', 'crea un modelo 3D', 'objeto 3D', 'asset para juego'.
---

# Modelado 3D

**Categoría:** Animación 3D · **Skills relacionadas:** `3d-rigging`, `blender-animation`, `threejs-animation`

El constructor `build_character()` modela 27 tipos de personaje con primitivas suavizadas (esferas UV de 48 segmentos, cilindros, conos), modificadores (Bevel para robots, SimpleDeform Bend para plátano) y materiales Principled BSDF con subsurface. El mismo patrón sirve para props y escenarios.

## Cuándo usar esta Skill

- Crear un modelo 3D nuevo o un asset.
- Exportar personajes del estudio a otros programas.

## Principios profesionales

- Formas primarias primero (silueta), secundarias después (orejas, hojas), terciarias al final (brillos, mejillas).
- Topología ligera y shading suave; usar modificadores no destructivos.
- Escala real: personaje ≈1 m de alto, origen en los pies.
- Materiales con nombre descriptivo para editarlos luego.

## Procedimiento paso a paso

1. Para personajes del catálogo: `python -m studio character3d <especie>` → GLB.
2. Para un modelo nuevo, crea una función en un script bpy siguiendo `build_character` (obj_add + mat).
3. Ejecuta: `blender -b --factory-startup -P mi_modelo.py`.
4. Exporta: `bpy.ops.export_scene.gltf(filepath='x.glb', export_format='GLB')` o FBX/OBJ.
5. Verifica en el visor Three.js.

## Comandos del estudio

```bash
python -m studio character3d aguacate --action idle --duration 1 -o projects/aguacate3d
blender -b --factory-startup --python-expr "import bpy; bpy.ops.mesh.primitive_monkey_add(); bpy.ops.export_scene.gltf(filepath='mono.glb')"
```

## Ejemplo completo

«Modela una piña 3D para mi juego»: `python -m studio character3d pina --action idle -o projects/pina` → `pina.glb` listo para Godot/Unity/Three.js.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender 4.0 | modelado procedural | ✅ instalado y probado |
| glTF/GLB | intercambio web y juegos | ✅ instalado y probado |
| Meshy / Tripo / Rodin (texto→3D) | modelos 3D con IA | 🔑 requiere clave API |
| Hunyuan3D / TripoSR (open source, GPU) | imagen→3D local | 💻 programa externo recomendado |

## Control de calidad

- [ ] Normales correctas (sin caras negras).
- [ ] Origen en la base del modelo.
- [ ] Archivo GLB < 10 MB.

## Errores comunes y cómo evitarlos

- Aplicar escala antes de exportar (Ctrl+A) si se edita a mano.
- Draco no disponible en la build de Ubuntu: exporta sin compresión.

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
