# Banda sonora final: voz (ElevenLabs) + música con ducking + efectos sintetizados y sincronizados con datos.json.
# Ejecutar desde la raíz del repo: python projects/datos-curiosos-3d/v2/mezcla.py
import json, subprocess
import numpy as np
from pathlib import Path

V2 = Path("projects/datos-curiosos-3d/v2"); A = V2 / "audio"; SR = 48000
D = json.load(open(V2 / "datos.json", encoding="utf-8")); E = D["events"]; TOT = D["total"]
rs = np.random.default_rng(7)

def load(p):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2).copy()
def N(d): return rs.standard_normal(int(d * SR)).astype(np.float32)
def t_(d): return np.arange(int(d * SR)) / SR
def band(x, lo, hi):                      # paso banda suave por FFT
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.clip((f - lo * .7) / (lo * .3 + 1e-9), 0, 1) * np.clip((hi * 1.3 - f) / (hi * .3), 0, 1)
    return np.fft.irfft(X * m, len(x)).astype(np.float32)
def mavg(x, w):                          # media móvil rápida (suma acumulada)
    c = np.cumsum(np.concatenate([np.zeros(w // 2 + 1), x, np.zeros(w - w // 2)])); return ((c[w:w + len(x)] - c[:len(x)]) / w).astype(np.float32)
def norm(x, p=1.0): return (x / (np.max(np.abs(x)) + 1e-9) * p).astype(np.float32)
def env(n, a, r):                         # ataque lineal + caída exponencial
    t = np.arange(n) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / r)).astype(np.float32)
def reverb(x, d=1.2, wet=.25):
    ir = N(d) * np.exp(-t_(d) * 5); ir = band(ir, 200, 6000); n = len(x) + len(ir)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:n].astype(np.float32)
    out = np.zeros(n, np.float32); out[:len(x)] += x; out += norm(y, np.max(np.abs(x)) * wet * 3); return out

# ---------- efectos
def whoosh(d=.55, up=True, bright=1.0):
    n = N(d); bs = [band(n, f, f * 2) for f in (250, 500, 1000, 2000, 4000)]; t = np.linspace(0, 1, len(n))
    c = (t if up else 1 - t) * 4 * bright; out = np.zeros_like(n)
    for i, b in enumerate(bs): out += b * np.clip(1 - np.abs(c - i), 0, 1)
    return norm(out * np.sin(np.pi * t) ** 2, .8)
def boom(d=1.4, f0=110, f1=38):
    t = t_(d); ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 9)) / SR
    s = np.sin(ph) * np.exp(-t * 3.2) + band(N(d), 40, 400) * np.exp(-t * 12) * .8 + band(N(d), 2000, 9000) * np.exp(-t * 60) * .5
    return norm(reverb(s.astype(np.float32), 1.0, .2), .95)
def pop(f=700, d=.14):
    t = t_(d); return norm(np.sin(2 * np.pi * (f + f * 1.6 * t / d) * t) * np.exp(-t * 38), .7)
def ding(f=1320, d=1.2):
    t = t_(d); s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + k)) for a, k in ((1, 1), (.5, 2.76), (.25, 5.4)))
    return norm(reverb(s.astype(np.float32), .9, .15), .6)
def tick(): t = t_(.012); return norm(band(N(.012), 2500, 9000) * np.exp(-t * 400), .5)
def click(): return norm(np.concatenate([band(N(.004), 1500, 8000), np.zeros(int(.03 * SR), np.float32), band(N(.003), 1500, 8000) * .6]), .7)
def riser(d=2.0):
    t = t_(d); n = N(d); bs = [band(n, f, f * 2) for f in (300, 600, 1200, 2400, 4800)]; c = (t / d) * 4.2; out = np.zeros_like(n)
    for i, b in enumerate(bs): out += b * np.clip(1 - np.abs(c - i), 0, 1)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 1000 * (t / d) ** 2) / SR) * .3
    return norm((out + tone) * (t / d) ** 1.6, .7)
def glitch(d=.5):
    out = np.zeros(int(d * SR), np.float32); i = 0
    while i < len(out):
        L = int(rs.uniform(.015, .05) * SR); f = rs.uniform(90, 1800); tt = np.arange(L) / SR
        seg = np.sign(np.sin(2 * np.pi * f * tt)) * rs.uniform(.3, 1) if rs.random() < .6 else rs.standard_normal(L) * .6
        out[i:i + L] = seg[:len(out) - i]; i += L + int(rs.uniform(0, .02) * SR)
    return norm(np.round(out * 6) / 6, .55)
def sparkle(d=1.0, k=14):
    out = np.zeros(int(d * SR), np.float32)
    for _ in range(k):
        s = int(rs.uniform(0, d - .25) * SR); f = rs.uniform(2500, 6500); tt = t_(.25)
        out[s:s + len(tt)] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 18) * rs.uniform(.3, 1)
    return norm(out, .5)
def heartbeat():
    def th(a): t = t_(.16); return np.sin(2 * np.pi * 58 * t) * np.exp(-t * 26) * a
    out = np.zeros(int(.45 * SR), np.float32); a = th(1); b = th(.7); out[:len(a)] += a; s = int(.17 * SR); out[s:s + len(b)] += b; return norm(out, .9)
def bloop(): t = t_(.09); f = 300 + 900 * (t / .09) ** .5; return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30), .5)
def thunder(d=3.2, seed=0):
    t = t_(d); crack = band(N(d), 1500, 9000) * np.exp(-t * 18); rum = band(N(d), 30, 260) * (np.exp(-t * 1.2) * (1 + .6 * np.sin(t * 9 + seed)))
    return norm(reverb((crack * .9 + rum * 1.6).astype(np.float32), 1.6, .3), .95)
def crunch(): t = t_(.07); return norm(band(N(.07), 900, 3500) * np.exp(-t * 55), .5)
def buzz(d):
    t = t_(d); f = 215 + 6 * np.sin(2 * np.pi * 7 * t); s = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return norm(band((s * (.6 + .4 * np.sin(2 * np.pi * 23 * t))).astype(np.float32), 150, 2500), .25)
def bed(d, lo, hi, g, am=.3, rate=.2):   # ambiente: ruido filtrado con modulación lenta
    t = t_(d); return norm(band(N(d), lo, hi) * (1 - am + am * np.sin(2 * np.pi * rate * t)), g)
def chirps(d):
    out = np.zeros(int(d * SR), np.float32)
    for _ in range(int(d * 1.3)):
        s = int(rs.uniform(0, d - .4) * SR); f0 = rs.uniform(2800, 4500)
        for j in range(int(rs.integers(2, 5))):
            tt = t_(.07); f = f0 + 900 * np.sin(np.pi * tt / .07); a = int(s + j * .1 * SR)
            out[a:a + len(tt)] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / .07) * .4
    return norm(out, .3)
def applause(d):
    out = np.zeros(int(d * SR), np.float32)
    for _ in range(int(d * 45)):
        s = int(rs.uniform(0, d - .03) * SR); c = band(N(.02), 900, 3200) * np.exp(-t_(.02) * 160); out[s:s + len(c)] += c * rs.uniform(.3, 1)
    return norm(band(out, 300, 6000) * np.minimum(1, t_(d) / .8), .45)
def drone(d):
    t = t_(d); s = sum(np.sin(2 * np.pi * f * t + i) * a for i, (f, a) in enumerate(((55, .5), (82.5, .35), (110, .25), (165, .12))))
    return norm(s * (.7 + .3 * np.sin(2 * np.pi * .15 * t)) + band(N(d), 2000, 7000) * .05, .3)

# ---------- línea de tiempo
FX = []
def at(t, x, g=1.0, pan=0.0): FX.append((t, x, g, pan))
B = [s["start"] for s in D["scenes"]]
# transiciones e inicio de cada dato
at(0, glitch(.35), .45); at(.02, boom(), .55)
at(B[1] - .32, whoosh(.5), .75); at(B[2] - .34, whoosh(.45, bright=1.2), .8); at(B[3] - .6, riser(.62), .6); at(B[3], boom(1.0, 90, 35), .45)
at(B[4] - .3, glitch(.6), .5); at(B[5] - .05, boom(1.2, 120, 45), .5); at(B[5], sparkle(1.2), .5); at(B[6] - .32, whoosh(.5), .75)
for k in range(1, 6): at(B[k] + .27, boom(1.1, 130, 42), .6); at(B[k] + 1.02, whoosh(.4, False), .4)
# intro
for i, dt in enumerate((-.1, .1, .26, .42)): at(E["heartsTeaser"] + dt, pop(600 + i * 180), .55, .4)
at(E["planetTeaser"] - .15, whoosh(.6), .55, .5); at(E["dayYearTeaser"] + .3, pop(900), .45)
at(E["titleSlam"], boom(1.6, 140, 40), .9); at(E["titleSlam"] + .02, sparkle(1.4, 24), .5)
for i in range(6): at(E["titleSlam"] + .05 + i * .07, pop(800 + 300 * i, .1), .3, (i % 2) * .6 - .3)
at(E["mindBlown"], boom(1.2, 160, 50), .55); at(E["mindBlown"] + .05, pop(500), .5)
# dato 1: pulpo
at(B[1], bed(B[2] - B[1], 60, 500, .3, .4, .15), .5)
for k in range(28): at(B[1] + rs.uniform(0, B[2] - B[1] - .2), bloop(), .25, rs.uniform(-.6, .6))
at(E["octoReveal"], whoosh(.5), .4); at(E["octoReveal"] + .35, pop(300, .2), .5)
at(E["xray"], riser(.5) * .6, .5); at(E["xray"] + .1, boom(.9, 140, 50), .45)
for i in range(3): at(E["xray"] + .25 + i * .22, pop(700 + i * 220), .55)
hb = heartbeat(); t = E["xray"] + .3
while t < 20.2: at(t, hb, .5); t += 2 * np.pi / 7.5
at(E["gills"] + .1, pop(1000), .4); at(E["third"] + .05, pop(1150), .4)
at(E["riser1"], riser(E["blue"] - E["riser1"]), .55); at(E["blue"] - .02, boom(1.6, 150, 40), .85); at(E["blue"], sparkle(1.2, 20), .5)
for i in range(4): at(E["blue"] + .15 + i * .1, pop(900 + i * 150), .35, (i % 2) * .8 - .4)
# dato 2: miel
at(B[2], bed(B[3] - B[2], 200, 2500, .12, .5, 3), .5)
at(E["honey"], pop(260, .22), .8); at(E["honey"] + .05, sparkle(1.0), .45); at(E["honey"] + .1, pop(650), .5); at(E["honey"] + 1.0, pop(900), .4)
at(E["honey"] + .5, buzz(B[3] - E["honey"] - .5), .5, .3)
at(E["egypt"] - .1, whoosh(.9, False), .5); at(E["egypt"], drone(E["years"] + .4 - E["egypt"]), .6)
t = E["egypt"]
while t < E["years"] + .3: at(t, tick(), .12); t += 1 / 24
k = 0
while k < 15: at(E["years"] + k / 15, tick(), .5); k += 1
at(E["years"] + 1.0, ding(1500), .55); at(E["years"] + .4, pop(800), .4)
at(E["good"] - .05, boom(1.0, 140, 50), .55); at(E["good"] + .02, ding(1320), .45); at(E["good"] + .18, ding(1760), .4); at(E["good"] + .35, pop(700), .5)
# dato 3: Venus
at(B[3], drone(B[4] - B[3]), .7); at(B[3] + 1, sparkle(B[4] - B[3] - 1.5, 30), .25)
at(E["venus"] - .05, boom(1.0, 120, 45), .5); at(E["venus"] - .3, whoosh(.5), .45); at(E["dayGtYear"] + .1, pop(850), .45)
at(E["day243"] - .1, pop(700), .45); t = 38.6
while t < 44.8: at(t, tick(), .22); t += .13
at(E["year225"] - .1, pop(950), .45); at(38.6 + 6.2 * 225 / 243, ding(1500), .6); at(E["orbitDone"], sparkle(1.2), .4)
# dato 4: rayo
at(B[4], bed(B[5] - B[4], 2500, 12000, .3, .2, .5), .6); at(B[4], bed(B[5] - B[4], 80, 500, .25, .3, .1), .6)
for i, s in enumerate((E["strike1"], E["strike2"], E["x5"], E["sunCmp"] + .55)): at(s, thunder(3.2, i), .95 if i < 3 else .7, (i % 2) * .4 - .2)
at(E["strike1"] + .02, boom(.9, 150, 50), .45)
k = 0
while k < 24: at(E["deg"] - .1 + k * 1.3 / 24, tick(), .45); k += 1
at(E["deg"] + 1.25, ding(1700), .5); at(E["deg"] + .3, pop(800), .35)
at(E["x5"] - .02, boom(1.4, 160, 40), .75); at(E["sunCmp"] - .15, pop(700), .45); at(E["sunCmp"] + .1, whoosh(.9), .35)
# dato 5: panda
at(B[5], chirps(B[6] - B[5]), .6, .3); at(B[5], bed(B[6] - B[5], 500, 3000, .08, .5, .3), .5)
for k in range(int((B[6] - B[5]) / .35)): at(B[5] + .2 + k * .35, crunch(), .3, -.1)
at(E["panda"] - .05, boom(1.0, 120, 45), .5)
at(E["hours"] - .1, whoosh(1.9, True, 1.3), .45); k = 0
while k < 26: at(E["hours"] - .1 + k * 1.8 / 26, tick(), .5); k += 1
at(E["hours"] + 1.6, ding(1320), .5); at(E["hours"] + .5, pop(700), .4)
for i in range(3): at(E["bamboo"] + i * .15, pop(650 + i * 200), .45)
at(E["eat"] - .05, boom(1.0, 130, 45), .55); at(E["eat"] + .25, pop(600), .45)
for k in range(6): at(E["eat"] + .1 + k * .17, crunch(), .55)
# final
at(B[6], applause(TOT - B[6]), .35)
for i in range(5): at(E["recap"] + .1 + i * .17, pop(600 + i * 150), .5, (i - 2) * .2)
at(E["recap"], sparkle(1.0), .35); at(E["comment"] - .1, pop(500, .2), .5); at(E["comment"], bloop(), .4)
at(E["subscribe"] - .15, pop(700), .5); at(E["subscribe"] + .6, click(), .8); at(E["subscribe"] + .62, ding(1580), .65); at(E["subscribe"] + .85, ding(1180), .5)
at(E["subscribe"] + 1.1, pop(820), .5)

# ---------- mezcla
n = int((TOT + .5) * SR); fx = np.zeros((n, 2), np.float32)
for t0, x, g, pan in FX:
    i = int(t0 * SR); x = x[: max(0, n - i)]
    if i < 0 or not len(x): continue
    fx[i:i + len(x), 0] += x * g * np.sqrt(.5 * (1 - pan)) * 1.41; fx[i:i + len(x), 1] += x * g * np.sqrt(.5 * (1 + pan)) * 1.41
voz = load(A / "voz.wav")[:n]; voz = np.pad(voz, ((0, n - len(voz)), (0, 0)))
mus = load(A / "musica.wav")[:n]; mus = np.pad(mus, ((0, n - len(mus)), (0, 0)))
# ducking: la música baja ~8 dB cuando habla la voz (envolvente suavizada)
e = mavg(np.abs(voz).mean(1), int(.02 * SR)); act = np.clip(e / (np.percentile(e, 90) + 1e-9) * 2, 0, 1)
act = mavg(act, int(.25 * SR)); duck = 1 - .6 * act
tt = np.arange(n) / SR; lift = np.where(tt < E["titleSlam"], .7, 1.0); lift = mavg(lift, int(.1 * SR))
fade = np.clip((TOT - tt) / 1.6, 0, 1)
mix = voz * 1.0 + mus * (.42 * duck * lift * fade)[:, None] + fx * .55 * np.clip((TOT + .3 - tt) / .4, 0, 1)[:, None]
mix = np.tanh(mix * 1.1) / 1.1
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), str(A / "banda_sonora.wav")], input=mix.astype(np.float32).tobytes(), check=True)
print("ok", len(FX), "efectos ·", round(n / SR, 2), "s")
