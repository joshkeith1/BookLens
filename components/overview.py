import streamlit as st
import pandas as pd


def render(df: pd.DataFrame):
    st.header("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Books", f"{len(df):,}")
    with col2:
        unique_authors = df["authors"].nunique() if "authors" in df.columns else "N/A"
        st.metric("Unique Authors", f"{unique_authors:,}" if isinstance(unique_authors, int) else unique_authors)
    with col3:
        if "average_rating" in df.columns:
            st.metric("Avg Rating", f"{df['average_rating'].mean():.2f} / 5")
        else:
            st.metric("Avg Rating", "N/A")
    with col4:
        if "year" in df.columns:
            valid = df["year"].dropna()
            if len(valid):
                st.metric("Year Range", f"{int(valid.min())} – {int(valid.max())}")
            else:
                st.metric("Year Range", "N/A")

    st.subheader("Sample Records")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Column Schema")
    schema = pd.DataFrame({
        "Column": df.columns,
        "Type": [str(df[c].dtype) for c in df.columns],
        "Non-Null Count": [int(df[c].notna().sum()) for c in df.columns],
        "Null Count": [int(df[c].isna().sum()) for c in df.columns],
        "Sample Value": [str(df[c].dropna().iloc[0]) if df[c].notna().any() else "" for c in df.columns],
    })
    st.dataframe(schema, use_container_width=True, hide_index=True)
