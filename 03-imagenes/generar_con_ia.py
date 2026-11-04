"""
Genera una imagen a partir de una descripción en texto usando un servicio de IA.

Este script usa la API de OpenAI (modelo de imágenes), porque es uno de los más
sencillos de configurar. Necesitas una clave de API (de pago).

Pasos:
  1. Crea una cuenta en https://platform.openai.com y genera una clave (API key).
  2. Instala la librería:      pip install openai
  3. Guarda la clave (en la terminal):
         export OPENAI_API_KEY="tu-clave-aqui"
  4. Ejecuta:
         python3 generar_con_ia.py "un gato astronauta pintado en acuarela"

La imagen se guarda en la carpeta "salida".
NUNCA subas tu clave a GitHub ni la pegues dentro del código.
"""
import base64
import os
import sys
from datetime import datetime
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print('Escribe una descripción. Ejemplo:\n  python3 generar_con_ia.py "un faro al atardecer"')
        sys.exit(1)
    if not os.environ.get("OPENAI_API_KEY"):
        print("Falta la clave. Ejecuta primero:  export OPENAI_API_KEY=\"tu-clave\"")
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print("Falta la librería. Ejecuta:  pip install openai")
        sys.exit(1)

    descripcion = " ".join(sys.argv[1:])
    print("Generando imagen para:", descripcion)

    cliente = OpenAI()
    respuesta = cliente.images.generate(model="gpt-image-1", prompt=descripcion, size="1024x1024")
    datos = base64.b64decode(respuesta.data[0].b64_json)

    carpeta = Path(__file__).parent / "salida"
    carpeta.mkdir(exist_ok=True)
    ruta = carpeta / f"ia_{datetime.now():%Y%m%d_%H%M%S}.png"
    ruta.write_bytes(datos)
    print("Imagen guardada en:", ruta)


if __name__ == "__main__":
    main()
