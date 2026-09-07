// archivo: src/html/js/llamadas.js

// 🔸 Muestra un mensaje inicial mientras carga la tabla
document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.querySelector("#tabla-llamadasxid tbody");
  if (tbody) {
    tbody.innerHTML = "<tr><td colspan='100%'>Cargando llamadas...</td></tr>";
  }
});

// 🔹 Función llamada desde botones inyectados por Python
function verDetalles(idLlamada) {
  alert("Ver detalles de la llamada: " + idLlamada);
  // Si usas QWebChannel:
  // window.bridge.verDetallesLlamada(idLlamada);
}

// 🔹 Función auxiliar para recargar la tabla
function recargarTabla() {
  if (window.bridge && window.bridge.cargarLlamadas) {
    window.bridge.cargarLlamadas();
  } else {
    console.warn("⚠️ Bridge no disponible, no se puede recargar la tabla de llamadas.");
  }
}

// 🔹 Actualiza el total de llamadas
function actualizarLlamadas() {
  if (window.bridge && window.bridge.obtener_cantidad_llamadasxid) {
    console.log("📞 Solicitando total de llamadas al bridge...");
    window.bridge.obtener_cantidad_llamadasxid((total) => {
      console.log("🔢 Total recibido desde Python:", total);
      const contador = document.getElementById("total-llamadas");
      if (contador) contador.textContent = total;
    });
  } else {
    console.warn("⚠️ Bridge no disponible todavía para obtener el total de llamadas.");
  }
}

// 🔹 Actualiza el promedio de llamadas
function actualizarPromedio() {
  if (window.bridge && window.bridge.obtener_promedio_llamadas) {
    console.log("📊 Solicitando promedio de llamadas al bridge...");
    window.bridge.obtener_promedio_llamadas((promedio) => {
      console.log("⭐ Promedio recibido desde Python:", promedio);
      const contador = document.getElementById("puntaje-valoracion");
      if (contador) contador.textContent = promedio;
    });
  } else {
    console.warn("⚠️ Bridge no disponible todavía para obtener el promedio de llamadas.");
  }
}

// 🔸 Inicializa el canal QWebChannel correctamente
document.addEventListener("DOMContentLoaded", function () {
  // Espera a que PyQt cree el canal
  if (typeof qt !== "undefined" && qt.webChannelTransport) {
    new QWebChannel(qt.webChannelTransport, function (channel) {
      window.bridge = channel.objects.bridge; // Guarda referencia global
      console.log("🟢 Conectado al bridge de PyQt");

      // ✅ Llama a ambas funciones solo cuando el bridge esté listo
      actualizarLlamadas();
      actualizarPromedio();
    });
  } else {
    console.error("❌ QWebChannel no disponible. Asegúrate de crear el canal en PyQt.");
  }
});
