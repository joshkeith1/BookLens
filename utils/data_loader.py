import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, on_bad_lines="skip")
    return preprocess(df)


_COLUMN_ALIASES = {
    "name": "title",
    "author": "authors",
    "user_rating": "average_rating",
    "reviews": "ratings_count",
}


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace("-", "_").replace(" ", "_") for c in df.columns]
    df.rename(columns={k: v for k, v in _COLUMN_ALIASES.items() if k in df.columns}, inplace=True)

    if "isbn" in df.columns:
        df = df.drop_duplicates(subset="isbn")

    str_cols = ["title", "authors", "publisher", "language_code"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace("nan", pd.NA)

    if "average_rating" in df.columns:
        df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce")
        df["average_rating"] = df["average_rating"].clip(0, 5)

    for col in ["num_pages", "ratings_count", "text_reviews_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "publication_date" in df.columns:
        df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")
        df["year"] = df["publication_date"].dt.year
    elif "year" not in df.columns:
        df["year"] = pd.NA

    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    stats = {
        "total_books": len(df),
        "unique_authors": df["authors"].nunique() if "authors" in df.columns else 0,
        "avg_rating": round(df["average_rating"].mean(), 2) if "average_rating" in df.columns else None,
        "year_range": None,
        "top_languages": [],
        "top_authors": [],
        "missing_values": {},
        "rating_distribution": {},
    }

    if "year" in df.columns:
        valid_years = df["year"].dropna()
        if len(valid_years):
            stats["year_range"] = (int(valid_years.min()), int(valid_years.max()))

    if "language_code" in df.columns:
        stats["top_languages"] = df["language_code"].value_counts().head(10).to_dict()

    if "authors" in df.columns:
        stats["top_authors"] = df["authors"].value_counts().head(10).to_dict()

    stats["missing_values"] = {col: int(df[col].isna().sum()) for col in df.columns}

    if "average_rating" in df.columns:
        bins = [0, 1, 2, 3, 4, 5]
        labels = ["0-1", "1-2", "2-3", "3-4", "4-5"]
        df["_rating_bin"] = pd.cut(df["average_rating"], bins=bins, labels=labels, include_lowest=True)
        stats["rating_distribution"] = df["_rating_bin"].value_counts().sort_index().to_dict()
        df.drop(columns=["_rating_bin"], inplace=True)

    return stats
