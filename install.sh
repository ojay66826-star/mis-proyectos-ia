#!/usr/bin/env bash
# Instalador del Estudio de Animación IA.
# Ubuntu/Debian (probado en Ubuntu 24.04). En macOS usa Homebrew. En Windows usa WSL2 (Ubuntu).
set -e
cd "$(dirname "$0")"

echo "==> 1/6 Paquetes del sistema (FFmpeg, Blender, espeak-ng, sox, OpenGL por software)"
if command -v apt-get >/dev/null; then
  sudo apt-get update
  sudo apt-get install -y ffmpeg blender espeak-ng sox python3-numpy python3-pip \
       libegl1 libegl-mesa0 libgl1-mesa-dri libgl1 nodejs npm
elif command -v brew >/dev/null; then
  brew install ffmpeg espeak-ng sox node python
  brew install --cask blender
else
  echo "Instala manualmente: ffmpeg, blender, espeak-ng, sox, Node.js 18+ y Python 3.10+"
fi

echo "==> 2/6 Dependencias de Python"
python3 -m pip install -r requirements.txt

echo "==> 3/6 Librerías web (Three.js, GSAP, Lottie)"
npm install --no-audit --no-fund

echo "==> 4/6 Navegador para capturar animaciones web (Playwright + Chromium)"
if ! node -e "require('playwright')" 2>/dev/null; then
  npm install -g playwright@1.49.1 && npx playwright install --with-deps chromium || \
    echo "Aviso: no se pudo instalar Playwright; la captura de plantillas web no estará disponible."
fi

echo "==> 5/6 Remotion (videos con React)"
(cd remotion && npm install --no-audit --no-fund)

echo "==> 6/6 Configuración"
[ -f .env ] || cp .env.example .env
python3 -m studio doctor

echo ""
echo "Listo. Abre la interfaz con:   python3 -m studio serve   →   http://127.0.0.1:8765"
