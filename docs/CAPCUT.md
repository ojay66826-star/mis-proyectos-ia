# Editar en CapCut

CapCut no tiene API pública ni conector para Claude, así que el estudio se conecta con él mediante un **paquete de
capas editables** que se importa en CapCut (escritorio o móvil).

```bash
python -m studio export projects/<carpeta>/final.mp4 --preset capcut   # o la carpeta del proyecto
```

Genera `projects/<carpeta>/capcut/` y `projects/<carpeta>/<carpeta>_capcut.zip`:

| Archivo | Para qué |
|---|---|
| `video/video_limpio.mp4` | el video re-renderizado **sin** título, rótulos ni subtítulos y sin audio (misma resolución que `final.mp4`) |
| `video/video_con_texto.mp4` | el `final.mp4` original, como referencia |
| `audio/voces.wav`, `efectos.wav`, `musica.wav` | pistas separadas, todas desde 0:00; juntas suman exactamente `mezcla.wav` |
| `audio/voces_sueltas/` | cada frase; el nombre empieza por el segundo donde va |
| `subtitulos.srt` | Texto → Subtítulos → Importar archivo local |
| `personajes/*.png` | cada personaje en 8 expresiones y 4 poses con fondo transparente + hoja de personaje |
| `LEEME.txt` | pasos para montarlo en CapCut |

También está en la interfaz web (botón **Paquete CapCut** junto a las exportaciones).

**Llevarlo al móvil:** si Claude tiene el conector de Google Drive, puede subir el zip (o el `final.mp4` exportado con
`--preset tiktok`, etc.) a tu Drive; en el móvil lo abres desde Drive y lo importas en CapCut.

Limitaciones: los proyectos 3D no se re-renderizan sin texto (el video limpio conserva los textos del render). Si
`espeak-ng` no está instalado y no hay clave de voz en la nube, las voces salen en silencio (lo avisa `doctor`).
