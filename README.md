# 🚀 Mis Proyectos con IA

Espacio de trabajo para crear **páginas web, aplicaciones, imágenes y videos** sin necesidad de saber programar.
Cada carpeta es un proyecto independiente y ya funciona: puedes abrirlo, probarlo y pedirme cambios.

| Carpeta | Qué es | Cómo verlo |
|---|---|---|
| `01-pagina-web/` | Página web con estudio creativo (crea imágenes y videos) y formulario | Doble clic en `index.html` |
| `02-app-tareas/` | App de lista de tareas que recuerda tus datos | Doble clic en `index.html` |
| `03-imagenes/` | Generador de imágenes (arte abstracto y con IA) | `python3 generar_arte.py` |
| `04-videos/` | Generador de videos animados MP4 | `python3 crear_video.py` |

---

## 🧭 Cómo trabajamos juntos (sin programar)

1. **Me dices la idea** con tus palabras: *"quiero una web para mi panadería con fotos y horario"*.
2. **Yo escribo y organizo el código** en una carpeta nueva.
3. **Lo pruebo** (abro la web en un navegador automático, ejecuto los scripts, reviso errores).
4. **Te muestro el resultado** (capturas, imágenes, videos) y lo guardo en GitHub.
5. **Pides cambios** (*"pon el botón en verde"*, *"añade una sección de precios"*) y repetimos.

> 💡 Cuanto más concreto seas (colores, textos, para quién es), mejor queda a la primera.

---

## 🌐 1. Página web — `01-pagina-web/`

- `index.html` → el **contenido** (textos, secciones).
- `estilos.css` → el **aspecto** (colores, tamaños). Los colores están arriba del todo, en `:root`.
- `script.js` → el **comportamiento** (qué pasa al pulsar "Enviar").
- `estudio.js` → el **Estudio creativo**: botones *Crear imagen* (PNG con estilo y texto) y *Crear video* (MP4/WebM animado de 3–8 s). Todo se crea en el navegador, sin claves ni instalar nada.

**Para verla:** abre `index.html` con tu navegador.
**Para publicarla gratis en internet:** se puede activar *GitHub Pages* en este repositorio, o arrastrar la carpeta a [Netlify Drop](https://app.netlify.com/drop).

## ✅ 2. App de tareas — `02-app-tareas/`

App completa en un solo archivo: añadir, marcar como hecha, borrar y filtrar tareas.
Las tareas se guardan en tu navegador, así que siguen ahí al cerrar y volver a abrir.

## 🎨 3. Imágenes — `03-imagenes/`

**Sin claves ni internet** (gratis):
```bash
pip install pillow
python3 generar_arte.py --cantidad 5
```
Las imágenes aparecen en `03-imagenes/salida/`.

**Con IA a partir de un texto** (necesita una clave de pago de OpenAI):
```bash
pip install openai
export OPENAI_API_KEY="tu-clave"
python3 generar_con_ia.py "un faro al atardecer estilo acuarela"
```
> 🔒 Nunca pegues tu clave dentro del código ni la subas a GitHub.

## 🎬 4. Videos y animaciones — `04-videos/`

Necesita [ffmpeg](https://ffmpeg.org/download.html) y Pillow.
```bash
python3 crear_video.py --texto "¡Feliz cumpleaños!" --segundos 6
```
Crea `04-videos/salida/animacion.mp4` (1080×1080, ideal para Instagram) y una `vista_previa.png`.

---

## 🧰 Herramientas de IA recomendadas para ir más allá

| Para… | Opciones |
|---|---|
| Imágenes a partir de texto | OpenAI Images, Stability AI, Ideogram, Midjourney |
| Video a partir de texto o imagen | Runway, Luma, Kling, Pika |
| Voz y narración | ElevenLabs, OpenAI TTS |
| Textos inteligentes dentro de tus apps | API de Claude (Anthropic) |

Muchas tienen API: dime cuál quieres usar y la conecto a tus proyectos.

## 📖 Mini-glosario

- **Código**: las instrucciones que le dicen al ordenador qué hacer.
- **HTML / CSS / JavaScript**: contenido / diseño / comportamiento de una web.
- **Python**: lenguaje que usamos para generar imágenes y videos.
- **Terminal**: ventana donde se escriben comandos como `python3 crear_video.py`.
- **API y clave (API key)**: la "puerta" y la "llave" para usar un servicio de IA desde el código.
- **GitHub / commit / push**: dónde se guarda tu proyecto / guardar una versión / subirla a internet.
