---
name: 3d-rigging
description: Prepara personajes 3D para animación: jerarquías de pivotes, armaduras (Armature), pesos automáticos, controles IK/FK y shape keys faciales en Blender. Úsala para 'rig', 'esqueleto', 'huesos', 'preparar para animar', 'skinning'.
---

# Rigging 3D

**Categoría:** Animación 3D · **Skills relacionadas:** `3d-character-animation`, `3d-facial-animation`, `3d-modeling`

El estudio usa rigs de pivotes (empties) para personajes estilizados — robustos y rápidos — y documenta cómo pasar a Armature con pesos automáticos o Rigify cuando se necesita deformación orgánica.

## Cuándo usar esta Skill

- El modelo debe deformarse (codos, rodillas, cara).
- Se van a usar animaciones de Mixamo o mocap.

## Principios profesionales

- Nombres consistentes con sufijos .L/.R para simetría.
- Huesos de control separados de huesos de deformación.
- IK en piernas para pies fijos; FK en brazos para arcos naturales.
- Shape keys para visemas (A, E, O, U, M, F).

## Procedimiento paso a paso

1. Rig de pivotes (rápido): cada extremidad hija de un empty en la articulación (ver `build_character`).
2. Armature: añade huesos, `Ctrl+P → With Automatic Weights`, prueba poses extremas.
3. Rigify: añade metarig humano, ajusta, `Generate Rig`.
4. Facial: crea shape keys por visema y conéctalas a la pista de lip-sync.
5. Exporta GLB con `export_animations=True` y verifica.

## Comandos del estudio

```bash
blender -b --factory-startup --python-expr "
import bpy
bpy.ops.object.armature_add(location=(0,0,0))
arm = bpy.context.object; bpy.ops.object.mode_set(mode='EDIT')
b = arm.data.edit_bones[0]; b.name='cuerpo'; b.tail=(0,0,0.6)
bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.wm.save_as_mainfile(filepath='rig_base.blend')"
```

## Ejemplo completo

«Riggea mi personaje para usar animaciones de Mixamo»: exportar el modelo a FBX, subirlo a mixamo.com (cuenta gratis de Adobe), descargar con esqueleto y reimportar en Blender.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender Armature / Rigify | rig profesional | ✅ instalado y probado |
| Mixamo | auto-rig humanoide | 🌐 gratis, requiere internet |
| AccuRIG (ActorCore) | auto-rig gratuito | 💻 programa externo recomendado |

## Control de calidad

- [ ] Poses extremas sin roturas de malla.
- [ ] Simetría correcta L/R.
- [ ] Animación exportada en el GLB.

## Errores comunes y cómo evitarlos

- Pesos automáticos fallan con mallas no cerradas: unir y limpiar primero.
- Escala no aplicada distorsiona el rig.

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
