# src/nlp/keywords.py
from __future__ import annotations

"""
Módulo simples para extração de keywords por texto.

Não usamos aqui KeyBERT/YAKE para evitar dependências pesadas.
Em vez disso:

- limpamos o texto
- tokenizamos
- removemos stopwords
- escolhemos as palavras mais frequentes de cada texto como "keywords"

Resultado:
- coluna 'keywords' com string do tipo "palavra1, palavra2, ..."
"""

from collections import Counter
from typing import List

import pandas as pd
import re

# Stopwords muito básicas (PT + EN) — as mesmas que usamos em topics.py
BASIC_STOPWORDS = {
    "a", "o", "os", "as", "um", "uma", "de", "da", "do", "das", "dos",
    "e", "é", "foi", "ser", "estar", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem", "não", "nao", "sim", "mas", "que",
    "this", "that", "the", "and", "or", "to", "for", "of", "in", "on",
    "my", "me", "you", "your", "our", "us", "we", "they", "their",
}


def _tokenize(text: str) -> List[str]:
    """
    Transforma o texto em lista de tokens:

    - lowercase
    - remove pontuação/caracteres estranhos
    - remove stopwords
    - remove tokens muito curtos
    """
    if not isinstance(text, str):
        return []

    text = text.lower()
    text = re.sub(r"[^a-z0-9áéíóúàâêôãõç]", " ", text, flags=re.IGNORECASE)

    tokens = [t.strip() for t in text.split() if t.strip()]
    tokens = [t for t in tokens if t not in BASIC_STOPWORDS and len(t) > 2]
    return tokens


def apply_keywords(
    df: pd.DataFrame,
    text_col: str = "text",
    top_k: int = 5,
) -> pd.DataFrame:
    """
    Adiciona uma coluna 'keywords' ao DataFrame.

    Para cada linha:
      - tokeniza o texto
      - conta frequência dentro desse texto
      - escolhe até 'top_k' palavras mais frequentes
      - junta numa string: "palavra1, palavra2, palavra3"

    Se a coluna text_col não existir, devolve df sem alterações.
    """
    if text_col not in df.columns:
        return df

    keywords_col: list[str] = []

    for txt in df[text_col].fillna("").astype(str).tolist():
        tokens = _tokenize(txt)

        if not tokens:
            keywords_col.append("")
            continue

        counter = Counter(tokens)
        # top_k mais frequentes
        most_common = [w for (w, _) in counter.most_common(top_k)]
        kw_str = ", ".join(most_common)
        keywords_col.append(kw_str)

    df_out = df.copy()
    df_out["keywords"] = keywords_col
    return df_out
