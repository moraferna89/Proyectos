document.addEventListener("DOMContentLoaded", function() {
    new QWebChannel(qt.webChannelTransport, function(channel) {
        window.bridge = channel.objects.bridge;
        bridge.actualizar_ranking_js();  // ✅ llama al método correcto
        actualizarLlamadas();
    });
});

function actualizarLlamadas() {
    bridge.obtener_cantidad_llamadas().then(total => {
        // Actualiza el contenido del span
        document.getElementById("total-llamadas").textContent = total;
    });
}
