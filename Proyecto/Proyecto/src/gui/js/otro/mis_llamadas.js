// archivo: src/html/js/llamadas.js
new QWebChannel(qt.webChannelTransport, function (channel) {
    window.bridge = channel.objects.bridge;
});
// Muestra mensaje inicial
document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.querySelector("#tabla-todasllamadasxid tbody");
  if (tbody) {
    tbody.innerHTML = "<tr><td colspan='100%'>Cargando llamadas...</td></tr>";
  }
});

// 🔹 Función que es llamada por los botones inyectados desde Python
function verDetalles(id) {
    if (window.bridge && window.bridge.verDetallesLlamadaXejecutivo) {
    bridge.verDetallesLlamadaXejecutivo(id.toString());
    } else {
    console.error("El bridge no está disponible o verDetallesLlamadaXejecutivo no está definido");
    }
}

// 🔹 (Opcional) Función que podrías usar si luego agregas recarga
function recargarTabla() {
  if (window.bridge && window.bridge.cargarLlamadas) {
    window.bridge.cargarLlamadas(); // Esto podría llamar a tu método Python
  } else {
    console.warn("Bridge no disponible, no se puede recargar");
  }
}

window.addEventListener("load", () => {
  console.log("✅ Página lista (evento load)");
});
