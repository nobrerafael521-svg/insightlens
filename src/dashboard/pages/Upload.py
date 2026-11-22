# src/dashboard/pages/Upload.py

import os
import sys

# --- garantir que a pasta raiz do projeto (onde está "src") fica no sys.path ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd

from src.dashboard.state import state
from src.core.config import load_app_config
from src.dashboard.load_data import load_and_process_csv

cfg = load_app_config()

st.title("📤 Upload & Ingestion")

st.markdown(
    """
This section allows you to **upload CSV files** with customer feedback and
run the **ingestion + NLP pipeline**.

The uploaded data is stored in memory and will feed the other pages
(**Sentiment**, **Topics & Keywords**, **Insights & Reports**).
"""
)

uploaded_file = st.file_uploader(
    "Upload a CSV file with feedback / reviews",
    type=["csv"],
    help="Minimum columns: id, date, text, rating (optional), source (optional).",
)

run_btn = st.button("Run analysis pipeline")

if run_btn:
    if uploaded_file is None:
        st.warning("Please upload a CSV file first.")
    else:
        with st.spinner("Running ingestion + NLP pipeline..."):
            df: pd.DataFrame = load_and_process_csv(uploaded_file)

            # guardar no estado global do dashboard
            state.df = df
            state.ready = True

        st.success("Analysis completed and data loaded into the dashboard ✅")

        st.subheader("Data preview")
        st.dataframe(df.head(20), use_container_width=True)
