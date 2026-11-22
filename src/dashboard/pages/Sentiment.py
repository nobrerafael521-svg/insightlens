# src/dashboard/pages/Sentiment.py

import streamlit as st
import plotly.express as px
import pandas as pd

from src.dashboard.state import state


def _get_df() -> pd.DataFrame:
    """Tenta usar o DF já analisado; se não existir, tenta o raw."""
    if getattr(state, "processed_df", None) is not None:
        df = state.processed_df
        if df is not None and not df.empty:
            return df.copy()

    if getattr(state, "raw_df", None) is not None:
        df = state.raw_df
        if df is not None and not df.empty:
            return df.copy()

    return pd.DataFrame()


# ----------------- UI -----------------
st.title("📈 Sentiment overview")

df = _get_df()

if df.empty:
    st.info("Upload a CSV on the **Upload** page to see sentiment analytics.")
    st.stop()

st.caption(f"{len(df):,} records loaded for analysis.")

# Escolher coluna de texto, rating e data (quando existirem)
text_col = next((c for c in ["text", "review", "comment", "feedback"] if c in df.columns), None)
rating_col = next((c for c in ["rating", "score", "stars"] if c in df.columns), None)
date_col = next((c for c in ["date", "created_at", "timestamp"] if c in df.columns), None)
sentiment_col = next((c for c in ["sentiment_label", "sentiment", "sentiment_class"] if c in df.columns), None)

# --------- Top KPIs ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total feedbacks", f"{len(df):,}")

with col2:
    if rating_col:
        try:
            avg_rating = float(df[rating_col].astype(float).mean())
            st.metric("Average rating", f"{avg_rating:.2f}")
        except Exception:
            st.metric("Average rating", "N/A")
    else:
        st.metric("Average rating", "N/A")

with col3:
    if sentiment_col:
        pos = (df[sentiment_col] == "positive").sum()
        percent_pos = 100 * pos / len(df)
        st.metric("Positive feedback", f"{percent_pos:.1f}%")
    else:
        st.metric("Positive feedback", "N/A")

st.markdown("---")

# 1) Distribuição de sentimentos
if sentiment_col:
    st.subheader("Sentiment distribution")

    counts = (
        df[sentiment_col]
        .value_counts()
        .rename_axis("sentiment")
        .reset_index(name="count")
    )

    fig = px.bar(
        counts,
        x="sentiment",
        y="count",
        text="count",
        title="Feedbacks per sentiment",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_title="Count", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No sentiment column detected. Make sure your analysis step adds a `sentiment_label` column.")

# 2) Rating distribution
if rating_col:
    st.subheader("Rating distribution")

    fig_hist = px.histogram(
        df,
        x=rating_col,
        nbins=10,
        title="Rating distribution",
    )
    fig_hist.update_layout(xaxis_title="Rating", yaxis_title="Count")
    st.plotly_chart(fig_hist, use_container_width=True)

# 3) Sentiment over time
if date_col and sentiment_col:
    st.subheader("Sentiment over time")

    df_time = df.copy()
    df_time[date_col] = pd.to_datetime(df_time[date_col], errors="coerce")
    df_time = df_time.dropna(subset=[date_col])

    if not df_time.empty:
        daily = (
            df_time.groupby([date_col, sentiment_col])
            .size()
            .reset_index(name="count")
        )

        fig_line = px.line(
            daily,
            x=date_col,
            y="count",
            color=sentiment_col,
            markers=True,
            title="Daily sentiment trend",
        )
        fig_line.update_layout(xaxis_title="Date", yaxis_title="Count")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Date column present but could not be parsed as datetime.")

st.markdown("----")
st.caption("This page summarises how your customers feel over time and by segment.")
