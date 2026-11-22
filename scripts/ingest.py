from __future__ import annotations

from pathlib import Path
from typing import Union

from src.core.logger import get_logger
from src.dataio.reader import load_feedback_csv

log = get_logger(__name__)

PathLike = Union[str, Path]


def ingest_file(path: PathLike):
    """
    Função simples de ingestão.

    - Recebe o caminho para um CSV.
    - Usa load_feedback_csv para ler e validar.
    - Devolve um DataFrame pronto a ser usado no dashboard.
    """
    path = Path(path)

    df = load_feedback_csv(path)
    log.info("Ingestão concluída: %s linhas carregadas de %s", len(df), path)

    return df
