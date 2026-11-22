from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

import json
import pandas as pd

from src.core.logger import get_logger

log = get_logger(__name__)

DataFormat = Literal["csv", "parquet", "xlsx", "json"]


def _ensure_parent(path: Path) -> None:
    """Garante que a pasta de destino existe."""
    path.parent.mkdir(parents=True, exist_ok=True)


def save_dataframe(
    df: pd.DataFrame,
    path: str | Path,
    fmt: Optional[DataFormat] = None,
    index: bool = False,
) -> Path:
    """
    Guarda um DataFrame em disco num formato simples (csv / parquet / xlsx / json).

    - Se fmt for None, tenta inferir pelo sufixo do ficheiro.
    - Cria as pastas em falta.
    """
    p = Path(path)

    # inferir formato pela extensão, se não vier explícito
    if fmt is None:
        ext = p.suffix.lower().lstrip(".")
        if ext in {"csv", "parquet", "xlsx", "json"}:
            fmt = ext  # type: ignore[assignment]
        else:
            fmt = "parquet"  # type: ignore[assignment]

    _ensure_parent(p)

    if fmt == "csv":
        df.to_csv(p, index=index)
    elif fmt == "xlsx":
        df.to_excel(p, index=index)
    elif fmt == "json":
        df.to_json(p, orient="records", force_ascii=False)
    elif fmt == "parquet":
        df.to_parquet(p, index=index)
    else:
        raise ValueError(f"Formato não suportado: {fmt}")

    log.info(
        "DataFrame gravado em %s (%s linhas, formato=%s)",
        p,
        len(df),
        fmt,
    )
    return p


def save_json(obj: dict, path: str | Path, indent: int = 2) -> Path:
    """
    Pequeno helper para guardar um dicionário em JSON.
    Útil para guardar configs, métricas, etc.
    """
    p = Path(path)
    _ensure_parent(p)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)

    log.info("JSON gravado em %s", p)
    return p
