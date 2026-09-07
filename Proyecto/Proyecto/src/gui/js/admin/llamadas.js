

    // 🔹 Espera a que el canal esté listo antes de usar bridge
new QWebChannel(qt.webChannelTransport, function (channel) {
    window.bridge = channel.objects.bridge;
});

function buscarLlamada() {
    const idLlamada = document.getElementById("id_llamada")?.value || "";

    if (idLlamada.trim() === "") {
    alert("Por favor, ingresa un ID de llamada.");
    return;
    }

    if (window.bridge && window.bridge.buscarLlamadaPorId) {
    bridge.buscarLlamadaPorId(idLlamada);
    } else {
    console.error("El bridge no está disponible o buscarLlamadaPorId no está definido");
    }
}

// 🔹 Nueva función para abrir detalle
function verDetalles(id) {
    if (window.bridge && window.bridge.verDetallesLlamada) {
    bridge.verDetallesLlamada(id.toString());
    } else {
    console.error("El bridge no está disponible o verDetallesLlamada no está definido");
    }
}

function subirAudio() {
    const idLlamada = document.getElementById("id_llamada_audio").value;
    if (!idLlamada) {
        alert("Ingresa un ID de llamada");
        return;
    }
    if (window.bridge && window.bridge.seleccionarAudio) {
        window.bridge.seleccionarAudio(parseInt(idLlamada));
    } else {
        console.error("Bridge no disponible o seleccionarAudio no definido");
    }
}
