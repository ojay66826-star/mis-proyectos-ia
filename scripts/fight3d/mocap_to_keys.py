"""Convierte una captura de movimiento (pose.json de scripts/mocap/video_pose.py) en claves de coreografía fight3d.

    python3 scripts/fight3d/mocap_to_keys.py pose.json coreografia.json --fighter A --start 1.6 --desde 0 --hasta 2.5
        [--persona 0] [--cada 0.08] [--escala auto] [--salida coreografia_mocap.json]

- Toma los 33 puntos 3D "world" (metros, origen entre las caderas) de la persona indicada.
- Define los ejes del luchador (delante, derecha, arriba) a partir de la postura media del primer medio segundo,
  así los giros posteriores (una patada giratoria) se conservan.
- Muestrea cada `--cada` s y escribe por clave: pelvis_h, lean, roll, twist, pelvis_yaw, manos y pies en
  coordenadas locales, escaladas a las medidas del luchador. Las claves sustituyen a las existentes del luchador en
  el intervalo [start, start + (hasta - desde)].
"""
import argparse
import json
import math

import numpy as np

IDX = {"nose": 0, "lsh": 11, "rsh": 12, "lwr": 15, "rwr": 16, "lhip": 23, "rhip": 24, "lan": 27, "ran": 28,
       "lkn": 25, "rkn": 26}


def load(pose_path, person):
    d = json.load(open(pose_path))
    ts, pts = [], []
    for fr in d["frames"]:
        if len(fr["people"]) > person:
            w = np.array(fr["people"][person]["world"], dtype=float)
            # MediaPipe: x derecha de la imagen, y hacia abajo, z profundidad → arriba = -y
            pts.append(np.stack([w[:, 0], -w[:, 2], -w[:, 1]], axis=1))
            ts.append(fr["t"])
    if not pts:
        raise SystemExit("La captura no contiene a esa persona.")
    P = np.array(pts)
    k = np.ones(5) / 5      # suavizado temporal ligero
    for j in range(P.shape[1]):
        for c in range(3):
            P[:, j, c] = np.convolve(np.pad(P[:, j, c], 2, mode="edge"), k, mode="valid")
    return np.array(ts), P


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def yaw_of(v, fwd, right):
    return math.degrees(math.atan2(v @ right, v @ fwd))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pose")
    ap.add_argument("choreo")
    ap.add_argument("--fighter", default="A")
    ap.add_argument("--persona", type=int, default=0)
    ap.add_argument("--start", type=float, required=True, help="segundo de la coreografía donde empieza la captura")
    ap.add_argument("--desde", type=float, default=0.0)
    ap.add_argument("--hasta", type=float, default=None)
    ap.add_argument("--cada", type=float, default=0.08)
    ap.add_argument("--salida", default=None)
    a = ap.parse_args()

    ts, P = load(a.pose, a.persona)
    C = json.load(open(a.choreo, encoding="utf-8"))
    F = C["fighters"][a.fighter]
    d = F["dims"]
    up = np.array([0, 0, 1.0])
    first = P[ts <= ts[0] + 0.5]
    right = unit(np.mean(first[:, IDX["rsh"]] - first[:, IDX["lsh"]] + first[:, IDX["rhip"]] - first[:, IDX["lhip"]], axis=0))
    right = unit(right - up * (right @ up))
    fwd = unit(np.cross(up, right))
    leg_mocap = np.median(np.linalg.norm(P[:, IDX["lhip"]] - P[:, IDX["lkn"]], axis=1)
                          + np.linalg.norm(P[:, IDX["lkn"]] - P[:, IDX["lan"]], axis=1))
    s = (d["thigh"] + d["shin"]) / max(leg_mocap, 1e-3)

    hasta = a.hasta if a.hasta is not None else ts[-1]
    keys = []
    t = a.desde
    while t <= hasta + 1e-6:
        i = int(np.argmin(np.abs(ts - t)))
        p = P[i]
        floor = min(p[IDX["lan"], 2], p[IDX["ran"], 2]) - 0.08 / s
        hipc = (p[IDX["lhip"]] + p[IDX["rhip"]]) / 2
        shc = (p[IDX["lsh"]] + p[IDX["rsh"]]) / 2
        ground = np.array([hipc[0], hipc[1], floor])
        loc = lambda v: [round(float((v - ground) @ fwd) * s, 3), round(float((v - ground) @ right) * s, 3),  # noqa: E731
                         round(float((v - ground) @ up) * s, 3)]
        spine = unit(shc - hipc)
        k = {"t": round(a.start + (t - a.desde), 3), "ease": "lin",
             "pelvis_h": round(float((hipc[2] - floor) * s) + 0.05, 3),
             "lean": round(math.degrees(math.atan2(spine @ fwd, spine @ up)), 1),
             "roll": round(math.degrees(math.atan2(spine @ right, spine @ up)), 1),
             "pelvis_yaw": round(yaw_of(np.cross(up, unit(p[IDX["rhip"]] - p[IDX["lhip"]])), fwd, right), 1),
             "twist": round(yaw_of(np.cross(up, unit(p[IDX["rsh"]] - p[IDX["lsh"]])), fwd, right), 1),
             "handL": loc(p[IDX["lwr"]]), "handR": loc(p[IDX["rwr"]]),
             "footL": loc(p[IDX["lan"]]), "footR": loc(p[IDX["ran"]]), "bob": 0.0}
        keys.append(k)
        t += a.cada

    t0, t1 = keys[0]["t"], keys[-1]["t"]
    F["keys"] = [k for k in F["keys"] if not (t0 <= k["t"] <= t1)] + keys
    F["keys"].sort(key=lambda k: k["t"])
    out = a.salida or a.choreo
    json.dump(C, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"claves": len(keys), "desde": t0, "hasta": t1, "escala": round(s, 3), "salida": out}))


if __name__ == "__main__":
    main()
