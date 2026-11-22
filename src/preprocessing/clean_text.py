from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from src.core.logger import get_logger

log = get_logger(__name__)


_URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
_EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b")
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#\w+")
_MULTI_SPACE_RE = re.compile(r"\s+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_accents(text: str) -> str:
    """
    Remove acentos mantendo apenas caracteres ASCII básicos.
    """
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def clean_text(
    text: Optional[str],
    options: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Limpa uma string de texto de forma configurável.

    options suportadas:
        - lower: bool (default=True)
        - strip_accents: bool (default=True)
        - remove_urls: bool (default=True)
        - remove_emails: bool (default=True)
        - remove_mentions: bool (default=True)   # @user
        - remove_hashtags: bool (default=False)  # "#produto" → "produto" ou remover
        - keep_hashtag_word: bool (default=True) # se True, "#produto" → "produto"
        - remove_html: bool (default=True)
        - remove_extra_spaces: bool (default=True)
        - trim: bool (default=True)

    Esta função não faz lematização nem remoção de stopwords
    (isso é feito em normalize.py).
    """
    if text is None:
        return ""

    if options is None:
        options = {}

    s = str(text)

    lower = bool(options.get("lower", True))
    strip_accents_opt = bool(options.get("strip_accents", True))
    remove_urls = bool(options.get("remove_urls", True))
    remove_emails = bool(options.get("remove_emails", True))
    remove_mentions = bool(options.get("remove_mentions", True))
    remove_hashtags = bool(options.get("remove_hashtags", False))
    keep_hashtag_word = bool(options.get("keep_hashtag_word", True))
    remove_html = bool(options.get("remove_html", True))
    remove_extra_spaces = bool(options.get("remove_extra_spaces", True))
    trim = bool(options.get("trim", True))

    if remove_html:
        s = _HTML_TAG_RE.sub(" ", s)

    if remove_urls:
        s = _URL_RE.sub(" ", s)

    if remove_emails:
        s = _EMAIL_RE.sub(" ", s)

    if remove_mentions:
        s = _MENTION_RE.sub(" ", s)

    if remove_hashtags:
        if keep_hashtag_word:
            # "#produto top" → "produto top"
            s = _HASHTAG_RE.sub(lambda m: m.group(0)[1:], s)
        else:
            s = _HASHTAG_RE.sub(" ", s)

    if strip_accents_opt:
        s = _strip_accents(s)

    if lower:
        s = s.lower()

    if remove_extra_spaces:
        s = _MULTI_SPACE_RE.sub(" ", s)

    if trim:
        s = s.strip()

    return s


def clean_series(
    series: pd.Series,
    options: Optional[Dict[str, Any]] = None,
) -> pd.Series:
    """
    Aplica clean_text a uma Series de texto.
    """
    if options is None:
        options = {}

    log.debug(
        "clean_series: start",
        extra={"n": int(series.shape[0]), "options": options},
    )
    cleaned = series.astype(str).map(lambda x: clean_text(x, options))
    log.debug("clean_series: end")
    return cleaned


def clean_dataframe_column(
    df: pd.DataFrame,
    column: str,
    options: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Limpa uma coluna específica de um DataFrame, in-place friendly
    (mas retorna df para chaining).
    """
    if column not in df.columns:
        raise KeyError(f"clean_dataframe_column: coluna '{column}' não existe no DataFrame.")

    df = df.copy()
    df[column] = clean_series(df[column], options)
    return df
