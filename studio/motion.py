"""Ciclos de movimiento procedurales (principios de animación aplicados).

Cada acción convierte un tiempo ``t`` (segundos) en una ``Pose``: anticipación,
squash & stretch, arcos, acción secundaria (brazos opuestos al caminar) y
parpadeo automático.
"""
from __future__ import annotations

import math

from .characters import Pose
from .core import clamp, ease_in_out

ACTIONS = {
    "idle": "Reposo (respira y parpadea)",
    "walk": "Caminar",
    "run": "Correr",
    "jump": "Saltar",
    "dance": "Bailar",
    "talk": "Hablar con gestos",
    "wave": "Saludar",
    "punch": "Golpear (pelea)",
    "kick": "Patada (pelea)",
    "celebrate": "Celebrar",
    "float": "Flotar / volar",
    "scared_shake": "Temblar de miedo",
    "spin": "Girar",
    "think": "Pensar",
    "sit_bounce": "Rebotar sentado",
}


def blink_at(t: float, seed: float = 0.0) -> float:
    """Parpadeo cada ~3 s con duración 0.15 s."""
    period = 3.1 + (seed % 1.0)
    ph = (t + seed * 1.7) % period
    if ph < 0.15:
        return math.sin(ph / 0.15 * math.pi)
    return 0.0


def pose_for(action: str, t: float, emotion: str = "neutral", tempo: float = 110.0, seed: float = 0.0,
             speed: float = 1.0) -> Pose:
    p = Pose(emotion=emotion)
    p.blink = blink_at(t, seed)
    beat = tempo / 60.0
    if action == "walk":
        ph = t * 2 * math.pi * 1.6 * speed
        s = math.sin(ph)
        p.leg_front = (32 * s, -max(0, -s) * 40)
        p.leg_back = (-32 * s, -max(0, s) * 40)
        p.arm_front = (14 + 22 * s, 12)
        p.arm_back = (14 - 22 * s, 12)
        p.body_dy = abs(math.cos(ph)) * 0.035
        p.squash = 1 + 0.04 * math.cos(2 * ph)
        p.tilt = 3
    elif action == "run":
        ph = t * 2 * math.pi * 2.6 * speed
        s = math.sin(ph)
        p.leg_front = (50 * s, -max(0, -s) * 70 - 10)
        p.leg_back = (-50 * s, -max(0, s) * 70 - 10)
        p.arm_front = (30 + 40 * s, 75)
        p.arm_back = (30 - 40 * s, 75)
        p.body_dy = abs(math.cos(ph)) * 0.08
        p.squash = 1 + 0.07 * math.cos(2 * ph)
        p.tilt = 10
    elif action == "jump":
        period = 1.2
        ph = (t % period) / period
        if ph < 0.2:      # anticipación
            k = ph / 0.2
            p.squash = 1 + 0.25 * math.sin(k * math.pi / 2)
            p.leg_front = p.leg_back = (20 * k, -40 * k)
            p.arm_front = p.arm_back = (10 + 30 * k, -10 * k)
        elif ph < 0.8:    # vuelo (arco parabólico)
            k = (ph - 0.2) / 0.6
            p.body_dy = 4 * 0.45 * k * (1 - k)
            p.squash = 0.82 + 0.18 * abs(2 * k - 1)
            p.arm_front = p.arm_back = (155 - 60 * k, 20)
            p.leg_front = (-25, 50)
            p.leg_back = (25, -40)
        else:             # aterrizaje
            k = (ph - 0.8) / 0.2
            p.squash = 1 + 0.3 * math.sin(k * math.pi)
            p.leg_front = p.leg_back = (15, -30 * (1 - k))
        p.extras.append("blush") if emotion in ("happy", "joy") else None
    elif action == "dance":
        ph = t * 2 * math.pi * beat / 2
        b = abs(math.sin(t * math.pi * beat))
        p.body_dy = b * 0.06
        p.squash = 1 + 0.08 * (1 - b)
        p.tilt = 12 * math.sin(ph)
        up = math.sin(ph) > 0
        p.arm_front = (150 + 20 * math.sin(ph * 2), -25) if up else (45, -100)
        p.arm_back = (45, -100) if up else (150 + 20 * math.sin(ph * 2), -25)
        p.leg_front = (20 * math.sin(ph), -20 * max(0, math.sin(ph)))
        p.leg_back = (-20 * math.sin(ph), -20 * max(0, -math.sin(ph)))
        p.look = (math.sin(ph) * 0.8, -0.3)
    elif action == "talk":
        ph = t * 2 * math.pi * 0.6
        p.arm_front = (40 + 25 * math.sin(ph), 50 + 20 * math.sin(ph * 1.7))
        p.arm_back = (12, 6)
        p.squash = 1 + 0.02 * math.sin(t * 2 * math.pi * 0.5)
        p.tilt = 3 * math.sin(ph * 0.5)
    elif action == "wave":
        ph = t * 2 * math.pi * 2.2
        p.arm_front = (150, 28 * math.sin(ph))
        p.arm_back = (12, 6)
        p.tilt = -4
        p.squash = 1 + 0.02 * math.sin(t * 2 * math.pi * 0.5)
    elif action in ("punch", "kick"):
        period = 0.7
        ph = (t % period) / period
        hit = math.sin(clamp(ph / 0.35) * math.pi / 2) if ph < 0.35 else 1 - ease_in_out((ph - 0.35) / 0.65)
        if action == "punch":
            alt = int(t / period) % 2
            fwd = (50 + 40 * hit, 90 * (1 - hit))
            guard = (35, 115)
            p.arm_front, p.arm_back = (fwd, guard) if alt == 0 else (guard, fwd)
            p.leg_front = (25, -10)
            p.leg_back = (-25, -10)
        else:
            p.leg_front = (-80 * hit - 5, 10)
            p.leg_back = (-15, -10)
            p.arm_front = (35, 115)
            p.arm_back = (35, 115)
        p.tilt = 8 * hit
        p.squash = 1 - 0.05 * hit
        p.emotion = emotion if emotion != "neutral" else "angry"
    elif action == "celebrate":
        ph = (t % 0.6) / 0.6
        p.body_dy = 4 * 0.18 * ph * (1 - ph)
        p.squash = 1.15 if ph < 0.08 or ph > 0.92 else 0.92
        p.arm_front = (160 + 12 * math.sin(t * 20), 0)
        p.arm_back = (160 - 12 * math.sin(t * 20), 0)
        p.leg_front = (-15, 20)
        p.leg_back = (15, -20)
        p.emotion = emotion if emotion != "neutral" else "joy"
    elif action == "float":
        p.body_dy = 0.12 + 0.05 * math.sin(t * 2 * math.pi * 0.5)
        p.leg_front = (15 + 8 * math.sin(t * 3), 25)
        p.leg_back = (-10 + 8 * math.sin(t * 3 + 1), 25)
        p.arm_front = (95 + 15 * math.sin(t * 3), -20)
        p.arm_back = (95 + 15 * math.sin(t * 3 + 2), -20)
        p.tilt = 4 * math.sin(t * 2)
    elif action == "scared_shake":
        p.tilt = 3 * math.sin(t * 60)
        p.squash = 1.06
        p.arm_front = (40, 120)
        p.arm_back = (40, 120)
        p.extras.append("hands_front")
        p.leg_front = (12, -15)
        p.leg_back = (-12, -15)
        p.emotion = "scared"
    elif action == "spin":
        p.tilt = (t * 360) % 360
        p.arm_front = (90, 0)
        p.arm_back = (90, 0)
    elif action == "think":
        p.arm_front = (30, 140)
        p.arm_back = (12, 6)
        p.extras.append("hands_front")
        p.look = (0.6, -0.8)
        p.tilt = -5
        p.emotion = emotion if emotion != "neutral" else "confused"
    elif action == "sit_bounce":
        b = abs(math.sin(t * math.pi * beat))
        p.squash = 1.05 + 0.07 * b
        p.leg_front = (-80, 70)
        p.leg_back = (-70, 70)
    else:  # idle
        br = math.sin(t * 2 * math.pi * 0.4 + seed)
        p.squash = 1 + 0.025 * br
        p.arm_front = (12 + 4 * br, 8)
        p.arm_back = (12 - 4 * br, 8)
        p.look = (0.3 * math.sin(t * 0.7 + seed), 0)
    return p


def actor_position(actor: dict, t: float, duration: float):
    """Posición normalizada (x, y) del actor en la escena, con easing."""
    fx, fy = actor.get("from", actor.get("pos", [0.5, 0.82]))
    tx, ty = actor.get("to", [fx, fy])
    t0 = actor.get("move_start", 0.0)
    t1 = actor.get("move_end", duration)
    k = clamp((t - t0) / max(0.01, t1 - t0))
    if actor.get("action") in ("walk", "run"):
        k = k  # velocidad constante evita patinaje
    else:
        k = ease_in_out(k)
    return fx + (tx - fx) * k, fy + (ty - fy) * k


def emotion_at(actor: dict, t: float) -> str:
    em = actor.get("emotion", "neutral")
    for change in actor.get("emotions", []):
        if t >= change.get("t", 0):
            em = change.get("emotion", em)
    return em


def action_at(actor: dict, t: float) -> str:
    act = actor.get("action", "idle")
    for change in actor.get("actions", []):
        if t >= change.get("t", 0):
            act = change.get("action", act)
    return act
