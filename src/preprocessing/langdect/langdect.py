from .exceptions import LangDetectException

def detect(text: str) -> str:
    """Dummy language detector (a sério será implementado depois)."""
    if not text:
        raise LangDetectException("Texto vazio")

    
    return "en"
