document.addEventListener("DOMContentLoaded", function() {
  new QWebChannel(qt.webChannelTransport, function(channel) {
    window.bridge = channel.objects.bridge;

    // Botón Agregar Ejecutivo
    document.getElementById("btn-agregar-ejecutivo")?.addEventListener("click", function() {
      bridge.abrir_agregar_ejecutivo();
    });
    // Botón editar Ejecutivo
    document.getElementById("btn-editar-ejecutivo")?.addEventListener("click", function() {
      bridge.abrir_editar_ejecutivo();
    });
    // Botón eliminar Ejecutivo
    document.getElementById("btn-eliminar-ejecutivo")?.addEventListener("click", function() {
      bridge.abrir_eliminar_ejecutivo();
    });


    // Botón Agregar Cliente 
    document.getElementById("btn-agregar-cliente")?.addEventListener("click", function() {
      bridge.abrir_agregar_cliente();
    });
    
    // Botón Agregar Cliente 
    document.getElementById("btn-editar-cliente")?.addEventListener("click", function() {
      bridge.abrir_editar_cliente();
    });
    // Botón Eliminar Cliente
    document.getElementById("btn-eliminar-cliente")?.addEventListener("click", function() {
      bridge.abrir_eliminar_cliente();
    });


        // Botón Agregar Supervisor 
    document.getElementById("btn-agregar-supervisor")?.addEventListener("click", function() {
      bridge.abrir_agregar_supervisor();
    });
    
    // Botón Agregar Supervisor 
    document.getElementById("btn-editar-supervisor")?.addEventListener("click", function() {
      bridge.abrir_editar_supervisor();
    });
    // Botón Eliminar Supervisor
    document.getElementById("btn-eliminar-supervisor")?.addEventListener("click", function() {
      bridge.abrir_eliminar_supervisor();
    });



    // Botón Agregar Llamada
    document.getElementById("btn-agregar-llamada")?.addEventListener("click", function() {
      bridge.abrir_agregar_llamada();
    });
    // Botón Eliminar Llamada
    document.getElementById("btn-eliminar-llamada")?.addEventListener("click", function() {
      bridge.abrir_eliminar_llamada();
    });

        // 📞 Reporte de Llamadas
    document.getElementById("btn-reporte-llamadas")?.addEventListener("click", function() {
      console.log("📞 Generando reporte de llamadas...");
      bridge.generarReporte("llamadas");
    });

    // 👤 Reporte de Clientes
    document.getElementById("btn-reporte-clientes")?.addEventListener("click", function() {
      console.log("👤 Generando reporte de clientes...");
      bridge.generarReporte("clientes");
    });

    // 💼 Reporte de Ejecutivos
    document.getElementById("btn-reporte-ejecutivos")?.addEventListener("click", function() {
      console.log("💼 Generando reporte de ejecutivos...");
      bridge.generarReporte("ejecutivos");
    });
  });
});

