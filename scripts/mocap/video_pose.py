"""Captura de movimiento sin trajes: extrae la pose 3D (33 puntos, MediaPipe Pose Landmarker) de un video
de referencia (por ejemplo, tú grabándote al lanzar un puñetazo) y la guarda en JSON + un video de control.

Requiere el entorno aislado /opt/mocap-py (mediapipe + opencv) y el modelo /opt/mocap-models/pose_landmarker_full.task.
Uso:
    /opt/mocap-py/bin/python scripts/mocap/video_pose.py entrada.mp4 -o projects/mocap/golpe
Salida:
    <out>/pose.json       fps, tamaño y, por fotograma, 33 puntos normalizados (x, y, z, visibilidad) y en metros (world)
    <out>/control.mp4     el video con el esqueleto dibujado, para revisar la captura
El JSON sirve de referencia de timing y poses para coreografías (2D del estudio, Blender o Three.js).
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp

MODEL = "/opt/mocap-models/pose_landmarker_full.task"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--poses", type=int, default=2, help="personas a seguir (2 para una pelea)")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(a.video)
    if not cap.isOpened():
        sys.exit(f"No se pudo abrir {a.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    v = mp.tasks.vision
    opts = v.PoseLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=a.model),
                                   running_mode=v.RunningMode.VIDEO, num_poses=a.poses)
    edges = [(c.start, c.end) for c in v.PoseLandmarksConnections.POSE_LANDMARKS]
    writer = cv2.VideoWriter(str(out / "control.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    frames, detected = [], 0
    with v.PoseLandmarker.create_from_options(opts) as lm:
        i = 0
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
            res = lm.detect_for_video(img, int(i * 1000 / fps))
            people = []
            for p, pw in zip(res.pose_landmarks, res.pose_world_landmarks):
                people.append({"norm": [[round(q.x, 4), round(q.y, 4), round(q.z, 4), round(q.visibility or 0, 3)] for q in p],
                               "world": [[round(q.x, 4), round(q.y, 4), round(q.z, 4)] for q in pw]})
                pts = [(int(q.x * w), int(q.y * h)) for q in p]
                for s, e in edges:
                    cv2.line(bgr, pts[s], pts[e], (0, 220, 255), 3)
                for pt in pts:
                    cv2.circle(bgr, pt, 4, (255, 80, 40), -1)
            detected += bool(people)
            frames.append({"t": round(i / fps, 4), "people": people})
            writer.write(bgr)
            i += 1
    writer.release()
    names = [n.name.lower() for n in v.PoseLandmark]
    (out / "pose.json").write_text(json.dumps({"fps": fps, "width": w, "height": h, "landmarks": names,
                                               "frames": frames}), encoding="utf-8")
    print(json.dumps({"frames": len(frames), "frames_con_persona": detected, "json": str(out / "pose.json"),
                      "control": str(out / "control.mp4")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
