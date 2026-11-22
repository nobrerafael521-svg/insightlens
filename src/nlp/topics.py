# src/nlp/topics.py
from __future__ import annotations

"""
Módulo simples de extração de "tópicos".

Não usamos BERTopic nem LDA aqui para evitar dependências pesadas.
Em vez disso, fazemos:

- limpeza básica do texto
- contagem de palavras (frequência global)
- escolhemos as N palavras mais frequentes como "tópicos globais"
- para cada linha:
    - topic_label   = palavra mais forte presente naquele texto
    - topic_keywords = lista das palavras-tópico encontradas nesse texto

Isto é simples mas gera algo visual e interessante para o dashboard.
"""

from collections import Counter
from typing import List, Iterable

import pandas as pd
import re

# Stopwords muito básicas (português + inglês misturado)
BASIC_STOPWORDS = {
    "a", "o", "os", "as", "um", "uma", "de", "da", "do", "das", "dos",
    "e", "é", "foi", "ser", "estar", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem", "não", "nao", "sim", "mas", "que",
    "this", "that", "the", "and", "or", "to", "for", "of", "in", "on",
    "my", "me", "you", "your", "our", "us", "we", "they", "their",
}


def _tokenize(text: str) -> List[str]:
    """
    Transforma o texto numa lista de tokens simples (palavras):
    - passa para lowercase
    - remove caracteres não alfanuméricos
    - remove stopwords básicas
    """
    if not isinstance(text, str):
        return []

    text = text.lower()
    # substitui tudo o que não é letra ou número por espaço
    text = re.sub(r"[^a-z0-9áéíóúàâêôãõç]", " ", text, flags=re.IGNORECASE)

    tokens = [t.strip() for t in text.split() if t.strip()]
    tokens = [t for t in tokens if t not in BASIC_STOPWORDS and len(t) > 2]
    return tokens


def _extract_global_topics(texts: Iterable[str], top_n: int = 8) -> List[str]:
    """
    Conta as palavras mais frequentes em todos os textos e devolve
    as top_n como "tópicos globais".
    """
    counter: Counter[str] = Counter()

    for t in texts:
        tokens = _tokenize(t or "")
        counter.update(tokens)

    if not counter:
        return []

    most_common = [w for (w, _) in counter.most_common(top_n)]
    return most_common


def apply_topics(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    """
    Adiciona duas colunas ao DataFrame:

    - topic_label:  tópico principal daquele texto
    - topic_keywords: palavras-tópico encontradas nesse texto (string separada por vírgulas)

    Se a coluna text_col não existir, devolve o DF original sem alterações.
    """
    if text_col not in df.columns:
        # nada a fazer
        return df

    texts = df[text_col].fillna("").astype(str).tolist()

    # 1) Descobrir tópicos globais (palavras mais frequentes)
    global_topics = _extract_global_topics(texts, top_n=8)

    # Se não conseguimos extrair nada, apenas adicionamos colunas vazias
    if not global_topics:
        df_out = df.copy()
        df_out["topic_label"] = pd.NA
        df_out["topic_keywords"] = pd.NA
        return df_out

    topic_labels: List[str] = []
    topic_keywords_list: List[str] = []

    for t in texts:
        tokens = _tokenize(t)
        # palavras deste texto que fazem parte dos tópicos globais
        local_hits = [w for w in tokens if w in global_topics]

        if local_hits:
            # tópico principal = a primeira palavra-tópico que aparece
            main_topic = local_hits[0]
            # keywords = únicos, numa string "palavra1, palavra2, ..."
            uniq = sorted(set(local_hits), key=local_hits.index)
            kw_str = ", ".join(uniq)
        else:
            main_topic = "other"
            kw_str = ""

        topic_labels.append(main_topic)
        topic_keywords_list.append(kw_str)

    df_out = df.copy()
    df_out["topic_label"] = topic_labels
    df_out["topic_keywords"] = topic_keywords_list

    return df_out
 