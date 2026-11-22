# src/analytics/metrics.py

from __future__ import annotations

from typing import Dict, Any
import pandas as pd


def _safe_col(df: pd.DataFrame, col: str):
    """Devolve a série se existir, senão devolve uma série vazia."""
    return df[col] if col in df.columns else pd.Series(dtype="object")


def compute_all_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula um conjunto de métricas simples a partir do DataFrame de feedbacks.

    Espera (se existirem) colunas como:
      - sentiment_label  (positivo/negativo/neutro)
      - sentiment_score  (float)
      - rating           (1–5 ou 1–10)
      - created_at / date (datas)

    A função é defensiva: se alguma coluna não existir, a métrica vira 0/None.
    """

    metrics: Dict[str, Any] = {}

    # 1) Contagem base
    total = len(df)
    metrics["total_reviews"] = int(total)

    # 2) Sentimentos
    sent_col = _safe_col(df, "sentiment_label").astype(str).str.lower()

    metrics["positive_reviews"] = int((sent_col == "positive").sum())
    metrics["negative_reviews"] = int((sent_col == "negative").sum())
    metrics["neutral_reviews"] = int((sent_col == "neutral").sum())

    if total > 0:
        metrics["positive_ratio"] = round(
            metrics["positive_reviews"] / total, 4
        )
        metrics["negative_ratio"] = round(
            metrics["negative_reviews"] / total, 4
        )
    else:
        metrics["positive_ratio"] = 0.0
        metrics["negative_ratio"] = 0.0

    # 3) Pontuação média de sentimento (se existir)
    if "sentiment_score" in df.columns:
        metrics["avg_sentiment_score"] = float(df["sentiment_score"].mean())
    else:
        metrics["avg_sentiment_score"] = None

    # 4) Rating médio (se existir)
    if "rating" in df.columns:
        metrics["avg_rating"] = float(df["rating"].mean())
    else:
        metrics["avg_rating"] = None

    # 5) Nº de fontes diferentes (se existir coluna source)
    if "source" in df.columns:
        metrics["unique_sources"] = int(df["source"].nunique())
    else:
        metrics["unique_sources"] = 0

    return metrics
 