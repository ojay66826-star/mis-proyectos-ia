// Pone el año actual en el pie de página
document.getElementById("anio").textContent = new Date().getFullYear();

// Formulario de contacto: por ahora solo muestra un mensaje de agradecimiento.
// (Para recibir los mensajes de verdad se puede conectar un servicio como Formspree.)
document.getElementById("formulario").addEventListener("submit", (evento) => {
  evento.preventDefault();
  const nombre = evento.target.nombre.value.trim();
  document.getElementById("aviso").textContent = `¡Gracias, ${nombre}! Te responderemos pronto.`;
  evento.target.reset();
});
