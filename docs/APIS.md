# Servicios y APIs de IA

El estudio funciona **completo sin ninguna clave**. Las APIs externas son mejoras opcionales.
Configúralas copiando `.env.example` a `.env` (el archivo `.env` nunca se sube a GitHub) y comprueba con:

```bash
python -m studio doctor          # qué claves están configuradas
python -m studio doctor --online # si tu red llega a cada servicio
```

## Estado real de cada integración

| Servicio | Para qué | Clave (.env) | Coste | Estado |
|---|---|---|---|---|
| **Motor 2D propio** | animación completa | — | gratis | ✅ Probado |
| **Blender 4.0** (EEVEE/Workbench/Cycles) | 3D, GLB | — | gratis | ✅ Probado |
| **FFmpeg 6.1** | edición, codificación, QC | — | gratis | ✅ Probado |
| **espeak-ng** | voces en español (es-419) | — | gratis | ✅ Probado |
| **Three.js 0.170 / GSAP 3.15 / lottie-web 5.12** | animación web | — | gratis | ✅ Probado (captura con Chromium) |
| **Remotion 4.0.290** | video con React | — | gratis para personas y empresas pequeñas ([licencia](https://www.remotion.dev/license)) | ✅ Probado |
| **Pollinations.ai** | imágenes FLUX sin cuenta | — | gratis | ⚠️ Implementado, **no probado** (el dominio estaba bloqueado en el entorno de construcción) |
| **Hugging Face Inference** | imágenes FLUX.1-schnell | `HF_TOKEN` | gratis con límite | ⚠️ Implementado, no probado (sin token) |
| **OpenAI Images** (`gpt-image-1`) | imágenes | `OPENAI_API_KEY` | de pago | ⚠️ Implementado, no probado |
| **Stability AI** (Stable Image Core) | imágenes | `STABILITY_API_KEY` | de pago | ⚠️ Implementado, no probado |
| **Replicate** (por defecto `minimax/video-01`) | texto/imagen → video | `REPLICATE_API_TOKEN` | pago por uso | ⚠️ Implementado, no probado |
| **ElevenLabs TTS** | voces realistas | `ELEVENLABS_API_KEY` + `STUDIO_TTS=elevenlabs` | plan gratis limitado | ⚠️ Implementado, no probado |
| **OpenAI TTS** | voces | `OPENAI_API_KEY` + `STUDIO_TTS=openai` | de pago | ⚠️ Implementado, no probado |
| **Claude API** (`claude-opus-5-5`, salida estructurada) | guiones creativos (`--ai`) | `ANTHROPIC_API_KEY` | de pago | ⚠️ Implementado con el SDK oficial, no probado (sin clave) |
| **Conector ElevenLabs en Claude** | imagen/video/voz desde la conversación | conexión en claude.ai | créditos de tu cuenta | 🔌 Disponible para Claude si lo tienes conectado |

"Implementado, no probado" significa: el código sigue la documentación oficial del servicio, pero no se pudo ejecutar
contra el servicio real durante la construcción. Si algo falla, el estudio vuelve al motor local y muestra el error.

## Cómo obtener cada clave

1. **Hugging Face (gratis)**: crea cuenta en https://huggingface.co → Settings → Access Tokens → *New token* (tipo *Read*
   con permiso "Inference Providers"). Pega en `HF_TOKEN=`.
2. **Replicate**: https://replicate.com → Account → API tokens. Requiere método de pago. Elige modelo en
   `REPLICATE_VIDEO_MODEL` (ej. `minimax/video-01`, o el que recomiende Replicate en "Video generation").
   Si el modelo usa otro nombre para la imagen inicial, ajusta `REPLICATE_IMAGE_FIELD` (`image`, `first_frame_image`…).
3. **ElevenLabs**: https://elevenlabs.io → Profile → API Keys. Opcional `ELEVENLABS_VOICE_ID` (Voice Library → ID).
4. **OpenAI**: https://platform.openai.com/api-keys (requiere saldo).
5. **Stability**: https://platform.stability.ai/account/keys.
6. **Anthropic (Claude)**: https://console.anthropic.com → API Keys.

## Alternativas de código abierto (en tu propio PC con GPU)

| Necesidad | Proyecto | Requisito |
|---|---|---|
| Texto/imagen → video | Wan 2.x, LTX-Video, CogVideoX vía **ComfyUI** | GPU NVIDIA ≥ 12–24 GB |
| Imágenes | FLUX.1-schnell / SDXL vía ComfyUI o diffusers | GPU ≥ 8–12 GB |
| Upscaling | Real-ESRGAN ncnn (`realesrgan-ncnn-vulkan`, detectado automáticamente) | GPU con Vulkan |
| Lip-sync preciso | Rhubarb Lip Sync | CPU |
| Lip-sync sobre caras reales | Wav2Lip / SadTalker | GPU |
| Voces locales naturales | Piper TTS (voces es_ES / es_MX) | CPU |

Para conectar uno de estos, añade una función en `studio/providers.py` siguiendo el patrón de `_img_hf`.
