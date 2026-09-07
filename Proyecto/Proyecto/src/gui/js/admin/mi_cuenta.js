document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ DOM cargado");

    if (typeof qt === "undefined") {
        console.log("❌ qt.webChannelTransport no disponible");
        return;
    }

    new QWebChannel(qt.webChannelTransport, function(channel) {
        console.log("✅ Conectado al bridge");
        window.bridge = channel.objects.bridge;

        // Llamada segura a PyQt
        bridge.obtener_datos_usuario().then(function(datos) {
            console.log("Datos recibidos del bridge:", datos);
            if (!datos) return;

            const nombre = document.getElementById("nombre");
            const apellido = document.getElementById("apellido");
            const cargo = document.getElementById("cargo");
            const rut = document.getElementById("rut");

            if (nombre) nombre.textContent = datos.nombre;
            if (apellido) apellido.textContent = datos.apellido;
            if (cargo) cargo.textContent = datos.cargo;
            if (rut) rut.textContent = datos.rut;
        }).catch(function(err) {
            console.error("Error al obtener datos del bridge:", err);
        });
    });
});
