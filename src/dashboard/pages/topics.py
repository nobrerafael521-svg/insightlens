import streamlit as st
import plotly.express as px
import pandas as pd

from src.dashboard.state import state


def _get_df() -> pd.DataFrame:
    if getattr(state, "processed_df", None) is not None:
        df = state.processed_df
        if df is not None and not df.empty:
            return df.copy()
    return pd.DataFrame()


st.title("🧩 Topics & Themes")

df = _get_df()

if df.empty:
    st.info("Upload a CSV on the **Upload** page and run the analysis to see topics.")
    st.stop()

# Tenta encontrar coluna de tópicos
topic_col = None
for c in ["topic", "topic_label", "main_topic"]:
    if c in df.columns:
        topic_col = c
        break

if not topic_col:
    st.info("No topic column found. Make sure your pipeline adds a `topic` or `topic_label` column.")
    st.stop()

st.caption(f"{len(df):,} records with assigned topics.")

# 1) Top N topics
st.subheader("Top topics")

top_n = st.slider("Number of topics to show", 3, 20, 10)

counts = (
    df[topic_col]
    .value_counts()
    .head(top_n)
    .rename_axis("topic")
    .reset_index(name="count")
)

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        counts,
        x="topic",
        y="count",
        text="count",
        title="Most frequent topics",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("Top topics")
    st.dataframe(counts, use_container_width=True, height=400)

# 2) Drilldown: exemplos por tópico
st.subheader("Topic drilldown")

selected_topic = st.selectbox(
    "Select a topic to see sample comments",
    counts["topic"].tolist(),
)

text_col = None
for c in ["text", "review", "comment", "feedback"]:
    if c in df.columns:
        text_col = c
        break

if text_col:
    sample = df[df[topic_col] == selected_topic][[topic_col, text_col]].head(20)
    st.write(f"Showing up to 20 comments for topic **{selected_topic}**:")
    st.table(sample)
else:
    st.info("No text column found to show examples for this topic.")
