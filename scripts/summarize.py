"""
scripts/summarize.py

CLI para:
- Ler ficheiro analisado (sentimento/tópicos/keywords)
- Gerar texto de insights utilizando src.nlp.summarize
- Guardar .txt em data/processed
"""

from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd

from src.core.logger import get_logger, setup_logging
from src.dataio.reader import load_feedback_csv
from src.analytics.metrics import compute_all_metrics
from src.nlp.summarize import generate_insights

log = get_logger(__name__)


def run_summary(input_path: Path, lang: str = "en") -> Path:
    setup_logging()

    log.info(f"Summarize: a ler ficheiro {input_path}")
    df = load_feedback_csv(str(input_path))

    metrics = compute_all_metrics(df)
    insights_text = generate_insights(df, options={"lang": lang})

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("data") / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"insights_{timestamp}.txt"

    # guarda texto + métricas básicas
    with out_path.open("w", encoding="utf-8") as f:
        f.write("=== InsightLens – Feedback Insights ===\n\n")
        f.write(insights_text)
        f.write("\n\n---\nMetrics:\n")
        for k, v in metrics.items():
            f.write(f"- {k}: {v}\n")

    log.info(f"Resumo de insights guardado em: {out_path}")
    print("\n" + insights_text + "\n")

    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera resumo de insights a partir de feedbacks analisados."
    )
    parser.add_argument(
        "input_csv",
        type=str,
        help="Caminho para o CSV analisado (saída do analyze.py).",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="en",
        choices=["en", "pt"],
        help="Idioma do resumo (en ou pt).",
    )
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {input_path}")

    run_summary(input_path, lang=args.lang)


if __name__ == "__main__":
    main()
