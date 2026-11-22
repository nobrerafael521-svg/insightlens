# src/dashboard/load_data.py
from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from src.dashboard.state import state
from src.core.logger import get_logger
from scripts.analyze import analyze_df

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

log = get_logger(__name__)


def _read_csv_with_fallback(content: bytes) -> pd.DataFrame:
    """
    Lê CSV de forma robusta:
    - tenta UTF-8
    - se falhar, tenta latin-1
    - ignora linhas estragadas
    - autodetecta separador
    """
    common_kwargs = dict(
        sep=None,          # autodetect ; , \t
        engine="python",   # necessário p/ sep=None + on_bad_lines
        on_bad_lines="skip",
    )

    buf = io.BytesIO(content)
    try:
        return pd.read_csv(buf, **common_kwargs)
    except UnicodeDecodeError:
        log.warning("Falha a ler CSV em UTF-8; a tentar encoding 'latin-1'...")
        buf.seek(0)
        return pd.read_csv(buf, encoding="latin-1", **common_kwargs)


def load_and_process_csv(uploaded_file: "UploadedFile") -> pd.DataFrame:
    """
    Lê o ficheiro enviado pelo upload, guarda uma cópia em data/raw,
    corre a análise (sentimento, etc.) e atualiza o estado global.
    """
    if uploaded_file is None:
        raise ValueError("Nenhum ficheiro foi carregado.")

    content: bytes = uploaded_file.getvalue()

    # 1) Ler CSV bruto
    df_raw = _read_csv_with_fallback(content)

    # 2) Guardar cópia em disco para debug
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "uploaded_latest.csv"
    try:
        df_raw.to_csv(raw_path, index=False)
        log.info("Ficheiro carregado guardado em %s", raw_path)
    except Exception as e:
        log.warning("Não foi possível guardar cópia do CSV: %s", e)

    # 3) Correr pipeline de análise (sentimento, etc.)
    df_processed = analyze_df(df_raw)

    # 4) Atualizar estado global do dashboard
    state.raw_df = df_raw
    state.processed_df = df_processed
    state.last_uploaded_file = uploaded_file.name

    log.info(
        "CSV '%s' carregado com %d linhas (processadas).",
        uploaded_file.name,
        len(df_processed),
    )

    # devolve o DataFrame já processado
    return df_processed
