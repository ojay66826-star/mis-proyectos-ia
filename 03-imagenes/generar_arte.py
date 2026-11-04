"""
Genera imágenes de arte abstracto SIN internet y SIN claves (solo Python + Pillow).

Uso:
    python3 generar_arte.py                # crea 3 imágenes
    python3 generar_arte.py --cantidad 5   # crea 5 imágenes
    python3 generar_arte.py --semilla 42   # mismo número = misma imagen

Las imágenes aparecen en la carpeta "salida".
"""
import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

PALETAS = {
    "atardecer": ["#ff7a59", "#ffb347", "#ff5e78", "#6a4c93", "#1d1a39"],
    "oceano": ["#0b3954", "#087e8b", "#bfd7ea", "#ff5a5f", "#c81d25"],
    "bosque": ["#2d6a4f", "#40916c", "#95d5b2", "#d8f3dc", "#081c15"],
}

CARPETA = Path(__file__).parent / "salida"


def crear_imagen(semilla: int, paleta: str, ancho=1024, alto=1024) -> Path:
    rng = random.Random(semilla)
    colores = PALETAS[paleta]

    imagen = Image.new("RGB", (ancho, alto), colores[-1])
    capa = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(capa)

    # Círculos grandes y difuminados de fondo
    for _ in range(12):
        r = rng.randint(150, 450)
        x, y = rng.randint(0, ancho), rng.randint(0, alto)
        color = colores[rng.randint(0, len(colores) - 2)]
        dibujo.ellipse((x - r, y - r, x + r, y + r), fill=color + "90")
    capa = capa.filter(ImageFilter.GaussianBlur(60))
    imagen.paste(capa, (0, 0), capa)

    # Formas nítidas encima
    dibujo = ImageDraw.Draw(imagen)
    for _ in range(25):
        x, y = rng.randint(0, ancho), rng.randint(0, alto)
        tam = rng.randint(10, 90)
        color = rng.choice(colores[:-1])
        if rng.random() < 0.5:
            dibujo.ellipse((x, y, x + tam, y + tam), outline=color, width=4)
        else:
            dibujo.line((x, y, x + tam * 2, y - tam), fill=color, width=5)

    CARPETA.mkdir(exist_ok=True)
    ruta = CARPETA / f"arte_{paleta}_{semilla}.png"
    imagen.save(ruta)
    return ruta


def main():
    parser = argparse.ArgumentParser(description="Generador de arte abstracto")
    parser.add_argument("--cantidad", type=int, default=3)
    parser.add_argument("--semilla", type=int, default=None)
    args = parser.parse_args()

    base = args.semilla if args.semilla is not None else random.randint(0, 99999)
    nombres = list(PALETAS)
    for i in range(args.cantidad):
        ruta = crear_imagen(base + i, nombres[i % len(nombres)])
        print("Imagen creada:", ruta)


if __name__ == "__main__":
    main()
