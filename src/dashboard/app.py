"""
InsightLens - Dashboard principal (Streamlit).

Este ficheiro é o ponto de entrada visual do projeto:
- Define layout base (wide, tema "corporate").
- Cria navegação lateral entre secções.
- Mostra uma Home bonita e moderna para impressões rápidas.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import streamlit as st

# Import opcional da config — se ainda não estiver 100% pronta, fazemos fallback.
try:
    from src.core.config import load_app_config  # type: ignore
except Exception:  # fallback simples
    load_app_config = None  # type: ignore


# ---------- Helpers internos ----------

def _load_title_and_theme() -> tuple[str, str]:
    """
    Lê o título da app a partir de config/app.yaml se existir.
    Se não existir, usa defaults seguros.
    """
    if load_app_config is None:
        return "InsightLens - Feedback Intelligence", "light"

    try:
        cfg = load_app_config()
        title = cfg.get("title", "InsightLens - Feedback Intelligence")
        theme = cfg.get("theme", "light")
        return str(title), str(theme)
    except Exception:
        return "InsightLens - Feedback Intelligence", "light"


def _set_page_config() -> None:
    title, _ = _load_title_and_theme()
    st.set_page_config(
        page_title=title,
        page_icon="📊",
        layout="wide",
    )


def _render_header() -> None:
    col1, col2 = st.columns([3, 1], vertical_alignment="center")

    with col1:
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:0.6rem;">
              <div style="
                  width:40px; height:40px; border-radius:12px;
                  background:linear-gradient(135deg,#4F46E5,#06B6D4);
                  display:flex; align-items:center; justify-content:center;
                  color:white; font-weight:700; font-size:1.2rem;">
                IL
              </div>
              <div>
                <div style="font-size:1.4rem; font-weight:700;">
                  InsightLens – Customer Feedback Intelligence
                </div>
                <div style="font-size:0.9rem; color:#6B7280;">
                  From raw reviews to clear business decisions.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="text-align:right; font-size:0.9rem; color:#9CA3AF;">
              Prototype · Data Science & NLP · v0.1
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_home_cards() -> None:
    st.markdown("### 🔍 Overview at a glance")

    col1, col2, col3 = st.columns(3)

    card_style = """
        background: linear-gradient(135deg, #111827, #020617);
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        color: #E5E7EB;
        box-shadow: 0 14px 30px rgba(15,23,42,0.45);
    """

    with col1:
        st.markdown(
            f"""
            <div style="{card_style}">
              <div style="font-size:0.8rem; text-transform:uppercase; color:#9CA3AF; letter-spacing:0.08em;">
                Sentiment
              </div>
              <div style="font-size:1.6rem; font-weight:700; margin-top:0.4rem;">
                62% 😊
              </div>
              <div style="font-size:0.9rem; color:#9CA3AF; margin-top:0.2rem;">
                Positive reviews (last import)
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="{card_style}">
              <div style="font-size:0.8rem; text-transform:uppercase; color:#9CA3AF; letter-spacing:0.08em;">
                Volume
              </div>
              <div style="font-size:1.6rem; font-weight:700; margin-top:0.4rem;">
                1 280
              </div>
              <div style="font-size:0.9rem; color:#9CA3AF; margin-top:0.2rem;">
                Reviews processed this week
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="{card_style}">
              <div style="font-size:0.8rem; text-transform:uppercase; color:#9CA3AF; letter-spacing:0.08em;">
                Risk signals
              </div>
              <div style="font-size:1.6rem; font-weight:700; margin-top:0.4rem;">
                37 ⚠️
              </div>
              <div style="font-size:0.9rem; color:#9CA3AF; margin-top:0.2rem;">
                Potential churn / critical reviews
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_home_explainer() -> None:
    st.markdown("### 🧠 What InsightLens does")

    left, right = st.columns([1.4, 1])

    with left:
        txt = textwrap.dedent(
            """
            InsightLens is a **NLP-powered feedback intelligence tool**.

            You upload a CSV with **customer reviews, NPS comments or support logs**  
            and the system automatically:

            - Cleans and normalises the text (language, emojis, URLs…)
            - Detects **sentiment** (positive / neutral / negative)
            - Extracts **topics and keywords** that keep appearing
            - Generates a compact **“Insights of the Week”** summary

            The result is a **clear dashboard** that turns noise into  
            **data-driven decisions for Product, Marketing and Support**.
            """
        )
        st.markdown(txt)

    with right:
        st.markdown(
            """
            <div style="
                border-radius: 18px;
                padding: 1rem 1.2rem;
                background: radial-gradient(circle at top left,#1D4ED8,#020617);
                color: #E5E7EB;
                box-shadow: 0 18px 40px rgba(15,23,42,0.6);
            ">
              <div style="font-size:0.9rem; text-transform:uppercase; letter-spacing:0.09em; color:#BFDBFE;">
                Typical workflow
              </div>
              <ol style="font-size:0.9rem; margin-top:0.6rem; padding-left:1.2rem;">
                <li>Upload a <strong>CSV</strong> with reviews / tickets</li>
                <li>Run the <strong>analysis pipeline</strong></li>
                <li>Explore <strong>sentiment & topics</strong> in the dashboard</li>
                <li>Export a <strong>ready-to-share report</strong> for stakeholders</li>
              </ol>
              <div style="margin-top:0.7rem; font-size:0.85rem; color:#E5E7EB;">
                Fully built with <strong>Python · NLP · Streamlit</strong>.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_footer() -> None:
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.8rem; color:#9CA3AF;">
          Prototype designed for portfolio purposes · Data Science & AI Developer · InsightLens
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Main ----------

def main() -> None:
    _set_page_config()

    # Sidebar de navegação
    with st.sidebar:
        st.markdown("### 📊 InsightLens")
        st.caption("Feedback & Reviews Intelligence")

        section = st.radio(
            "Go to",
            [
                "🏠 Home",
                "📤 Upload & Ingest",
                "📈 Sentiment",
                "🧩 Topics & Keywords",
                "📝 Insights & Reports",
            ],
            index=0,
        )

        st.markdown("---")
        st.caption(
            "This is a **portfolio project** showcasing NLP + Data Science + Dashboarding."
        )

    # Roteamento simples por secção
    if section == "🏠 Home":
        _render_header()
        _render_home_cards()
        st.markdown("")
        _render_home_explainer()
        _render_footer()

    elif section == "📤 Upload & Ingest":
        _render_header()
        st.markdown("### 📤 Upload & data ingestion")
        st.info(
            "This section will allow users to upload CSV files and run the ingestion pipeline.\n"
            "It will be wired to `scripts/ingest.py` and `src/dataio/*`."
        )

    elif section == "📈 Sentiment":
        _render_header()
        st.markdown("### 📈 Sentiment analysis")
        st.info(
            "This page will expose sentiment distributions, trends and NPS-like metrics,\n"
            "powered by `src/nlp/sentiment.py` and `src/analytics/metrics.py`."
        )

    elif section == "🧩 Topics & Keywords":
        _render_header()
        st.markdown("### 🧩 Topics & Keywords")
        st.info(
            "Here we will display extracted topics (LDA / BERTopic) and key phrases (KeyBERT / YAKE).\n"
            "Useful for Product, CX and Marketing teams."
        )

    elif section == "📝 Insights & Reports":
        _render_header()
        st.markdown("### 📝 Weekly insights & exports")
        st.info(
            "This page will centralise the auto-generated weekly summary and export options "
            "(CSV, Excel, PDF-ready visuals)."
        )
        st.markdown(
            "> For now this is a placeholder while we finish the core NLP pipeline."
        )

        _render_footer()


if __name__ == "__main__":
    main()
