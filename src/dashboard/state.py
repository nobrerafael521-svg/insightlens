"""
State manager for InsightLens dashboard.
Keeps the latest loaded and processed datasets in memory.
"""

import pandas as pd


class DashboardState:
    def __init__(self) -> None:
        # Dataframes em diferentes fases do pipeline
        self.raw_df: pd.DataFrame | None = None          # CSV bruto
        self.cleaned_df: pd.DataFrame | None = None      # após limpeza/preprocessamento
        self.processed_df: pd.DataFrame | None = None    # após NLP (sentiment, topics, etc.)

        # Info extra
        self.last_uploaded_file: str | None = None

    def has_data(self) -> bool:
        """Returns True if there is a processed dataframe ready to be used."""
        return self.processed_df is not None and not self.processed_df.empty

    # --- Conveniência: alias .df -> .processed_df ---
    @property
    def df(self) -> pd.DataFrame | None:
        """Main dataframe used by the dashboard pages."""
        return self.processed_df

    @df.setter
    def df(self, value: pd.DataFrame | None) -> None:
        self.processed_df = value


# Singleton (one global state)
state = DashboardState()
