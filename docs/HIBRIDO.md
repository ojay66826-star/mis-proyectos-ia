# Modo híbrido: arte IA + motor del estudio

La IA de imagen crea **una vez** el arte de alta calidad (fondo por escena y personaje con variantes) y el motor lo
anima de forma determinista: deformación de malla (squash & stretch con volumen, respiración, inclinación hacia donde
se mueve, follow-through al acelerar/frenar), saltos y bailes con las curvas de `motion.pose_for`, lip-sync con la
variante de boca abierta, parpadeo, sombra de contacto, tinte de luz ambiente, fondo vivo (deriva lenta, rayos de luz,
motas) y cámara `speaker` que se acerca a quien habla.

## Flujo (Claude con el conector de ElevenLabs)

1. `creative_create_flow` (un flujo por proyecto).
2. **Fondo** por escena: `creative_generate_image`, modelo `gpt-image-2.5-sunburst`, aspecto 16:9 (por defecto) o 9:16.
   Prompt: *"Wide 16:9 background plate for a 2D animated short, no characters. <lugar>. <estilo>, <luz>. Leave open
   ground in the lower third for characters to stand. No text, no people, no animals."*
3. **Personaje**: crear el nodo con `estimate_only`, `creative_update_node` → `aspect_ratio: "2:3"`, y
   `creative_run_flow_nodes`. Prompt: cuerpo entero, de frente/3⁄4, brazos algo separados, **"Plain flat pure white
   background, no shadow on the ground, no props, no text."** Personajes siempre originales.
4. **Variantes** (boca abierta, ojos cerrados, expresiones): fijar la imagen elegida con `creative_add_flow_asset_node`
   y `creative_edit_image` con el esquema *Change / Preserve / Constraints* (solo cambia boca u ojos).
5. Descargar (`content_url`) a `projects/ia-assets/<proyecto>/` — necesita el host `elevenlabsusercontent.com`
   permitido en la red del entorno.
6. Preparar:
   ```bash
   python -m studio sprite cutout miso.png                      # → miso_cut.png (fondo liso fuera, local)
   python -m studio sprite patch miso_cut.png boca_*_cut.png -o miso_boca.png   # elige la mejor y pega solo boca
   python -m studio sprite patch miso_cut.png ojos_*_cut.png -o miso_ojos.png
   ```
   `patch` es necesario porque el editor IA redibuja al personaje entero con pequeñas diferencias: intercambiar
   imágenes completas lo haría "saltar". Se alinea la cabeza y se pega solo lo que cambia.
7. `project.json` (o editar el de `plan`) y `python -m studio render`.

## Campos del project.json

```jsonc
{
  "assets_dir": "projects/ia-assets/miso_parque",          // rutas relativas de las imágenes
  "characters": [{"id": "miso", "name": "Miso", "voice": "child",
                  "sprite": {"base": "miso_base.png", "talk": "miso_boca.png", "blink": "miso_ojos.png",
                             "expressions": {"sad": "miso_triste.png"},   // opcional, por emoción
                             "facing": 1}}],                              // hacia dónde mira el dibujo
  "scenes": [{"background": "park", "background_image": "fondo.png", "lighting": true,
              "camera": {"type": "speaker"}, "actors": […], "dialogue": […]}]
}
```

Todo lo demás (acciones, emociones, efectos, transiciones, audio, subtítulos, QC, `export --preset capcut`) funciona
igual que con personajes procedurales.

## Coste orientativo (ElevenLabs, gpt-image-2.5-sunburst, calidad high, 1K)

| Imagen | Créditos por imagen |
|---|---|
| Fondo 16:9 | ~190 |
| Personaje 2:3 | ~268 |
| Edición (variante boca/ojos/expresión) | ~433 |

Se generan 4 opciones por llamada salvo que se pida otra cosa: un personaje con fondo, boca y ojos son 4×(190+268+433+433)
≈ 5.300 créditos; con 1 opción por imagen, ≈ 1.300. Usar `estimate_only` antes de generar y avisar al usuario.

## Límites

- El sprite es un dibujo único deformado: camina "deslizándose" con rebote e inclinación, no mueve piernas ni brazos
  por separado. Para gestos de brazos hacen falta más variantes de pose (otra edición por pose) o video IA.
- `patch` funciona bien con cambios locales (boca, ojos, cejas); un cambio de pose completo no se puede parchear.
