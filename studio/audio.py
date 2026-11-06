"""Audio: voces (TTS), música procedural, efectos de sonido, mezcla y lip-sync."""
from __future__ import annotations

import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

from .core import rng, which

SR = 44100

# --------------------------------------------------------------------- utilidades


def write_wav(path, data: np.ndarray, sr: int = SR):
    data = np.asarray(data, dtype=np.float32)
    if data.ndim == 1:
        data = np.stack([data, data], axis=1)
    peak = np.max(np.abs(data)) if data.size else 0
    if peak > 0.99:
        data = data / peak * 0.99
    pcm = (data * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(data.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def read_wav(path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        raw = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768
    raw = raw.reshape(-1, ch)
    if ch == 1:
        raw = np.repeat(raw, 2, axis=1)
    if sr != SR:
        idx = np.linspace(0, len(raw) - 1, int(len(raw) * SR / sr))
        raw = np.stack([np.interp(idx, np.arange(len(raw)), raw[:, c]) for c in range(2)], axis=1)
    return raw.astype(np.float32)


def duration_of(path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


# --------------------------------------------------------------------- voces
VOICE_PRESETS = {
    "fruit": dict(voice="es-419+f3", pitch=78, speed=165),
    "animal": dict(voice="es-419+f4", pitch=70, speed=160),
    "robot": dict(voice="es-419+robosoft", pitch=35, speed=150),
    "human": dict(voice="es-419", pitch=55, speed=160),
    "blob": dict(voice="es-419+f2", pitch=85, speed=170),
    "ghost": dict(voice="es-419+whisper", pitch=40, speed=130),
    "monster": dict(voice="es-419+croak", pitch=15, speed=140),
    "narrator": dict(voice="es-419", pitch=45, speed=150),
}


def voice_for(spec: dict | None) -> dict:
    if not spec:
        return dict(VOICE_PRESETS["narrator"])
    if spec.get("voice") and isinstance(spec["voice"], dict):
        return spec["voice"]
    shape = spec.get("shape")
    if shape in ("ghost",):
        v = dict(VOICE_PRESETS["ghost"])
    elif shape == "monster":
        v = dict(VOICE_PRESETS["monster"])
    else:
        v = dict(VOICE_PRESETS.get(spec.get("kind"), VOICE_PRESETS["human"]))
    if spec.get("species") == "nino":
        v.update(pitch=80, voice="es-419")
    if spec.get("species") in ("nina",):
        v.update(pitch=75, voice="es-419+f3")
    # variación determinista por personaje para distinguir voces
    r = rng(spec.get("id", "x"))
    v["pitch"] = int(max(0, min(99, v["pitch"] + r.randint(-8, 8))))
    return v


def tts(text: str, out_path, voice: dict | None = None, provider: str = "auto") -> Path:
    """Genera voz. Proveedores: espeak (local, gratis) o elevenlabs/openai (clave)."""
    from . import providers
    out_path = Path(out_path)
    voice = voice or VOICE_PRESETS["narrator"]
    if provider in ("auto", "elevenlabs", "openai"):
        try:
            res = providers.tts_cloud(text, out_path, voice, provider)
            if res:
                return res
        except Exception as e:  # noqa: BLE001
            if provider != "auto":
                raise
            print(f"[tts] proveedor en la nube falló ({e}); uso espeak-ng")
    if provider in ("auto", "piper") and piper_available():
        try:
            return tts_piper(text, out_path, voice)
        except Exception as e:  # noqa: BLE001
            if provider == "piper":
                raise
            print(f"[tts] piper falló ({e}); uso espeak-ng")
    exe = which("espeak-ng") or which("espeak")
    if not exe:
        # sin TTS: silencio con la duración estimada (para que el resto funcione)
        dur = max(0.8, len(text) * 0.07)
        write_wav(out_path, np.zeros(int(dur * SR), dtype=np.float32))
        return out_path
    raw = out_path.with_suffix(".raw.wav")
    subprocess.run([exe, "-v", voice.get("voice", "es-419"), "-p", str(voice.get("pitch", 50)),
                    "-s", str(voice.get("speed", 160)), "-w", str(raw), text], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = read_wav(raw)
    raw.unlink(missing_ok=True)
    # suavizado ligero del timbre robótico (eco corto de sala)
    data = data * 0.9 + np.roll(data, int(SR * 0.012), axis=0) * 0.1
    write_wav(out_path, data)
    return out_path


# --------------------------------------------------------------------- Piper (voz neuronal local)
PIPER_DIR = Path(__file__).resolve().parent.parent / "models" / "piper"
# voz femenina/aguda, masculina/grave y narrador (descarga: scripts/download_voices.sh)
PIPER_VOICES = {"female": ("es_MX-claude-high", 0), "male": ("es_MX-ald-medium", 0),
                "narrator": ("es_ES-davefx-medium", 0), "female2": ("es_ES-sharvard-medium", 1),
                "male2": ("es_ES-sharvard-medium", 0)}


def piper_available() -> bool:
    try:
        import piper  # noqa: F401
    except ImportError:
        return False
    return any(PIPER_DIR.glob("*.onnx"))


def _piper_model(voice: dict):
    """Elige modelo/hablante a partir del preset estilo espeak (voz +fN = femenina, tono, etc.)."""
    if voice.get("piper"):
        name, spk = (voice["piper"], voice.get("speaker", 0)) if isinstance(voice["piper"], str) else voice["piper"]
    else:
        v = voice.get("voice", "")
        pitch = voice.get("pitch", 50)
        if "whisper" in v or "croak" in v:
            key = "male2"
        elif "+f" in v or pitch >= 72:
            key = "female" if pitch < 82 else "female2"
        elif pitch <= 46:
            key = "narrator"
        else:
            key = "male"
        name, spk = PIPER_VOICES[key]
    path = PIPER_DIR / f"{name}.onnx"
    if not path.exists():
        path = next(iter(sorted(PIPER_DIR.glob("*.onnx"))))
        spk = 0
    return path, spk


def tts_piper(text: str, out_path, voice: dict) -> Path:
    """Voz natural local con Piper; el tono del preset se aplica como desplazamiento de semitonos."""
    out_path = Path(out_path)
    model, spk = _piper_model(voice)
    raw = out_path.with_suffix(".piper.wav")
    length = 160 / max(90, voice.get("speed", 160))
    cmd = [sys.executable, "-m", "piper", "-m", str(model), "-f", str(raw), "-s", str(spk),
           "--length-scale", f"{length:.3f}", "--", text]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # tono: el modelo ya es femenino/masculino; solo se ajusta lo que se sale del rango típico
    pitch = voice.get("pitch", 50)
    female = "+f" in voice.get("voice", "") or pitch >= 72
    semis = voice.get("semitones")
    if semis is None:
        semis = (pitch - (76 if female else 52)) / 7.0
        if "croak" in voice.get("voice", ""):
            semis -= 3
    semis = max(-6.0, min(6.0, semis))
    f = 2 ** (semis / 12)
    af = f"asetrate={{sr}}*{f:.4f},aresample={SR},atempo={1 / f:.4f}" if abs(semis) > 0.3 else f"aresample={SR}"
    sr_in = json.loads(Path(str(model) + ".json").read_text(encoding="utf-8"))["audio"]["sample_rate"]
    af = af.replace("{sr}", str(sr_in))
    if "whisper" in voice.get("voice", ""):
        af += ",highpass=f=300,aecho=0.6:0.5:60:0.3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ac", "2", str(out_path)], check=True)
    raw.unlink(missing_ok=True)
    return out_path


# --------------------------------------------------------------------- lip-sync
_VIS = {"a": "A", "á": "A", "e": "E", "é": "E", "i": "E", "í": "E", "y": "E", "o": "O", "ó": "O",
        "u": "U", "ú": "U", "m": "M", "b": "M", "p": "M", "f": "F", "v": "F"}


def lipsync_track(text: str, wav_path, fps: int) -> list[str]:
    """Lista de visemas por frame combinando texto + envolvente de amplitud."""
    data = read_wav(wav_path).mean(axis=1)
    n = max(1, int(len(data) / SR * fps))
    hop = len(data) / n
    rms = np.array([np.sqrt(np.mean(data[int(i * hop):int((i + 1) * hop)] ** 2) + 1e-12) for i in range(n)])
    thr = max(0.012, np.percentile(rms, 35) * 0.8)
    letters = [c for c in text.lower() if c.isalpha() or c in " ,.;!?¡¿"]
    voiced = np.where(rms > thr)[0]
    out = ["X"] * n
    if not len(voiced) or not letters:
        return out
    first, last = voiced[0], voiced[-1]
    span = max(1, last - first + 1)
    prev = "X"
    for i in range(first, last + 1):
        li = letters[min(len(letters) - 1, int((i - first) / span * len(letters)))]
        v = _VIS.get(li)
        if li in " ,.;!?¡¿":
            v = "X" if rms[i] < thr * 1.5 else prev
        if v is None:
            v = "E" if prev in ("X", "M") else prev
        if rms[i] < thr:
            v = "X"
        out[i] = v
        prev = v
    # evita parpadeo de boca de un solo frame
    for i in range(1, n - 1):
        if out[i] != out[i - 1] and out[i] != out[i + 1] and out[i - 1] == out[i + 1]:
            out[i] = out[i - 1]
    return out


# --------------------------------------------------------------------- síntesis
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _env(n, a=0.01, d=0.1, s=0.7, r=0.2, sr=SR):
    a_, d_, r_ = int(a * sr), int(d * sr), int(r * sr)
    s_ = max(0, n - a_ - d_ - r_)
    e = np.concatenate([np.linspace(0, 1, a_, endpoint=False), np.linspace(1, s, d_, endpoint=False),
                        np.full(s_, s), np.linspace(s, 0, r_)])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def tone(freq, dur, kind="sine", vol=0.3, env=(0.01, 0.1, 0.7, 0.2)):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == "sine":
        w = np.sin(2 * np.pi * freq * t)
    elif kind == "tri":
        w = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))
    elif kind == "saw":
        w = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 9)) * 0.6
    elif kind == "square":
        w = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 12, 2)) * 0.8
    elif kind == "bell":
        w = (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t * 6)
             + 0.25 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t * 10))
        return (w * np.exp(-t * 3.5) * vol).astype(np.float32)
    elif kind == "piano":
        w = sum(np.sin(2 * np.pi * freq * k * t) * (0.6 ** k) for k in range(1, 6))
        return (w * np.exp(-t * 2.8) * vol * _env(n, 0.005, 0.05, 1, 0.05)).astype(np.float32)
    elif kind == "pluck":
        w = sum(np.sin(2 * np.pi * freq * k * t) * (0.5 ** k) for k in range(1, 5))
        return (w * np.exp(-t * 7) * vol).astype(np.float32)
    else:
        w = np.sin(2 * np.pi * freq * t)
    return (w * _env(n, *env) * vol).astype(np.float32)


def _seed(seed) -> int:
    if isinstance(seed, (int, np.integer)):
        return int(seed)
    import zlib
    return zlib.crc32(str(seed).encode("utf-8"))


def noise(dur, seed=0):
    return np.random.default_rng(_seed(seed)).uniform(-1, 1, int(dur * SR)).astype(np.float32)


def smooth(x, k):
    k = max(1, int(k))
    return np.convolve(x, np.ones(k) / k, mode="same").astype(np.float32)


def kick(vol=0.9):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t * 18) + 45
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 9) * vol).astype(np.float32)


def snare(vol=0.5, seed=1):
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    nz = noise(0.2, seed) - smooth(noise(0.2, seed), 6)
    return ((nz * 0.8 + np.sin(2 * np.pi * 190 * t) * 0.4) * np.exp(-t * 18) * vol).astype(np.float32)


def hat(vol=0.18, seed=2):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    nz = noise(0.05, seed)
    nz = nz - smooth(nz, 3)
    return (nz * np.exp(-t * 80) * vol).astype(np.float32)


def _add(buf, sig, at, pan=0.0):
    i = int(at * SR)
    if i >= len(buf) or i < 0:
        return
    j = min(len(buf), i + len(sig))
    seg = sig[: j - i]
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[i:j, 0] += seg * l * 1.41
    buf[i:j, 1] += seg * r * 1.41


MOODS = {
    "happy": dict(bpm=118, root="C", scale="major", prog=[0, 7, 9, 5], lead="pluck", drums="pop", pad="tri"),
    "cute": dict(bpm=108, root="F", scale="major", prog=[0, 5, 7, 0], lead="bell", drums="light", pad="sine"),
    "sad": dict(bpm=70, root="A", scale="minor", prog=[0, 8, 3, 10], lead="piano", drums=None, pad="sine"),
    "epic": dict(bpm=92, root="D", scale="minor", prog=[0, 8, 10, 0], lead="saw", drums="epic", pad="saw"),
    "spooky": dict(bpm=60, root="E", scale="dim", prog=[0, 6, 1, 6], lead="bell", drums=None, pad="saw"),
    "dance": dict(bpm=124, root="G", scale="minor", prog=[0, 8, 3, 10], lead="square", drums="dance", pad="saw"),
    "action": dict(bpm=140, root="E", scale="minor", prog=[0, 0, 8, 10], lead="square", drums="rock", pad="saw"),
    "calm": dict(bpm=84, root="D", scale="major", prog=[0, 5, 9, 7], lead="piano", drums=None, pad="sine"),
    "fantasy": dict(bpm=96, root="Eb", scale="major", prog=[0, 9, 5, 7], lead="bell", drums="light", pad="sine"),
}
SCALES = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10], "dim": [0, 1, 3, 6, 7, 8, 11]}


def synth_music(mood: str, duration: float, seed=0, bpm: float | None = None) -> np.ndarray:
    m = MOODS.get(mood, MOODS["happy"])
    bpm = bpm or m["bpm"]
    beat = 60 / bpm
    root = 48 + NOTE.get(m["root"].replace("b", ""), 0) - (1 if "b" in m["root"] else 0)
    scale = SCALES[m["scale"]]
    buf = np.zeros((int((duration + 2) * SR), 2), dtype=np.float32)
    r = rng(f"music{seed}{mood}")
    bar = beat * 4
    nbars = int(duration / bar) + 1
    minor = m["scale"] != "major"
    melody_deg = 0
    for b in range(nbars):
        t0 = b * bar
        chord_root = root + m["prog"][b % len(m["prog"])]
        third = 3 if (minor and m["prog"][b % len(m["prog"])] in (0, 5, 7)) or m["prog"][b % len(m["prog"])] in (2, 4, 9) else 4
        if m["scale"] == "dim":
            third = 3
        chord = [chord_root, chord_root + third, chord_root + 7]
        # pad
        for nnote in chord:
            _add(buf, tone(midi_hz(nnote + 12), bar * 1.02, m["pad"], 0.05, (0.3, 0.2, 0.8, 0.4)), t0, r.uniform(-0.4, 0.4))
        # bajo
        steps = 8 if m["drums"] in ("dance", "rock") else 4
        for s in range(steps):
            if m["drums"] == "dance" and s % 2 == 0:
                continue
            _add(buf, tone(midi_hz(chord_root - 12), bar / steps * 0.9, "tri", 0.22, (0.005, 0.05, 0.7, 0.05)), t0 + s * bar / steps)
        # melodía (paseo aleatorio por la escala)
        notes_per_bar = {"pluck": 8, "bell": 6, "piano": 4, "saw": 4, "square": 8}.get(m["lead"], 4)
        for s in range(notes_per_bar):
            if r.random() < 0.22:
                continue
            melody_deg = max(-3, min(9, melody_deg + r.choice([-2, -1, -1, 0, 1, 1, 2])))
            octave, deg = divmod(melody_deg, 7)
            note = root + 24 + scale[deg] + 12 * octave
            dur = bar / notes_per_bar
            _add(buf, tone(midi_hz(note), dur * (1.6 if m["lead"] in ("bell", "piano") else 0.9), m["lead"], 0.13,
                           (0.005, 0.08, 0.5, 0.1)), t0 + s * dur, r.uniform(-0.3, 0.3))
        # batería
        dk = m["drums"]
        if dk:
            for q in range(4):
                tq = t0 + q * beat
                if dk in ("dance", "epic") or (dk in ("pop", "rock") and q in (0, 2)) or (dk == "light" and q == 0):
                    _add(buf, kick(0.8 if dk != "light" else 0.4), tq)
                if dk in ("pop", "dance", "rock") and q in (1, 3):
                    _add(buf, snare(0.4), tq)
                if dk == "epic" and q == 3:
                    _add(buf, snare(0.5) + 0, tq)
                if dk in ("pop", "dance", "rock", "light"):
                    _add(buf, hat(0.12), tq + beat / 2, 0.3)
                    if dk in ("dance", "rock"):
                        _add(buf, hat(0.08), tq, -0.3)
    if mood == "spooky":
        drone = tone(midi_hz(root - 12), duration + 1, "saw", 0.06, (2, 0.5, 1, 2))
        wind = smooth(noise(duration + 1, seed), 40) * 0.25
        _add(buf, drone + wind[: len(drone)], 0)
    out = buf[: int(duration * SR)]
    fade = min(len(out), int(1.5 * SR))
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
    return out * 0.8


SFX = ["whoosh", "pop", "boing", "footstep", "explosion", "magic", "thunder", "fire", "punch", "splash",
       "sparkle", "rain", "jump", "ding", "transform", "energy", "wind"]


def synth_sfx(name: str, dur: float = None, seed=0) -> np.ndarray:
    if name == "whoosh":
        d = dur or 0.6
        n = noise(d, seed)
        t = np.linspace(0, 1, len(n))
        k = (2 + 30 * np.sin(np.pi * t)).astype(int)
        out = np.array([0.0] * len(n), dtype=np.float32)
        sm = smooth(n, 12)
        out = (sm * np.sin(np.pi * t) ** 2) * 1.5
        return out.astype(np.float32)
    if name == "pop":
        t = np.arange(int(0.12 * SR)) / SR
        return (np.sin(2 * np.pi * (600 + 900 * t / 0.12) * t) * np.exp(-t * 40) * 0.6).astype(np.float32)
    if name == "boing":
        t = np.arange(int(0.6 * SR)) / SR
        f = 220 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 3)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.5).astype(np.float32)
    if name == "footstep":
        t = np.arange(int(0.12 * SR)) / SR
        return ((np.sin(2 * np.pi * 90 * t) + smooth(noise(0.12, seed), 10)[: len(t)] * 0.6) * np.exp(-t * 35) * 0.35).astype(np.float32)
    if name == "jump":
        t = np.arange(int(0.25 * SR)) / SR
        return (np.sin(2 * np.pi * np.cumsum(300 + 1200 * t) / SR) * np.exp(-t * 10) * 0.35).astype(np.float32)
    if name in ("explosion", "thunder"):
        d = dur or (2.0 if name == "explosion" else 2.5)
        t = np.arange(int(d * SR)) / SR
        nz = smooth(noise(d, seed), 30 if name == "explosion" else 60)
        boom = np.sin(2 * np.pi * np.cumsum(60 * np.exp(-t * 2) + 30) / SR)
        env = np.exp(-t * (2.2 if name == "explosion" else 1.4))
        if name == "thunder":
            env *= 0.6 + 0.4 * np.abs(np.sin(t * 7))
        return ((nz * 3 + boom * 0.7) * env * 0.8).astype(np.float32)
    if name in ("magic", "sparkle", "transform", "ding"):
        out = np.zeros(int(1.5 * SR), dtype=np.float32)
        notes = {"magic": [84, 88, 91, 96, 100], "sparkle": [96, 100, 103, 108], "transform": [72, 76, 79, 84, 88, 91, 96],
                 "ding": [88]}[name]
        for i, nn in enumerate(notes):
            s = tone(midi_hz(nn), 1.0, "bell", 0.25)
            st = int(i * 0.07 * SR)
            out[st:st + len(s)] += s[: len(out) - st]
        return out
    if name == "punch":
        t = np.arange(int(0.18 * SR)) / SR
        return ((np.sin(2 * np.pi * 70 * t) + smooth(noise(0.18, seed), 4)[: len(t)]) * np.exp(-t * 25) * 0.7).astype(np.float32)
    if name == "splash":
        d = dur or 0.8
        t = np.arange(int(d * SR)) / SR
        nz = noise(d, seed) - smooth(noise(d, seed), 4)
        return (nz * np.exp(-t * 5) * 0.5).astype(np.float32)
    if name in ("rain", "fire", "wind"):
        d = dur or 4.0
        nz = noise(d, seed)
        if name == "rain":
            out = (nz - smooth(nz, 3)) * 0.18
        elif name == "wind":
            out = smooth(nz, 80) * 2.0 * (0.6 + 0.4 * np.sin(np.arange(len(nz)) / SR * 0.7))
        else:
            out = smooth(nz, 25) * 0.6
            cr = np.random.default_rng(_seed(seed)).random(len(nz)) < 0.0008
            out += np.convolve(cr.astype(np.float32), np.exp(-np.arange(200) / 30), mode="same") * 0.4
        return out.astype(np.float32)
    if name == "energy":
        d = dur or 2.0
        t = np.arange(int(d * SR)) / SR
        return (tone(110, d, "saw", 0.12, (0.2, 0.1, 1, 0.3)) * (0.7 + 0.3 * np.sin(2 * np.pi * 6 * t))).astype(np.float32)
    return synth_sfx("pop")


EFFECT_SFX = {"fire": "fire", "rain": "rain", "lightning": "thunder", "explosion": "explosion", "magic": "magic",
              "sparkles": "sparkle", "energy": "energy", "energy_beam": "whoosh", "water_splash": "splash",
              "snow": "wind", "fog": "wind", "confetti": "pop"}
LOOPING = {"fire", "rain", "wind", "energy"}


def mix_timeline(duration: float, clips: list[dict], music: np.ndarray | None = None, music_gain=0.45,
                 duck: bool = True, normalize: bool = True) -> np.ndarray:
    """clips: [{audio: ndarray(mono/estéreo), start, gain, pan, kind}]"""
    buf = np.zeros((int(duration * SR) + 1, 2), dtype=np.float32)
    voice_env = np.zeros(len(buf), dtype=np.float32)
    for c in clips:
        a = c["audio"]
        if a.ndim == 2:
            a = a.mean(axis=1)
        a = a * c.get("gain", 1.0)
        _add(buf, a, c.get("start", 0), c.get("pan", 0))
        if c.get("kind") == "voice":
            i = int(c["start"] * SR)
            j = min(len(buf), i + len(a))
            if i < len(buf):
                voice_env[i:j] = 1
    if music is not None:
        mus = music[: len(buf)]
        if len(mus) < len(buf):
            mus = np.pad(mus, ((0, len(buf) - len(mus)), (0, 0)))
        if duck and voice_env.any():
            env = smooth(voice_env, int(0.25 * SR))
            mus = mus * (1 - 0.55 * env)[:, None]
        buf += mus * music_gain
    if not normalize:
        return buf
    peak = np.max(np.abs(buf)) or 1
    return buf / max(1.0, peak / 0.95)
