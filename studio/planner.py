"""Planificador: convierte una instrucción en lenguaje natural en un proyecto.

Funciona 100 % local con reglas (español e inglés básico).  Si existe
``ANTHROPIC_API_KEY`` puede usar Claude para escribir un guion más creativo
(``use_ai=True``); el resultado se normaliza con las mismas reglas.
"""
from __future__ import annotations

import re
import unicodedata

from .backgrounds import BACKGROUNDS
from .characters import ACCESSORIES, EMOTIONS, SPECIES, make_character
from .core import rng
from .effects import EFFECTS
from .motion import ACTIONS
from .styles import STYLES


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


SPECIES_WORDS = {
    "manzana": ["manzana", "apple"], "platano": ["platano", "banana", "banano", "guineo"],
    "naranja": ["naranja", "orange"], "fresa": ["fresa", "frutilla", "strawberry"], "uva": ["uva", "grape"],
    "sandia": ["sandia", "watermelon", "patilla"], "pina": ["pina", "pineapple", "anana"], "limon": ["limon", "lemon"],
    "pera": ["pera", "pear"], "cereza": ["cereza", "cherry"], "aguacate": ["aguacate", "palta", "avocado"],
    "gato": ["gato", "gata", "gatito", "cat", "kitten"], "perro": ["perro", "perrito", "dog", "puppy", "cachorro"],
    "conejo": ["conejo", "conejito", "bunny", "rabbit"], "oso": ["oso", "osito", "bear"], "rana": ["rana", "sapo", "frog"],
    "pinguino": ["pinguino", "penguin"], "zorro": ["zorro", "fox"], "panda": ["panda"],
    "robot": ["robot", "androide", "cyborg"], "nino": ["nino", "chico", "muchacho", "boy", "kid"],
    "nina": ["nina", "chica", "muchacha", "girl", "princesa"], "persona": ["persona", "hombre", "mujer", "senor", "senora", "heroe", "man", "woman"],
    "fantasma": ["fantasma", "ghost", "espectro"], "monstruo": ["monstruo", "monster", "criatura"],
    "estrella": ["estrella", "star"], "mago": ["mago", "maga", "hechicero", "bruja", "brujo", "wizard", "witch"],
    "mascota": ["mascota", "mascot", "blob"],
}
GROUPS = {
    "frutas": ["manzana", "platano", "fresa", "naranja"], "fruits": ["manzana", "platano", "fresa", "naranja"],
    "animales": ["gato", "perro", "conejo"], "animals": ["gato", "perro", "conejo"],
    "robots": ["robot", "robot"], "amigos": ["nino", "nina"],
}
STYLE_WORDS = {
    "anime": ["anime", "manga", "japones", "chibi"], "pixel": ["pixel", "8 bits", "8-bit", "16 bits", "retro juego", "sprite"],
    "minimalist": ["minimalista", "minimal", "plano", "flat"], "cute": ["tierno", "tierna", "kawaii", "cute", "adorable", "lindo", "linda"],
    "cinematic": ["cinematografic", "cinematic", "pelicula", "epico", "epica", "trailer"],
    "horror": ["terror", "miedo", "horror", "susto", "embrujad", "halloween", "tenebros"],
    "fantasy": ["fantasia", "fantasy", "magico", "magica", "hada", "reino", "dragon"],
    "paper": ["papel", "paper", "recortable", "cutout", "recortes"], "clay": ["plastilina", "arcilla", "clay", "claymation"],
    "stopmotion": ["stop motion", "stop-motion", "stopmotion"], "realistic": ["realista", "realistic", "fotorreal"],
    "comic": ["comic", "historieta", "motion comic"], "retro": ["vhs", "retro", "ochentas", "80s"],
    "cartoon": ["caricatura", "cartoon", "dibujo animado", "dibujos animados"],
}
BG_WORDS = {
    "park": ["parque", "jardin", "park", "campo", "pradera"], "city": ["ciudad", "calle", "city", "urbano"],
    "forest": ["bosque", "selva", "jungla", "forest"], "beach": ["playa", "beach", "mar", "costa", "verano"],
    "space": ["espacio", "planeta", "galaxia", "space", "luna", "cohete", "astronauta"],
    "kitchen": ["cocina", "kitchen", "refrigerador", "nevera", "frutero", "mesa"],
    "stage": ["escenario", "discoteca", "fiesta", "concierto", "stage", "show"],
    "castle": ["castillo", "castle", "reino", "palacio"], "underwater": ["submarino", "fondo del mar", "oceano", "underwater", "acuario"],
    "desert": ["desierto", "desert"], "snow": ["nieve", "montana", "invierno", "snow", "navidad"],
    "haunted": ["embrujad", "cementerio", "haunted", "tenebros"], "classroom": ["escuela", "clase", "aula", "colegio", "classroom", "leccion"],
    "dojo": ["dojo", "arena", "ring", "torneo"], "studio": ["estudio", "fondo liso", "fondo blanco"],
}
ACTION_WORDS = {
    "walk": ["camina", "caminar", "pasea", "walk"], "run": ["corre", "correr", "carrera", "run"],
    "jump": ["salta", "saltar", "brinca", "jump"], "dance": ["baila", "bailar", "baile", "dance", "danza", "fiesta"],
    "talk": ["habla", "hablar", "conversa", "dialogo", "platica", "dice", "talk", "explica", "cuenta"],
    "wave": ["saluda", "saludar", "wave", "hola"], "punch": ["pelea", "pelear", "lucha", "golpe", "fight", "combate", "batalla"],
    "celebrate": ["celebra", "festeja", "gana", "celebrate", "victoria"], "float": ["vuela", "volar", "flota", "fly"],
    "spin": ["gira", "girar", "spin"], "think": ["piensa", "pensar", "think"],
}
EMOTION_WORDS = {
    "happy": ["feliz", "contento", "alegre", "happy"], "sad": ["triste", "llora", "sad"], "angry": ["enojad", "furios", "angry", "molest"],
    "surprised": ["sorprend", "surprised", "asombr"], "scared": ["asustad", "miedo", "scared"], "love": ["amor", "enamorad", "love"],
    "sleepy": ["dormid", "sueno", "sleepy", "cansad"], "excited": ["emocionad", "excited"],
}
EFFECT_WORDS = {
    "fire": ["fuego", "llama", "fire", "incendio", "volcan"], "smoke": ["humo", "smoke", "niebla toxica"],
    "rain": ["lluvia", "llueve", "tormenta", "rain"], "snow": ["nieve", "nevando", "snow"],
    "lightning": ["rayo", "relampago", "tormenta", "lightning", "trueno"], "explosion": ["explosion", "explota", "boom", "bomba"],
    "magic": ["magia", "magico", "hechizo", "magic", "varita"], "energy": ["energia", "poder", "aura", "super", "energy", "kamehameha"],
    "sparkles": ["brillo", "brilla", "destello", "sparkle"], "confetti": ["confeti", "cumpleanos", "fiesta", "celebra"],
    "hearts": ["corazon", "amor", "hearts"], "bubbles": ["burbuja", "bubble"], "water_splash": ["salpica", "agua", "splash", "chapuz"],
    "fog": ["niebla", "neblina", "fog"], "fireflies": ["luciernaga", "firefly"], "leaves": ["otono", "hojas", "autumn"],
    "speedlines": ["velocidad", "rapido", "speed"],
}
FORMAT_WORDS = {
    "9:16": ["tiktok", "short", "shorts", "reel", "reels", "vertical", "historia de instagram", "stories"],
    "1:1": ["cuadrado", "instagram post", "square"],
}


def _find(text, table):
    hits = []
    for k, words in table.items():
        for w in words:
            idx = text.find(w)
            if idx >= 0:
                hits.append((idx, k))
                break
    return [k for _, k in sorted(hits)]


def _word_find(text, table):
    hits = []
    for k, words in table.items():
        for w in words:
            m = re.search(r"\b" + re.escape(w) + r"s?\b", text)
            if m:
                hits.append((m.start(), k))
                break
    return [k for _, k in sorted(hits)]


def detect(prompt: str) -> dict:
    t = norm(prompt)
    species = _word_find(t, SPECIES_WORDS)
    for g, members in GROUPS.items():
        if re.search(r"\b" + g + r"\b", t):
            for m in members:
                if m not in species:
                    species.append(m)
    names = re.findall(r"(?:llamad[oa]|named|que se llama)\s+([A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)", prompt)
    styles = _find(t, STYLE_WORDS)
    fmt = "16:9"
    for f, words in FORMAT_WORDS.items():
        if any(w in t for w in words):
            fmt = f
    is3d = bool(re.search(r"\b3d\b|tridimensional|blender|three", t))
    return dict(
        species=species, names=names, style=styles[0] if styles else None, backgrounds=_find(t, BG_WORDS),
        actions=_find(t, ACTION_WORDS), emotions=_find(t, EMOTION_WORDS), effects=_find(t, EFFECT_WORDS),
        format=fmt, is3d=is3d, story=any(w in t for w in ["historia", "cuento", "story", "aventura", "episodio", "fabula"]),
        image2video=any(w in t for w in ["esta imagen", "convierte", "imagen en video", "image to video", "foto en video"]),
        night=any(w in t for w in ["noche", "night", "nocturn"]), sunset=any(w in t for w in ["atardecer", "sunset", "ocaso"]),
        youtube="youtube" in t, short=fmt == "9:16",
    )


# ------------------------------------------------------------------ líneas de diálogo
LINES = {
    "greet": ["¡Hola! Soy {n}.", "¡Hola a todos! Me llamo {n}.", "¡Qué día tan bonito!", "¡Hola, amigos!"],
    "reply": ["¡Hola, {o}! ¿Cómo estás?", "¡Qué gusto verte, {o}!", "¡Hola! ¿Jugamos un rato?"],
    "problem": ["¡Oh no! ¿Qué está pasando?", "¡Cuidado, viene algo!", "¡Ay, qué susto!"],
    "idea": ["¡Tengo una idea!", "¡Juntos podemos lograrlo!", "No te preocupes, yo te ayudo."],
    "dance": ["¡A bailar!", "¡Sube la música!", "¡Mira mis pasos!"],
    "fight": ["¡Prepárate!", "¡No me rendiré!", "¡Toma esto!"],
    "win": ["¡Lo logramos!", "¡Somos un gran equipo!", "¡Hurra!"],
    "end": ["¡Hasta la próxima!", "¡Adiós, amigos!", "¡Gracias por ver!"],
    "spooky": ["¿Escuchaste eso?", "Aquí hay algo extraño…", "¡Corre!"],
    "magic": ["¡Abracadabra!", "¡Mira esta magia!", "¡Que brille todo!"],
    "explain": ["Hoy vamos a aprender algo nuevo.", "Presta atención, es muy fácil.", "¡Y así de simple funciona!"],
}


def _line(kind, seed, **kw):
    r = rng(f"{kind}{seed}")
    return r.choice(LINES[kind]).format(**kw)


def _actor(cid, action, emotion, x0, x1=None, y=0.82, **extra):
    a = {"character": cid, "action": action, "emotion": emotion, "from": [x0, y], "to": [x1 if x1 is not None else x0, y]}
    a.update(extra)
    return a


def plan(prompt: str, style: str | None = None, fmt: str | None = None, background: str | None = None,
         characters: list | None = None, effects: list | None = None, use_ai: bool = False,
         duration: float | None = None, mood: str | None = None) -> dict:
    """Crea la especificación completa del proyecto a partir de un texto."""
    info = detect(prompt)
    style = style or info["style"] or "cartoon"
    fmt = fmt or info["format"]
    if style == "pixel" and not info["species"]:
        pass

    # ---- personajes
    if characters:
        chars = [c if isinstance(c, dict) else make_character(c) for c in characters]
    else:
        sp = info["species"] or (["manzana", "platano"] if info["story"] else ["mascota"])
        if style == "horror" and not info["species"]:
            sp = ["nino", "fantasma"]
        chars = []
        for i, s in enumerate(sp[:4]):
            name = info["names"][i] if i < len(info["names"]) else None
            acc = None
            if s == "mago":
                acc = "wizard"
            c = make_character(s, name, accessory=acc)
            if any(c["id"] == o["id"] for o in chars):
                c["id"] += f"_{i + 1}"
                c["name"] += f" {i + 1}"
                c["color"] = rng(c["id"]).choice(["#8e24aa", "#00897b", "#f4511e", "#3949ab"])
            chars.append(c)
    for c in chars:
        if style == "anime":
            c["eyes"] = "anime"
    ids = [c["id"] for c in chars]
    names = {c["id"]: c["name"] for c in chars}

    bgs = [background] if background else (info["backgrounds"] or [])
    tod = "night" if info["night"] else ("sunset" if info["sunset"] else "day")
    actions = info["actions"]
    emos = info["emotions"]
    fx_words = effects or info["effects"]
    scenes = []
    seed = prompt

    def bg(i, default):
        return bgs[i] if i < len(bgs) else (bgs[0] if bgs else default)

    def pos(i, n):
        return 0.5 if n == 1 else 0.25 + 0.5 * i / (n - 1)

    a0 = actions[0] if actions else None
    if style == "horror" or "haunted" in bgs:
        mood = mood or "spooky"
        scenes = [
            dict(background=bg(0, "haunted"), duration=4, camera={"type": "dolly_in"}, effects=[{"type": "fog"}, {"type": "fireflies", "intensity": 0.5}],
                 actors=[_actor(ids[0], "walk", "scared", 0.15, 0.45)], caption="Era una noche oscura…",
                 dialogue=[{"character": ids[0], "text": _line("spooky", seed)}]),
            dict(background=bg(0, "haunted"), duration=4, camera={"type": "shake"}, effects=[{"type": "lightning", "period": 1.8}, {"type": "fog"}],
                 actors=[_actor(ids[0], "scared_shake", "scared", 0.35)] + ([_actor(ids[1], "float", "angry", 0.95, 0.7)] if len(ids) > 1 else []),
                 dialogue=[{"character": ids[-1], "text": "Buuu…"}]),
            dict(background=bg(0, "haunted"), duration=3, camera={"type": "zoom_in"}, effects=[{"type": "smoke", "x": 0.5, "y": 0.85}],
                 actors=[_actor(ids[0], "run", "scared", 0.4, 1.15)], caption="Continuará…"),
        ]
    elif a0 == "dance" or "stage" in bgs:
        mood = mood or "dance"
        scenes = [
            dict(background=bg(0, "stage"), time_of_day="night", duration=5, camera={"type": "zoom_in"},
                 effects=[{"type": "confetti"}, {"type": "sparkles", "intensity": 0.6, "y": 0.4}],
                 actors=[_actor(c, "dance", "joy", pos(i, len(ids))) for i, c in enumerate(ids)],
                 dialogue=[{"character": ids[0], "text": _line("dance", seed)}]),
            dict(background=bg(0, "stage"), time_of_day="night", duration=5, camera={"type": "pan"},
                 effects=[{"type": "confetti"}],
                 actors=[_actor(c, "dance" if i % 2 == 0 else "jump", "excited", pos(i, len(ids))) for i, c in enumerate(ids)]),
            dict(background=bg(0, "stage"), time_of_day="night", duration=3, camera={"type": "static"},
                 effects=[{"type": "confetti", "intensity": 1.5}],
                 actors=[_actor(c, "celebrate", "joy", pos(i, len(ids))) for i, c in enumerate(ids)],
                 caption="¡Fin de la fiesta!"),
        ]
    elif a0 in ("punch",) or "dojo" in bgs:
        mood = mood or "action"
        if len(ids) < 2:
            extra = make_character("robot", "Rival")
            chars.append(extra)
            ids.append(extra["id"])
            names[extra["id"]] = extra["name"]
        A, B = ids[0], ids[1]
        scenes = [
            dict(background=bg(0, "dojo"), duration=3.5, camera={"type": "static"}, effects=[],
                 actors=[_actor(A, "idle", "angry", 0.25, facing=1), _actor(B, "idle", "angry", 0.75, facing=-1)],
                 dialogue=[{"character": A, "text": _line("fight", seed)}, {"character": B, "text": _line("fight", seed + "b")}]),
            dict(background=bg(0, "dojo"), duration=3.5, camera={"type": "shake"}, effects=[{"type": "speedlines", "intensity": 0.6}, {"type": "energy", "on": A}],
                 actors=[_actor(A, "punch", "angry", 0.35, 0.42, facing=1), _actor(B, "kick", "angry", 0.66, 0.6, facing=-1)]),
            dict(background=bg(0, "dojo"), duration=3, camera={"type": "zoom_in"}, effects=[{"type": "explosion", "x": 0.5, "y": 0.62, "start": 0.4}],
                 actors=[_actor(A, "celebrate", "joy", 0.3, facing=1), _actor(B, "scared_shake", "surprised", 0.75, facing=-1)],
                 dialogue=[{"character": A, "text": _line("win", seed)}]),
        ]
    elif "magic" in fx_words or "mago" in info["species"] or style == "fantasy" or "transform" in norm(prompt):
        mood = mood or "fantasy"
        A = ids[0]
        transform = "transform" in norm(prompt) or "convierte en" in norm(prompt)
        scenes = [
            dict(background=bg(0, "castle"), duration=4, camera={"type": "pan"}, effects=[{"type": "fireflies"}],
                 actors=[_actor(A, "walk", "happy", 0.15, 0.45)], dialogue=[{"character": A, "text": _line("greet", seed, n=names[A])}]),
            dict(background=bg(0, "castle"), duration=4, camera={"type": "zoom_in"},
                 effects=[{"type": "magic", "on": A}, {"type": "sparkles", "on": A, "start": 1.0}],
                 actors=[_actor(A, "wave", "excited", 0.45, **({"transform_to": "estrella", "transform_at": 2.0} if transform else {}))],
                 dialogue=[{"character": A, "text": _line("magic", seed)}]),
            dict(background=bg(0, "castle"), duration=3, camera={"type": "static"}, effects=[{"type": "sparkles", "intensity": 1.4, "y": 0.5}],
                 actors=[_actor(c, "celebrate", "joy", pos(i, len(ids))) for i, c in enumerate(ids)], caption="Fin"),
        ]
    elif info["story"] or len(ids) >= 2:
        mood = mood or ("cute" if style == "cute" else "happy")
        n = len(ids)
        A = ids[0]
        B = ids[1] if n > 1 else ids[0]
        problem_fx = [{"type": f} for f in fx_words if f in ("rain", "lightning", "explosion", "fire", "snow", "smoke")] or [{"type": "rain"}]
        scenes = [
            dict(background=bg(0, "kitchen" if any(c.get("kind") == "fruit" for c in chars) else "park"), duration=4.5,
                 camera={"type": "pan"}, effects=[],
                 actors=[_actor(A, "walk", "happy", 0.1, 0.35, facing=1)] + ([_actor(B, "wave", "happy", 0.7, facing=-1)] if n > 1 else []),
                 dialogue=[{"character": A, "text": _line("greet", seed, n=names[A])}] + ([{"character": B, "text": _line("reply", seed, o=names[A])}] if n > 1 else []),
                 caption=None),
            dict(background=bg(1, "park"), duration=4, camera={"type": "shake" if any(f["type"] in ("lightning", "explosion") for f in problem_fx) else "zoom_in"},
                 effects=problem_fx,
                 actors=[_actor(c, "scared_shake" if i == 0 else "think", "scared" if i == 0 else "surprised", pos(i, n)) for i, c in enumerate(ids)],
                 dialogue=[{"character": A, "text": _line("problem", seed)}] + ([{"character": B, "text": _line("idea", seed)}] if n > 1 else [])),
            dict(background=bg(1, "park"), duration=4, camera={"type": "static"}, effects=[{"type": "sparkles", "y": 0.45}, {"type": "confetti", "start": 1.0}],
                 actors=[_actor(c, "celebrate" if i % 2 == 0 else "jump", "joy", pos(i, n)) for i, c in enumerate(ids)],
                 dialogue=[{"character": B, "text": _line("win", seed)}]),
            dict(background=bg(1, "park"), time_of_day="sunset", duration=3, camera={"type": "zoom_out"}, effects=[],
                 actors=[_actor(c, "wave", "happy", pos(i, n)) for i, c in enumerate(ids)],
                 dialogue=[{"character": A, "text": _line("end", seed)}], caption="Fin"),
        ]
    else:
        # una sola acción / personaje
        A = ids[0]
        act = a0 or "wave"
        em = emos[0] if emos else ("happy" if act not in ("punch",) else "angry")
        mood = mood or {"dance": "dance", "punch": "action", "float": "fantasy"}.get(act, "cute" if style == "cute" else "happy")
        if act in ("walk", "run"):
            act_list = [_actor(A, act, em, 0.1, 0.9, facing=1)]
        else:
            act_list = [_actor(A, act, em, 0.5)]
        first = dict(background=bg(0, "park"), duration=5, camera={"type": "pan" if act in ("walk", "run") else "zoom_in"},
                     effects=[{"type": f} for f in fx_words], actors=act_list,
                     dialogue=[{"character": A, "text": _line("greet", seed, n=names[A])}] if act in ("talk", "wave") else [])
        scenes = [first]
        if len(emos) > 1:
            scenes.append(dict(background=bg(0, "studio"), duration=1.6 * len(emos), camera={"type": "zoom_in"}, effects=[],
                               actors=[dict(_actor(A, "idle", emos[0], 0.5), emotions=[{"t": i * 1.6, "emotion": e} for i, e in enumerate(emos)])]))
        else:
            scenes.append(dict(background=bg(0, "park"), duration=3, camera={"type": "static"}, effects=[{"type": "sparkles", "y": 0.5}],
                               actors=[_actor(A, "celebrate", "joy", 0.5 if act not in ("walk", "run") else 0.6)],
                               dialogue=[{"character": A, "text": _line("end", seed)}]))
    for s in scenes:
        s.setdefault("time_of_day", tod if s["background"] not in ("haunted", "space") else "night")
        if info["night"]:
            s["time_of_day"] = "night"
    # efectos pedidos explícitamente que aún no aparecen
    used = {f["type"] for s in scenes for f in s["effects"]}
    for f in fx_words:
        if f not in used and f in EFFECTS:
            scenes[min(1, len(scenes) - 1)]["effects"].append({"type": f})

    spec = dict(
        title=_title(prompt), prompt=prompt, style=style, format=fmt, fps=STYLES.get(style, {}).get("fps", 24),
        mood=mood or "happy", music=True, voices=True, subtitles=True, engine="3d" if info["is3d"] else "2d",
        characters=chars, scenes=scenes,
    )
    if info["short"]:
        spec["subtitles"] = "big"
    if duration:
        _fit_duration(spec, duration)
    if use_ai:
        ai = _ai_plan(prompt, spec)
        if ai:
            return ai
    return normalize(spec)


def _title(prompt):
    words = re.sub(r"[^\wáéíóúñÁÉÍÓÚÑ ]", " ", prompt).split()
    stop = {"crea", "haz", "hazme", "una", "un", "la", "el", "de", "con", "que", "para", "animacion", "animación", "quiero", "me", "por", "favor", "estilo"}
    keep = [w for w in words if w.lower() not in stop][:6]
    return " ".join(keep).capitalize() or "Mi animación"


def _fit_duration(spec, total):
    cur = sum(s["duration"] for s in spec["scenes"])
    k = total / cur
    for s in spec["scenes"]:
        s["duration"] = round(max(1.5, s["duration"] * k), 2)


def normalize(spec: dict) -> dict:
    """Valida y completa una especificación (también las editadas a mano)."""
    spec.setdefault("title", "Mi animación")
    spec.setdefault("style", "cartoon")
    if spec["style"] not in STYLES:
        spec["style"] = "cartoon"
    spec.setdefault("format", "16:9")
    spec.setdefault("fps", STYLES[spec["style"]]["fps"])
    spec.setdefault("mood", "happy")
    spec.setdefault("music", True)
    spec.setdefault("voices", True)
    spec.setdefault("subtitles", True)
    spec.setdefault("quality", "hd")
    spec.setdefault("transition", "fade")
    chars = []
    for c in spec.get("characters", []):
        base = make_character(c.get("species", "mascota"), c.get("name"))
        base.update({k: v for k, v in c.items() if v is not None})
        if base.get("accessory") not in ACCESSORIES:
            base["accessory"] = "none"
        chars.append(base)
    if not chars:
        chars = [make_character("mascota")]
    spec["characters"] = chars
    ids = {c["id"] for c in chars}
    for i, s in enumerate(spec.get("scenes", [])):
        s.setdefault("id", f"escena_{i + 1}")
        if s.get("background") not in BACKGROUNDS:
            s["background"] = "park"
        s.setdefault("time_of_day", "day")
        s["duration"] = float(max(1.0, min(30.0, s.get("duration", 4))))
        cam = s.get("camera", {"type": "static"})
        s["camera"] = cam if isinstance(cam, dict) else {"type": str(cam)}
        s["effects"] = [f if isinstance(f, dict) else {"type": f} for f in s.get("effects", []) if (f if isinstance(f, str) else f.get("type")) in EFFECTS]
        for f in s["effects"]:
            if f.get("on") and f["on"] not in ids:
                f.pop("on")
        acts = []
        for a in s.get("actors", []):
            if a.get("character") not in ids:
                continue
            if a.get("action") not in ACTIONS:
                a["action"] = "idle"
            if a.get("emotion") not in EMOTIONS:
                a["emotion"] = "neutral"
            a.setdefault("from", [0.5, 0.82])
            a.setdefault("to", list(a["from"]))
            if "facing" not in a:
                a["facing"] = 1 if a["to"][0] >= a["from"][0] else -1
            acts.append(a)
        s["actors"] = acts
        s["dialogue"] = [d for d in s.get("dialogue", []) if d.get("character") in ids and d.get("text")]
    if not spec.get("scenes"):
        spec["scenes"] = [dict(id="escena_1", background="park", time_of_day="day", duration=4, camera={"type": "static"},
                               effects=[], actors=[_actor(chars[0]["id"], "wave", "happy", 0.5)], dialogue=[])]
        normalize(spec)
    return spec


def catalog() -> dict:
    return dict(species=list(SPECIES), backgrounds=list(BACKGROUNDS), actions=list(ACTIONS), emotions=EMOTIONS,
                effects=list(EFFECTS), styles=list(STYLES), accessories=ACCESSORIES,
                cameras=["static", "pan", "zoom_in", "zoom_out", "dolly_in", "shake"])


def _ai_plan(prompt, base):
    from .providers import plan_with_claude
    try:
        data = plan_with_claude(prompt, catalog())
    except Exception as e:  # noqa: BLE001
        print(f"[planner] Claude no disponible ({e}); uso el planificador local")
        return None
    if not data:
        return None
    chars = []
    name2id = {}
    for c in data.get("characters", []):
        ch = make_character(c.get("species", "mascota"), c.get("name"), accessory=c.get("accessory"), personality=c.get("personality"))
        chars.append(ch)
        name2id[c.get("name")] = ch["id"]
    scenes = []
    for s in data.get("scenes", []):
        scenes.append(dict(background=s["background"], time_of_day=s["time_of_day"], duration=s["duration"],
                           camera={"type": s["camera"]}, caption=s.get("caption") or None,
                           effects=[{"type": e} for e in s.get("effects", [])],
                           actors=[_actor(name2id.get(a["character"], ""), a["action"], a["emotion"], a["start_x"], a["end_x"]) for a in s["actors"]],
                           dialogue=[{"character": name2id.get(d["character"], ""), "text": d["text"]} for d in s["dialogue"]]))
    spec = dict(base, title=data.get("title", base["title"]), mood=data.get("mood", base["mood"]), characters=chars, scenes=scenes,
                planner="claude")
    return normalize(spec)
