let bridgeObj = null;
new QWebChannel(qt.webChannelTransport, function (channel) {
    bridgeObj = channel.objects.bridge;
});

function cargarDetalle(datos) {
    document.getElementById("fecha").textContent =
        datos.Fecha ? datos.Fecha.split(" ")[0] : "";

    document.getElementById("hora").textContent =
        datos.Hora ? datos.Hora.split(" ")[1] : "";

    const clasificacionNumero = datos.CLASIFI_LLAMADA_Id_Clasifi_Llam ?? "Sin datos";
    const clasificacionNombre = datos.Nombre_Clasificacion ?? "Sin datos";

    document.getElementById("clasificacion").textContent = clasificacionNumero;
    document.getElementById("clasificacionNombre").textContent = clasificacionNombre;

    // ✔ Actualizar círculo de clasificación
    if (!isNaN(parseInt(clasificacionNumero))) {
        actualizarClasificacion(parseInt(clasificacionNumero));
    }

    if (datos.audio_llamada) {
        const audioElem = document.getElementById("audioLlamada");
        const duracionElem = document.getElementById("duracionLlamada");
        const audioContainer = document.getElementById("audioContainer");
        audioContainer.style.display = "block";
        audioElem.src = "data:audio/wav;base64," + datos.audio_llamada;

        audioElem.addEventListener("loadedmetadata", () => {
            const duracion = audioElem.duration;
            const min = Math.floor(duracion / 60);
            const seg = Math.floor(duracion % 60);
            duracionElem.textContent = `${min}m ${seg.toString().padStart(2, "0")}s`;
        });
    }
}

function transcribirAudio() {
    const resultadoElem = document.getElementById("resultadoTranscripcion");
    resultadoElem.textContent = "⏳ Transcribiendo, por favor espera...";

    if (bridgeObj && bridgeObj.transcribirAudioActualAssemblyai) {
        bridgeObj.transcribirAudioActualAssemblyai();
    } else {
        console.error("El bridge no está disponible o transcribirAudioActualAssemblyai no está definido");
        resultadoElem.textContent = "⚠️ Error: No se pudo iniciar la transcripción.";
    }
}

// Esta función será llamada desde Python cuando termine la transcripción
function mostrarTranscripcionFinal(texto) {
    const resultadoElem = document.getElementById("resultadoTranscripcion");
    const elementoPresiona = document.getElementById('presiona'); // Obtener el elemento a eliminar

    // 1. ELIMINAR el texto de instrucción "Presiona 'Transcribir'..."
    if (elementoPresiona) {
        elementoPresiona.remove();
    }

    // 2. MOSTRAR la transcripción final
    resultadoElem.innerText = texto ? texto : "No se detectó texto en el audio.";
}

function volverLlamadas() {
    if (bridgeObj && bridgeObj.volverTablaLlamadas) {
        bridgeObj.volverTablaLlamadas();
    } else {
        console.error("El bridge no está disponible o el slot no existe");
    }
}

/* ==========================================================
   ✔ FUNCIÓN PARA ACTUALIZAR EL CÍRCULO DE CLASIFICACIÓN
   ========================================================== */
function actualizarClasificacion(numero) {
    const circle = document.querySelector(".progress-ring-fill");
    if (!circle) return;

    const total = 282;

    // Escala visual ajustada
    const escala = {
        1: 0.04,  // ~ 6% de 0.70
        2: 0.08,  // ~ 11% de 0.70
        3: 0.15,  // ~ 21% de 0.70
        4: 0.28,  // ~ 40% de 0.70
        5: 0.42,  // ~ 60% de 0.70
        6: 0.59,  // ~ 84% de 0.70 (Alto)
        7: 0.70    // 100% de Llenado Visual (NUEVO MÁXIMO)
    };

    const porcentaje = escala[numero] ?? 0;
    const offset = total - (total * porcentaje);

    circle.style.strokeDashoffset = offset;

    // === Colores ===
    let color = "#2aff5a";

    if (numero <= 2) color = "#ff4040";
    else if (numero == 3) color = "#ff7f24";
    else if (numero <= 5) color = "#ffe600";
    else if (numero == 6) color = "#c8ff00ff";
    else color = "#2aff5a";

    circle.style.stroke = color;
}