import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _has(df, *cols):
    return all(c in df.columns for c in cols)


def _has_any(df, *cols):
    return any(c in df.columns for c in cols)


def render(df: pd.DataFrame):
    st.header("Visualizations")

    year_col = "year_read" if "year_read" in df.columns else "year"
    cat_col = "genre" if "genre" in df.columns else "language_code"

    # Build only tabs that have the required data
    available = {}
    if _has_any(df, "genre", "language_code"):
        available["Genre / Language"] = _render_category
    if _has(df, "average_rating"):
        available["Ratings"] = _render_ratings
    if _has_any(df, "year", "year_read"):
        available["Publication Trends"] = _render_trends
    if _has(df, "authors"):
        available["Top Authors"] = _render_authors
    if _has(df, "average_rating", "num_pages"):
        available["Rating vs Pages"] = _render_rating_vs_pages
    if _has(df, "genre") and _has_any(df, "year", "year_read"):
        available["Genre Over Time"] = _render_genre_over_time
        available["Genre Heatmap"] = _render_genre_heatmap
    if _has(df, "price"):
        available["Price Analysis"] = _render_price
    if _has(df, "publisher"):
        available["Publisher Distribution"] = _render_publishers
    if _has(df, "series"):
        available["Series Breakdown"] = _render_series
    if _has(df, "format", "year_read"):
        available["Reading Format"] = _render_format_over_time

    if not available:
        st.info("No visualizable columns found in this dataset.")
        return

    tabs = st.tabs(list(available.keys()))
    for tab, fn in zip(tabs, available.values()):
        with tab:
            fn(df, year_col=year_col, cat_col=cat_col)


def _render_category(df, **kw):
    cat_col = kw["cat_col"]
    cat_label = "Genre" if cat_col == "genre" else "Language"
    cat_counts = df[cat_col].dropna().value_counts().head(15).reset_index()
    cat_counts.columns = [cat_label, "count"]
    fig = px.bar(
        cat_counts, x=cat_label, y="count",
        title=f"Top 15 {cat_label}s by Book Count",
        labels={cat_label: cat_label, "count": "Number of Books"},
        color="count", color_continuous_scale="Blues",
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)


def _render_ratings(df, **kw):
    fig = px.histogram(
        df.dropna(subset=["average_rating"]),
        x="average_rating", nbins=50,
        title="Distribution of Average Ratings",
        labels={"average_rating": "Average Rating", "count": "Number of Books"},
        color_discrete_sequence=["#F28E2B"],
    )
    st.plotly_chart(fig, use_container_width=True)

    if "ratings_count" in df.columns:
        pool = df.dropna(subset=["average_rating", "ratings_count"])
        sampled = pool.sample(min(2000, len(pool)), random_state=42)
        fig2 = px.scatter(
            sampled, x="ratings_count", y="average_rating",
            title="Rating vs Number of Ratings",
            labels={"ratings_count": "Number of Ratings", "average_rating": "Average Rating"},
            opacity=0.5, color_discrete_sequence=["#E15759"],
        )
        st.plotly_chart(fig2, use_container_width=True)


def _render_trends(df, **kw):
    year_col = kw["year_col"]
    is_read = year_col == "year_read"
    yearly = (
        df.dropna(subset=[year_col])
        .query(f"1800 <= {year_col} <= 2030")
        .groupby(year_col)
        .size()
        .reset_index(name="count")
    )
    yearly.rename(columns={year_col: "year"}, inplace=True)
    title = "Books Read per Year" if is_read else "Books Published per Year"
    xlabel = "Year Read" if is_read else "Year Published"
    fig = px.line(
        yearly, x="year", y="count",
        title=title,
        labels={"year": xlabel, "count": "Number of Books"},
        color_discrete_sequence=["#59A14F"],
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_authors(df, **kw):
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


def _render_rating_vs_pages(df, **kw):
    scatter_df = (
        df.dropna(subset=["average_rating", "num_pages"])
        .query("num_pages > 0 and num_pages < 2000")
    )
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


def _render_genre_over_time(df, **kw):
    year_col = kw["year_col"]
    pivot = (
        df.dropna(subset=[year_col, "genre"])
        .groupby([year_col, "genre"])
        .size()
        .reset_index(name="count")
    )
    is_read = year_col == "year_read"
    pivot.rename(columns={year_col: "year"}, inplace=True)
    title = "Genre Mix by Year Read" if is_read else "Genre Mix by Publication Year"
    xlabel = "Year Read" if is_read else "Year Published"
    fig = px.bar(
        pivot, x="year", y="count", color="genre",
        title=title,
        labels={"year": xlabel, "count": "Number of Books", "genre": "Genre"},
        barmode="stack",
    )
    fig.update_layout(legend_title_text="Genre")
    st.plotly_chart(fig, use_container_width=True)


def _render_price(df, **kw):
    fig = px.histogram(
        df.dropna(subset=["price"]),
        x="price", nbins=30,
        title="Price Distribution",
        labels={"price": "Price (USD)", "count": "Number of Books"},
        color_discrete_sequence=["#76B7B2"],
    )
    st.plotly_chart(fig, use_container_width=True)

    if _has(df, "average_rating"):
        fig2 = px.scatter(
            df.dropna(subset=["price", "average_rating"]),
            x="price", y="average_rating",
            color="genre" if "genre" in df.columns else None,
            title="Price vs Average Rating",
            labels={"price": "Price (USD)", "average_rating": "Average Rating"},
            opacity=0.7,
        )
        st.plotly_chart(fig2, use_container_width=True)


def _render_publishers(df, **kw):
    top_pubs = df["publisher"].value_counts().head(20).reset_index()
    top_pubs.columns = ["publisher", "count"]
    fig = px.bar(
        top_pubs, x="count", y="publisher", orientation="h",
        title="Top 20 Publishers by Number of Books",
        labels={"count": "Number of Books", "publisher": "Publisher"},
        color="count", color_continuous_scale="Teal",
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_series(df, **kw):
    is_series = df["series"].notna() & (df["series"].astype(str).str.strip() != "")
    counts = {"Part of a Series": int(is_series.sum()), "Standalone": int((~is_series).sum())}
    donut_df = pd.DataFrame({"type": list(counts.keys()), "count": list(counts.values())})
    fig = px.pie(
        donut_df, names="type", values="count",
        title="Series vs Standalone Books",
        hole=0.45,
        color_discrete_sequence=["#4C78A8", "#F28E2B"],
    )
    st.plotly_chart(fig, use_container_width=True)

    top_series = (
        df[is_series]["series"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_series.columns = ["series", "count"]
    fig2 = px.bar(
        top_series, x="count", y="series", orientation="h",
        title="Top 10 Series by Books Read",
        labels={"count": "Books Read", "series": "Series"},
        color="count", color_continuous_scale="Purples",
    )
    fig2.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig2, use_container_width=True)


def _render_genre_heatmap(df, **kw):
    year_col = kw["year_col"]
    is_read = year_col == "year_read"
    xlabel = "Year Read" if is_read else "Year Published"
    title = "Genre Heatmap by Year Read" if is_read else "Genre Heatmap by Publication Year"

    clean = df.dropna(subset=[year_col, "genre"]).query(f"1800 <= {year_col} <= 2030")

    metric = st.radio(
        "Color by",
        ["Book Count", "Avg Rating"] if "average_rating" in df.columns else ["Book Count"],
        horizontal=True,
        key="genre_heatmap_metric",
    )

    top_n = st.slider("Top N genres", min_value=5, max_value=30, value=15, key="genre_heatmap_topn")
    top_genres = clean["genre"].value_counts().head(top_n).index.tolist()
    filtered = clean[clean["genre"].isin(top_genres)]

    if metric == "Avg Rating":
        pivot = (
            filtered.groupby([year_col, "genre"])["average_rating"]
            .mean()
            .unstack(fill_value=None)
        )
        color_label = "Avg Rating"
        colorscale = "RdYlGn"
    else:
        pivot = (
            filtered.groupby([year_col, "genre"])
            .size()
            .unstack(fill_value=0)
        )
        color_label = "Book Count"
        colorscale = "Blues"

    pivot = pivot[top_genres]

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values.T,
            x=pivot.index.tolist(),
            y=pivot.columns.tolist(),
            colorscale=colorscale,
            colorbar={"title": color_label},
            hoverongaps=False,
            hovertemplate=f"{xlabel}: %{{x}}<br>Genre: %{{y}}<br>{color_label}: %{{z}}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title="Genre",
        height=max(400, top_n * 28),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_format_over_time(df, **kw):
    pivot = (
        df.dropna(subset=["year_read", "format"])
        .groupby(["year_read", "format"])
        .size()
        .reset_index(name="count")
    )
    fig = px.bar(
        pivot, x="year_read", y="count", color="format",
        title="Reading Format Over Time",
        labels={"year_read": "Year", "count": "Number of Books", "format": "Format"},
        barmode="stack",
        color_discrete_map={"physical": "#4C78A8", "ebook": "#F28E2B", "audiobook": "#59A14F"},
    )
    st.plotly_chart(fig, use_container_width=True)
