# test_nlp.py
from google.cloud import language_v1

def analizar_sentimiento(texto: str) -> int:
    """
    Analiza la transcripción usando Google NLP y devuelve un score 1-7.
    """
    client = language_v1.LanguageServiceClient()

    document = language_v1.Document(
        content=texto,
        type_=language_v1.Document.Type.PLAIN_TEXT
    )

    response = client.analyze_sentiment(request={"document": document})
    score_sentimiento = response.document_sentiment.score  # [-1,1]

    # Normalizamos a 1-7
    score = int(((score_sentimiento + 1) / 2) * 6 + 1)
    score = max(1, min(7, score))

    return score
