# src/nlp/keywords.py
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Iterable, Optional

import pandas as pd


@dataclass
class KeywordConfig:
    """
    Configuração simples para extração de keywords.
    """
    min_len: int = 4          # comprimento mínimo da palavra
    top_n: int = 5            # nº máximo de keywords por texto
    stopwords: List[str] = field(default_factory=lambda: [
        # PT
        "de", "da", "do", "das", "dos", "que", "com", "para", "uma", "numa",
        "num", "não", "nao", "sim", "mas", "por", "como", "este", "esta",
        "estar", "ser", "foi", "era", "sobre", "ainda", "muito", "pouco",
        "mais", "menos", "nos", "nós", "eu", "ele", "ela", "eles", "elas",
        "vocês", "voce", "você",
        # EN
        "the", "and", "for", "with", "this", "that", "very", "really",
        "just", "have", "has", "had", "was", "were", "are", "is", "you",
        "your", "our", "they", "them", "i", "we", "he", "she", "it",
    ])


class KeywordExtractor:
    """
    Extrator de keywords MUITO leve:
    - converte para minúsculas
    - remove caracteres estranhos
    - remove stopwords e palavras curtas
    - devolve as top N palavras mais frequentes por texto
    """

    def __init__(self, config: Optional[KeywordConfig] = None) -> None:
        self.config = config or KeywordConfig()
        self._stop = set(w.lower() for w in self.config.stopwords)

    def _tokenize(self, text: str) -> List[str]:
        # manter letras, números e espaços
        clean = re.sub(
            r"[^0-9a-zA-ZáàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ ]",
            " ",
            (text or "").lower(),
        )
        tokens = clean.split()
        tokens = [
            t for t in tokens
            if len(t) >= self.config.min_len and t not in self._stop
        ]
        return tokens

    def extract_for_text(self, text: str) -> List[str]:
        tokens = self._tokenize(text or "")
        if not tokens:
            return []
        counts = Counter(tokens)
        # top N mais frequentes
        keywords = [w for (w, _) in counts.most_common(self.config.top_n)]
        return keywords

    def extract_for_series(self, texts: Iterable[str]) -> List[List[str]]:
        return [self.extract_for_text(t or "") for t in texts]


def apply_keywords(
    df: pd.DataFrame,
    text_col: str = "text",
    out_col: str = "keywords",
    config: Optional[KeywordConfig] = None,
) -> pd.DataFrame:
    """
    Aplica extração de keywords ao DataFrame:

    - lê coluna `text_col` (por defeito 'text')
    - cria coluna `out_col` (por defeito 'keywords') com string "kw1; kw2; kw3"
    """
    if text_col not in df.columns:
        # nada a fazer
        return df

    extractor = KeywordExtractor(config=config)
    texts = df[text_col].fillna("").astype(str).tolist()
    kw_lists = extractor.extract_for_series(texts)

    df_out = df.copy()
    df_out[out_col] = ["; ".join(kws) for kws in kw_lists]
    return df_out
