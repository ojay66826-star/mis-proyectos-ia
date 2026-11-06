---
name: scenario-3d
description: Use when generating or handling 3D assets through the Scenario MCP server, including text-to-3D or image-to-3D meshes, GPT-6 Astra 3D or Claude Opus 5.5 3D, GLB, FBX, OBJ, STL, or VOX files, PBR-textured or game-ready models, voxel models, multi-view reconstruction, editing a mesh by prompt, retexture, remesh, UV unwrap, auto-rigging a biped or quadruped, or retargeting an animation, previewing a mesh in the 3D viewer, or downloading a model for import into Unity, Unreal, Godot, or Blender.
---

# Recursos 3D con Scenario (MCP)

Skill del estudio para crear y manejar **modelos 3D descargables** (no video) con el servidor MCP de Scenario:
texto→3D, imagen→3D, reconstrucción multivista, edición de malla por prompt, retexturizado, remallado, desplegado UV,
auto-rig de bípedos/cuadrúpedos, retargeting de animaciones, vista previa en el visor 3D y descarga para Unity,
Unreal, Godot o Blender (GLB, FBX, OBJ, STL, VOX).

## Reglas del usuario (las mismas de `CLAUDE.md`)

- Responder **siempre en español**.
- **Antes de gastar créditos**: estimar el coste si la herramienta lo permite, decir la cifra y esperar su «sí».
- Personajes **originales** (nunca de terceros).

## 1. Comprobar que Scenario está conectado

1. Buscar las herramientas: `ToolSearch` con `scenario` (y `+scenario 3d`). Si aparecen herramientas `mcp__…scenario…`,
   cargarlas y leer sus descripciones: **usar sus nombres y parámetros reales**, no inventarlos.
2. Si no aparecen: `SearchMcpRegistry` con `["scenario", "3d"]`. Si el conector no está conectado, decir al usuario en
   una frase que lo conecte en claude.ai → **Configuración → Conectores** (o que añada el servidor MCP de Scenario en
   la configuración) y ofrecer la alternativa local (sección 6). No fingir resultados.

## 2. Elegir la vía

| Necesidad | Vía en Scenario |
|---|---|
| Objeto/personaje nuevo desde una idea | texto → 3D |
| Llevar a 3D un personaje ya diseñado (p. ej. Miso y Pipa) | imagen → 3D con la hoja de `biblioteca/personajes/*/hoja_personajes.jpg`, mejor una vista frontal de cuerpo entero por personaje sobre fondo liso; si hay varias vistas, reconstrucción multivista |
| Cambiar forma o detalle de un modelo | edición de malla por prompt |
| Cambiar materiales/colores | retexturizar (PBR) |
| Modelo pesado o malla sucia para juego | remallado (game-ready, menos polígonos) + desplegado UV |
| Que se pueda animar | auto-rig (bípedo para Miso; cuadrúpedo o bípedo para Pipa según la pose) → retargeting de la animación |
| Estilo pixel/bloques | modelo voxel (VOX) |
| Impresión 3D | exportar STL |

Modelos que pueden aparecer en Scenario: GPT-6 Astra 3D, Claude Opus 5.5 3D (u otros que liste la herramienta). Elegir
según lo que el usuario pida (fidelidad a la imagen, estilo, velocidad) y lo que diga la guía de cada modelo.

## 3. Prompts para texto→3D

Describir como a un modelador: **objeto o personaje + proporciones + materiales + estilo + uso**.
Ejemplo: *"Stylized 3D character, young orange tabby cat standing upright, large head, short body, teal neckerchief,
soft fur look, PBR materials, game-ready, A-pose with arms slightly away from the body, single mesh, no base."*

- Para personajes que se van a riggear: **A-pose o T-pose**, brazos separados del cuerpo y piernas separadas.
- Para juegos: pedir *game-ready*, recuento de polígonos moderado y texturas PBR.
- Reutilizar las descripciones exactas de `biblioteca/personajes/*/ficha.json` para que el modelo 3D se parezca al
  personaje de los cortos.

## 4. Revisar antes de entregar

- **Vista previa en el visor 3D** de Scenario y comprobar: silueta, proporciones, que no falten partes (cola, orejas,
  pañuelo), texturas sin manchas, malla cerrada.
- Tras el rig: probar al menos una animación (caminar o saludar) con retargeting y mirar que no se deforme.
- Mostrar al usuario una captura o la vista previa antes de descargar formatos adicionales.

## 5. Descargar e importar

Guardar en `projects/modelos-3d/<nombre>/` (no se versiona; los modelos pesan). Formato según destino:

| Destino | Formato | Nota |
|---|---|---|
| Blender | GLB (o FBX si lleva rig + animaciones) | Archivo → Importar → glTF/FBX |
| Unity | FBX (rig + animaciones) o GLB con un importador glTF | escala 1, revisar el tipo de rig (Humanoid para bípedos) |
| Unreal | FBX | importar como Skeletal Mesh si está riggeado |
| Godot | GLB | Godot importa glTF de forma nativa |
| Impresión 3D | STL | sin texturas |
| Voxel | VOX | MagicaVoxel |

Si la descarga llega como URL, puede que el host necesite estar permitido en la red del entorno: si la descarga falla
con una negativa del proxy, pedir al usuario que permita ese host (herramientas de entorno) y reintentar.
Entregar el archivo con `SendUserFile` y decir el coste real gastado.

## 6. Alternativa si Scenario no está disponible

- `python -m studio character3d <especie> --action dance`: personaje 3D procedural con Blender (GLB + video), gratis
  pero con formas simples; requiere Blender instalado.
- Para **video** con calidad de película (no modelos descargables) usar la Skill `corto-3d-ia`.

## Relacionadas

`corto-3d-ia`, `3d-modeling`, `3d-rigging`, `3d-character-animation`, `blender-animation`, `threejs-animation`,
`sprite-animation`.
