# Prepara datos.json para la plantilla 3D: escenas, subtítulos por palabra, envolvente de voz (lip-sync),
# beats de la música y eventos sincronizados con la narración. Ejecutar desde la raíz del repo.
import json, subprocess
import numpy as np
from pathlib import Path

V2 = Path("projects/datos-curiosos-3d/v2"); A = V2 / "audio"
FPS, OFF, SR = 30, 0.35, 48000          # OFF: la voz empieza 0,35 s después del primer frame
STRETCH = 0.962                         # música un 4 % más lenta: su final cae con la última frase

def load(path, sr=SR):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32).copy()

W = json.load(open(A / "transcripcion.json", encoding="utf-8"))["voz_b.mp3"]
for w in W: w["s"] += OFF; w["e"] += OFF

# ---- palabras para subtítulos (cifras unidas, ortografía del guion)
fix = {"bamboo.": "bambú.", "1.": "1", "2.": "2", "3.": "3", "4.": "4", "5.": "5"}
words = []
i = 0
while i < len(W):
    w = dict(W[i]); t = fix.get(w["w"], w["w"])
    if i + 1 < len(W) and W[i + 1]["w"].startswith(".000"):
        t = t + "." + "000" + W[i + 1]["w"][4:]; w["e"] = W[i + 1]["e"]; i += 1
    words.append(dict(w=t, s=round(w["s"], 3), e=round(w["e"], 3))); i += 1

def at(word, after=0.0, n=0):
    hits = [w for w in words if w["w"].lower().strip("¿?¡!.,") == word.lower() and w["s"] >= after]
    return hits[n]

KEY = {"tres", "corazones", "corazones.", "planeta", "cinco", "azul.", "miel", "3.000", "egipto", "venus,", "243", "225",
       "rayo", "30.000", "veces", "sol.", "panda", "14", "horas", "bambú.", "comer.", "sorprendió", "comentarios", "suscríbete"}
for w in words:
    w["k"] = 1 if w["w"].lower().strip("¿?¡!.,") in {k.strip("¿?¡!.,") for k in KEY} else 0

# ---- límites de escena: 0,1 s antes de «Número…»/«Y el número…»/«¿Cuál…»
starts = [0.0, at("número", 10)["s"], at("número", 20)["s"], at("número", 33)["s"], at("número", 45)["s"],
          at("y", 54)["s"], at("cuál", 62)["s"]]
starts = [0.0] + [s - 0.1 for s in starts[1:]]
total = words[-1]["e"] + 1.9
F = [round(s * FPS) for s in starts] + [round(total * FPS)]
scenes = [dict(start=F[k] / FPS, frames=F[k + 1] - F[k], dur=(F[k + 1] - F[k]) / FPS) for k in range(7)]

# ---- eventos (tiempo global, s)
E = {
  "heartsTeaser": at("tres")["s"], "planetTeaser": at("planeta")["s"], "dayYearTeaser": at("día")["s"],
  "titleSlam": at("cinco")["s"], "mindBlown": at("volar")["s"],
  "octoReveal": at("pulpo")["s"] - 0.3, "xray": at("tres", 12)["s"], "gills": at("dos", 14)["s"],
  "third": at("tercero")["s"], "riser1": at("loco")["s"] - 0.3, "blue": at("azul")["s"],
  "honey": at("miel", 23)["s"], "egypt": at("egipto")["s"] - 0.5, "years": at("3.000")["s"], "good": at("buen")["s"],
  "venus": at("venus")["s"], "dayGtYear": at("día", 35)["s"], "day243": at("243")["s"], "year225": at("225")["s"],
  "orbitDone": at("sol", 44)["s"],
  "strike1": at("rayo")["s"], "deg": at("30.000")["s"], "strike2": at("grados")["s"], "x5": at("cinco", 50)["s"],
  "sunCmp": at("superficie")["s"],
  "panda": at("panda")["s"], "hours": at("14")["s"], "bamboo": at("bambú")["s"], "eat": at("comer")["s"],
  "recap": at("cuál")["s"], "comment": at("comentarios")["s"], "subscribe": at("suscríbete")["s"],
}
E = {k: round(v, 3) for k, v in E.items()}

# ---- voz: retardo + envolvente por frame (lip-sync)
voz = load(A / "voz_b.mp3"); voz = np.concatenate([np.zeros(int(OFF * SR), np.float32), voz])
hop = SR // FPS; nfr = F[-1]
voz = np.concatenate([voz, np.zeros(max(0, nfr * hop - len(voz)), np.float32)])
env = np.array([np.sqrt(np.mean(voz[j * hop:(j + 1) * hop] ** 2) + 1e-12) for j in range(nfr)])
env = np.clip(env / np.percentile(env, 97), 0, 1.2)
env = np.convolve(env, [0.25, 0.5, 0.25], "same")

# ---- música estirada + beats
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(A / "musica_2.mp3"), "-af", f"atempo={STRETCH}", "-ar", str(SR), "-ac", "2",
                str(A / "musica.wav")], check=True)
mus = load(A / "musica.wav", 22050); h2 = 256; fr = 22050 / h2
e = np.array([np.sum(np.abs(mus[j:j + h2])) for j in range(0, len(mus) - h2, h2)]); on = np.maximum(0, np.diff(e))
bpm = 117.4 * STRETCH; period = 60 / bpm * fr
best = max(np.arange(0, period, 0.5), key=lambda ph: sum(on[int(ph + k * period)] for k in range(int((len(on) - ph) / period))))
beats = [round((best + k * period) / fr, 3) for k in range(int((len(on) - best) / period)) if (best + k * period) / fr < total]

subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(A / "voz.wav")],
               input=voz.tobytes(), check=True)
data = dict(fps=FPS, total=F[-1] / FPS, voiceOffset=OFF, scenes=scenes, words=words, events=E,
            env=[round(float(v), 3) for v in env], beats=beats, bpm=round(bpm, 2))
json.dump(data, open(V2 / "datos.json", "w", encoding="utf-8"), ensure_ascii=False)
print("total", data["total"], "s ·", F[-1], "frames · bpm", data["bpm"], "· beats", len(beats))
for k, s in enumerate(scenes): print(k, s)
print(E)
