# Plantilla «datos curiosos 3D» (Three.js + capa de edición)

Video de datos curiosos en 3D real (Three.js), renderizado frame a frame con `scripts/capture.mjs`.
Cada escena es un módulo en `scenes/sN.js`; todo es función del tiempo, así que el render es determinista.

## Piezas

| Archivo | Qué hace |
|---|---|
| `index.html` | página base: estilos de subtítulos, chip «DATO n/5», sellos, tarjetas y transiciones |
| `core.js` | render (luz HDR de ambiente, sombras suaves, bloom), pasada de edición (aberración cromática, grano, viñeta, zoom blur, whip blur, glitch, flash, sepia), utilidades y transiciones |
| `overlay.js` | subtítulos palabra a palabra, golpe «#n», stickers con rebote, contadores, tarjetas |
| `panda.js` | Profe Bambú: panda 3D con boca sincronizada a la voz, parpadeo, cejas y accesorios |
| `scenes/s0…s6.js` | intro, 5 datos y final |
| `tools/preparar_datos.py` | crea `datos.json`: escenas, palabras (faster-whisper), envolvente de voz, beats y eventos |
| `tools/mezcla.py` | banda sonora: voz + música con ducking + ~350 efectos sintetizados y sincronizados |

## Flujo

1. Narración y música (ElevenLabs, con aprobación de coste) en `projects/<video>/v2/audio/`.
2. Transcribir con `faster-whisper` (marcas por palabra) → `transcripcion.json`
   (`HF_HUB_DISABLE_XET=1` en este entorno; decodificar el audio con ffmpeg, no con PyAV).
3. `python templates/web/datos3d/tools/preparar_datos.py` → `datos.json`.
4. Render por tramos en paralelo (4 núcleos ⇒ 6 procesos):
   `node scripts/capture.mjs templates/web/datos3d/index.html sN_a.mp4 --fps 30 --start 0 --duration <s> --query "scene=N"`.
5. `python templates/web/datos3d/tools/mezcla.py` → `banda_sonora.wav` (-14 LUFS).
6. Concatenar tramos + audio, escalar a 1080p, `python -m studio qc final.mp4`.

## Decisiones (por qué)

- Partículas con textura redonda y geometría con muchos segmentos: el usuario rechazó lo «cuadrado».
- Tone mapping Neutral + bloom con umbral 1.0: solo brilla lo emisivo; con bloom alto todo quedaba lechoso.
- Las transiciones se pintan dentro de cada escena (mitad al final, mitad al principio): el corte entre clips queda invisible.
- Eventos visuales anclados a palabras de la narración (`datos.json → events`), no a segundos fijos.
- Rendimiento con SwiftShader: ~2 s/frame a 1280×720 por proceso; 2.151 frames ≈ 50 min con 6 procesos.
