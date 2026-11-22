from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from src.core.logger import get_logger

log = get_logger(__name__)

try:
    import spacy

    _SPACY_AVAILABLE = True
except Exception:
    _SPACY_AVAILABLE = False
    log.warning(
        "normalize: spaCy não disponível. "
        "Será usada normalização simples (lower + split)."
    )


_SPACY_MODELS: Dict[str, Any] = {}


def _get_spacy_model(model_name: str) -> Optional[Any]:
    """
    Carrega e faz cache de um modelo spaCy.
    Se falhar, devolve None (fallback simples).
    """
    if model_name in _SPACY_MODELS:
        return _SPACY_MODELS[model_name]

    if not _SPACY_AVAILABLE:
        return None

    try:
        nlp = spacy.load(model_name)
        _SPACY_MODELS[model_name] = nlp
        log.info(f"normalize: spaCy model '{model_name}' carregado.")
        return nlp
    except Exception as e:
        log.error(f"normalize: falha ao carregar modelo spaCy '{model_name}': {e}")
        return None


def normalize_text(
    text: Optional[str],
    options: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Normaliza texto para análise NLP.

    options:
        - use_spacy: bool (default=True)
        - spacy_model: str (default='en_core_web_sm')
        - remove_stopwords: bool (default=True)
        - only_alpha: bool (default=True)
        - lemmatize: bool (default=True)
        - min_len: int (default=2)  # comprimento mínimo de token
    """
    if text is None:
        return ""

    s = str(text).strip()
    if not s:
        return ""

    if options is None:
        options = {}

    use_spacy = bool(options.get("use_spacy", True))
    spacy_model_name = options.get("spacy_model", "en_core_web_sm")
    remove_stopwords = bool(options.get("remove_stopwords", True))
    only_alpha = bool(options.get("only_alpha", True))
    lemmatize = bool(options.get("lemmatize", True))
    min_len = int(options.get("min_len", 2))

    if use_spacy:
        nlp = _get_spacy_model(spacy_model_name)
        if nlp is not None:
            doc = nlp(s)
            tokens: List[str] = []
            for token in doc:
                if remove_stopwords and token.is_stop:
                    continue
                if only_alpha and not token.is_alpha:
                    continue

                text_token = token.lemma_ if lemmatize else token.text
                text_token = text_token.strip()
                if len(text_token) < min_len:
                    continue
                tokens.append(text_token.lower())
            return " ".join(tokens)


    simple_tokens = []
    for tok in s.split():
        t = tok.strip().lower()
        if not t:
            continue
        if only_alpha and not t.isalpha():
            continue
        if len(t) < min_len:
            continue
        simple_tokens.append(t)
    return " ".join(simple_tokens)


def normalize_series(
    series: pd.Series,
    options: Optional[Dict[str, Any]] = None,
) -> pd.Series:
    """
    Aplica normalize_text a uma Series.
    """
    if options is None:
        options = {}

    log.debug(
        "normalize_series: start",
        extra={"n": int(series.shape[0]), "options": options},
    )
    norm = series.astype(str).map(lambda x: normalize_text(x, options))
    log.debug("normalize_series: end")
    return norm


def normalize_dataframe_column(
    df: pd.DataFrame,
    column: str,
    options: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Normaliza uma coluna específica de um DataFrame, retornando nova cópia.
    """
    if column not in df.columns:
        raise KeyError(f"normalize_dataframe_column: coluna '{column}' não existe.")

    df = df.copy()
    df[column] = normalize_series(df[column], options)
    return df
