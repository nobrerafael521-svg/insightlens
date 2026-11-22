from __future__ import annotations

from typing import List

import pandas as pd

from src.core.logger import get_logger

log = get_logger(__name__)

# Colunas mínimas esperadas no CSV de feedback
MANDATORY_COLUMNS: List[str] = [
    "id",      # id único do feedback
    "date",    # data do comentário
    "text",    # texto do comentário / review
    "rating",  # pontuação (1–5, 0–10, etc.)
    "source",  # origem (App, Site, Email, etc.)
    "lang",    # idioma (pt, en, es, ...)
]


def validate_feedback_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida e normaliza um DataFrame de feedback de clientes.

    - Garante que as colunas mínimas existem.
    - Converte tipos básicos (date, rating).
    - Remove linhas vazias de texto.
    """

    missing = [c for c in MANDATORY_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias em falta no CSV: {missing}")

    df = df.copy()

    # Normalizar data
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Normalizar rating para numérico
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Garantir texto em string e sem espaços extra
    df["text"] = df["text"].astype(str).str.strip()

    # Remover linhas sem texto
    before = len(df)
    df = df[df["text"].str.len() > 0]
    removed = before - len(df)

    if removed > 0:
        log.info("Schema: removidas %s linha(s) sem texto.", removed)

    return df
