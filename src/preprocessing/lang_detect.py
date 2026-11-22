from langdetect import detect, LangDetectException

def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"
