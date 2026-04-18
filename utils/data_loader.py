import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, on_bad_lines="skip", low_memory=False)
    df = preprocess(df)
    df = _maybe_join_bx_ratings(df, path)
    df = _maybe_merge_amazon_genres(df, path)
    return df


_COLUMN_ALIASES = {
    # Amazon bestsellers
    "name": "title",
    "author": "authors",
    "user_rating": "average_rating",
    "reviews": "ratings_count",
    # Book-Crossings / BX dataset
    "book_title": "title",
    "book_author": "authors",
    "year_of_publication": "year",
}


def _maybe_join_bx_ratings(df: pd.DataFrame, path: str) -> pd.DataFrame:
    """If a Ratings.csv sibling exists, aggregate and merge ratings into df."""
    ratings_path = Path(path).parent / "Ratings.csv"
    if "isbn" not in df.columns or not ratings_path.exists():
        return df

    ratings = pd.read_csv(ratings_path, usecols=["ISBN", "Book-Rating"], low_memory=False)
    ratings.columns = ["isbn", "book_rating"]
    ratings = ratings[ratings["book_rating"] > 0]  # 0 = implicit (not rated)

    agg = (
        ratings.groupby("isbn")["book_rating"]
        .agg(average_rating="mean", ratings_count="count")
        .reset_index()
    )
    # BX ratings are 1–10; scale to 0–5 to match other datasets
    agg["average_rating"] = (agg["average_rating"] / 2).round(2)

    df = df.merge(agg, on="isbn", how="left")
    return df


def _maybe_merge_amazon_genres(df: pd.DataFrame, path: str) -> pd.DataFrame:
    """Replaces coarse Fiction/Non Fiction genre with detailed labels from amazon_genres.csv."""
    genres_path = Path(path).parent / "amazon_genres.csv"
    if "price" not in df.columns or not genres_path.exists():
        return df

    genres = pd.read_csv(genres_path)
    df = df.merge(genres[["title", "genre_detail"]], on="title", how="left")
    df["genre"] = df["genre_detail"].fillna(df.get("genre", pd.NA))
    df.drop(columns=["genre_detail"], inplace=True)
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace("-", "_").replace(" ", "_") for c in df.columns]
    df.rename(columns={k: v for k, v in _COLUMN_ALIASES.items() if k in df.columns}, inplace=True)

    # Drop image URL columns (BX dataset)
    url_cols = [c for c in df.columns if "image" in c or "url" in c]
    if url_cols:
        df.drop(columns=url_cols, inplace=True)

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

    for col in ["num_pages", "ratings_count", "text_reviews_count", "year", "price"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "publication_date" in df.columns:
        df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")
        df["year"] = df["publication_date"].dt.year
    elif "year" not in df.columns:
        df["year"] = pd.NA

    if "year" in df.columns:
        df["year"] = df["year"].where(df["year"].between(1800, 2026), other=pd.NA)

    return df


def load_uploaded(file) -> pd.DataFrame:
    df = pd.read_csv(file, on_bad_lines="skip", low_memory=False)
    return preprocess(df)


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
