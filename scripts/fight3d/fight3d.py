"""fight3d — escenas de pelea 3D estilo anime en Blender 5.2 a partir de una coreografía JSON.

Construye dos luchadores originales (partes musculares ligadas a un esqueleto de 17 huesos), un ring con público y
focos, anima los cuerpos con cinemática inversa (manos y pies hacia objetivos, incluidos puntos del rival como
"@B.head"), aplica rampas de cámara lenta, monta los planos de cámara con temblor en los impactos y añade destellos
3D de impacto. Exporta además eventos (impactos, barridos, caídas) con su fotograma y posición en pantalla para la
post-producción y el sonido.

Uso (headless):
    blender5 -b -P scripts/fight3d/fight3d.py -- coreografia.json salida.blend eventos.json
"""
import json
import math
import sys

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion, Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
CHOREO, OUT_BLEND, OUT_EVENTS = ARGS[0], ARGS[1], ARGS[2]
C = json.load(open(CHOREO, encoding="utf-8"))
FPS = C.get("fps", 24)
UP = Vector((0, 0, 1))

# ------------------------------------------------------------------ utilidades


def ease(u, kind):
    u = min(1.0, max(0.0, u))
    if kind == "in":        # acelera hacia el contacto (golpes secos)
        return u * u * u
    if kind == "out":       # frena al llegar (recogidas, reacciones)
        return 1 - (1 - u) ** 3
    if kind == "lin":
        return u
    return u * u * (3 - 2 * u)


def lerp(a, b, e):
    if isinstance(a, (list, tuple)):
        return [x + (y - x) * e for x, y in zip(a, b)]
    return a + (b - a) * e


def rot_about(v, axis, deg):
    return Quaternion(axis, math.radians(deg)) @ v


def frame_matrix(origin, ydir, ref):
    y = ydir.normalized()
    z = ref - y * ref.dot(y)
    if z.length < 1e-5:
        z = Vector((0, 0, 1)) if abs(y.z) < 0.9 else Vector((1, 0, 0))
        z = z - y * z.dot(y)
    z.normalize()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = origin
    return m


def ik2(s, t, a, b, pole):
    d_vec = t - s
    d = max(1e-4, min(d_vec.length, (a + b) * 0.999))
    u = d_vec.normalized()
    cos_a = max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d)))
    v = pole - u * pole.dot(u)
    if v.length < 1e-5:
        v = UP - u * UP.dot(u)
    v.normalize()
    joint = s + u * (a * cos_a) + v * (a * math.sqrt(max(0.0, 1 - cos_a * cos_a)))
    end = s + u * d
    return joint, end


# ------------------------------------------------------------------ tiempo (cámara lenta)

def build_timemap():
    tau, taus = 0.0, []
    end = C["tau_end"]
    while tau <= end + 1e-6:
        taus.append(tau)
        sp = 1.0
        for s in C.get("speed", []):
            if s["from"] <= tau < s["to"]:
                sp = s["speed"]
        tau += sp / FPS
    return taus


TAUS = build_timemap()
NFR = len(TAUS)


def frame_of(tau):
    best = min(range(NFR), key=lambda i: abs(TAUS[i] - tau))
    return best + 1


# ------------------------------------------------------------------ esqueleto y poses

PARAMS = ["root", "yaw_off", "pelvis_h", "shift", "lean", "roll", "twist", "pelvis_yaw", "head_tilt", "head_turn",
          "handL", "handR", "footL", "footR", "foot_yawL", "foot_yawR", "knee_poleL", "knee_poleR",
          "elbow_poleL", "elbow_poleR", "bob"]
DEFAULTS = {"yaw_off": 0.0, "pelvis_h": 0.86, "shift": [0, 0], "lean": 10.0, "roll": 0.0, "twist": 0.0,
            "pelvis_yaw": 0.0, "head_tilt": 8.0, "head_turn": 0.0, "foot_yawL": 10.0, "foot_yawR": -45.0,
            "knee_poleL": [1, -0.15, 0], "knee_poleR": [1, 0.15, 0], "elbow_poleL": [-0.3, -0.6, -1],
            "elbow_poleR": [-0.3, 0.6, -1], "bob": 0.0}
SKEL = {}       # skeletons computed per fighter per frame index


class Fighter:
    def __init__(self, name, spec):
        self.name, self.spec = name, spec
        d = spec["dims"]
        self.d = d
        keys, state = [], dict(DEFAULTS)
        for k in sorted(spec["keys"], key=lambda k: k["t"]):
            state = {**state, **{p: v for p, v in k.items() if p not in ("t", "ease")}}
            keys.append({"t": k["t"], "ease": k.get("ease", "io"), **state})
        self.keys = keys

    # raíz y orientación (el luchador siempre mira al rival + yaw_off)
    def root_at(self, tau, other):
        p = self.interp_raw(tau)
        r = Vector((p["root"][0], p["root"][1], 0))
        if other is not None:
            o = other.interp_raw(tau)["root"]
            yaw = math.degrees(math.atan2(o[1] - r.y, o[0] - r.x)) + p["yaw_off"]
        else:
            yaw = p["yaw_off"]
        return r, yaw

    def interp_raw(self, tau):
        ks = self.keys
        if tau <= ks[0]["t"]:
            return ks[0]
        if tau >= ks[-1]["t"]:
            return ks[-1]
        for k0, k1 in zip(ks, ks[1:]):
            if k0["t"] <= tau <= k1["t"]:
                e = ease((tau - k0["t"]) / max(1e-6, k1["t"] - k0["t"]), k1["ease"])
                out = {}
                for p in PARAMS:
                    a, b = k0.get(p), k1.get(p)
                    if isinstance(a, (str, dict)) or isinstance(b, (str, dict)):
                        out[p] = b if e > 0.5 else a
                    elif a is None:
                        out[p] = b
                    else:
                        out[p] = lerp(a, b, e)
                return out
        return ks[-1]


def local_basis(yaw):
    f = Vector((math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0))
    r = f.cross(UP).normalized()
    return f, r


def to_world(root, yaw, loc):
    f, r = local_basis(yaw)
    return root + f * loc[0] + r * loc[1] + UP * loc[2]


def to_local(root, yaw, w):
    f, r = local_basis(yaw)
    v = w - root
    return [v.dot(f), v.dot(r), v.z]


FIGHTERS = {n: Fighter(n, s) for n, s in C["fighters"].items()}
ORDER = C.get("order", list(FIGHTERS))


def opponent(name):
    return next((FIGHTERS[n] for n in FIGHTERS if n != name), None)


def resolve_target(fname, spec, tau, root, yaw):
    """Objetivo local de una mano/pie: lista local o referencia "@B.head" (+ "off" local)."""
    if isinstance(spec, dict):
        ref, off = spec["ref"], spec.get("off", [0, 0, 0])
    elif isinstance(spec, str):
        ref, off = spec, [0, 0, 0]
    else:
        return spec
    who, joint = ref[1:].split(".")
    w = skeleton_at(who, tau)["joints"][joint]
    loc = to_local(root, yaw, w)
    return [loc[0] + off[0], loc[1] + off[1], loc[2] + off[2]]


_cache = {}


def skeleton_at(name, tau):
    key = (name, round(tau, 5))
    if key in _cache:
        return _cache[key]
    F = FIGHTERS[name]
    d = F.d
    other = opponent(name)
    root, yaw = F.root_at(tau, other)
    # resolver referencias en cada clave a coordenadas locales de esa clave y luego interpolar
    ks = F.keys
    if tau <= ks[0]["t"]:
        seg = (ks[0], ks[0], 0.0)
    elif tau >= ks[-1]["t"]:
        seg = (ks[-1], ks[-1], 0.0)
    else:
        for k0, k1 in zip(ks, ks[1:]):
            if k0["t"] <= tau <= k1["t"]:
                seg = (k0, k1, ease((tau - k0["t"]) / max(1e-6, k1["t"] - k0["t"]), k1["ease"]))
                break
    k0, k1, e = seg
    p = {}
    for prm in PARAMS:
        a, b = k0.get(prm), k1.get(prm)
        if prm in ("handL", "handR", "footL", "footR"):
            ra, rb = F.root_at(k0["t"], other), F.root_at(k1["t"], other)
            a = resolve_target(name, a, k0["t"], *ra)
            b = resolve_target(name, b, k1["t"], *rb)
        p[prm] = lerp(a, b, e) if a is not None and b is not None else (b if b is not None else a)

    f, r = local_basis(yaw)
    ph = p["pelvis_h"] + p["bob"] * math.sin(2 * math.pi * 1.7 * tau + d.get("phase", 0))
    pelvis = root + f * p["shift"][0] + r * p["shift"][1] + UP * ph
    f_p = rot_about(f, UP, p["pelvis_yaw"])
    r_p = f_p.cross(UP).normalized()
    f_c = rot_about(f, UP, p["twist"])
    r_c = f_c.cross(UP).normalized()
    spine = rot_about(UP, r_c, -p["lean"])         # lean > 0 = hacia delante (regla de la mano derecha sobre el eje derecho)
    spine = rot_about(spine, f_c, p["roll"]).normalized()
    r_c = f_c.cross(spine).normalized()
    f_c = spine.cross(r_c).normalized()
    waist = pelvis + spine * 0.10
    chest = waist + spine * 0.14
    neck = chest + spine * d["chest"]
    sh_c = neck - spine * 0.04
    shL, shR = sh_c - r_c * d["shoulder"], sh_c + r_c * d["shoulder"]
    head_up = rot_about(spine, r_c, -p["head_tilt"]).normalized()   # head_tilt > 0 = barbilla abajo
    look = rot_about(f_c, head_up, p["head_turn"])
    neck_top = neck + head_up * d["neck"]
    head = neck_top + head_up * d["head"]
    hipL, hipR = pelvis - r_p * d["hip"] - spine * 0.05, pelvis + r_p * d["hip"] - spine * 0.05
    J = {"pelvis": pelvis, "waist": waist, "chest": chest, "neck": neck, "neck_top": neck_top, "head": head,
         "shoulderL": shL, "shoulderR": shR, "hipL": hipL, "hipR": hipR}
    for side, sh, sgn in (("L", shL, -1), ("R", shR, 1)):
        t = to_world(root, yaw, p["hand" + side])
        pl = p["elbow_pole" + side]
        pole = f * pl[0] + r * pl[1] + UP * pl[2]
        el, wr = ik2(sh, t, d["uarm"], d["farm"], pole)
        J["elbow" + side], J["wrist" + side] = el, wr
        J["hand" + side] = wr + (wr - el).normalized() * 0.05
    for side, hip in (("L", hipL), ("R", hipR)):
        t = to_world(root, yaw, p["foot" + side])
        t.z = max(t.z, 0.06)
        pl = p["knee_pole" + side]
        pole = f * pl[0] + r * pl[1] + UP * pl[2]
        kn, an = ik2(hip, t, d["thigh"], d["shin"], pole)
        J["knee" + side], J["ankle" + side] = kn, an
        fdir = rot_about(f, UP, p["foot_yaw" + side])
        if an.z > 0.25:     # pie en el aire: apunta en la dirección de la espinilla (empeine)
            fdir = (an - kn).normalized() * 0.6 + fdir * 0.4
        J["toe" + side] = an + fdir.normalized() * 0.2
        J["foot" + side] = an
    frames = {
        "pelvis": frame_matrix(pelvis, spine * 0.4 + UP * 0.6, f_p),
        "waist": frame_matrix(waist, spine, f_c),
        "chest": frame_matrix(chest, spine, f_c),
        "neck": frame_matrix(neck, head_up, look),
        "head": frame_matrix(neck_top, head_up, look),
    }
    for s in "LR":
        frames["uarm" + s] = frame_matrix(J["shoulder" + s], J["elbow" + s] - J["shoulder" + s], f_c)
        frames["farm" + s] = frame_matrix(J["elbow" + s], J["wrist" + s] - J["elbow" + s], f_c)
        frames["hand" + s] = frame_matrix(J["wrist" + s], J["wrist" + s] - J["elbow" + s], UP)
        frames["thigh" + s] = frame_matrix(J["hip" + s], J["knee" + s] - J["hip" + s], f_p)
        frames["shin" + s] = frame_matrix(J["knee" + s], J["ankle" + s] - J["knee" + s], f_p)
        frames["foot" + s] = frame_matrix(J["ankle" + s], J["toe" + s] - J["ankle" + s], UP)
    res = {"joints": J, "frames": frames, "root": root, "yaw": yaw}
    _cache[key] = res
    return res


# ------------------------------------------------------------------ escena

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, NFR
    sc.render.resolution_x, sc.render.resolution_y = C.get("resolution", [1280, 720])
    sc.eevee.taa_render_samples = C.get("samples", 12)
    sc.render.film_transparent = False
    return sc


MATS = {}


def mat(name, color, emission=None, alpha=None):
    key = name
    if key in MATS:
        return MATS[key]
    m = bpy.data.materials.new(name)
    if hasattr(m, "use_nodes"):
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*srgb(color), 1)
    bsdf.inputs["Roughness"].default_value = 0.6
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*srgb(emission), 1)
        bsdf.inputs["Emission Strength"].default_value = 4.0
    MATS[key] = m
    return m


def srgb(c):
    if isinstance(c, str):
        c = [int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def ellipsoid(name, radii, center, material, parent=None, rot=None, seg=(24, 14), coll=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=1.0)
    M = Matrix.Translation(Vector(center))
    if rot:
        M = M @ rot
    M = M @ Matrix.Diagonal((*radii, 1.0))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    ob = link(bpy.data.objects.new(name, me), coll)
    me.materials.append(material)
    if parent:
        ob.parent = parent
    return ob


def cone(name, r1, depth, base, direction, material, parent=None, coll=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=r1, radius2=0.0, depth=depth)
    q = Vector((0, 0, 1)).rotation_difference(Vector(direction).normalized())
    M = Matrix.Translation(Vector(base) + Vector(direction).normalized() * depth / 2) @ q.to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me), coll)
    me.materials.append(material)
    if parent:
        ob.parent = parent
    return ob


BONES = ["pelvis", "waist", "chest", "neck", "head", "uarmL", "farmL", "handL", "uarmR", "farmR", "handR",
         "thighL", "shinL", "footL", "thighR", "shinR", "footR"]


def build_fighter(F):
    s, d = F.spec, F.d
    coll = bpy.data.collections.new("Luchador_" + F.name)
    bpy.context.scene.collection.children.link(coll)
    m = d.get("muscle", 1.0)
    skin, pants, wrap, hair = (mat(f"{F.name}_skin", s["skin"]), mat(f"{F.name}_pants", s["pants"]),
                               mat(f"{F.name}_wrap", s["wraps"]), mat(f"{F.name}_hair", s["hair"]))
    belt, white, dark = mat(f"{F.name}_belt", s.get("belt", "#111111")), mat("eye_white", "#f4f4f4"), mat("ink", "#141018")
    B = {}
    for b in BONES:
        e = link(bpy.data.objects.new(f"{F.name}_{b}", None), coll)
        e.empty_display_size = 0.05
        e.rotation_mode = "QUATERNION"
        B[b] = e
    P = lambda *a, **k: ellipsoid(*a, coll=coll, **k)          # noqa: E731
    n = F.name
    # pelvis / pantalón
    P(f"{n}_hips", (0.165 * m, 0.13, 0.125), (0, 0.0, 0), pants, B["pelvis"])
    P(f"{n}_belt", (0.172 * m, 0.035, 0.13), (0, 0.1, 0), belt, B["pelvis"])
    # abdomen y abdominales
    P(f"{n}_abdomen", (0.135 * m, 0.11, 0.105), (0, 0.07, 0), skin, B["waist"])
    for i in range(3):
        for sx in (-1, 1):
            P(f"{n}_abs{i}{sx}", (0.033, 0.024, 0.02), (sx * 0.036, 0.025 + 0.052 * i, 0.088), skin, B["waist"])
    # pecho, pectorales, dorsales, trapecio
    P(f"{n}_ribs", (0.19 * m, 0.17, 0.125), (0, 0.16, 0), skin, B["chest"])
    for sx in (-1, 1):
        P(f"{n}_pec{sx}", (0.09 * m, 0.068, 0.055), (sx * 0.078, 0.205, 0.075), skin, B["chest"])
        P(f"{n}_lat{sx}", (0.065 * m, 0.15, 0.09), (sx * 0.15 * m, 0.13, -0.02), skin, B["chest"])
    P(f"{n}_traps", (0.14 * m, 0.065, 0.075), (0, 0.29, -0.03), skin, B["chest"])
    # cuello y cabeza
    nk = d.get("neck_r", 0.062)
    P(f"{n}_neck", (nk, 0.085, nk), (0, 0.05, 0), skin, B["neck"])
    P(f"{n}_skull", (0.1, 0.122, 0.11), (0, 0.115, 0), skin, B["head"])
    P(f"{n}_jaw", (0.084, 0.06, 0.08), (0, 0.055, 0.03), skin, B["head"])
    P(f"{n}_nose", (0.012, 0.02, 0.016), (0, 0.098, 0.108), skin, B["head"])
    for sx in (-1, 1):
        P(f"{n}_eyew{sx}", (0.027, 0.014, 0.012), (sx * 0.038, 0.122, 0.094), white, B["head"])
        P(f"{n}_iris{sx}", (0.011, 0.012, 0.006), (sx * 0.035, 0.12, 0.104), dark, B["head"])
        P(f"{n}_brow{sx}", (0.032, 0.008, 0.011), (sx * 0.04, 0.146, 0.097), hair, B["head"],
          rot=Matrix.Rotation(math.radians(-16 * sx), 4, "Z"))
    P(f"{n}_mouth", (0.026, 0.004, 0.006), (0, 0.058, 0.107), dark, B["head"])
    if s.get("hair_style") == "spiky":
        spikes = [((0, 0.2, -0.02), (0, 1, -0.5)), ((0.05, 0.19, 0.0), (0.5, 1, -0.4)),
                  ((-0.05, 0.19, 0.0), (-0.5, 1, -0.4)), ((0, 0.17, -0.07), (0, 0.6, -1)),
                  ((0.07, 0.16, -0.05), (0.8, 0.6, -0.8)), ((-0.07, 0.16, -0.05), (-0.8, 0.6, -0.8)),
                  ((0.03, 0.21, 0.05), (0.2, 1, 0.5)), ((-0.03, 0.21, 0.05), (-0.2, 1, 0.5)),
                  ((0.09, 0.12, -0.04), (1, 0.2, -0.6)), ((-0.09, 0.12, -0.04), (-1, 0.2, -0.6))]
        for i, (base, dr) in enumerate(spikes):
            cone(f"{n}_spike{i}", 0.05, 0.17, base, dr, hair, B["head"], coll=coll)
        P(f"{n}_haircap", (0.105, 0.09, 0.115), (0, 0.16, -0.01), hair, B["head"])
    else:
        P(f"{n}_beard", (0.085, 0.055, 0.06), (0, 0.035, 0.06), hair, B["head"])
        P(f"{n}_band", (0.104, 0.022, 0.114), (0, 0.17, 0), wrap, B["head"])
    # brazos
    for sx, s_ in ((-1, "L"), (1, "R")):
        ua, fa = d["uarm"], d["farm"]
        P(f"{n}_delt{s_}", (0.078 * m, 0.075, 0.078 * m), (0, 0.03, 0), skin, B["uarm" + s_])
        P(f"{n}_uarm{s_}", (0.056 * m, ua * 0.55, 0.06 * m), (0, ua / 2, 0), skin, B["uarm" + s_])
        P(f"{n}_bicep{s_}", (0.046 * m, ua * 0.3, 0.042 * m), (0, ua * 0.45, 0.026), skin, B["uarm" + s_])
        P(f"{n}_elbow{s_}", (0.046 * m, 0.046, 0.046 * m), (0, 0, 0), skin, B["farm" + s_])
        P(f"{n}_farm{s_}", (0.052 * m, fa * 0.56, 0.048 * m), (0, fa * 0.45, 0), skin, B["farm" + s_])
        P(f"{n}_wrap{s_}", (0.046 * m, 0.055, 0.046 * m), (0, fa * 0.88, 0), wrap, B["farm" + s_])
        P(f"{n}_fist{s_}", (0.052 * m ** 0.5, 0.058, 0.048 * m ** 0.5), (0, 0.045, 0), wrap, B["hand" + s_])
    # piernas
    long_pants = s.get("pants_style", "long") == "long"
    for s_ in "LR":
        th, sh = d["thigh"], d["shin"]
        P(f"{n}_thigh{s_}", (0.088 * m, th * 0.57, 0.092 * m), (0, th / 2, 0), pants, B["thigh" + s_])
        P(f"{n}_knee{s_}", (0.065 * m, 0.065, 0.065 * m), (0, 0, 0), pants if long_pants else skin, B["shin" + s_])
        P(f"{n}_shin{s_}", (0.062 * m, sh * 0.56, 0.066 * m), (0, sh / 2, 0), pants if long_pants else skin, B["shin" + s_])
        P(f"{n}_foot{s_}", (0.045, 0.115, 0.034), (0, 0.085, 0), skin, B["foot" + s_])
    return B


def build_arena():
    coll = bpy.data.collections.new("Arena")
    bpy.context.scene.collection.children.link(coll)
    A = C.get("arena", {})
    R = A.get("radius", 3.6)
    # suelo octogonal (lona) y base
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=8, radius=R)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 8, 3, "Z"))
    me = bpy.data.meshes.new("lona")
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new("Lona", me), coll)
    me.materials.append(mat("lona", A.get("canvas", "#c9c2b6")))
    # logotipo central (círculo) y suelo exterior
    ellipsoid("Logo", (1.1, 1.1, 0.004), (0, 0, 0.002), mat("logo", A.get("logo", "#8f1d1d")), coll=coll, seg=(48, 8))
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=30)
    me = bpy.data.meshes.new("suelo")
    bm.to_mesh(me)
    bm.free()
    fl = link(bpy.data.objects.new("SueloExterior", me), coll)
    fl.location.z = -0.45
    me.materials.append(mat("suelo", "#1a1620"))
    # postes y cuerdas
    post_m, rope_m = mat("poste", "#2b2b33"), mat("cuerda", A.get("ropes", "#d32f2f"))
    pts = [Vector((R * math.cos(math.pi / 8 + i * math.pi / 4), R * math.sin(math.pi / 8 + i * math.pi / 4), 0))
           for i in range(8)]
    for i, p in enumerate(pts):
        ellipsoid(f"Poste{i}", (0.07, 0.07, 0.75), (p.x, p.y, 0.6), post_m, coll=coll, seg=(12, 8))
    for h in (0.55, 0.9, 1.25):
        for i in range(8):
            a, b = pts[i], pts[(i + 1) % 8]
            mid = (a + b) / 2
            L = (b - a).length
            rot = Vector((0, 1, 0)).rotation_difference((b - a).normalized()).to_matrix().to_4x4()
            ellipsoid(f"Cuerda{h}_{i}", (0.025, L / 2, 0.025), (0, 0, 0), rope_m, coll=coll, seg=(8, 6))
            o = bpy.data.objects[f"Cuerda{h}_{i}"]
            o.matrix_world = Matrix.Translation(Vector((mid.x, mid.y, h))) @ rot
    # público (siluetas en gradas): una sola malla para que el render sea rápido
    import random
    rnd = random.Random(7)
    bm = bmesh.new()
    crowd_mats = [mat("publico1", "#2a2333"), mat("publico2", "#332a3d"), mat("publico3", "#241d2c")]
    k = 0
    for row in range(4):
        rad = R + 1.8 + row * 0.9
        n = int(2 * math.pi * rad / 0.55)
        for i in range(n):
            ang = 2 * math.pi * i / n + rnd.uniform(-0.04, 0.04)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            z = -0.45 + row * 0.45
            sc = rnd.uniform(0.9, 1.1)
            for radii, cz in (((0.2 * sc, 0.2 * sc, 0.33 * sc), z + 0.35), ((0.1 * sc, 0.1 * sc, 0.11 * sc), z + 0.82 * sc)):
                res = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0)
                bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector((x, y, cz))) @ Matrix.Diagonal((*radii, 1.0)),
                                    verts=res["verts"])
                for f in {f for v in res["verts"] for f in v.link_faces}:
                    f.material_index = k % 3
                    f.smooth = True
            k += 1
    me = bpy.data.meshes.new("publico")
    bm.to_mesh(me)
    bm.free()
    for m_ in crowd_mats:
        me.materials.append(m_)
    link(bpy.data.objects.new("Publico", me), coll)
    # luces
    def light(name, kind, energy, color, loc, look=(0, 0, 0.8), size=None, spot=None):
        L = bpy.data.lights.new(name, kind)
        L.energy = energy
        L.color = srgb(color)
        if size and kind == "AREA":
            L.size = size
        if spot and kind == "SPOT":
            L.spot_size = math.radians(spot)
            L.spot_blend = 0.4
        ob = link(bpy.data.objects.new(name, L), coll)
        ob.location = loc
        ob.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return ob
    light("FocoCenital", "SPOT", A.get("key_power", 4200), "#fff1dc", (0, 0, 7.5), (0, 0, 0), spot=55)
    light("RimCian", "AREA", 1400, "#3fd2ff", (3.5, 3.5, 3.0), (0, 0, 1.2), size=2.5)
    light("RimNaranja", "AREA", 1300, "#ff7a2f", (-3.6, -3.2, 2.6), (0, 0, 1.2), size=2.5)
    light("Relleno", "AREA", 260, "#9a8cff", (0, -6, 2.0), (0, 0, 1.0), size=6)
    w = bpy.data.worlds.new("Mundo")
    bpy.context.scene.world = w
    if hasattr(w, "use_nodes"):
        w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (*srgb("#0b0812"), 1)
    bg.inputs[1].default_value = 1.0


# ------------------------------------------------------------------ cámaras, impactos y animación

def resolve_point(spec, tau):
    if isinstance(spec, str):
        if spec == "mid":
            a = skeleton_at("A", tau)["joints"]["chest"]
            b = skeleton_at("B", tau)["joints"]["chest"]
            return (a + b) / 2
        who, j = spec[1:].split(".")
        return skeleton_at(who, tau)["joints"][j].copy()
    if isinstance(spec, dict):
        p = resolve_point(spec["ref"], tau)
        return p + Vector(spec.get("off", [0, 0, 0]))
    return Vector(spec)


def shake_at(frame):
    off = Vector((0, 0, 0))
    for imp in C.get("impacts", []):
        fi = frame_of(imp["t"])
        dt = (frame - fi) / FPS
        if 0 <= dt < 0.45:
            amp = {"block": 0.012, "hit": 0.03, "big": 0.075, "land": 0.045, "whiff": 0.0}[imp["kind"]]
            k = amp * math.exp(-dt * 9)
            off += Vector((math.sin(frame * 2.7 + 1), math.sin(frame * 3.9 + 2), math.sin(frame * 3.1))) * k
    return off


def build_cameras():
    sc = bpy.context.scene
    cams = []
    for i, sh in enumerate(C["shots"]):
        cd = bpy.data.cameras.new(f"Cam{i + 1}")
        cd.lens = sh.get("lens", 35)
        cd.clip_end = 200
        cam = link(bpy.data.objects.new(f"Plano{i + 1}", cd))
        cam.rotation_mode = "QUATERNION"
        f0, f1 = frame_of(sh["from"]), frame_of(sh["to"])
        for fr in range(max(1, f0 - 1), min(NFR, f1 + 1) + 1):
            tau = TAUS[fr - 1]
            u = ease((tau - sh["from"]) / max(1e-6, sh["to"] - sh["from"]), sh.get("ease", "io"))
            if "orbit" in sh:
                ob = sh["orbit"]
                ang = math.radians(lerp(ob["a0"], ob["a1"], u))
                rad = lerp(ob["r0"], ob["r1"], u)
                ctr = Vector(ob.get("center", [0, 0, 0]))
                pos = ctr + Vector((rad * math.cos(ang), rad * math.sin(ang), lerp(ob["z0"], ob["z1"], u)))
            else:
                pos = Vector(lerp(sh["pos0"], sh["pos1"], u))
            look = resolve_point(sh.get("look0", "mid"), tau).lerp(resolve_point(sh.get("look1", sh.get("look0", "mid")), tau), u)
            pos = pos + shake_at(fr)
            cam.location = pos
            cam.rotation_quaternion = (look - pos).to_track_quat("-Z", "Y")
            cam.keyframe_insert("location", frame=fr)
            cam.keyframe_insert("rotation_quaternion", frame=fr)
        m = sc.timeline_markers.new(f"plano{i + 1}", frame=f0)
        m.camera = cam
        cams.append((cam, f0, f1))
    sc.camera = cams[0][0]
    return cams


def camera_for(frame, cams):
    cur = cams[0][0]
    for cam, f0, f1 in cams:
        if frame >= f0:
            cur = cam
    return cur


def build_impacts(cams):
    sc = bpy.context.scene
    ring_m = mat("impacto", "#fff6d0", emission="#ffe9a8")
    spike_m = mat("chispa", "#ffffff", emission="#ffffff")
    events = []
    for n, imp in enumerate(C.get("impacts", [])):
        fi = frame_of(imp["t"])
        pos = resolve_point(imp["at"], imp["t"])
        cam = camera_for(fi, cams)
        sc.frame_set(fi)
        co = world_to_camera_view(sc, cam, pos)
        events.append({"kind": imp["kind"], "frame": fi, "t": imp["t"], "screen": [co.x, 1 - co.y],
                       "label": imp.get("label", "")})
        if imp["kind"] in ("whiff",):
            continue
        size = {"block": 0.18, "hit": 0.3, "big": 0.55, "land": 0.4}[imp["kind"]]
        grp = link(bpy.data.objects.new(f"Impacto{n}", None))
        grp.location = pos
        cam_dir = (cam.matrix_world.translation - pos).normalized()
        grp.rotation_euler = cam_dir.to_track_quat("Z", "Y").to_euler()
        ring = ellipsoid(f"Onda{n}", (1, 1, 0.08), (0, 0, 0), ring_m, grp, seg=(32, 8))
        ring.scale = (0, 0, 0)
        spikes = []
        for k in range(8):
            a = 2 * math.pi * k / 8 + 0.3
            sp = cone(f"Chispa{n}_{k}", 0.08, 1.0, (0, 0, 0), (math.cos(a), math.sin(a), 0), spike_m, grp)
            sp.scale = (0, 0, 0)
            spikes.append(sp)
        for ob in [ring] + spikes:
            ob.keyframe_insert("scale", frame=max(1, fi - 1))
        steps = [(0, 0.35), (1, 0.75), (2, 1.0), (3, 1.15), (4, 1.2)]
        for df, sz in steps:
            for ob in [ring] + spikes:
                s = size * sz
                ob.scale = (s, s, s) if ob is ring else (s * (0.9 - 0.12 * df),) * 3
                ob.keyframe_insert("scale", frame=fi + df)
        for ob in [ring] + spikes:
            ob.scale = (0, 0, 0)
            ob.keyframe_insert("scale", frame=fi + 5)
    for w in C.get("whooshes", []):
        events.append({"kind": "whoosh", "frame": frame_of(w["t"]), "t": w["t"], "len": w.get("len", 0.15),
                       "end_frame": frame_of(w["t"] + w.get("len", 0.15))})
    for tl in C.get("titles", []):
        events.append({"kind": "title", "frame": frame_of(tl["t"]), "end_frame": frame_of(tl["t"] + tl["dur"]),
                       "text": tl["text"], "style": tl.get("style", "round")})
    for b in C.get("bells", []):
        events.append({"kind": "bell", "frame": frame_of(b["t"])})
    for sh in C["shots"]:
        events.append({"kind": "cut", "frame": frame_of(sh["from"])})
    return events


def animate(bones):
    for fr in range(1, NFR + 1):
        tau = TAUS[fr - 1]
        for name in ORDER:
            sk = skeleton_at(name, tau)
            for b, e in bones[name].items():
                M = sk["frames"][b]
                e.location = M.translation
                e.rotation_quaternion = M.to_quaternion()
                e.keyframe_insert("location", frame=fr)
                e.keyframe_insert("rotation_quaternion", frame=fr)


def main():
    reset_scene()
    build_arena()
    bones = {n: build_fighter(FIGHTERS[n]) for n in ORDER}
    animate(bones)
    cams = build_cameras()
    events = build_impacts(cams)
    sc = bpy.context.scene
    sc.view_settings.view_transform = "Standard"
    if C.get("motion_blur", True):
        sc.render.use_motion_blur = True
        sc.render.motion_blur_shutter = C.get("motion_blur_shutter", 0.2)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    fighter_meshes = [o.name for o in bpy.data.objects if o.type == "MESH" and o.name[:2] in ("A_", "B_")]
    arena_meshes = [o.name for o in bpy.data.objects if o.type == "MESH" and o.users_collection
                    and o.users_collection[0].name == "Arena"]
    json.dump({"fps": FPS, "frames": NFR, "taus": TAUS, "events": events,
               "fighter_meshes": fighter_meshes, "arena_meshes": arena_meshes}, open(OUT_EVENTS, "w"))
    print("@@JSON@@" + json.dumps({"ok": True, "frames": NFR, "seconds": round(NFR / FPS, 2),
                                   "objects": len(bpy.data.objects), "events": len(events)}))


main()
