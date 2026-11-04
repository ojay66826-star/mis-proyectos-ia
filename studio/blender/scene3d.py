"""Script de Blender (se ejecuta con: blender -b --factory-startup -P scene3d.py -- job.json).

Construye personajes 3D procedurales a partir de las mismas fichas del estudio,
anima acciones (caminar, bailar, saltar, saludar, hablar con lip-sync…),
coloca luces de tres puntos y cámara animada, y renderiza PNGs por escena.
También puede exportar el personaje a GLB (para Three.js) y un turntable.
No depende de PIL ni de otros paquetes: solo bpy y la librería estándar.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
JOB = json.load(open(argv[0], encoding="utf-8"))


def hex2lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, color, rough=0.45, emit=0.0, metallic=0.0, sss=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = color if len(color) == 4 else hex2lin(color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if "Subsurface Weight" in b.inputs:
        b.inputs["Subsurface Weight"].default_value = sss
    if emit:
        b.inputs["Emission Color"].default_value = b.inputs["Base Color"].default_value
        b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = b.inputs["Base Color"].default_value
    return m


def obj_add(kind, loc=(0, 0, 0), scale=(1, 1, 1), name=None, material=None, parent=None, smooth=True, **kw):
    ops = {"sphere": bpy.ops.mesh.primitive_uv_sphere_add, "cube": bpy.ops.mesh.primitive_cube_add,
           "cyl": bpy.ops.mesh.primitive_cylinder_add, "cone": bpy.ops.mesh.primitive_cone_add,
           "torus": bpy.ops.mesh.primitive_torus_add, "plane": bpy.ops.mesh.primitive_plane_add,
           "ico": bpy.ops.mesh.primitive_ico_sphere_add}
    if kind == "sphere":
        kw.setdefault("segments", 48)
        kw.setdefault("ring_count", 24)
    ops[kind](location=loc, **kw)
    o = bpy.context.active_object
    o.scale = scale
    if name:
        o.name = name
    if material:
        o.data.materials.append(material)
    if smooth and kind not in ("plane", "cube"):
        bpy.ops.object.shade_smooth()
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    if parent:
        o.parent = parent
    return o


# ------------------------------------------------------------------ personaje
def build_character(spec, x=0.0, facing=1):
    """Devuelve dict con los nodos animables del personaje."""
    shape = spec.get("shape", "blob")
    kind = spec.get("kind", "blob")
    col = spec.get("color", "#4fc3f7")
    M = mat(f"body_{spec['id']}", col, 0.35, sss=0.05)
    ink = mat("ink", "#1e161c", 0.5)
    white = mat("white", "#ffffff", 0.25)
    root = empty(f"root_{spec['id']}", (x, 0, 0))
    body = empty(f"body_{spec['id']}", (0, 0, 0.55), root)
    human = kind == "human"
    if human:
        skin = mat(f"skin_{spec['id']}", spec.get("skin", "#f1c27d"), 0.5, sss=0.1)
        torso = obj_add("cyl", (0, 0, 0.53), (0.16, 0.12, 0.16), material=M, parent=None, vertices=32)
        torso.parent = body
        torso.location = (0, 0, -0.02)
        head = obj_add("sphere", (0, 0, 0), (0.17, 0.17, 0.17), material=skin)
        head.parent = body
        head.location = (0, 0, 0.3)
        hair = obj_add("sphere", (0, 0, 0), (0.18, 0.18, 0.12), material=mat(f"hair_{spec['id']}", spec.get("hair_color", "#4e342e"), 0.6))
        hair.parent = body
        hair.location = (0, 0.01, 0.38)
        face_c, face_r = Vector((0, -0.16, 0.3)), 0.17
        limb_m, limb_r = skin, 0.04
        sh_x, sh_z, hip_x, hip_z, arm_l, leg_l = 0.17, 0.1, 0.07, -0.17, 0.28, 0.38
    else:
        sx, sy, sz = 0.33, 0.3, 0.31
        if shape == "banana":
            sx, sy, sz = 0.16, 0.16, 0.36
        elif shape in ("pineapple", "pear", "avocado"):
            sx, sy, sz = 0.28, 0.27, 0.34
        elif shape == "strawberry":
            sx, sy, sz = 0.3, 0.28, 0.32
        if shape == "robot":
            b = obj_add("cube", (0, 0, 0), (0.31, 0.25, 0.27), material=mat(f"robot_{spec['id']}", col, 0.3, metallic=0.6))
            bev = b.modifiers.new("bevel", "BEVEL")
            bev.width = 0.06
            bev.segments = 4
        else:
            b = obj_add("sphere", (0, 0, 0), (sx, sy, sz), material=M)
        b.parent = body
        if shape == "banana":
            d = b.modifiers.new("bend", "SIMPLE_DEFORM")
            d.deform_method = "BEND"
            d.angle = math.radians(50)
            d.deform_axis = "Y"
        if shape == "apple":
            stem = obj_add("cyl", (0, 0, 0), (0.02, 0.02, 0.08), material=mat("stem", "#795548"), vertices=12)
            stem.parent = body
            stem.location = (0, 0, sz + 0.05)
            leaf = obj_add("sphere", (0, 0, 0), (0.09, 0.03, 0.04), material=mat("leaf", "#4caf50"))
            leaf.parent = body
            leaf.location = (0.08, 0, sz + 0.08)
        if shape in ("strawberry", "pineapple"):
            for i in range(6):
                a = i / 6 * 2 * math.pi
                lf = obj_add("cone", (0, 0, 0), (0.05, 0.05, 0.14 if shape == "pineapple" else 0.06), material=mat("leaf", "#43a047"), vertices=8)
                lf.parent = body
                lf.location = (math.cos(a) * 0.06, math.sin(a) * 0.06, sz + 0.06)
                lf.rotation_euler = (math.cos(a) * 0.5, -math.sin(a) * 0.5, 0)
        if kind == "animal":
            ear_m = mat(f"ear_{spec['id']}", col, 0.5)
            for s in (-1, 1):
                if shape in ("cat", "fox"):
                    e = obj_add("cone", (0, 0, 0), (0.08, 0.05, 0.12), material=ear_m, vertices=16)
                    e.location = (0.17 * s, 0, sz + 0.02)
                elif shape == "bunny":
                    e = obj_add("sphere", (0, 0, 0), (0.06, 0.04, 0.2), material=ear_m)
                    e.location = (0.1 * s, 0, sz + 0.15)
                else:
                    e = obj_add("sphere", (0, 0, 0), (0.08, 0.05, 0.08), material=ear_m)
                    e.location = (0.22 * s, 0, sz - 0.02)
                e.parent = body
        face_c, face_r = Vector((0, -sy * 0.96, 0.04)), min(sx, 0.3)
        limb_m, limb_r = (ink if kind in ("fruit", "blob") else mat(f"limb_{spec['id']}", col, 0.5)), 0.025
        sh_x, sh_z, hip_x, hip_z, arm_l, leg_l = sx * 0.95, -0.02, 0.11, -0.26, 0.28, 0.27

    # cara
    eyes, pupils = [], []
    for s in (-1, 1):
        ex = face_c.x + s * face_r * 0.38
        e = obj_add("sphere", (0, 0, 0), (face_r * 0.2, face_r * 0.1, face_r * 0.26), material=white)
        e.parent = body
        e.location = (ex, face_c.y + 0.005, face_c.z + face_r * 0.1)
        p = obj_add("sphere", (0, 0, 0), (face_r * 0.11, face_r * 0.06, face_r * 0.13), material=ink)
        p.parent = body
        p.location = (ex, face_c.y - face_r * 0.07, face_c.z + face_r * 0.06)
        hl = obj_add("sphere", (0, 0, 0), (face_r * 0.04, face_r * 0.02, face_r * 0.04), material=mat("hl", "#ffffff", 0.1, emit=2))
        hl.parent = body
        hl.location = (ex - face_r * 0.04, face_c.y - face_r * 0.12, face_c.z + face_r * 0.12)
        eyes.append(e)
        pupils.append(p)
    mouth = obj_add("sphere", (0, 0, 0), (face_r * 0.22, face_r * 0.05, face_r * 0.06), material=mat("mouth", "#5a1423", 0.6))
    mouth.parent = body
    mouth.location = (face_c.x, face_c.y + 0.01, face_c.z - face_r * 0.42)
    cheeks = mat("cheek", "#ff8aa5", 0.6)
    for s in (-1, 1):
        ch = obj_add("sphere", (0, 0, 0), (face_r * 0.12, face_r * 0.03, face_r * 0.07), material=cheeks)
        ch.parent = body
        ch.location = (face_c.x + s * face_r * 0.55, face_c.y + 0.02, face_c.z - face_r * 0.22)

    # extremidades: pivotes en hombros/caderas
    glove = white if not human else limb_m
    shoe = mat("shoe", "#78482f", 0.5)
    limbs = {}
    for side, s in (("l", -1), ("r", 1)):
        sp = empty(f"sh_{side}_{spec['id']}", (s * sh_x, 0, sh_z), body)
        arm = obj_add("cyl", (0, 0, 0), (limb_r, limb_r, arm_l / 2), material=limb_m, vertices=16)
        arm.parent = sp
        arm.location = (0, 0, -arm_l / 2)
        hand = obj_add("sphere", (0, 0, 0), (0.05, 0.05, 0.05), material=glove)
        hand.parent = sp
        hand.location = (0, 0, -arm_l)
        hp = empty(f"hip_{side}_{spec['id']}", (s * hip_x, 0, hip_z), body)
        leg = obj_add("cyl", (0, 0, 0), (limb_r * 1.2, limb_r * 1.2, leg_l / 2), material=limb_m if not human else mat("pants", "#37474f"), vertices=16)
        leg.parent = hp
        leg.location = (0, 0, -leg_l / 2)
        foot = obj_add("sphere", (0, 0, 0), (0.06, 0.09, 0.04), material=shoe)
        foot.parent = hp
        foot.location = (0, -0.03, -leg_l)
        limbs[side] = (sp, hp)
    # ajusta altura para que los pies toquen el suelo
    body.location.z = -hip_z + leg_l + 0.04
    return dict(root=root, body=body, limbs=limbs, mouth=mouth, eyes=eyes, pupils=pupils, base_z=body.location.z,
                mouth_scale=tuple(mouth.scale))


VIS_OPEN = {"X": 0.25, "M": 0.15, "A": 1.6, "E": 1.0, "O": 1.4, "U": 0.9, "F": 0.6}


def animate(ch, action, fps, frames, start_frame, x0, x1, tempo, talks):
    root, body = ch["root"], ch["body"]
    for f in range(frames):
        t = f / fps
        fr = start_frame + f
        k = t / max(1e-3, (frames - 1) / fps)
        x = x0 + (x1 - x0) * k
        root.location = (x, 0, 0)
        heading = 0.0
        if action in ("walk", "run") and x1 != x0:
            heading = math.radians(90 if x1 > x0 else -90) * 0.75
        root.rotation_euler = (0, 0, heading)
        bz, sq, tilt = 0.0, 1.0, 0.0
        al = ar = (0.15, 0)
        ll = lr = 0.0
        if action in ("walk", "run"):
            fq = 1.6 if action == "walk" else 2.6
            s = math.sin(t * 2 * math.pi * fq)
            amp = 0.55 if action == "walk" else 0.9
            ll, lr = amp * s, -amp * s
            al, ar = (-amp * s, 0.2), (amp * s, 0.2)
            bz = abs(math.cos(t * 2 * math.pi * fq)) * (0.03 if action == "walk" else 0.07)
            tilt = 0.05 if action == "walk" else 0.18
        elif action == "dance":
            b = abs(math.sin(t * math.pi * tempo / 60))
            bz = b * 0.06
            sq = 1 + 0.08 * (1 - b)
            ph = t * math.pi * tempo / 60
            up = math.sin(ph) > 0
            al = (0.0, 2.6) if up else (0.0, 0.6)
            ar = (0.0, 0.6) if up else (0.0, 2.6)
            ll, lr = 0.3 * math.sin(ph), -0.3 * math.sin(ph)
            root.rotation_euler = (0, 0, 0.5 * math.sin(ph))
        elif action == "jump":
            ph = (t % 1.2) / 1.2
            if 0.2 < ph < 0.8:
                q = (ph - 0.2) / 0.6
                bz = 4 * 0.45 * q * (1 - q)
                al = ar = (0, 2.7)
            else:
                sq = 1.2
        elif action == "wave":
            ar = (0.2 * math.sin(t * 14), 2.6)
        elif action == "celebrate":
            ph = (t % 0.6) / 0.6
            bz = 4 * 0.15 * ph * (1 - ph)
            al = ar = (0, 2.8)
        elif action in ("punch", "kick"):
            ph = (t % 0.7) / 0.7
            hit = math.sin(min(1, ph / 0.35) * math.pi / 2) if ph < 0.35 else 1 - (ph - 0.35) / 0.65
            ar = (-1.57 * hit, 0.3)
            if action == "kick":
                lr = -1.4 * hit
        elif action == "float":
            bz = 0.15 + 0.06 * math.sin(t * math.pi)
        elif action == "spin":
            root.rotation_euler = (0, 0, t * 2 * math.pi)
        else:
            sq = 1 + 0.025 * math.sin(t * 2 * math.pi * 0.4)
            ar = al = (0.05 * math.sin(t * 2), 0.15)
        body.location.z = ch["base_z"] + bz
        body.scale = (sq ** 0.5, sq ** 0.5, 1 / sq)
        body.rotation_euler = (tilt, 0, 0)
        (spl, hpl), (spr, hpr) = ch["limbs"]["l"], ch["limbs"]["r"]
        spl.rotation_euler = (al[0], al[1], 0)
        spr.rotation_euler = (ar[0], -ar[1], 0)
        hpl.rotation_euler = (ll, 0, 0)
        hpr.rotation_euler = (lr, 0, 0)
        for o in (root, body):
            o.keyframe_insert("location", frame=fr)
        for o in (root, body, spl, spr, hpl, hpr):
            o.keyframe_insert("rotation_euler", frame=fr)
        body.keyframe_insert("scale", frame=fr)
        # boca (lip-sync) y parpadeo
        v = "X"
        for (ts, dur, vis) in talks:
            if ts <= t < ts + dur:
                i = int((t - ts) * fps)
                v = vis[i] if i < len(vis) else "X"
        ms = ch["mouth_scale"]
        o = VIS_OPEN.get(v, 0.3)
        ch["mouth"].scale = (ms[0] * (0.8 + 0.2 * o), ms[1], ms[2] * (0.6 + o * 1.4))
        ch["mouth"].keyframe_insert("scale", frame=fr)
        blink = 0.1 if ((t + 0.3) % 3.1) < 0.12 else 1.0
        for e in ch["eyes"]:
            e["bz"] = e.get("bz", e.scale.z)
            e.scale.z = e["bz"] * blink
            e.keyframe_insert("scale", frame=fr)
        for p in ch["pupils"]:
            p["bz"] = p.get("bz", p.scale.z)
            p.scale.z = p["bz"] * blink
            p.keyframe_insert("scale", frame=fr)


# ------------------------------------------------------------------ escenario
GROUND = {"park": "#7cb342", "forest": "#558b2f", "beach": "#ffe0a3", "desert": "#ffca7a", "snow": "#f5f9ff", "city": "#616161",
          "space": "#786e8c", "kitchen": "#bcaaa4", "stage": "#3c1e46", "castle": "#8bc34a", "underwater": "#d7be8c",
          "haunted": "#263238", "classroom": "#a1887f", "studio": "#e4ddd2", "dojo": "#c8a96a"}
SKY = {"day": "#8fd3fe", "sunset": "#ffab7a", "night": "#151a38"}


def build_set(bg, tod):
    world = bpy.data.worlds.new("w")
    bpy.context.scene.world = world
    world.use_nodes = True
    sky = SKY.get(tod, SKY["day"]) if bg not in ("space", "haunted", "stage") else "#0b0b1a"
    if bg == "underwater":
        sky = "#0d5fa0"
    world.node_tree.nodes["Background"].inputs["Color"].default_value = hex2lin(sky)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8 if tod != "night" else 0.3
    g = obj_add("plane", (0, 0, 0), (40, 40, 1), material=mat("ground", GROUND.get(bg, "#7cb342"), 0.9), smooth=False)
    import random
    r = random.Random(bg)
    if bg in ("park", "forest", "castle", "haunted"):
        for i in range(10 if bg != "forest" else 20):
            x, y = r.uniform(-8, 8), r.uniform(3, 12)
            obj_add("cyl", (x, y, 0.5), (0.12, 0.12, 0.5), material=mat("trunk", "#6d4c41"), vertices=10)
            if bg != "haunted":
                obj_add("ico", (x, y, 1.4), (0.7, 0.7, 0.8), material=mat("leaves", "#388e3c", 0.8), subdivisions=2)
    elif bg == "city":
        for i in range(14):
            x, y, h = r.uniform(-10, 10), r.uniform(5, 14), r.uniform(1.5, 5)
            obj_add("cube", (x, y, h / 2), (0.7, 0.7, h / 2), material=mat(f"bld{i % 3}", ["#546e7a", "#78909c", "#455a64"][i % 3], 0.7))
    elif bg in ("stage", "studio", "kitchen", "classroom", "dojo"):
        wall = {"stage": "#2a1446", "studio": "#efe9df", "kitchen": "#fff3e0", "classroom": "#e8f5e9", "dojo": "#efebe9"}[bg]
        w = obj_add("plane", (0, 4, 4), (12, 1, 4), material=mat("wall", wall, 0.8), smooth=False)
        w.rotation_euler = (math.radians(90), 0, 0)
        if bg == "stage":
            for i, c in enumerate([(1, 0.3, 0.3), (0.3, 0.75, 1), (1, 0.9, 0.3)]):
                L = bpy.data.lights.new(f"spot{i}", "SPOT")
                L.energy, L.color, L.spot_size = 900, c, math.radians(40)
                lo = bpy.data.objects.new(f"spot{i}", L)
                bpy.context.collection.objects.link(lo)
                lo.location = (-2.5 + 2.5 * i, -1.5, 4.5)
                lo.rotation_euler = (math.radians(20), math.radians(-12 + 12 * i), 0)
    elif bg == "space":
        for i in range(3):
            obj_add("sphere", (r.uniform(-8, 8), r.uniform(8, 15), r.uniform(2, 6)), (1.2, 1.2, 1.2),
                    material=mat(f"planet{i}", r.choice(["#ef6c00", "#7e57c2", "#26a69a"]), 0.6))
    elif bg == "beach":
        sea = obj_add("plane", (0, 9, 0.02), (40, 6, 1), material=mat("sea", "#039be5", 0.1), smooth=False)
    return g


def lights(tod):
    key = bpy.data.lights.new("key", "SUN")
    key.energy = 2.2 if tod != "night" else 0.8
    key.color = (1.0, 0.95, 0.88) if tod != "sunset" else (1.0, 0.7, 0.5)
    ko = bpy.data.objects.new("key", key)
    bpy.context.collection.objects.link(ko)
    ko.rotation_euler = (math.radians(50), math.radians(15), math.radians(-35))
    fill = bpy.data.lights.new("fill", "AREA")
    fill.energy = 120 if tod != "night" else 60
    fill.size = 5
    fo = bpy.data.objects.new("fill", fill)
    bpy.context.collection.objects.link(fo)
    fo.location = (-4, -5, 3)
    fo.rotation_euler = (math.radians(65), 0, math.radians(-40))
    rim = bpy.data.lights.new("rim", "AREA")
    rim.energy = 150
    rim.color = (0.7, 0.85, 1.0)
    ro = bpy.data.objects.new("rim", rim)
    bpy.context.collection.objects.link(ro)
    ro.location = (3, 4, 3)
    ro.rotation_euler = (math.radians(-60), 0, math.radians(140))


def camera(kind, frames, start, target_z=0.5, spread=1.0):
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 35
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    tgt = empty("cam_target", (0, 0, target_z))
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    dist = 1.9 + spread * 0.75
    for f in range(frames):
        k = f / max(1, frames - 1)
        e = k * k * (3 - 2 * k)
        ang, d, h = 0.0, dist, 0.85
        if kind == "orbit":
            ang = -0.6 + 1.2 * e
        elif kind in ("zoom_in", "dolly_in"):
            d = dist * (1 - 0.3 * e)
        elif kind == "zoom_out":
            d = dist * (0.75 + 0.25 * e)
        elif kind == "pan":
            ang = -0.35 + 0.7 * e
        elif kind == "shake":
            h += 0.02 * math.sin(f * 2.1)
        cam.location = (math.sin(ang) * d, -math.cos(ang) * d, h)
        cam.keyframe_insert("location", frame=start + f)


def setup_render(W, H, out_pattern, engine, samples):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = out_pattern
    sc.render.film_transparent = False
    if engine == "CYCLES":
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.samples = samples
        # Las compilaciones de Blender de algunas distros no traen OpenImageDenoise
        sc.cycles.use_denoising = bool(JOB.get("denoise", False))
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.max_bounces = 4
    elif engine == "EEVEE":
        sc.render.engine = "BLENDER_EEVEE"
        sc.eevee.taa_render_samples = samples
        sc.eevee.use_gtao = True
        sc.eevee.use_soft_shadows = True
    else:
        sc.render.engine = "BLENDER_WORKBENCH"
        sh = sc.display.shading
        sh.light = "STUDIO"
        sh.studio_light = "basic.sl" if "basic.sl" in [l.name for l in bpy.context.preferences.studio_lights] else sh.studio_light
        sh.color_type = "MATERIAL"
        sh.show_shadows = True
        sh.show_cavity = True
        sh.cavity_type = "BOTH"
        sh.show_specular_highlight = True
        sc.display.render_aa = "16"
        sc.display_settings.display_device = "sRGB"
    try:
        sc.view_settings.view_transform = "Standard" if engine == "WORKBENCH" else "AgX"
    except TypeError:
        sc.view_settings.view_transform = "Filmic"


def main():
    mode = JOB.get("mode", "scenes")
    W, H = JOB.get("width", 1280), JOB.get("height", 720)
    fps = JOB.get("fps", 24)
    engine = JOB.get("engine", "WORKBENCH")
    samples = JOB.get("samples", 16)
    out = JOB["out_dir"]
    os.makedirs(out, exist_ok=True)
    chars = {c["id"]: c for c in JOB["characters"]}
    if mode == "character":
        clear()
        spec = JOB["characters"][0]
        ch = build_character(spec)
        bpy.context.scene.render.fps = fps
        frames = int(JOB.get("duration", 4) * fps)
        animate(ch, JOB.get("action", "idle"), fps, frames, 1, 0, 0, 110, [])
        if JOB.get("glb"):
            bpy.ops.export_scene.gltf(filepath=JOB["glb"], export_format="GLB", export_animations=True)
        build_set("studio", "day")
        lights("day")
        camera("orbit", frames, 1)
        bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, frames
        setup_render(W, H, os.path.join(out, "turn_####"), engine, samples)
        bpy.ops.render.render(animation=True)
        return
    for si, s in enumerate(JOB["scenes"]):
        clear()
        sc = bpy.context.scene
        sc.render.fps = fps
        frames = max(1, int(round(s["duration"] * fps)))
        build_set(s["background"], s.get("time_of_day", "day"))
        lights(s.get("time_of_day", "day"))
        n = max(1, len(s["actors"]))
        for ai, a in enumerate(s["actors"]):
            spec = chars[a["character"]]
            x0 = (a["from"][0] - 0.5) * 3.2
            x1 = (a["to"][0] - 0.5) * 3.2
            ch = build_character(spec, x0)
            talks = [(d["start"], d["duration"], d.get("visemes", [])) for d in s.get("dialogue", []) if d["character"] == a["character"]]
            act = a["action"]
            if talks and act == "idle":
                act = "talk"
            animate(ch, act, fps, frames, 1, x0, x1, JOB.get("tempo", 110), talks)
        camera(s.get("camera", {}).get("type", "static"), frames, 1, spread=n)
        sc.frame_start, sc.frame_end = 1, frames
        setup_render(W, H, os.path.join(out, f"s{si + 1:02d}_####"), engine, samples)
        bpy.ops.render.render(animation=True)
        if JOB.get("save_blend"):
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f"escena_{si + 1}.blend"))
        if JOB.get("glb") and si == 0:
            bpy.ops.export_scene.gltf(filepath=JOB["glb"], export_format="GLB", export_animations=True)


main()
