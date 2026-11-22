
from __future__ import annotations

from typing import Dict
import pandas as pd


def build_full_report(
    df: pd.DataFrame,
    metrics: Dict[str, object],
    insights: str,
) -> pd.DataFrame:
    """
    Constrói um DataFrame "executivo" de relatório:

    - Primeira parte: tabela com métricas agregadas.
    - Última linha: texto de insights.
    - Os dados detalhados continuam disponíveis no CSV do analyze.py,
      este relatório é mais para partilhar com gestores/empresas.
    """


    metrics_rows = [
        {"section": "metric", "name": name, "value": value}
        for name, value in metrics.items()
    ]

    metrics_rows.append(
        {
            "section": "insights",
            "name": "summary",
            "value": insights,
        }
    )

    report_df = pd.DataFrame(metrics_rows)

    return report_df
