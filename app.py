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

import pandas as pd
from utils.data_loader import load_data
from components import overview, profiling, visualizations, exploration, ai_insights

GOODREADS_PATH = Path(__file__).parent / "data" / "books.csv"
PERSONAL_PATH = Path(__file__).parent / "data" / "my_books.csv"
AMAZON_PATH = Path(__file__).parent / "data" / "AmazonTop50Bestsellers(2009-19).csv"


def build_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filter widgets and return the filtered DataFrame."""
    st.sidebar.subheader("Filters")

    search = st.sidebar.text_input("Search title or author", placeholder="e.g. Tolkien")

    # Genre or language filter
    cat_col = "genre" if "genre" in df.columns else "language_code"
    cat_label = "Genre" if cat_col == "genre" else "Language"
    selected_cats = []
    if cat_col in df.columns:
        all_cats = sorted(df[cat_col].dropna().unique().tolist())
        selected_cats = st.sidebar.multiselect(cat_label, all_cats)

    # Year filter
    year_col = "year_read" if "year_read" in df.columns else "year"
    year_min, year_max = 1800, 2025
    if year_col in df.columns:
        valid_years = df[year_col].dropna()
        if len(valid_years):
            year_min, year_max = int(valid_years.min()), int(valid_years.max())
    year_label = "Year Read" if year_col == "year_read" else "Publication Year"
    year_range = st.sidebar.slider(year_label, year_min, year_max, (year_min, year_max))

    # Rating filter (Goodreads dataset only)
    rating_range = None
    if "average_rating" in df.columns:
        rating_range = st.sidebar.slider("Average Rating", 0.0, 5.0, (0.0, 5.0), step=0.1)

    # Apply filters
    filtered = df.copy()

    if search:
        mask = pd.Series(False, index=filtered.index)
        for col in ["title", "authors"]:
            if col in filtered.columns:
                mask |= filtered[col].fillna("").str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    if selected_cats and cat_col in filtered.columns:
        filtered = filtered[filtered[cat_col].isin(selected_cats)]

    if year_col in filtered.columns:
        filtered = filtered[
            filtered[year_col].isna()
            | ((filtered[year_col] >= year_range[0]) & (filtered[year_col] <= year_range[1]))
        ]

    if rating_range and "average_rating" in filtered.columns:
        filtered = filtered[
            filtered["average_rating"].isna()
            | ((filtered["average_rating"] >= rating_range[0]) & (filtered["average_rating"] <= rating_range[1]))
        ]

    return filtered


def main():
    st.title("📚 BookLens")
    st.markdown("*Human-Centered Book Dataset Exploration Assistant*")

    with st.sidebar:
        available = {}
        if PERSONAL_PATH.exists():
            available["My Personal Library"] = str(PERSONAL_PATH)
        if GOODREADS_PATH.exists():
            available["Goodreads Dataset"] = str(GOODREADS_PATH)
        if AMAZON_PATH.exists():
            available["Amazon Top 50 Bestsellers (2009–2019)"] = str(AMAZON_PATH)

        if not available:
            st.error(
                "No dataset found. Add `data/books.csv` (Goodreads) or `data/my_books.csv` (personal)."
            )
            st.stop()

        dataset_choice = st.selectbox("Dataset", list(available.keys()))
        chosen_path = available[dataset_choice]
        st.divider()

    df = load_data(chosen_path)
    filtered_df = build_filters(df)

    with st.sidebar:
        st.divider()
        st.markdown(f"**{len(filtered_df):,}** / {len(df):,} books")
        st.markdown("*BookLens — Interactive Data Exploration*")

    tabs = st.tabs(["Overview", "Profiling", "Visualizations", "Explore", "AI Insights"])

    with tabs[0]:
        overview.render(filtered_df)
    with tabs[1]:
        profiling.render(filtered_df)
    with tabs[2]:
        visualizations.render(filtered_df)
    with tabs[3]:
        exploration.render(filtered_df)
    with tabs[4]:
        ai_insights.render(filtered_df)


if __name__ == "__main__":
    main()
