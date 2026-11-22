from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

import pandas as pd

try:
    import spacy
except ImportError: 
    spacy = None 

from src.core.config import get_nlp_config

log = logging.getLogger(__name__)


_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
_HTML_TAG_RE = re.compile(r"<.*?>")
_MULTI_SPACE_RE = re.compile(r"\s+")
_NON_WORD_RE = re.compile(r"[^\w\s]", re.UNICODE)


@dataclass
class TextPreprocessor:
    """
    Centralized text cleaning and normalization.

    Responsibilities:
    - Lowercasing (optional)
    - Removing URLs, emails, HTML tags, punctuation
    - Normalizing whitespace
    - Optional lemmatization via spaCy
    - Optional stopword removal
    """

    language: str = "en"
    lowercase: bool = True
    remove_stopwords: bool = True
    use_lemmatization: bool = True

    def __post_init__(self) -> None:
        cfg = get_nlp_config().raw
        self.language = cfg.get("language", self.language)
        self.lowercase = cfg.get("lowercase", self.lowercase)
        self.remove_stopwords = cfg.get("remove_stopwords", self.remove_stopwords)
        self.use_lemmatization = cfg.get("use_lemmatization", self.use_lemmatization)

        self._nlp = None
        if self.use_lemmatization:
            if spacy is None:
                log.warning("spaCy not installed; lemmatization disabled.")
                self.use_lemmatization = False
            else:
                model_name = cfg.get("spacy_model", "en_core_web_sm")
                try:
                    self._nlp = spacy.load(model_name, disable=["ner"])
                    log.info(f"Loaded spaCy model: {model_name}")
                except Exception as e:
                    log.warning(f"Could not load spaCy model '{model_name}': {e}")
                    self.use_lemmatization = False



    def clean_series(self, texts: pd.Series) -> pd.Series:
        """
        Applies base cleaning operations to a pandas Series of text.
        """
        return texts.fillna("").astype(str).map(self._clean_text)

    def tokenize_series(self, texts: pd.Series) -> List[List[str]]:
        """
        Returns a list of tokens per document after cleaning & tokenization.
        """
        cleaned = self.clean_series(texts)
        return [self._tokenize(t) for t in cleaned]



    def _clean_text(self, text: str) -> str:
        original = text

        
        text = _URL_RE.sub(" ", text)
        text = _EMAIL_RE.sub(" ", text)
        text = _HTML_TAG_RE.sub(" ", text)

    
        if self.lowercase:
            text = text.lower()

        text = _NON_WORD_RE.sub(" ", text)
        text = _MULTI_SPACE_RE.sub(" ", text).strip()

        if not text:
            return text

        if self.use_lemmatization and self._nlp is not None:
            doc = self._nlp(text)
            tokens: Iterable[str] = (
                token.lemma_ for token in doc if not token.is_punct and not token.is_space
            )
            if self.remove_stopwords:
                tokens = (t for t in tokens if t and t not in self._nlp.Defaults.stop_words)
            text = " ".join(tokens)

        return text

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        return text.split()
