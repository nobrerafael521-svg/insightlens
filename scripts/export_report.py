"""
scripts/export_report.py

CLI para:
- Ler ficheiro analisado
- Calcular métricas + gerar insights
- Produzir relatório final (Excel ou CSV) para partilhar com empresas
"""

from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd

from src.core.logger import get_logger, setup_logging
from src.dataio.reader import load_feedback_csv
from src.dataio.writer import save_dataframe
from src.analytics.metrics import compute_all_metrics
from src.nlp.summarize import generate_insights
from src.export.reports import build_full_report

log = get_logger(__name__)


def run_export_report(input_path: Path, fmt: str = "xlsx") -> Path:
    setup_logging()

    log.info(f"Export report: a ler ficheiro {input_path}")
    df = load_feedback_csv(str(input_path))

    metrics = compute_all_metrics(df)
    insights_text = generate_insights(df, options={"lang": "en"})

    report_df = build_full_report(df, metrics=metrics, insights=insights_text)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("data") / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"report_{timestamp}.{fmt}"
    save_dataframe(report_df, str(out_path), fmt=fmt)

    log.info(f"Relatório exportado para: {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exporta relatório final (Excel/CSV) de feedbacks analisados."
    )
    parser.add_argument(
        "input_csv",
        type=str,
        help="Caminho para o CSV analisado (saída do analyze.py).",
    )
    parser.add_argument(
        "--fmt",
        type=str,
        default="xlsx",
        choices=["xlsx", "csv"],
        help="Formato do relatório final.",
    )
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {input_path}")

    run_export_report(input_path, fmt=args.fmt)


if __name__ == "__main__":
    main()
