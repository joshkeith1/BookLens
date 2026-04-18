import streamlit as st
import pandas as pd


def render(df: pd.DataFrame):
    st.header("Explore & Filter")

    with st.sidebar:
        st.subheader("Filters")

        search = st.text_input("Search title or author", placeholder="e.g. Tolkien")

        languages = []
        if "language_code" in df.columns:
            all_langs = sorted(df["language_code"].dropna().unique().tolist())
            languages = st.multiselect("Language", all_langs, default=[])

        year_min, year_max = 1800, 2025
        if "year" in df.columns:
            valid_years = df["year"].dropna()
            if len(valid_years):
                year_min = int(valid_years.min())
                year_max = int(valid_years.max())
        year_range = st.slider("Publication Year", year_min, year_max, (year_min, year_max))

        rating_range = (0.0, 5.0)
        if "average_rating" in df.columns:
            rating_range = st.slider("Average Rating", 0.0, 5.0, (0.0, 5.0), step=0.1)

    filtered = df.copy()

    if search:
        mask = pd.Series(False, index=filtered.index)
        for col in ["title", "authors"]:
            if col in filtered.columns:
                mask |= filtered[col].fillna("").str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    if languages and "language_code" in filtered.columns:
        filtered = filtered[filtered["language_code"].isin(languages)]

    if "year" in filtered.columns:
        filtered = filtered[
            filtered["year"].isna() | ((filtered["year"] >= year_range[0]) & (filtered["year"] <= year_range[1]))
        ]

    if "average_rating" in filtered.columns:
        filtered = filtered[
            filtered["average_rating"].isna()
            | ((filtered["average_rating"] >= rating_range[0]) & (filtered["average_rating"] <= rating_range[1]))
        ]

    st.markdown(f"**{len(filtered):,}** books match your filters")

    display_cols = [c for c in ["title", "authors", "average_rating", "language_code", "year", "num_pages", "publisher"] if c in filtered.columns]
    st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True, height=500)

    csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered results as CSV",
        data=csv,
        file_name="booklens_filtered.csv",
        mime="text/csv",
    )
