# Referencia de la línea de comandos

Todos los comandos se ejecutan desde la carpeta del repositorio con `python -m studio <comando>`.
Los resultados se guardan en `projects/` (o en la ruta de `-o`).

## `make`

```text
usage: python -m studio make [-h] [--style STYLE] [--format FORMAT]
                             [--background BACKGROUND] [--duration DURATION]
                             [--mood MOOD] [--quality {preview,hd,fullhd}]
                             [--ai] [--3d] [--engine {rapido,eevee,cycles}]
                             [--transition {fade,wipe,slide,circle,dip,cut}]
                             [--no-voice] [--storyboard-only] [-o OUTPUT]
                             prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  --style STYLE         cartoon, anime, pixel, minimalist, cute, cinematic,
                        horror, fantasy, paper, clay, stopmotion, realistic,
                        comic, retro
  --format FORMAT       16:9 | 9:16 | 1:1 | 4:5
  --background BACKGROUND
  --duration DURATION
  --mood MOOD
  --quality {preview,hd,fullhd}
  --ai                  usar Claude para escribir el guion (requiere
                        ANTHROPIC_API_KEY)
  --3d                  renderizar en 3D con Blender
  --engine {rapido,eevee,cycles}
  --transition {fade,wipe,slide,circle,dip,cut}
  --no-voice
  --storyboard-only
  -o, --output OUTPUT
```

## `plan`

```text
usage: python -m studio plan [-h] [--style STYLE] [--format FORMAT]
                             [--background BACKGROUND] [--duration DURATION]
                             [--ai] [-o OUTPUT]
                             prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  --style STYLE         cartoon, anime, pixel, minimalist, cute, cinematic,
                        horror, fantasy, paper, clay, stopmotion, realistic,
                        comic, retro
  --format FORMAT       16:9 | 9:16 | 1:1 | 4:5
  --background BACKGROUND
  --duration DURATION
  --ai
  -o, --output OUTPUT
```

## `render`

```text
usage: python -m studio render [-h] [--quality {preview,hd,fullhd}]
                               [-o OUTPUT]
                               project

positional arguments:
  project

options:
  -h, --help            show this help message and exit
  --quality {preview,hd,fullhd}
  -o, --output OUTPUT
```

## `character`

```text
usage: python -m studio character [-h] [--name NAME] [--color COLOR]
                                  [--accessory ACCESSORY]
                                  [--eyes {round,anime,dot}] [--style STYLE]
                                  [-o OUTPUT]
                                  species

positional arguments:
  species

options:
  -h, --help            show this help message and exit
  --name NAME
  --color COLOR
  --accessory ACCESSORY
  --eyes {round,anime,dot}
  --style STYLE
  -o, --output OUTPUT
```

## `character3d`

```text
usage: python -m studio character3d [-h] [--name NAME] [--color COLOR]
                                    [--action ACTION] [--duration DURATION]
                                    [--engine {rapido,eevee,cycles}]
                                    [-o OUTPUT]
                                    species

positional arguments:
  species

options:
  -h, --help            show this help message and exit
  --name NAME
  --color COLOR
  --action ACTION
  --duration DURATION
  --engine {rapido,eevee,cycles}
  -o, --output OUTPUT
```

## `image`

```text
usage: python -m studio image [-h] [--style STYLE] [--format FORMAT]
                              [--background BACKGROUND] [--provider PROVIDER]
                              [--width WIDTH] [--height HEIGHT] [--seed SEED]
                              [-o OUTPUT]
                              prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  --style STYLE         cartoon, anime, pixel, minimalist, cute, cinematic,
                        horror, fantasy, paper, clay, stopmotion, realistic,
                        comic, retro
  --format FORMAT       16:9 | 9:16 | 1:1 | 4:5
  --background BACKGROUND
  --provider PROVIDER   auto | local | pollinations | huggingface | openai |
                        stability
  --width WIDTH
  --height HEIGHT
  --seed SEED
  -o, --output OUTPUT
```

## `img2video`

```text
usage: python -m studio img2video [-h] [--move MOVE] [--effects EFFECTS]
                                  [--style STYLE] [--format FORMAT]
                                  [--duration DURATION] [--fps FPS]
                                  [--music MUSIC] [--quality QUALITY]
                                  [--provider {local,replicate}]
                                  [--prompt PROMPT] [-o OUTPUT]
                                  image

positional arguments:
  image

options:
  -h, --help            show this help message and exit
  --move MOVE           zoom_in, zoom_out, pan_left, pan_right, pan_up, orbit,
                        parallax, breathe
  --effects EFFECTS     lista separada por comas: sparkles,rain,snow,fire,fog…
  --style STYLE
  --format FORMAT
  --duration DURATION
  --fps FPS
  --music MUSIC
  --quality QUALITY
  --provider {local,replicate}
  --prompt PROMPT
  -o, --output OUTPUT
```

## `text`

```text
usage: python -m studio text [-h] [--mode {pop,slide,wave,typewriter}]
                             [--format FORMAT] [--duration DURATION]
                             [--palette PALETTE] [--music MUSIC] [-o OUTPUT]
                             text

positional arguments:
  text

options:
  -h, --help            show this help message and exit
  --mode {pop,slide,wave,typewriter}
  --format FORMAT
  --duration DURATION
  --palette PALETTE
  --music MUSIC
  -o, --output OUTPUT
```

## `logo`

```text
usage: python -m studio logo [-h] [--tagline TAGLINE] [--color COLOR]
                             [--duration DURATION] [--format FORMAT]
                             [-o OUTPUT]
                             name

positional arguments:
  name

options:
  -h, --help           show this help message and exit
  --tagline TAGLINE
  --color COLOR
  --duration DURATION
  --format FORMAT
  -o, --output OUTPUT
```

## `infographic`

```text
usage: python -m studio infographic [-h] [--title TITLE] [--unit UNIT]
                                    [--duration DURATION] [--format FORMAT]
                                    [-o OUTPUT]
                                    data

positional arguments:
  data                 "Lunes=10,Martes=25,Miércoles=17"

options:
  -h, --help           show this help message and exit
  --title TITLE
  --unit UNIT
  --duration DURATION
  --format FORMAT
  -o, --output OUTPUT
```

## `background`

```text
usage: python -m studio background [-h] [--duration DURATION]
                                   [--format FORMAT] [--palette PALETTE]
                                   [-o OUTPUT]
                                   {blobs,gradient,grid,particles}

positional arguments:
  {blobs,gradient,grid,particles}

options:
  -h, --help            show this help message and exit
  --duration DURATION
  --format FORMAT
  --palette PALETTE
  -o, --output OUTPUT
```

## `lottie`

```text
usage: python -m studio lottie [-h] [--color COLOR] [-o OUTPUT]

options:
  -h, --help           show this help message and exit
  --color COLOR
  -o, --output OUTPUT
```

## `web`

```text
usage: python -m studio web [-h] [--duration DURATION] [--fps FPS]
                            [--width WIDTH] [--height HEIGHT] [--query QUERY]
                            [-o OUTPUT]
                            template

positional arguments:
  template             gsap-logo | svg-css-character | lottie-player |
                       kinetic-type | interactive | three-scene | ruta.html

options:
  -h, --help           show this help message and exit
  --duration DURATION
  --fps FPS
  --width WIDTH
  --height HEIGHT
  --query QUERY
  -o, --output OUTPUT
```

## `remotion`

```text
usage: python -m studio remotion [-h] [--style STYLE] [--format FORMAT]
                                 [-o OUTPUT]
                                 source

positional arguments:
  source               project.json o instrucción en texto

options:
  -h, --help           show this help message and exit
  --style STYLE
  --format FORMAT
  -o, --output OUTPUT
```

## `export`

```text
usage: python -m studio export [-h] [--preset PRESET] [-o OUTPUT] video

positional arguments:
  video

options:
  -h, --help           show this help message and exit
  --preset PRESET      youtube, youtube_shorts, tiktok, instagram, web,
                       whatsapp, webm, gif, zip
  -o, --output OUTPUT
```

## `upscale`

```text
usage: python -m studio upscale [-h] [--factor FACTOR]
                                [--method {lanczos,bicubic,realesrgan}]
                                [-o OUTPUT]
                                video

positional arguments:
  video

options:
  -h, --help            show this help message and exit
  --factor FACTOR
  --method {lanczos,bicubic,realesrgan}
  -o, --output OUTPUT
```

## `interpolate`

```text
usage: python -m studio interpolate [-h] [--fps FPS] [-o OUTPUT] video

positional arguments:
  video

options:
  -h, --help           show this help message and exit
  --fps FPS
  -o, --output OUTPUT
```

## `loop`

```text
usage: python -m studio loop [-h] [--crossfade CROSSFADE] [-o OUTPUT] video

positional arguments:
  video

options:
  -h, --help            show this help message and exit
  --crossfade CROSSFADE
  -o, --output OUTPUT
```

## `qc`

```text
usage: python -m studio qc [-h] [--duration DURATION] [--no-audio] video

positional arguments:
  video

options:
  -h, --help           show this help message and exit
  --duration DURATION
  --no-audio
```

## `doctor`

```text
usage: python -m studio doctor [-h] [--online]

options:
  -h, --help  show this help message and exit
  --online
```

## `serve`

```text
usage: python -m studio serve [-h] [--port PORT] [--host HOST]

options:
  -h, --help   show this help message and exit
  --port PORT
  --host HOST
```

## `check-skills`

```text
usage: python -m studio check-skills [-h]

options:
  -h, --help  show this help message and exit
```
