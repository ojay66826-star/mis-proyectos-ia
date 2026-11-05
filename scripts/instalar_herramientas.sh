#!/bin/bash
# Estudio de Animación IA: Blender 4 y 5.2, voz local, mocap, lip-sync y paquetes web
# Uso (como root, desde cualquier carpeta):  bash scripts/instalar_herramientas.sh
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq blender espeak-ng sox python3-numpy libegl1 libgles2 libgl1 libegl-mesa0 libgl1-mesa-dri
[ -x /opt/blender5-py/bin/python ] || { python3 -m venv /opt/blender5-py && /opt/blender5-py/bin/pip install -q bpy==5.2.3 numpy; }
[ -x /opt/mocap-py/bin/python ] || { python3 -m venv /opt/mocap-py && /opt/mocap-py/bin/pip install -q mediapipe opencv-python-headless; }
mkdir -p /opt/mocap-models
M=/opt/mocap-models/pose_landmarker_full.task
U=https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
[ -f $M ] || curl -sSL --fail -o $M $U || echo "aviso: no se pudo descargar el modelo de pose"
if [ ! -x /opt/rhubarb/rhubarb ]; then
  t=$(mktemp -d)
  curl -sSL --fail -o $t/r.zip https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Linux.zip \
    && echo "a9a9074862cff47b2d59b8bf399a678a3b0b74f9452ad6ad94cb292913dd8667  $t/r.zip" | sha256sum -c --quiet - \
    && unzip -q $t/r.zip -d $t && rm -rf /opt/rhubarb && mv $t/Rhubarb-Lip-Sync-1.14.0-Linux /opt/rhubarb \
    || echo "aviso: no se pudo instalar Rhubarb"
  rm -rf $t
fi
[ -x /opt/rhubarb/rhubarb ] && ln -sf /opt/rhubarb/rhubarb /usr/local/bin/rhubarb
R="$(cd "$(dirname "$0")/.." && pwd)"   # raíz del repositorio
(cd "$R" && npm ci --no-audit --no-fund && cd remotion && npm ci --no-audit --no-fund) || echo "aviso: npm ci falló"
ln -sf "$R/scripts/blender5" /usr/local/bin/blender5
