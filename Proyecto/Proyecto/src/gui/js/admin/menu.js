document.addEventListener("DOMContentLoaded", function() {
  // Crear conexión con PyQt
  new QWebChannel(qt.webChannelTransport, function(channel) {
    window.bridge = channel.objects.bridge;
    console.log("✅ Conectado al bridge de PyQt");

    // 🟢 Agregar evento al botón de cerrar sesión
    const logoutBtn = document.getElementById("btn-cerrar-sesion");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        console.log("🚪 Cerrando sesión...");
        window.bridge.cerrarSesion(); // Llama al método PyQt
      });
    } else {
      console.warn("⚠️ No se encontró el botón #btn-cerrar-sesion");
    }

    // 🔄 Actualizar contador de mensajes al cargar
    actualizarContadorMensajes();

    // ⏱️ Refrescar el contador cada 5 segundos
    setInterval(actualizarContadorMensajes, 5000);
  });

  // Marcar botón activo inicial
  marcarActivo(window.currentPage || "inicio");
});

// --- Función para abrir páginas del menú
function abrir(nombre, elemento) {
  console.log("📂 Solicitando carga de página:", nombre);

  if (window.bridge) {
    window.bridge.cargar_pagina(nombre);
  } else {
    console.warn("⚠️ Bridge aún no conectado, intenta de nuevo");
    return;
  }

  // Quitar 'active' de todos los botones
  const items = document.querySelectorAll(".menu-item");
  items.forEach(item => item.classList.remove("active"));

  // Agregar 'active' al botón clickeado
  if (elemento) {
    elemento.classList.add("active");
  }

  // Guardar página actual
  window.currentPage = nombre;
}

// --- Marcar botón activo por nombre (al cargar desde Python)
function marcarActivo(nombre) {
  const items = document.querySelectorAll(".menu-item");
  items.forEach(item => {
    const onclick = item.getAttribute("onclick");
    if (onclick && onclick.includes(`'${nombre}'`)) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });
}

// --- 🟢 NUEVO: contador de mensajes no leídos
async function actualizarContadorMensajes() {
  const contadorEl = document.getElementById("contador-mensajes");
  if (!contadorEl || !window.bridge) return;

  try {
    const noLeidos = await window.bridge.obtenerMensajesNoLeidos(); // Slot PyQt
    if (noLeidos > 0) {
      contadorEl.textContent = `(${noLeidos})`;
      contadorEl.style.display = "inline";
    } else {
      contadorEl.textContent = "";
      contadorEl.style.display = "none";
    }
  } catch (err) {
    console.error("❌ Error al actualizar contador de mensajes:", err);
  }
}
