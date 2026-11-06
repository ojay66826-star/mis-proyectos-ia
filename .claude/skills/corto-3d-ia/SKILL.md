---
name: corto-3d-ia
description: Método PREFERIDO por el usuario para cortos y animaciones de calidad película 3D (estilo animación de estudio) con IA: hoja de personajes → storyboard de fotogramas → video Kling 3 Pro desde cada fotograma (con voces en español y sonido) → montaje con `python -m studio assemble`. Incluye personajes guardados (Miso y Pipa), biblioteca de movimientos probados, costes reales y errores a evitar. Úsala para 'corto', 'animación 3D', 'tipo película', 'historia animada de calidad', 'como Pixar', 'personajes 3D', o cuando el usuario quiera reutilizar a Miso/Pipa o los movimientos guardados.
---

# Corto 3D con IA (método probado y aprobado por el usuario)

Resultado de referencia: **«Miso y la cometa perdida»** (62 s, 9 planos, 1080p) — el usuario dijo «me gustó mucho».
Todo lo necesario para repetirlo está en `biblioteca/`.

## Reglas del usuario (obligatorias)

- **Hablar SIEMPRE en español**, todos los mensajes, sin excepción.
- **Estilo**: película de animación 3D. **No** usar el motor procedural 2D ni el modo "sprite" (imagen fija que se
  desliza): el usuario lo rechazó («no me gustó para nada»). Tampoco la voz robótica (espeak).
- **Coste antes de gastar**: estimar con `estimate_only` y pedir confirmación con la cifra en créditos y US$. Avisar si
  el coste real supera lo dicho. Nunca repetir una generación para "reintentar" sin avisar.
- Personajes **originales** (nunca de terceros).

## Qué hay guardado

| Recurso | Ruta |
|---|---|
| Miso (gato atigrado naranja, pañuelo verde azulado) y Pipa (ardilla roja, flor amarilla) | `biblioteca/personajes/miso_y_pipa/` (`ficha.json` + `hoja_personajes.jpg`) |
| 9 movimientos/planos con prompt plantilla y resultado | `biblioteca/movimientos_3d.json` |
| Corto completo: guion, storyboard, prompts y costes | `biblioteca/cortos/miso_y_la_cometa/` |

Para reutilizar a Miso/Pipa sin subir archivos: en el flujo nuevo,
`creative_add_flow_asset_node(modality="image", generation_id="C4uTIhXNPkHeYERexjs0")` y usar el `node_id` devuelto
como `connect_from` en `creative_edit_image`. (Es la hoja guardada en el historial de ElevenLabs del usuario.)

## Pipeline (conector ElevenLabs)

0. **Red**: el entorno debe permitir `elevenlabsusercontent.com` (descargas). Ya está en el entorno «Axel».
1. **Guion** → `guion.json` (ver ejemplo en `biblioteca/cortos/miso_y_la_cometa/guion.json`): 8–10 planos de 6–8 s,
   1–2 frases cortas de diálogo por plano, gags visuales claros. Proponer y pedir aprobación + formato (16:9 / 9:16).
2. **Flujo**: `creative_create_flow` (todo en el mismo flujo para poder conectar nodos).
3. **Hoja de personajes** (1 imagen, `gpt-image-2.5-sunburst`, ~190 cr): ambos personajes de cuerpo entero, fondo gris
   liso, mismo estilo. Prompt en `ficha.json → prompt_hoja_completo`. O reutilizar la guardada (arriba).
4. **Storyboard** (1 fotograma por plano, `creative_edit_image` con `connect_from` = hoja, `generations_count: 1`,
   ~433 cr c/u): plantilla `movimientos_3d.json → plantilla_fotograma`. Descargar, montar hoja de contactos
   (`storyboard.jpg`) y **enseñarla al usuario antes del video**.
5. **Video** (Kling 3 Pro, ~1.018 cr/segundo = ~1,85 US$/10 s):
   - `creative_generate_video(model_id="kling-3-pro", connect_from=[nodo_fotograma], estimate_only=true, prompt=…)`
     para crear cada nodo sin gastar;
   - `creative_update_node(model_parameters={"duration_secs": N, "aspect_ratio": "16:9", "generate_audio": true, "resolution": "1080p"})`;
   - `creative_run_flow_nodes(node_ids=[…todos…], estimate_only=true)` → cifra exacta → confirmar → mismo call sin
     `estimate_only`. Los 9 se generan en paralelo (~5–6 min).
   - Esperar con `Bash run_in_background` + `until [ $(date +%s) -ge $end ]; do sleep 2; done` (sleep directo está
     bloqueado) y consultar `creative_get_flow_run_status`.
6. **Descargar** `content_url` de cada plano a `projects/ia-assets/<corto>/planos/pN.mp4` y **revisar 4 fotogramas por
   plano** (consistencia del personaje, que la acción ocurra). Rehacer solo el plano roto, avisando del coste.
7. **Montaje** (gratis):
   ```bash
   python -m studio assemble planos/p{1..9}.mp4 --title "Título" --end "Fin" --music happy --music-gain 0.16 \
       --fade-into 9 -o final.mp4
   python -m studio qc final.mp4
   ```
   Normaliza 1920×1080@24, título con fundido sobre el plano 1, música procedural con ducking bajo las voces de Kling,
   fundido hacia el plano indicado, cartela final y -14 LUFS. (El aviso de "tramo negro" en QC es la cartela final.)
8. **Entregar** con `SendUserFile` (no Google Drive: no admite archivos grandes). Decir el coste total real y pedir al
   usuario que **escuche** el audio (Claude no puede oírlo): pronunciación en español y sincronía labial.

## Costes reales (noviembre 2026, cuenta del usuario)

| Paso | Créditos | ~US$ |
|---|---|---|
| Imagen 16:9 (`gpt-image-2.5-sunburst`, high, 1K) | 190 | 0,035 |
| Imagen 2:3 | 268 | 0,05 |
| Edición / fotograma de storyboard | 433 | 0,08 |
| Kling 3 Pro, por segundo de video con audio 1080p | ~1.018 | ~0,185 |
| Corto de 60 s completo (hoja + 9 fotogramas + 9 planos) | ~65.200 | ~11,85 |

Otros modelos estimados (5 s): Veo 3.1 Fast ~7.270 cr; Seedance 2.5 ~14.000 cr.

## Errores a evitar (aprendidos)

- Texto→video sin fotograma inicial: el personaje cambia en cada plano. Siempre storyboard primero.
- Editar imágenes con IA para variantes de cara redibuja todo el cuerpo (no sirve para "sprites").
- Kling a veces cambia un detalle del gag (ej. trepa antes de caer) o no completa el último beat (no asoma de las
  hojas): describir beats en orden y, si un beat es esencial, darle su propio plano.
- No prometer subtítulos sincronizados sin tiempos reales de las frases.
- La música se añade en el montaje (en los prompts: "No music").

## Relacionadas

`animation-workflow` (orquestador), `animated-storytelling`, `animation-scripting`, `animation-storyboarding`,
`ai-video-generation`, `animation-quality-control`, `animation-optimization` (exportes y paquete CapCut).
