window.addEventListener("DOMContentLoaded", () => {
  const lista = document.getElementById("lista-usuarios");
  const chatBox = document.getElementById("chat");
  const chatInput = document.getElementById("chat-input");
  const nombreChat = document.getElementById("nombre-chat");
  const input = document.getElementById("msg-input");
  const sendBtn = document.getElementById("send-btn");

  let usuarioSeleccionado = null;

  // Inicializar QWebChannel
  new QWebChannel(qt.webChannelTransport, function(channel) {
      window.bridge = channel.objects.bridge;
      console.log("✅ Bridge inicializado:", window.bridge);
      cargarUsuarios();
  });

  // Cargar lista de usuarios
    async function cargarUsuarios() {
    try {
        const usuarios = await window.bridge.obtenerUsuarios();
        const usuariosConNoLeidos = await window.bridge.obtenerUsuariosConMensajesNoLeidos();
        console.log("📋 Usuarios:", usuarios);
        console.log("🔔 Con mensajes no leídos:", usuariosConNoLeidos);

        lista.innerHTML = "";
        usuarios.forEach(u => {
            const div = document.createElement("div");
            div.className = "usuario-item";
            div.textContent = u.nombre;
            div.dataset.id = u.usuario;

            // 🟡 Marcar si tiene mensajes no leídos
            if (usuariosConNoLeidos.includes(u.usuario)) {
                div.classList.add("no-leido");
            }

            div.addEventListener("click", () => abrirChat(u));
            lista.appendChild(div);
        });
    } catch (err) {
        console.error("❌ Error al cargar usuarios:", err);
    }
    }


  // Abrir chat
  async function abrirChat(usuario) {
      usuarioSeleccionado = usuario;
      console.log("🟢 Usuario seleccionado:", usuarioSeleccionado);

      nombreChat.textContent = "Chat con " + usuario.nombre;
      chatInput.style.display = "flex";
      await cargarConversacion();
  }

  // Cargar conversación
  async function cargarConversacion() {
      if (!usuarioSeleccionado) return;
      console.log("📨 Cargando conversación con ID:", usuarioSeleccionado.usuario);

      try {
          const mensajes = await window.bridge.obtenerConversacion(usuarioSeleccionado.usuario);
          console.log("💬 Mensajes recibidos:", mensajes);

          chatBox.innerHTML = "";
          const miId = await window.bridge.obtenerIdUsuario();
          console.log("👤 Mi ID:", miId);

          mensajes.forEach(m => {
              const div = document.createElement("div");
              div.className = "msg " + (m.remitente_id === miId ? "mine" : "their");
              div.textContent = m.mensaje;
              chatBox.appendChild(div);
          });

            chatBox.scrollTop = chatBox.scrollHeight;
            // ✅ Marcar los mensajes de este chat como leídos
            await window.bridge.marcarLeidosDe(usuarioSeleccionado.usuario);

      } catch (err) {
          console.error("❌ Error al cargar conversación:", err);
      }
  }

  // Enviar mensaje
  sendBtn.addEventListener("click", async () => {
      const texto = input.value.trim();
      if (!texto || !usuarioSeleccionado) return;

      console.log("✉️ Enviando mensaje a:", usuarioSeleccionado.usuario, "Mensaje:", texto);

      try {
          await window.bridge.enviarMensaje(usuarioSeleccionado.usuario, texto);
          input.value = "";
          await cargarConversacion();
      } catch (err) {
          console.error("❌ Error al enviar mensaje:", err);
      }
  });
});
window.addEventListener("DOMContentLoaded", () => {
  const lista = document.getElementById("lista-usuarios");
  const chatBox = document.getElementById("chat");
  const chatInput = document.getElementById("chat-input");
  const nombreChat = document.getElementById("nombre-chat");
  const input = document.getElementById("msg-input");
  const sendBtn = document.getElementById("send-btn");

  let usuarioSeleccionado = null;

  // Inicializar QWebChannel
  new QWebChannel(qt.webChannelTransport, function(channel) {
      window.bridge = channel.objects.bridge;
      console.log("✅ Bridge inicializado:", window.bridge);
      cargarUsuarios();
  });

  // Cargar lista de usuarios
    async function cargarUsuarios() {
    try {
        const usuarios = await window.bridge.obtenerUsuarios();
        const usuariosConNoLeidos = await window.bridge.obtenerUsuariosConMensajesNoLeidos();
        console.log("📋 Usuarios:", usuarios);
        console.log("🔔 Con mensajes no leídos:", usuariosConNoLeidos);

        lista.innerHTML = "";
        usuarios.forEach(u => {
            const div = document.createElement("div");
            div.className = "usuario-item";
            div.textContent = u.nombre;
            div.dataset.id = u.usuario;

            // 🟡 Marcar si tiene mensajes no leídos
            if (usuariosConNoLeidos.includes(u.usuario)) {
                div.classList.add("no-leido");
            }

            div.addEventListener("click", () => abrirChat(u));
            lista.appendChild(div);
        });
    } catch (err) {
        console.error("❌ Error al cargar usuarios:", err);
    }
    }


  // Abrir chat
  async function abrirChat(usuario) {
      usuarioSeleccionado = usuario;
      console.log("🟢 Usuario seleccionado:", usuarioSeleccionado);

      nombreChat.textContent = "Chat con " + usuario.nombre;
      chatInput.style.display = "flex";
      await cargarConversacion();
  }

  // Cargar conversación
  async function cargarConversacion() {
      if (!usuarioSeleccionado) return;
      console.log("📨 Cargando conversación con ID:", usuarioSeleccionado.usuario);

      try {
          const mensajes = await window.bridge.obtenerConversacion(usuarioSeleccionado.usuario);
          console.log("💬 Mensajes recibidos:", mensajes);

          chatBox.innerHTML = "";
          const miId = await window.bridge.obtenerIdUsuario();
          console.log("👤 Mi ID:", miId);

          mensajes.forEach(m => {
              const div = document.createElement("div");
              div.className = "msg " + (m.remitente_id === miId ? "mine" : "their");
              div.textContent = m.mensaje;
              chatBox.appendChild(div);
          });

            chatBox.scrollTop = chatBox.scrollHeight;
            // ✅ Marcar los mensajes de este chat como leídos
            await window.bridge.marcarLeidosDe(usuarioSeleccionado.usuario);

      } catch (err) {
          console.error("❌ Error al cargar conversación:", err);
      }
  }

  // Enviar mensaje
  sendBtn.addEventListener("click", async () => {
      const texto = input.value.trim();
      if (!texto || !usuarioSeleccionado) return;

      console.log("✉️ Enviando mensaje a:", usuarioSeleccionado.usuario, "Mensaje:", texto);

      try {
          await window.bridge.enviarMensaje(usuarioSeleccionado.usuario, texto);
          input.value = "";
          await cargarConversacion();
      } catch (err) {
          console.error("❌ Error al enviar mensaje:", err);
      }
  });
});
