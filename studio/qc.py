"""Control de calidad automático de videos (ffprobe + filtros de FFmpeg)."""
from __future__ import annotations

import re
import subprocess

from .exporter import probe


def _ffmpeg_filter_log(video, vf=None, af=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video)]
    if vf:
        cmd += ["-vf", vf]
    if af:
        cmd += ["-af", af]
    cmd += ["-f", "null", "-"]
    return subprocess.run(cmd, capture_output=True, text=True).stderr


def check_video(video, expected_duration=None, expect_audio=True, target_lufs=-14.0) -> dict:
    info = probe(video)
    checks = []

    def add(name, ok, detail, severity="error"):
        checks.append(dict(check=name, ok=bool(ok), detail=detail, severity=severity if not ok else "ok"))

    add("archivo válido", info["duration"] > 0, f"{info['duration']:.2f}s, {info['width']}x{info['height']} @ {info['fps']} fps")
    add("códec H.264", info["vcodec"] == "h264", f"video: {info['vcodec']}", "warning")
    add("dimensiones pares", (info["width"] or 1) % 2 == 0 and (info["height"] or 1) % 2 == 0, "requerido por yuv420p")
    if expected_duration:
        diff = abs(info["duration"] - expected_duration)
        add("duración esperada", diff < 0.6, f"esperada {expected_duration:.2f}s, real {info['duration']:.2f}s (Δ {diff:.2f}s)", "warning")
    if expect_audio:
        add("pista de audio", info["acodec"] is not None, f"audio: {info['acodec']}")
    log = _ffmpeg_filter_log(video, vf="blackdetect=d=0.5:pix_th=0.06,freezedetect=n=0.001:d=2.5")
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)
    freezes = re.findall(r"freeze_duration: ([\d.]+)", log)
    add("sin tramos negros largos", not blacks, f"{len(blacks)} tramo(s) negros ≥0.5s" if blacks else "ninguno", "warning")
    add("sin congelamientos", not freezes, f"{len(freezes)} congelamiento(s) ≥2.5s" if freezes else "ninguno", "warning")
    if info["acodec"]:
        alog = _ffmpeg_filter_log(video, af="ebur128=peak=true")
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", alog)
        pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", alog)
        if m:
            lufs = float(m[-1])
            add("sonoridad (LUFS)", -24 <= lufs <= -8, f"{lufs:.1f} LUFS integrado (objetivo redes ≈ {target_lufs})", "warning")
        if pk:
            add("sin saturación", float(pk[-1]) <= 0.0, f"pico {pk[-1]} dBFS", "warning")
    passed = all(c["ok"] or c["severity"] != "error" for c in checks)
    return dict(video=str(video), passed=passed, info=info, checks=checks,
                warnings=sum(1 for c in checks if not c["ok"] and c["severity"] == "warning"))
