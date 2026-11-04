"""
Crea un video animado (MP4) con texto y formas en movimiento.
No necesita internet ni claves: usa Python + Pillow para dibujar cada
fotograma y ffmpeg para unirlos en un video.

Uso:
    python3 crear_video.py
    python3 crear_video.py --texto "¡Feliz cumpleaños!" --segundos 6

El video aparece en la carpeta "salida".
"""
import argparse
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ANCHO, ALTO, FPS = 1080, 1080, 30  # formato cuadrado, ideal para redes sociales
CARPETA = Path(__file__).parent / "salida"
COLORES = [(255, 122, 89), (255, 179, 71), (106, 76, 147), (8, 126, 139), (149, 213, 178)]


def fuente(tam):
    for ruta in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "C:/Windows/Fonts/arialbd.ttf"]:
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tam)
    return ImageFont.load_default(size=tam)


def fotograma(n, total, texto, letra):
    t = n / total  # avance de 0 a 1
    img = Image.new("RGB", (ANCHO, ALTO), (15, 16, 32))
    d = ImageDraw.Draw(img)

    # Círculos que giran alrededor del centro
    for i, color in enumerate(COLORES):
        angulo = 2 * math.pi * (t + i / len(COLORES))
        radio_orbita = 300 + 40 * math.sin(4 * math.pi * t + i)
        x = ANCHO / 2 + radio_orbita * math.cos(angulo)
        y = ALTO / 2 + radio_orbita * math.sin(angulo)
        r = 60 + 20 * math.sin(6 * math.pi * t + i)
        d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    # Texto que aparece poco a poco (fundido) en el centro
    opacidad = min(1, t * 3)
    gris = int(255 * opacidad)
    caja = d.textbbox((0, 0), texto, font=letra)
    w, h = caja[2] - caja[0], caja[3] - caja[1]
    d.text(((ANCHO - w) / 2, (ALTO - h) / 2), texto, font=letra, fill=(gris, gris, gris))
    return img


def main():
    parser = argparse.ArgumentParser(description="Crea un video animado")
    parser.add_argument("--texto", default="Hola, mundo")
    parser.add_argument("--segundos", type=float, default=5)
    parser.add_argument("--nombre", default="animacion.mp4")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        print("Falta ffmpeg. Instálalo desde https://ffmpeg.org/download.html")
        return

    CARPETA.mkdir(exist_ok=True)
    salida = CARPETA / args.nombre
    total = int(args.segundos * FPS)
    letra = fuente(90)

    # Enviamos los fotogramas directamente a ffmpeg (sin guardar miles de imágenes)
    comando = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{ANCHO}x{ALTO}", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", str(salida)]
    proceso = subprocess.Popen(comando, stdin=subprocess.PIPE)
    for n in range(total):
        proceso.stdin.write(fotograma(n, total, args.texto, letra).tobytes())
    proceso.stdin.close()
    proceso.wait()

    # También guardamos una imagen de vista previa
    fotograma(total // 2, total, args.texto, letra).save(CARPETA / "vista_previa.png")
    print(f"Video creado: {salida}  ({args.segundos}s, {total} fotogramas)")


if __name__ == "__main__":
    main()
