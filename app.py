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
from utils.data_loader import load_data, load_uploaded
from components import home, overview, profiling, visualizations, exploration, ai_insights

st.markdown("""
<style>
/* Sidebar */
[data-testid="stSidebar"] { background-color: #1F1A14; border-right: 1px solid #3A3028; }

/* Tabs */
[data-testid="stTabs"] button { font-size: 0.9rem; letter-spacing: 0.03em; }
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #E8A838;
    border-bottom-color: #E8A838;
    font-weight: 600;
}

/* Cards / containers */
[data-testid="stVerticalBlock"] > div > div[data-testid="stHorizontalBlock"] { gap: 0.75rem; }

/* Metric cards */
[data-testid="stMetric"] {
    background: #26211B;
    border: 1px solid #3A3028;
    border-radius: 10px;
    padding: 0.8rem 1rem;
}
[data-testid="stMetricValue"] { color: #E8A838; }

/* Buttons */
[data-testid="stButton"] > button {
    background: #E8A838;
    color: #1A1612;
    border: none;
    font-weight: 600;
    border-radius: 8px;
}
[data-testid="stButton"] > button:hover { background: #F0B84A; color: #1A1612; }

/* Title */
h1 { letter-spacing: -0.01em; }

/* Divider */
hr { border-color: #3A3028; }
</style>
""", unsafe_allow_html=True)

GOODREADS_PATH = Path(__file__).parent / "data" / "books.csv"
PERSONAL_PATH = Path(__file__).parent / "data" / "my_books.csv"
AMAZON_PATH = Path(__file__).parent / "data" / "AmazonTop50Bestsellers(2009-19).csv"
BX_PATH = Path(__file__).parent / "data" / "BookRecommendations" / "BookRecomendations_Books.csv"

DATASET_DESCRIPTIONS = {
    "My Personal Library": (
        "381 books read by Joshua Keith from 2016–2025. "
        "Includes series tracking, format (physical/ebook/audiobook), re-reads, and exact finish dates where recorded."
    ),
    "Goodreads Dataset": (
        "~11,000 books sourced from Goodreads. "
        "Covers a wide range of genres with community ratings, review counts, page counts, and publication metadata."
    ),
    "Amazon Top 50 (2009-2019)": (
        "550 entries representing the Amazon Top 50 bestselling books each year from 2009 to 2019. "
        "Includes user ratings, review counts, and price — split between Fiction and Non Fiction."
    ),
    "Book-Crossing (271K books)": (
        "271,000 books from the Book-Crossings dataset, paired with over 1 million community ratings. "
        "Ratings are aggregated per book and scaled to 0–5. ~45% of books have no ratings."
    ),
}


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
            available["Amazon Top 50 (2009-2019)"] = str(AMAZON_PATH)
        if BX_PATH.exists():
            available["Book-Crossing (271K books)"] = str(BX_PATH)

        st.subheader("Upload your own")
        uploaded_file = st.file_uploader("Upload a CSV", type="csv", label_visibility="collapsed")
        if uploaded_file is not None:
            available["Uploaded: " + uploaded_file.name] = uploaded_file
        st.divider()

        if not available:
            st.error(
                "No dataset found. Add `data/books.csv` (Goodreads) or `data/my_books.csv` (personal)."
            )
            st.stop()

        dataset_choice = st.selectbox("Dataset", list(available.keys()))
        chosen = available[dataset_choice]
        if dataset_choice in DATASET_DESCRIPTIONS:
            st.caption(DATASET_DESCRIPTIONS[dataset_choice])
        st.divider()

    if dataset_choice.startswith("Uploaded:"):
        df = load_uploaded(chosen)
    else:
        df = load_data(chosen)
    filtered_df = build_filters(df)

    with st.sidebar:
        st.divider()
        st.markdown(f"**{len(filtered_df):,}** / {len(df):,} books")
        st.markdown("*BookLens — Interactive Data Exploration*")

    tabs = st.tabs(["Home", "Overview", "Profiling", "Visualizations", "Explore", "AI Insights"])

    with tabs[0]:
        home.render(available, dataset_choice, DATASET_DESCRIPTIONS)
    with tabs[1]:
        overview.render(filtered_df)
    with tabs[2]:
        profiling.render(filtered_df)
    with tabs[3]:
        visualizations.render(filtered_df)
    with tabs[4]:
        exploration.render(filtered_df)
    with tabs[5]:
        ai_insights.render(filtered_df)


if __name__ == "__main__":
    main()
