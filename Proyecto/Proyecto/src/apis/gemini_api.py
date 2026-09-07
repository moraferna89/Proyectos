
from google import genai
import re

# Configura tu clave de API
client = genai.Client(api_key="AIzaSyBdghhHXgrXQzWK6zLMcrR4YB4r3qkiXT8")

def consultar_gemini(transcripcion: str) -> int:
    """
    Envía la transcripción a Gemini 2.5 y devuelve un puntaje del 1 al 7.
    Funciona incluso si la transcripción contiene %, {, } u otros caracteres especiales.
    """
    # Escapar caracteres problemáticos
    safe_transcripcion = transcripcion.replace("%", "%%").replace("{", "{{").replace("}", "}}")

    # Construir el prompt
    prompt = (
        "Eres un evaluador de llamadas de atención al cliente. La transcripción que recibirás corresponde "
        "únicamente al ejecutivo. Evalúa su desempeño en la llamada y entrega un puntaje del 1 al 7, "
        "donde 1 es muy insatisfactorio y 7 es excelente. Solo devuelve el número.\n\n"
        "Al evaluar, considera los siguientes aspectos:\n"
        "- Saludo inicial: ¿Fue cordial y profesional?\n"
        "- Cortesía y amabilidad durante la conversación.\n"
        "- Claridad y precisión en sus respuestas.\n"
        "- Escucha activa y comprensión de las necesidades del cliente.\n"
        "- Uso de lenguaje profesional y adecuado.\n"
        "- Capacidad de resolver dudas o problemas del cliente.\n"
        "- Cierre de la llamada: ¿Fue apropiado y cordial?\n"
        "- Fluidez y confianza al hablar.\n\n"
        "Transcripción:\n" + safe_transcripcion
    )


    # Llamada al modelo Gemini 2.5
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )

    contenido = response.text.strip()

    # Extraer un número del 1 al 7 de manera segura
    match = re.search(r'\b([1-7])\b', contenido)
    if match:
        puntaje = int(match.group(1))
    else:
        puntaje = 4  # fallback neutro si no se encuentra número

    return puntaje

# Ejemplo de uso
if __name__ == "__main__":
    transcripcion = "Hola, estoy llamando para resolver un problema con mi cuenta..."
    score = consultar_gemini(transcripcion)
    print("Score:", score)
