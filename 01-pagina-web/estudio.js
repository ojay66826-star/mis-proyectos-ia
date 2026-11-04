// ============================================================
//  Estudio creativo: crea imágenes y videos en el navegador.
//  No necesita internet, claves ni programas extra.
// ============================================================

const PALETAS = {
  atardecer: ["#ff7a59", "#ffb347", "#ff5e78", "#6a4c93", "#1d1a39"],
  oceano: ["#0b3954", "#087e8b", "#bfd7ea", "#ff5a5f", "#c81d25"],
  bosque: ["#2d6a4f", "#40916c", "#95d5b2", "#d8f3dc", "#081c15"],
};

// ---------- Descargas ----------
// Dentro de claude.ai se usa el permiso de descargas de la página;
// en cualquier otro sitio (tu ordenador, GitHub Pages) se descarga normal.
const descargasClaude =
  window.claude && typeof window.claude.use === "function"
    ? window.claude.use("downloads").catch(() => null)
    : Promise.resolve(null);

async function descargar(blob, nombre, estado) {
  const servicio = await descargasClaude;
  if (servicio) {
    try {
      await servicio.save({ filename: nombre, data: blob });
      avisar(estado, "Archivo guardado ✔");
    } catch (e) {
      if (e && e.code === "declined") avisar(estado, "Descarga cancelada.");
      else if (e && e.code === "rate_limited") avisar(estado, "Espera un momento y vuelve a intentarlo.", true);
      else avisar(estado, "Aquí no se puede descargar. Prueba a abrir la página desde tu ordenador.", true);
    }
    return;
  }
  const enlace = document.createElement("a");
  enlace.href = URL.createObjectURL(blob);
  enlace.download = nombre;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
  setTimeout(() => URL.revokeObjectURL(enlace.href), 10000);
  avisar(estado, "Descarga iniciada ✔");
}

function avisar(elemento, texto, esError = false) {
  elemento.textContent = texto;
  elemento.classList.toggle("error", esError);
}

// Números aleatorios repetibles: misma semilla = misma imagen
function aleatorio(semilla) {
  return () => {
    semilla = (semilla * 1664525 + 1013904223) % 4294967296;
    return semilla / 4294967296;
  };
}

function textoCentrado(ctx, texto, ancho, alto, tamano, opacidad = 1) {
  if (!texto) return;
  ctx.save();
  ctx.globalAlpha = opacidad;
  ctx.font = `700 ${tamano}px system-ui, -apple-system, "Segoe UI", sans-serif`;
  // Si el texto es muy largo, se encoge para que quepa
  while (ctx.measureText(texto).width > ancho * 0.88 && tamano > 16) {
    tamano -= 4;
    ctx.font = `700 ${tamano}px system-ui, -apple-system, "Segoe UI", sans-serif`;
  }
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.shadowColor = "rgba(0,0,0,.45)";
  ctx.shadowBlur = tamano / 3;
  ctx.fillStyle = "#fff";
  ctx.fillText(texto, ancho / 2, alto / 2);
  ctx.restore();
}

// ============================================================
//  1. CREAR IMAGEN
// ============================================================
const lienzoImg = document.getElementById("lienzo-imagen");
const ctxImg = lienzoImg.getContext("2d");
const imgEstado = document.getElementById("img-estado");
let semillaActual = Math.floor(Math.random() * 1e9);

function dibujarImagen() {
  const { width: W, height: H } = lienzoImg;
  const colores = PALETAS[document.getElementById("img-paleta").value];
  const azar = aleatorio(semillaActual);
  const entre = (a, b) => a + azar() * (b - a);

  // Fondo
  ctxImg.fillStyle = colores[colores.length - 1];
  ctxImg.fillRect(0, 0, W, H);

  // Manchas grandes y difuminadas
  ctxImg.save();
  ctxImg.filter = "blur(60px)";
  ctxImg.globalAlpha = 0.6;
  for (let i = 0; i < 12; i++) {
    ctxImg.fillStyle = colores[Math.floor(azar() * (colores.length - 1))];
    ctxImg.beginPath();
    ctxImg.arc(entre(0, W), entre(0, H), entre(150, 450), 0, Math.PI * 2);
    ctxImg.fill();
  }
  ctxImg.restore();

  // Formas nítidas encima
  ctxImg.lineWidth = 5;
  ctxImg.lineCap = "round";
  for (let i = 0; i < 25; i++) {
    const x = entre(0, W), y = entre(0, H), t = entre(10, 90);
    ctxImg.strokeStyle = colores[Math.floor(azar() * (colores.length - 1))];
    ctxImg.beginPath();
    if (azar() < 0.5) ctxImg.arc(x, y, t / 2, 0, Math.PI * 2);
    else { ctxImg.moveTo(x, y); ctxImg.lineTo(x + t * 2, y - t); }
    ctxImg.stroke();
  }

  textoCentrado(ctxImg, document.getElementById("img-texto").value.trim(), W, H, 110);
}

document.getElementById("img-generar").onclick = () => {
  semillaActual = Math.floor(Math.random() * 1e9);
  dibujarImagen();
  avisar(imgEstado, "");
};
document.getElementById("img-paleta").onchange = dibujarImagen;
document.getElementById("img-texto").oninput = dibujarImagen;
document.getElementById("img-descargar").onclick = () => {
  lienzoImg.toBlob((blob) => descargar(blob, `imagen-${semillaActual}.png`, imgEstado), "image/png");
};
dibujarImagen();

// ============================================================
//  2. CREAR VIDEO
// ============================================================
const lienzoVid = document.getElementById("lienzo-video");
const ctxVid = lienzoVid.getContext("2d");
const videoResultado = document.getElementById("video-resultado");
const vidEstado = document.getElementById("vid-estado");
const botonCrear = document.getElementById("vid-crear");
const botonDescargarVid = document.getElementById("vid-descargar");
const COLORES_VIDEO = ["#ff7a59", "#ffb347", "#6a4c93", "#087e8b", "#95d5b2"];
let videoListo = null; // { blob, extension }

// Dibuja el fotograma que corresponde al avance t (de 0 a 1)
function dibujarFotograma(t, texto) {
  const { width: W, height: H } = lienzoVid;
  ctxVid.fillStyle = "#0f1020";
  ctxVid.fillRect(0, 0, W, H);
  COLORES_VIDEO.forEach((color, i) => {
    const angulo = 2 * Math.PI * (t + i / COLORES_VIDEO.length);
    const orbita = W * 0.3 + W * 0.04 * Math.sin(4 * Math.PI * t + i);
    const r = W * 0.055 + W * 0.02 * Math.sin(6 * Math.PI * t + i);
    ctxVid.fillStyle = color;
    ctxVid.beginPath();
    ctxVid.arc(W / 2 + orbita * Math.cos(angulo), H / 2 + orbita * Math.sin(angulo), r, 0, Math.PI * 2);
    ctxVid.fill();
  });
  textoCentrado(ctxVid, texto, W, H, 64, Math.min(1, t * 3));
}

// Vista previa animada mientras no se graba
let grabando = false;
const inicioPrevia = performance.now();
function previa(ahora) {
  if (!grabando && videoResultado.hidden) {
    const t = ((ahora - inicioPrevia) / 5000) % 1;
    dibujarFotograma(t, document.getElementById("vid-texto").value.trim());
  }
  requestAnimationFrame(previa);
}
requestAnimationFrame(previa);

function formatoVideo() {
  if (typeof MediaRecorder === "undefined") return null;
  const opciones = [
    ["video/mp4;codecs=avc1", "mp4"],
    ["video/mp4", "mp4"],
    ["video/webm;codecs=vp9", "webm"],
    ["video/webm", "webm"],
  ];
  for (const [tipo, extension] of opciones) {
    if (MediaRecorder.isTypeSupported(tipo)) return { tipo, extension };
  }
  return null;
}

botonCrear.onclick = () => {
  const formato = formatoVideo();
  if (!formato || !lienzoVid.captureStream) {
    avisar(vidEstado, "Tu navegador no puede grabar video. Prueba con Chrome, Edge o Firefox.", true);
    return;
  }
  const segundos = Number(document.getElementById("vid-segundos").value);
  const texto = document.getElementById("vid-texto").value.trim();

  grabando = true;
  videoListo = null;
  botonCrear.disabled = true;
  botonDescargarVid.disabled = true;
  videoResultado.hidden = true;
  lienzoVid.hidden = false;

  const grabadora = new MediaRecorder(lienzoVid.captureStream(30), {
    mimeType: formato.tipo,
    videoBitsPerSecond: 5_000_000,
  });
  const trozos = [];
  grabadora.ondataavailable = (e) => e.data.size && trozos.push(e.data);
  grabadora.onstop = () => {
    const blob = new Blob(trozos, { type: formato.tipo.split(";")[0] });
    videoListo = { blob, extension: formato.extension };
    videoResultado.src = URL.createObjectURL(blob);
    videoResultado.hidden = false;
    lienzoVid.hidden = true;
    videoResultado.play().catch(() => {});
    grabando = false;
    botonCrear.disabled = false;
    botonCrear.textContent = "Crear otro";
    botonDescargarVid.disabled = false;
    avisar(vidEstado, `¡Video listo! (${formato.extension.toUpperCase()}, ${(blob.size / 1e6).toFixed(1)} MB)`);
  };

  const inicio = performance.now();
  grabadora.start();
  (function grabarFotograma() {
    const t = (performance.now() - inicio) / (segundos * 1000);
    if (t >= 1) { grabadora.stop(); return; }
    dibujarFotograma(t, texto);
    avisar(vidEstado, `Grabando… ${Math.round(t * 100)}%`);
    requestAnimationFrame(grabarFotograma);
  })();
};

botonDescargarVid.onclick = () => {
  if (videoListo) descargar(videoListo.blob, `video.${videoListo.extension}`, vidEstado);
};
