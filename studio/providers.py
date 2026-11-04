"""Integraciones externas OPCIONALES (imagen, video, voz y planificación con IA).

Todo el estudio funciona sin claves gracias a los motores locales. Si defines
claves en ``.env`` se activan estos proveedores.  Ver ``docs/APIS.md``.

Estado de verificación (ver README): estas llamadas siguen la documentación
oficial de cada servicio, pero en el contenedor donde se construyó el estudio
la red bloqueaba esos dominios, así que se marcan como "no probadas" hasta que
ejecutes ``python -m studio doctor --online`` en tu equipo.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import time
import urllib.parse
from pathlib import Path

from .core import ROOT, which

_ENV_LOADED = False


def load_env():
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    p = ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def key(name: str) -> str | None:
    load_env()
    v = os.environ.get(name, "").strip()
    return v or None


def _requests():
    import requests
    return requests


# ----------------------------------------------------------------- estado
KEYS = {
    "ANTHROPIC_API_KEY": "Claude (planificación de guiones con IA)",
    "HF_TOKEN": "Hugging Face Inference (imágenes FLUX gratis con cuenta)",
    "OPENAI_API_KEY": "OpenAI (imágenes gpt-image-1 y voz TTS)",
    "STABILITY_API_KEY": "Stability AI (imágenes Stable Image)",
    "REPLICATE_API_TOKEN": "Replicate (video IA: imagen→video, texto→video)",
    "ELEVENLABS_API_KEY": "ElevenLabs (voces realistas)",
}


def status() -> dict:
    load_env()
    tools = {}
    for exe in ("ffmpeg", "ffprobe", "blender", "espeak-ng", "sox", "node", "npx", "realesrgan-ncnn-vulkan", "rhubarb"):
        tools[exe] = bool(which(exe))
    chromium = Path("/opt/pw-browsers").exists() or bool(which("chromium")) or bool(which("google-chrome"))
    tools["chromium"] = chromium
    tools["three.js"] = (ROOT / "node_modules" / "three").exists()
    tools["gsap"] = (ROOT / "node_modules" / "gsap").exists()
    tools["lottie-web"] = (ROOT / "node_modules" / "lottie-web").exists()
    tools["remotion"] = (ROOT / "remotion" / "node_modules" / "remotion").exists()
    keys = {k: bool(key(k)) for k in KEYS}
    return {"tools": tools, "keys": keys, "key_descriptions": KEYS,
            "image_providers": image_providers(), "video_providers": video_providers()}


def image_providers():
    out = ["local"]
    out.append("pollinations")  # gratis, sin clave (requiere internet)
    if key("HF_TOKEN"):
        out.append("huggingface")
    if key("OPENAI_API_KEY"):
        out.append("openai")
    if key("STABILITY_API_KEY"):
        out.append("stability")
    return out


def video_providers():
    out = ["local"]
    if key("REPLICATE_API_TOKEN"):
        out.append("replicate")
    return out


# ----------------------------------------------------------------- imagen
def generate_image(prompt: str, out_path, width=1024, height=576, seed=42, provider="auto",
                   negative: str = "") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    order = [provider] if provider != "auto" else [p for p in ("huggingface", "openai", "stability", "pollinations") if p in image_providers()]
    errors = []
    for p in order:
        try:
            fn = {"pollinations": _img_pollinations, "huggingface": _img_hf, "openai": _img_openai,
                  "stability": _img_stability}.get(p)
            if fn is None:
                continue
            data = fn(prompt, width, height, seed, negative)
            out_path.write_bytes(data)
            _normalize_image(out_path)
            return out_path
        except Exception as e:  # noqa: BLE001
            errors.append(f"{p}: {e}")
    raise RuntimeError("Ningún proveedor de imagen respondió. " + " | ".join(errors))


def _normalize_image(path: Path):
    from PIL import Image
    im = Image.open(path)
    im.load()
    im.convert("RGB").save(path.with_suffix(".png"))
    if path.suffix.lower() != ".png":
        path.unlink(missing_ok=True)


def _img_pollinations(prompt, w, h, seed, negative):
    q = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{q}?width={w}&height={h}&seed={seed}&nologo=true&model=flux"
    r = _requests().get(url, timeout=180)
    r.raise_for_status()
    if not r.headers.get("content-type", "").startswith("image"):
        raise RuntimeError("respuesta no es imagen")
    return r.content


def _img_hf(prompt, w, h, seed, negative):
    model = os.environ.get("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    r = _requests().post(url, headers={"Authorization": f"Bearer {key('HF_TOKEN')}"},
                         json={"inputs": prompt, "parameters": {"width": w - w % 8, "height": h - h % 8, "seed": seed}},
                         timeout=300)
    r.raise_for_status()
    return r.content


def _img_openai(prompt, w, h, seed, negative):
    size = "1536x1024" if w > h else ("1024x1536" if h > w else "1024x1024")
    r = _requests().post("https://api.openai.com/v1/images/generations",
                         headers={"Authorization": f"Bearer {key('OPENAI_API_KEY')}"},
                         json={"model": os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1"), "prompt": prompt, "size": size},
                         timeout=300)
    r.raise_for_status()
    return base64.b64decode(r.json()["data"][0]["b64_json"])


def _img_stability(prompt, w, h, seed, negative):
    ar = "16:9" if w > h * 1.3 else ("9:16" if h > w * 1.3 else "1:1")
    r = _requests().post("https://api.stability.ai/v2beta/stable-image/generate/core",
                         headers={"Authorization": f"Bearer {key('STABILITY_API_KEY')}", "Accept": "image/*"},
                         files={"none": ""},
                         data={"prompt": prompt, "aspect_ratio": ar, "seed": seed, "output_format": "png",
                               **({"negative_prompt": negative} if negative else {})},
                         timeout=300)
    r.raise_for_status()
    return r.content


# ----------------------------------------------------------------- video
def generate_video_replicate(prompt: str, out_path, image_path=None, model: str | None = None) -> Path:
    """Texto→video o imagen→video con Replicate (modelo configurable)."""
    token = key("REPLICATE_API_TOKEN")
    if not token:
        raise RuntimeError("Falta REPLICATE_API_TOKEN en .env")
    model = model or os.environ.get("REPLICATE_VIDEO_MODEL", "minimax/video-01")
    inp = {"prompt": prompt}
    if image_path:
        mime = "image/png" if str(image_path).endswith(".png") else "image/jpeg"
        b64 = base64.b64encode(Path(image_path).read_bytes()).decode()
        inp[os.environ.get("REPLICATE_IMAGE_FIELD", "first_frame_image")] = f"data:{mime};base64,{b64}"
    rq = _requests()
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Prefer": "wait"}
    r = rq.post(f"https://api.replicate.com/v1/models/{model}/predictions", headers=h, json={"input": inp}, timeout=120)
    r.raise_for_status()
    pred = r.json()
    t0 = time.time()
    while pred.get("status") not in ("succeeded", "failed", "canceled"):
        if time.time() - t0 > 900:
            raise RuntimeError("Tiempo de espera agotado en Replicate")
        time.sleep(5)
        pred = rq.get(pred["urls"]["get"], headers=h, timeout=60).json()
    if pred["status"] != "succeeded":
        raise RuntimeError(f"Replicate: {pred.get('error')}")
    url = pred["output"] if isinstance(pred["output"], str) else pred["output"][0]
    out_path = Path(out_path)
    out_path.write_bytes(rq.get(url, timeout=300).content)
    return out_path


# ----------------------------------------------------------------- voz
def tts_cloud(text, out_path, voice, provider="auto"):
    """Devuelve ruta WAV o None si no hay proveedor configurado."""
    load_env()
    chosen = provider
    if provider == "auto":
        chosen = os.environ.get("STUDIO_TTS", "local")
    if chosen == "elevenlabs" and key("ELEVENLABS_API_KEY"):
        vid = (voice or {}).get("elevenlabs_voice_id") or os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        r = _requests().post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
                             headers={"xi-api-key": key("ELEVENLABS_API_KEY"), "Accept": "audio/mpeg"},
                             json={"text": text, "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")},
                             timeout=120)
        r.raise_for_status()
        return _mp3_to_wav(r.content, out_path)
    if chosen == "openai" and key("OPENAI_API_KEY"):
        r = _requests().post("https://api.openai.com/v1/audio/speech",
                             headers={"Authorization": f"Bearer {key('OPENAI_API_KEY')}"},
                             json={"model": os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
                                   "voice": (voice or {}).get("openai_voice", "alloy"), "input": text,
                                   "response_format": "mp3"}, timeout=120)
        r.raise_for_status()
        return _mp3_to_wav(r.content, out_path)
    if provider not in ("auto", "local"):
        raise RuntimeError(f"Proveedor de voz '{provider}' sin clave configurada")
    return None


def _mp3_to_wav(data: bytes, out_path):
    out_path = Path(out_path)
    tmp = out_path.with_suffix(".mp3")
    tmp.write_bytes(data)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-ar", "44100", "-ac", "2", str(out_path)], check=True)
    tmp.unlink(missing_ok=True)
    return out_path


# ----------------------------------------------------------------- Claude (planificador)
PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "mood": {"type": "string", "enum": ["happy", "cute", "sad", "epic", "spooky", "dance", "action", "calm", "fantasy"]},
        "characters": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"}, "species": {"type": "string"},
            "accessory": {"type": "string"}, "personality": {"type": "string"}},
            "required": ["name", "species", "accessory", "personality"], "additionalProperties": False}},
        "scenes": {"type": "array", "items": {"type": "object", "properties": {
            "background": {"type": "string"}, "time_of_day": {"type": "string", "enum": ["day", "sunset", "night"]},
            "duration": {"type": "number"}, "camera": {"type": "string"}, "caption": {"type": "string"},
            "effects": {"type": "array", "items": {"type": "string"}},
            "actors": {"type": "array", "items": {"type": "object", "properties": {
                "character": {"type": "string"}, "action": {"type": "string"}, "emotion": {"type": "string"},
                "start_x": {"type": "number"}, "end_x": {"type": "number"}},
                "required": ["character", "action", "emotion", "start_x", "end_x"], "additionalProperties": False}},
            "dialogue": {"type": "array", "items": {"type": "object", "properties": {
                "character": {"type": "string"}, "text": {"type": "string"}},
                "required": ["character", "text"], "additionalProperties": False}}},
            "required": ["background", "time_of_day", "duration", "camera", "caption", "effects", "actors", "dialogue"],
            "additionalProperties": False}},
    },
    "required": ["title", "mood", "characters", "scenes"],
    "additionalProperties": False,
}


def plan_with_claude(prompt: str, catalog: dict) -> dict | None:
    """Pide a Claude un guion estructurado. Devuelve None si no hay credenciales."""
    if not key("ANTHROPIC_API_KEY"):
        return None
    import anthropic
    client = anthropic.Anthropic(api_key=key("ANTHROPIC_API_KEY"))
    system = (
        "Eres el director de un estudio de animación 2D. Convierte la petición del usuario en un guion breve "
        "(2 a 5 escenas, 3-6 s cada una) usando SOLO estos valores del catálogo: " + json.dumps(catalog, ensure_ascii=False)
        + ". Los nombres de 'character' en actores y diálogos deben coincidir con 'name' de los personajes. "
        "Diálogos cortos (máx. 12 palabras) en el idioma del usuario. start_x/end_x entre 0.1 y 0.9."
    )
    resp = client.beta.messages.create(
        model=os.environ.get("STUDIO_CLAUDE_MODEL", "claude-opus-5-5"),
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": PLAN_SCHEMA}},
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":
        return None
    text = next((b.text for b in resp.content if b.type == "text"), None)
    return json.loads(text) if text else None
