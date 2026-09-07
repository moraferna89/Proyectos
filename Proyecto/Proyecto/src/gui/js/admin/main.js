document.addEventListener("DOMContentLoaded", function() {
  new QWebChannel(qt.webChannelTransport, function(channel) {
    window.bridge = channel.objects.bridge;

    // Botón Agregar Ejecutivo
    document.getElementById("btn-agregar-ejecutivo")?.addEventListener("click", function() {
      bridge.abrir_agregar_ejecutivo();
    });

    // Botón Editar Ejecutivo
    document.getElementById("btn-editar-ejecutivo")?.addEventListener("click", function() {
      bridge.abrir_editar_ejecutivo();
    });

    // Botón Eliminar Ejecutivo
    document.getElementById("btn-eliminar-ejecutivo").addEventListener("click", function() {
      bridge.abrir_eliminar_ejecutivo();
    });

  });
});
function buscarEjecutivo() {
  const idLlamada = document.getElementById("id_ejecutivo")?.value || "";

  if (idLlamada.trim() === "") {
    alert("Por favor, ingresa un ID de llamada.");
    return;
  }

  if (window.bridge && window.bridge.buscarEjecutivoPorId) {
    bridge.buscarEjecutivoPorId(idLlamada);
  } else {
    console.error("El bridge no está disponible o buscarEjecutivoPorId no está definido");
  }
}
