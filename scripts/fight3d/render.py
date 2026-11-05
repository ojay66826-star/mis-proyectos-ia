"""Renderiza fotogramas concretos de una escena fight3d (para lanzar varios procesos en paralelo).

    blender5 -b escena.blend -P scripts/fight3d/render.py -- carpeta_salida 1-193 [porcentaje] [muestras] [paso] [desfase]
Los fotogramas se guardan como f0001.png…; con paso/desfase cada proceso toma uno de cada N (reparto equilibrado).
"""
import json
import sys
import time

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
out, spec = a[0], a[1]
pct = int(a[2]) if len(a) > 2 else 100
samples = int(a[3]) if len(a) > 3 else None
step = int(a[4]) if len(a) > 4 else 1
offset = int(a[5]) if len(a) > 5 else 0

frames = []
for part in spec.split(","):
    if "-" in part:
        x, y = part.split("-")
        frames += list(range(int(x), int(y) + 1))
    else:
        frames.append(int(part))
frames = frames[offset::step]

sc = bpy.context.scene
sc.render.resolution_percentage = pct
if samples:
    sc.eevee.taa_render_samples = samples
sc.render.image_settings.file_format = "PNG"
t0 = time.time()
for f in frames:
    sc.frame_set(f)
    sc.render.filepath = f"{out}/f{f:04d}.png"
    bpy.ops.render.render(write_still=True)
print("@@JSON@@" + json.dumps({"ok": True, "frames": len(frames), "seconds": round(time.time() - t0, 1)}))
