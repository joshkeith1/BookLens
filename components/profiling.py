import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render(df: pd.DataFrame):
    st.header("Data Profiling")

    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        st.success("No missing values found in the dataset.")
    else:
        st.subheader("Missing Values")
        fig = px.bar(
            x=missing.index,
            y=missing.values,
            labels={"x": "Column", "y": "Missing Count"},
            title="Missing Values per Column",
            color=missing.values,
            color_continuous_scale="Reds",
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Numeric Column Distributions")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != "bookid"]

    if numeric_cols:
        selected = st.selectbox("Select column", numeric_cols)
        col_data = df[selected].dropna()
        fig = px.histogram(
            col_data,
            nbins=40,
            title=f"Distribution of {selected}",
            labels={"value": selected, "count": "Count"},
            color_discrete_sequence=["#4C78A8"],
        )
        st.plotly_chart(fig, use_container_width=True)

        desc = col_data.describe()
        cols = st.columns(6)
        labels = ["Count", "Mean", "Std Dev", "Min", "Median", "Max"]
        values = [
            f"{int(desc['count']):,}",
            f"{desc['mean']:.2f}",
            f"{desc['std']:.2f}",
            f"{desc['min']:.2f}",
            f"{desc['50%']:.2f}",
            f"{desc['max']:.2f}",
        ]
        for col, label, value in zip(cols, labels, values):
            col.metric(label, value)

    st.subheader("Data Type Breakdown")
    type_counts = df.dtypes.astype(str).value_counts().reset_index()
    type_counts.columns = ["dtype", "count"]
    fig = px.pie(type_counts, names="dtype", values="count", title="Column Data Types")
    st.plotly_chart(fig, use_container_width=True)
