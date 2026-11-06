#!/usr/bin/env bash
# Descarga las voces neuronales locales de Piper (gratis, ~270 MB) a models/piper/.
# Requiere: pip install piper-tts  y acceso a huggingface.co (+ su CDN us.aws.cdn.hf.co).
set -euo pipefail
cd "$(dirname "$0")/../models" 2>/dev/null || { mkdir -p "$(dirname "$0")/../models"; cd "$(dirname "$0")/../models"; }
mkdir -p piper && cd piper
for v in es/es_MX/claude/high/es_MX-claude-high es/es_MX/ald/medium/es_MX-ald-medium \
         es/es_ES/davefx/medium/es_ES-davefx-medium es/es_ES/sharvard/medium/es_ES-sharvard-medium; do
  n=$(basename "$v")
  [ -s "$n.onnx" ] && { echo "ya está $n"; continue; }
  curl -sSfL -o "$n.onnx" "https://huggingface.co/rhasspy/piper-voices/resolve/main/$v.onnx"
  curl -sSfL -o "$n.onnx.json" "https://huggingface.co/rhasspy/piper-voices/resolve/main/$v.onnx.json"
  echo "ok $n"
done
