import base64
import os
import uuid
import sys
import wave
import assemblyai as aai

# Carpeta temporal (compatible con PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AUDIO_TMP_DIR = os.path.join(BASE_DIR, "audios_temp")
os.makedirs(AUDIO_TMP_DIR, exist_ok=True)

# Frases típicas de un ejecutivo de call center
PATRONES_EJECUTIVO = [
    "buenos dias", "buenas tardes", "buenas noches",
    "hola, buen dia", "hola, buenas", "muy buenos dias",
    "como esta", "que tal",

    "mi nombre es", "habla con", "le habla",
    "soy su ejecutivo", "soy el ejecutivo", "soy la ejecutiva",
    "gracias por comunicarse", "gracias por llamar",
    "gracias por ponerse en contacto",

    "como puedo ayudar", "en que puedo ayudar",
    "en que le puedo ayudar", "como le puedo asistir",
    "en que lo puedo asistir", "como puedo apoyarlo",
    "cuenteme", "dígame por favor",

    "puede confirmar", "me puede indicar", "me confirma",
    "podria facilitarme", "puede entregarme", "necesito verificar",
    "su número", "su rut", "su direccion",
    "verificare la informacion", "permítame verificar",
    "permítame revisar", "permítame un momento",
    "permíteme", "un momento por favor", "deme un instante",

    "le informo que", "le comento que",
    "vamos a proceder", "voy a proceder",
    "debo realizar", "debemos realizar",
    "se encuentra registrado", "según el sistema",
    "estamos revisando", "estoy verificando en el sistema",
    "estoy comprobando",

    "entiendo su situación", "comprendo su molestia",
    "gracias por su paciencia", "gracias por esperar",
    "agradezco su tiempo", "con gusto", "por supuesto",
    "claro que sí", "perfecto", "correcto",
    "no se preocupe", "vamos a solucionarlo",
    "haré lo posible", "estoy aquí para ayudar",

    "la solución seria", "lo que podemos hacer",
    "voy a ayudarle con eso", "voy a solucionarlo",
    "se lo envio", "le enviaré",
    "procederemos", "quedará solucionado",

    "hay algo mas en que pueda ayudar",
    "necesita algo mas",
    "quedo atento", "quedo atenta",
    "gracias por llamar", "gracias por su contacto",
    "que tenga un buen dia", "que esté bien",
    "muchas gracias por su tiempo", "un gusto atenderle",

    "call center", "servicio al cliente",
    "cliente", "soporte", "ticket",
    "ayuda", "asistencia", "consulta",

    "estimado", "estimada",
    "señor", "señora", "señorita",
    "con todo gusto", "por favor",
    "permítame ayudarle"
]


def puntaje_ejecutivo(texto):
    texto = texto.lower()
    score = 0
    for p in PATRONES_EJECUTIVO:
        if p in texto:
            score += 1
    return score


# -------------------------------------------------------------------
#   🚀 TRANSCRIPCIÓN CON DIARIZACIÓN
#   ==> Devuelve todo, formateado por línea
# -------------------------------------------------------------------
def transcribir_audio_assemblyai(audio_base64, estado_callback=None):

    # 1. Convertir Base64 a archivo temporal
    audio_bytes = base64.b64decode(audio_base64)
    temp_filename = f"{uuid.uuid4()}.wav"
    temp_path = os.path.join(AUDIO_TMP_DIR, temp_filename)

    with open(temp_path, "wb") as f:
        f.write(audio_bytes)

    if estado_callback:
        estado_callback("🎧 Audio decodificado…")

    # 2. Configurar API
    aai.settings.api_key = "ab394cd6218f4a2c8c41d31bba4919d2"  # ← cambia esto
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        language_code="es"
    )

    transcriber = aai.Transcriber()

    if estado_callback:
        estado_callback("🔄 Enviando a AssemblyAI…")

    result = transcriber.transcribe(temp_path, config=config)

    if not result.utterances:
        os.remove(temp_path)
        return "⚠ No se detectaron hablantes ni texto."

    # ----------------------------------------------------
    # 3. Identificación del ejecutivo
    # ----------------------------------------------------
    puntajes = {}
    primeras = {}

    for seg in result.utterances:
        spk = seg.speaker
        if spk not in primeras:
            primeras[spk] = seg.text
        puntajes[spk] = puntajes.get(spk, 0) + puntaje_ejecutivo(seg.text)

    # Elegir el que más coincide con frases de ejecutivo
    ejecutivo = max(puntajes, key=puntajes.get)
    valores = list(puntajes.values())

    # Empate → usar el primero que habló
    if len(set(valores)) == 1:
        ejecutivo = result.utterances[0].speaker

    # ----------------------------------------------------
    # 4. Construir texto formateado
    # ----------------------------------------------------
    salida = ""

    for seg in result.utterances:

        if seg.speaker == ejecutivo:
            rol = "📞 Ejecutivo"
            etiqueta = "(A)"
        else:
            rol = "🙋 Cliente"
            etiqueta = "(B)"

        salida += f"{rol} : {seg.text}\n"

    os.remove(temp_path)
    return salida.strip()


# -------------------------------------------------------------------
#   🆕 NUEVA FUNCIÓN: Devuelve SOLO el texto del ejecutivo
# -------------------------------------------------------------------
def obtener_texto_ejecutivo_assemblyai(audio_base64, estado_callback=None):
    """
    Transcribe el audio y devuelve SOLAMENTE el texto hablado por el ejecutivo
    (identificado por la coincidencia con PATRONES_EJECUTIVO).
    """

    # 1. Convertir Base64 a archivo temporal
    audio_bytes = base64.b64decode(audio_base64)
    temp_filename = f"{uuid.uuid4()}.wav"
    temp_path = os.path.join(AUDIO_TMP_DIR, temp_filename)

    with open(temp_path, "wb") as f:
        f.write(audio_bytes)

    if estado_callback:
        estado_callback("🎧 Audio decodificado…")

    # 2. Configurar API
    aai.settings.api_key = "c553c9ccd1d54f81bef1c2fb7c0b8765"  # ← cambia esto
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        language_code="es"
    )

    transcriber = aai.Transcriber()

    if estado_callback:
        estado_callback("🔄 Enviando a AssemblyAI…")

    result = transcriber.transcribe(temp_path, config=config)

    if not result.utterances:
        os.remove(temp_path)
        return "" # Devuelve cadena vacía si no hay texto

    # ----------------------------------------------------
    # 3. Identificación del ejecutivo (Misma lógica)
    # ----------------------------------------------------
    puntajes = {}
    primeras = {}

    for seg in result.utterances:
        spk = seg.speaker
        if spk not in primeras:
            primeras[spk] = seg.text
        puntajes[spk] = puntajes.get(spk, 0) + puntaje_ejecutivo(seg.text)

    # Elegir el que más coincide con frases de ejecutivo
    ejecutivo = max(puntajes, key=puntajes.get)
    valores = list(puntajes.values())

    # Empate → usar el primero que habló
    if len(set(valores)) == 1:
        ejecutivo = result.utterances[0].speaker

    # ----------------------------------------------------
    # 4. Construir texto formateado (Solo Ejecutivo)
    # ----------------------------------------------------
    salida = [] # Usamos una lista para unir los segmentos después

    for seg in result.utterances:
        if seg.speaker == ejecutivo:
            # Solo agregamos el texto del ejecutivo a la lista
            salida.append(seg.text) 

    os.remove(temp_path)
    
    # Unimos todos los segmentos del ejecutivo con un espacio.
    return " ".join(salida).strip()