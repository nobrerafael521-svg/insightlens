# src/nlp/summarize.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class SummarizeConfig:
    """
    Configuração simples para sumarização.
    max_chars: nº máximo de caracteres no resumo final.
    """
    max_chars: int = 400


def summarize_texts(
    texts: Iterable[str],
    config: SummarizeConfig | None = None,
) -> str:
    """
    Recebe uma lista de textos (feedbacks) e devolve
    um resumo MUITO simples, apenas para ter algo funcional:

    - junta as frases mais curtas primeiro
    - corta no máximo a max_chars
    """
    cfg = config or SummarizeConfig()

    # filtrar textos vazios e normalizar
    clean: List[str] = []
    for t in texts:
        if not isinstance(t, str):
            continue
        s = t.strip()
        if not s:
            continue
        clean.append(s)

    if not clean:
        return ""

    # ordenar por tamanho (curtos primeiro) para ficar mais "compacto"
    clean.sort(key=len)

    joined = " ".join(clean)
    if len(joined) <= cfg.max_chars:
        return joined

    # cortar e garantir que não termina a meio de uma palavra
    snippet = joined[: cfg.max_chars]
    last_space = snippet.rfind(" ")
    if last_space > 0:
        snippet = snippet[:last_space]

    return snippet + "..."


def summarize_text_column(
    texts: Iterable[str],
    max_chars: int = 400,
) -> str:
    """
    Helper fino para resumir diretamente uma coluna de DataFrame:
    df['text'].tolist() → string com resumo.
    """
    return summarize_texts(texts, config=SummarizeConfig(max_chars=max_chars))
