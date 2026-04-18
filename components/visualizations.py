import streamlit as st
import pandas as pd
import plotly.express as px


def render(df: pd.DataFrame):
    st.header("Visualizations")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Language Distribution", "Ratings", "Publication Trends", "Top Authors", "Rating vs Pages"
    ])

    with tab1:
        if "language_code" in df.columns:
            lang_counts = df["language_code"].dropna().value_counts().head(15).reset_index()
            lang_counts.columns = ["language", "count"]
            fig = px.bar(
                lang_counts, x="language", y="count",
                title="Top 15 Languages by Book Count",
                labels={"language": "Language Code", "count": "Number of Books"},
                color="count", color_continuous_scale="Blues",
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No language_code column found.")

    with tab2:
        if "average_rating" in df.columns:
            fig = px.histogram(
                df.dropna(subset=["average_rating"]),
                x="average_rating", nbins=50,
                title="Distribution of Average Ratings",
                labels={"average_rating": "Average Rating", "count": "Number of Books"},
                color_discrete_sequence=["#F28E2B"],
            )
            st.plotly_chart(fig, use_container_width=True)

            if "ratings_count" in df.columns:
                sampled = df.dropna(subset=["average_rating", "ratings_count"]).sample(
                    min(2000, len(df)), random_state=42
                )
                fig2 = px.scatter(
                    sampled, x="ratings_count", y="average_rating",
                    title="Rating vs Number of Ratings",
                    labels={"ratings_count": "Number of Ratings", "average_rating": "Average Rating"},
                    opacity=0.5, color_discrete_sequence=["#E15759"],
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No average_rating column found.")

    with tab3:
        if "year" in df.columns:
            yearly = (
                df.dropna(subset=["year"])
                .query("1800 <= year <= 2025")
                .groupby("year")
                .size()
                .reset_index(name="count")
            )
            fig = px.line(
                yearly, x="year", y="count",
                title="Books Published per Year",
                labels={"year": "Year", "count": "Number of Books"},
                color_discrete_sequence=["#59A14F"],
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No publication year data found.")

    with tab4:
        if "authors" in df.columns:
            top_authors = df["authors"].value_counts().head(20).reset_index()
            top_authors.columns = ["author", "count"]
            fig = px.bar(
                top_authors, x="count", y="author", orientation="h",
                title="Top 20 Authors by Number of Books",
                labels={"count": "Number of Books", "author": "Author"},
                color="count", color_continuous_scale="Purples",
            )
            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                coloraxis_showscale=False,
                height=600,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No authors column found.")

    with tab5:
        if "average_rating" in df.columns and "num_pages" in df.columns:
            scatter_df = df.dropna(subset=["average_rating", "num_pages"]).query("num_pages > 0 and num_pages < 2000")
            color_col = "language_code" if "language_code" in df.columns else None
            sampled = scatter_df.sample(min(2000, len(scatter_df)), random_state=42)
            fig = px.scatter(
                sampled, x="num_pages", y="average_rating",
                color=color_col,
                title="Average Rating vs Number of Pages",
                labels={"num_pages": "Number of Pages", "average_rating": "Average Rating"},
                opacity=0.6,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Required columns (average_rating, num_pages) not found.")
