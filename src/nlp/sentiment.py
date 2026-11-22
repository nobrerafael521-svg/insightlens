# src/nlp/sentiment.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, List

import pandas as pd

try:
    # Opcional: backend avançado com Transformers
    from transformers import pipeline as hf_pipeline  # type: ignore
except Exception:  # se não existir, usamos regra simples
    hf_pipeline = None


SentimentBackend = Literal["rule", "transformers"]


@dataclass
class SentimentConfig:
    """
    Configuração do analisador de sentimentos.

    backend:
      - "rule"         → regras simples (positivo/negativo)
      - "transformers" → modelo pré-treinado (se disponível)
    """
    backend: SentimentBackend = "rule"
    transformer_model: str = "nlptown/bert-base-multilingual-uncased-sentiment"
    neutral_zone: float = 0.15  # zona morta para ser considerado "neutral"

    # listas simples para o backend rule-based
    positive_words: List[str] = field(default_factory=lambda: [
        "bom", "boa", "ótimo", "otimo", "excelente", "adoro", "gosto",
        "fantástico", "fantastico", "perfeito", "recomendo", "amazing",
        "great", "love", "awesome", "nice",
    ])
    negative_words: List[str] = field(default_factory=lambda: [
        "mau", "má", "péssimo", "pessimo", "horrível", "horrivel",
        "odiei", "odeio", "não gostei", "nao gostei", "terrível",
        "terrivel", "bad", "awful", "hate", "lixo",
    ])


class SentimentAnalyzer:
    """
    Camada de alto nível para análise de sentimento.

    - Se backend = "transformers" e transformers estiver instalado:
        usa modelo pré-treinado (ex: 1–5 estrelas).
    - Caso contrário:
        usa um backend simples rule-based.
    """

    def __init__(self, config: Optional[SentimentConfig] = None) -> None:
        self.config = config or SentimentConfig()
        self._pipe = None

        if self.config.backend == "transformers" and hf_pipeline is not None:
            try:
                # carrega pipeline de sentimento (multi-língua)
                self._pipe = hf_pipeline(
                    "sentiment-analysis",
                    model=self.config.transformer_model,
                )
            except Exception:
                # fallback silencioso para rule-based se der erro
                self._pipe = None
                self.config.backend = "rule"

    # ---------- API principal ----------

    def predict(self, texts: List[str]) -> pd.DataFrame:
        """
        Recebe lista de textos e devolve DataFrame com:

        - text
        - sentiment_label: "positive" | "neutral" | "negative"
        - sentiment_score: float entre -1 e 1
        """
        if not texts:
            return pd.DataFrame(
                columns=["text", "sentiment_label", "sentiment_score"]
            )

        if self.config.backend == "transformers" and self._pipe is not None:
            return self._predict_transformers(texts)

        # fallback: regra simples
        return self._predict_rule(texts)

    # ---------- Implementações internas ----------

    def _predict_rule(self, texts: List[str]) -> pd.DataFrame:
        pos_words = [w.lower() for w in self.config.positive_words]
        neg_words = [w.lower() for w in self.config.negative_words]

        labels: List[str] = []
        scores: List[float] = []

        for t in texts:
            txt = (t or "").lower()
            pos = sum(1 for w in pos_words if w in txt)
            neg = sum(1 for w in neg_words if w in txt)
            raw = pos - neg

            # normalizar aproximadamente para [-1, 1]
            if raw == 0:
                score = 0.0
            else:
                score = max(-1.0, min(1.0, raw / 5.0))

            if score > self.config.neutral_zone:
                label = "positive"
            elif score < -self.config.neutral_zone:
                label = "negative"
            else:
                label = "neutral"

            labels.append(label)
            scores.append(score)

        return pd.DataFrame(
            {
                "text": texts,
                "sentiment_label": labels,
                "sentiment_score": scores,
            }
        )

    def _predict_transformers(self, texts: List[str]) -> pd.DataFrame:
        """
        Backend com modelo de estrelas (ex: 1–5) ou labels POSITIVE/NEGATIVE,
        convertido para [-1, 1].
        """
        assert self._pipe is not None

        preds = self._pipe(texts, truncation=True)
        labels: List[str] = []
        scores: List[float] = []

        for t, out in zip(texts, preds):
            raw_label = str(out.get("label", "")).upper()
            raw_score = float(out.get("score", 0.0))

            # alguns modelos dão "1 star", "2 stars"... outros "POSITIVE"/"NEGATIVE"
            if "STAR" in raw_label:
                # extrair dígito
                try:
                    n_stars = int("".join(ch for ch in raw_label if ch.isdigit()))
                except Exception:
                    n_stars = 3
                # mapear 1–5 → -1 a 1
                value = (n_stars - 3) / 2.0
            else:
                # POSITIVE / NEGATIVE
                if "NEG" in raw_label:
                    value = -raw_score
                else:
                    value = raw_score

            value = float(max(-1.0, min(1.0, value)))

            if value > self.config.neutral_zone:
                label = "positive"
            elif value < -self.config.neutral_zone:
                label = "negative"
            else:
                label = "neutral"

            labels.append(label)
            scores.append(value)

        return pd.DataFrame(
            {
                "text": texts,
                "sentiment_label": labels,
                "sentiment_score": scores,
            }
        )


# ------------------------------------------------------------------
# Função usada pelo resto do projeto: apply_sentiment(df)
# ------------------------------------------------------------------

TEXT_COL_CANDIDATES = ["text", "review", "comment", "feedback"]


def apply_sentiment(df: pd.DataFrame,
                    config: Optional[SentimentConfig] = None) -> pd.DataFrame:
    """
    Aplica análise de sentimento a um DataFrame de feedbacks.

    - Procura automaticamente a coluna de texto (text/review/comment/feedback)
    - Adiciona:
        - sentiment_label  (positive / neutral / negative)
        - sentiment_score  (float [-1, 1])
    """
    if df is None or df.empty:
        return df

    text_col: Optional[str] = None
    for c in TEXT_COL_CANDIDATES:
        if c in df.columns:
            text_col = c
            break

    if text_col is None:
        raise ValueError(
            "Nenhuma coluna de texto encontrada. "
            "Procuro colunas: text, review, comment, feedback."
        )

    analyzer = SentimentAnalyzer(config)

    texts = df[text_col].astype(str).fillna("").tolist()
    preds = analyzer.predict(texts)

    df_out = df.copy()
    df_out["sentiment_label"] = preds["sentiment_label"].values
    df_out["sentiment_score"] = preds["sentiment_score"].values

    return df_out
