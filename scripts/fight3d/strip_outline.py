"""Quita el contorno NPR (modificador NPR_Outline de toon_setup.py) a todo lo que no sea un luchador."""
import bpy, json, sys
prefixes = tuple(sys.argv[sys.argv.index("--") + 1:] or ["A_", "B_"])
n = 0
for ob in bpy.data.objects:
    if ob.type == "MESH" and not ob.name.startswith(prefixes):
        for m in list(ob.modifiers):
            if m.name == "NPR_Outline":
                ob.modifiers.remove(m); n += 1
bpy.ops.wm.save_mainfile()
print("@@JSON@@" + json.dumps({"ok": True, "removed": n}))
