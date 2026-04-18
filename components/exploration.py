import streamlit as st
import pandas as pd


def render(df: pd.DataFrame):
    st.header("Explore & Filter")
    st.markdown(f"**{len(df):,}** books match your filters")

    display_cols = [c for c in ["title", "authors", "year_read", "date_read", "year", "genre", "series", "series_number", "format", "personal_rating", "average_rating", "ratings_count", "price", "language_code", "num_pages", "publisher", "notes"] if c in df.columns]
    st.dataframe(df[display_cols].reset_index(drop=True), use_container_width=True, height=500)

    csv = df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered results as CSV",
        data=csv,
        file_name="booklens_filtered.csv",
        mime="text/csv",
    )
