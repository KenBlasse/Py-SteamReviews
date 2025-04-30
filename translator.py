import re
from langdetect import detect
from deep_translator import GoogleTranslator

def clean_text(text: str) -> str:
    # HTML-Tags entfernen
    text = re.sub(r'<.*?>', '', text)
    # BBCode entfernen
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()

def translate_text(text: str, index: int = None) -> tuple[str | None, bool]:
    if not isinstance(text, str) or text.strip() == "":
        return None, True

    cleaned = clean_text(text)

    if not cleaned:
        return None

    # Sprache erkennen und Deutsch überspringen
    try:
        detected_lang = detect(cleaned)
        if detected_lang == 'de':
            if index is not None:
                print(f"⚠️ Skipping review {index} as it is already in German.")
                return "[Originaltext war bereits deutsch]", True
    except Exception:
        pass  # falls Sprache nicht erkannt werden kann, trotzdem versuchen

    try:
        # Kürzen bei sehr langen Texten
        if len(cleaned) > 4900:
            cleaned = cleaned[:4900]

        translated = GoogleTranslator(source='auto', target='de').translate(cleaned)
        return translated, False

    except Exception as e:
        if index is not None:
            print(f"⚠️ Übersetzungsfehler: {e}")
        return None