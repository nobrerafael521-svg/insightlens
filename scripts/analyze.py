# scripts/analyze.py
"""
CLI para:
- Ler ficheiro já limpo (saída do ingest.py)
- Aplicar sentimento, tópicos e keywords
- Guardar ficheiro enriquecido em data/processed
"""

from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime

from src.core.logger import get_logger, setup_logging
from src.dataio.reader import load_feedback_csv
from src.dataio.writer import save_dataframe
from src.nlp.sentiment import apply_sentiment
from src.nlp.topics import apply_topics
from src.nlp.keywords import apply_keywords

log = get_logger(__name__)


def run_analysis(input_path: Path, output_basename: str | None = None) -> Path:
    """
    Corre a pipeline de NLP em cima de um CSV já limpo.

    1) Lê o CSV de data/interim (saída do ingest.py)
    2) Aplica:
       - análise de sentimento  → sentiment_label, sentiment_score
       - extracção de tópicos   → topic / topic_label (quando implementado)
       - extracção de keywords  → keyword(s)           (quando implementado)
    3) Guarda o resultado em data/processed.
    """
    setup_logging()

    log.info(f"[analyze] A ler ficheiro limpo: {input_path}")
    df = load_feedback_csv(str(input_path))

    # --- NLP: sentimentos, tópicos, keywords ---
    # apply_sentiment agora auto-detecta a coluna de texto (text/review/comment/feedback)
    df = apply_sentiment(df)
    df = apply_topics(df)      # idem: funções devem auto-detectar a coluna de texto
    df = apply_keywords(df)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = output_basename or input_path.stem

    processed_dir = Path("data") / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    out_path = processed_dir / f"{base_name}_analyzed_{timestamp}.csv"
    save_dataframe(df, str(out_path), fmt="csv")

    log.info(f"[analyze] Concluído. Ficheiro enriquecido guardado em: {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Análise NLP (sentimento, tópicos, keywords) sobre feedbacks limpos."
    )
    parser.add_argument(
        "input_csv",
        type=str,
        help="Caminho para o CSV limpo (saída do ingest.py).",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Nome base opcional para o ficheiro de saída.",
    )
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {input_path}")

    run_analysis(input_path, args.name)


if __name__ == "__main__":
    main()
