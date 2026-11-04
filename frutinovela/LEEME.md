# Frutinovela: "Amor de Licuadora" (10 s)

`python3 render.py` crea `frutinovela_amor.mp4` (1080x1920, 30 fps).

La carpeta `voces/` ya trae las 10 voces de ElevenLabs (Betty, Ezequiel, Yadira y Josué Maya).
El video se alarga solo para que cada frase quepa con su ritmo natural: con estas voces
dura unos 19 s; con las voces sintéticas de respaldo, 10 s.

## Voces con ElevenLabs

**Opción A, automática (API):**

```bash
export ELEVENLABS_API_KEY=...      # tu clave de ElevenLabs
python3 render.py
```

Los audios se guardan en `voces/`, así que al volver a renderizar no se gastan créditos.
Para cambiar una voz, usa `ELEVENLABS_VOZ_FRESA`, `ELEVENLABS_VOZ_PLATANO`, `ELEVENLABS_VOZ_PINA`
o `ELEVENLABS_VOZ_NARRADOR` con el *voice ID* que quieras. Para cambiar el modelo, usa `ELEVENLABS_MODELO`.

**Opción B, manual (desde elevenlabs.io):** genera cada línea en la web, descárgala con
este nombre en la carpeta `voces/` y ejecuta `python3 render.py`. Si una línea dura de más,
la escena se alarga para que quepa (y la voz se acelera como máximo un 10 %, sin cambiar el tono).

| Archivo | Personaje | Línea | Máx. |
|---|---|---|---|
| `01_fresa.mp3` | Fresa | ¡¿Me engañaste con la piña?! | 1,4 s |
| `02_platano.mp3` | Plátano | ¡No es lo que parece, fresita! | 1,35 s |
| `03_pina.mp3` | Piña | ¡Alto ahí! | 0,4 s |
| `04_pina.mp3` | Piña | ¡Fresa! ¡Soy tu madre! | 1,2 s |
| `05_fresa.mp3` | Fresa | ¿Mamá? | 0,35 s |
| `06_platano.mp3` | Plátano | ¿Suegra? | 0,35 s |
| `07_fresa.mp3` | Fresa | ¿Y mi papá? | 0,38 s |
| `08_platano.mp3` | Plátano | Me da igual. ¿Te casas conmigo? | 1,2 s |
| `09_fresa.mp3` | Fresa | ¡Sí, mi platanito! | 1,0 s |
| `10_narrador.mp3` | Narrador | Continuará. | 0,65 s |

Las líneas que no tengan audio usan la voz sintética de respaldo (espeak-ng + MBROLA).
