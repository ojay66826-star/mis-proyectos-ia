"""Generador de animaciones Lottie (Bodymovin JSON v5) sin After Effects.

Crea personajes vectoriales animados (rebote con squash & stretch, parpadeo,
sombra) que se reproducen en web, Android, iOS y Telegram/Discord stickers.
"""
from __future__ import annotations

import json
from pathlib import Path

from .core import hex2rgb


def _c(hexcol):
    r, g, b = hex2rgb(hexcol)
    return [round(r / 255, 4), round(g / 255, 4), round(b / 255, 4), 1]


def _kf(frames_values, ease=(0.42, 0.58)):
    """Lista de (frame, valor) -> keyframes animados de Lottie con easing."""
    out = []
    for i, (t, v) in enumerate(frames_values):
        v = v if isinstance(v, list) else [v]
        k = {"t": t, "s": v}
        if i < len(frames_values) - 1:
            k["o"] = {"x": [ease[0]] * len(v), "y": [0] * len(v)}
            k["i"] = {"x": [ease[1]] * len(v), "y": [1] * len(v)}
        out.append(k)
    return {"a": 1, "k": out}


def _static(v):
    return {"a": 0, "k": v}


def _tr(p=(0, 0), s=(100, 100), r=0, o=100):
    return {"ty": "tr", "p": _static(list(p)), "a": _static([0, 0]), "s": _static(list(s)), "r": _static(r), "o": _static(o),
            "sk": _static(0), "sa": _static(0)}


def _ellipse(name, size, pos, color, scale=None, stroke=None):
    it = [{"ty": "el", "nm": name, "p": _static(list(pos)), "s": _static(list(size)), "d": 1},
          {"ty": "fl", "c": _static(_c(color)), "o": _static(100), "r": 1}]
    if stroke:
        it.append({"ty": "st", "c": _static(_c(stroke[0])), "o": _static(100), "w": _static(stroke[1]), "lc": 2, "lj": 2})
    tr = _tr()
    if scale:
        tr["s"] = scale
    it.append(tr)
    return {"ty": "gr", "nm": name, "it": it}


def _layer(ind, name, shapes, pos, scale=None, op=90):
    ks = {"o": _static(100), "r": _static(0), "p": pos if isinstance(pos, dict) else _static(list(pos) + [0]),
          "a": _static([0, 0, 0]), "s": scale or _static([100, 100, 100])}
    return {"ddd": 0, "ind": ind, "ty": 4, "nm": name, "sr": 1, "ks": ks, "ao": 0, "shapes": shapes,
            "ip": 0, "op": op, "st": 0, "bm": 0}


def bouncing_character(out_path, color="#e53935", size=512, fps=30, seconds=2.0, name="personaje") -> Path:
    op = int(fps * seconds)
    half, low = op // 2, int(op * 0.5)
    cx, top, floor = size / 2, size * 0.36, size * 0.62
    pos = _kf([(0, [cx, floor, 0]), (int(op * 0.08), [cx, floor, 0]), (half, [cx, top, 0]), (op - int(op * 0.08), [cx, floor, 0]), (op, [cx, floor, 0])])
    scl = _kf([(0, [118, 84, 100]), (int(op * 0.12), [92, 110, 100]), (half, [100, 100, 100]), (op - int(op * 0.1), [94, 108, 100]), (op, [118, 84, 100])])
    blink = _kf([(0, [100, 100]), (int(op * 0.7), [100, 100]), (int(op * 0.74), [100, 10]), (int(op * 0.78), [100, 100]), (op, [100, 100])])
    shadow_s = _kf([(0, [100, 100, 100]), (half, [55, 55, 100]), (op, [100, 100, 100])])
    body_r = size * 0.34
    ink = "#1e161c"
    face = [
        _ellipse("ojo_izq", [body_r * 0.28, body_r * 0.36], [-body_r * 0.22, -body_r * 0.1], "#ffffff", blink, (ink, 4)),
        _ellipse("ojo_der", [body_r * 0.28, body_r * 0.36], [body_r * 0.22, -body_r * 0.1], "#ffffff", blink, (ink, 4)),
        _ellipse("pupila_izq", [body_r * 0.14, body_r * 0.16], [-body_r * 0.2, -body_r * 0.07], ink, blink),
        _ellipse("pupila_der", [body_r * 0.14, body_r * 0.16], [body_r * 0.24, -body_r * 0.07], ink, blink),
        _ellipse("mejilla_izq", [body_r * 0.2, body_r * 0.1], [-body_r * 0.38, body_r * 0.16], "#ff8aa5"),
        _ellipse("mejilla_der", [body_r * 0.2, body_r * 0.1], [body_r * 0.38, body_r * 0.16], "#ff8aa5"),
        _ellipse("boca", [body_r * 0.26, body_r * 0.14], [0, body_r * 0.22], "#8a1c2f", None, (ink, 4)),
    ]
    body = [_ellipse("hoja", [body_r * 0.34, body_r * 0.16], [body_r * 0.14, -body_r * 1.0], "#4caf50"),
            _ellipse("cuerpo", [body_r * 2, body_r * 1.9], [0, 0], color, None, (ink, 7)),
            _ellipse("brillo", [body_r * 0.3, body_r * 0.18], [-body_r * 0.5, -body_r * 0.5], "#ffffff")]
    # En Lottie el primer elemento de la lista se dibuja ENCIMA: invertimos el orden de pintado
    face = face[::-1]
    body = body[::-1]
    data = {
        "v": "5.7.4", "fr": fps, "ip": 0, "op": op, "w": size, "h": size, "nm": name, "ddd": 0, "assets": [],
        "layers": [
            _layer(1, "cara", face, pos, scl, op),
            _layer(2, "cuerpo", body, pos, scl, op),
            _layer(3, "sombra", [_ellipse("sombra", [size * 0.42, size * 0.06], [0, 0], "#000000")], [cx, floor + body_r * 0.98], shadow_s, op),
        ],
    }
    data["layers"][2]["ks"]["o"] = _static(25)
    out_path = Path(out_path)
    out_path.write_text(json.dumps(data), encoding="utf-8")
    return out_path
