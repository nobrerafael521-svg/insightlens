from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from src.core.logger import get_logger
from src.dataio.schema import validate_feedback_df

log = get_logger(__name__)

PathLike = Union[str, Path]


def load_feedback_csv(path: PathLike, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Lê um ficheiro CSV com feedback de clientes.

    - Garante que o ficheiro existe.
    - Faz o read_csv com encoding configurável.
    - Faz uma validação básica de schema (se falhar, apenas dá warning).
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"CSV não encontrado: {path}")

    log.info(f"Carregar feedback CSV: {path}")
    df = pd.read_csv(path, encoding=encoding)

    # limpeza muito simples de texto
    if "text" in df.columns:
        df["text"] = df["text"].astype(str).str.strip()

    # validação de schema (não deixamos rebentar a app se falhar)
    try:
        df = validate_feedback_df(df)
    except Exception as e:  # noqa: BLE001
        log.warning(f"Falha na validação do schema, a continuar mesmo assim: {e}")

    return df
