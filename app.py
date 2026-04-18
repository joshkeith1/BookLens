import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="BookLens",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.data_loader import load_data
from components import overview, profiling, visualizations, exploration, ai_insights

DATA_PATH = Path(__file__).parent / "data" / "books.csv"


def main():
    st.title("📚 BookLens")
    st.markdown("*Human-Centered Book Dataset Exploration Assistant*")

    if not DATA_PATH.exists():
        st.error(
            f"Dataset not found at `{DATA_PATH}`.\n\n"
            "Download `books.csv` from [Kaggle Goodreads Books](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks) "
            "and place it in the `data/` folder."
        )
        st.stop()

    df = load_data(str(DATA_PATH))

    with st.sidebar:
        st.markdown("### Dataset")
        st.markdown(f"**{len(df):,}** books loaded")
        if "year" in df.columns:
            valid = df["year"].dropna()
            if len(valid):
                st.markdown(f"**{int(valid.min())} – {int(valid.max())}**")
        st.divider()
        st.markdown("*BookLens — Interactive Data Exploration*")

    tabs = st.tabs(["Overview", "Profiling", "Visualizations", "Explore", "AI Insights"])

    with tabs[0]:
        overview.render(df)
    with tabs[1]:
        profiling.render(df)
    with tabs[2]:
        visualizations.render(df)
    with tabs[3]:
        exploration.render(df)
    with tabs[4]:
        ai_insights.render(df)


if __name__ == "__main__":
    main()
