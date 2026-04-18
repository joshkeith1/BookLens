import streamlit as st
import pandas as pd


_FEATURE_ICONS = {
    "Overview": "📊",
    "Profiling": "🔬",
    "Visualizations": "📈",
    "Explore": "🔍",
    "AI Insights": "🤖",
}

_FEATURE_DESC = {
    "Overview": "Key stats, missing-value heatmap, and a snapshot of the dataset.",
    "Profiling": "Column-level breakdown — types, cardinality, nulls, and distributions.",
    "Visualizations": "Interactive charts that adapt to whichever columns your dataset has.",
    "Explore": "Sort, scroll, and filter the full table, then download the result.",
    "AI Insights": "Ask Claude questions about your data and get narrative summaries.",
}


def render(available: dict, dataset_choice: str, descriptions: dict):
    st.header("Welcome to BookLens")
    st.markdown(
        "BookLens is an interactive explorer for book datasets. "
        "Pick a dataset from the sidebar — or upload your own CSV — "
        "then dig in using the tabs above."
    )

    st.divider()

    # Dataset cards
    st.subheader("Available Datasets")
    cols = st.columns(len(available), gap="small")
    for col, (name, path) in zip(cols, available.items()):
        is_selected = name == dataset_choice
        border_color = "#4C78A8" if is_selected else "#444"
        with col:
            try:
                if hasattr(path, "read"):
                    path.seek(0)
                    row_count = sum(1 for _ in path) - 1
                    path.seek(0)
                else:
                    row_count = sum(1 for _ in open(path)) - 1
            except Exception:
                row_count = None

            count_str = f"{row_count:,} books" if row_count else ""
            selected_badge = " ✓ selected" if is_selected else ""
            desc = descriptions.get(name, "")

            st.markdown(
                f"""
                <div style="border:1px solid {border_color};border-radius:8px;padding:14px 16px;min-height:140px">
                    <div style="font-weight:600;font-size:1rem">{name}{selected_badge}</div>
                    <div style="color:#888;font-size:0.8rem;margin:4px 0 8px">{count_str}</div>
                    <div style="font-size:0.85rem">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # Feature highlights
    st.subheader("What you can do")
    feat_cols = st.columns(len(_FEATURE_ICONS), gap="small")
    for col, (feature, icon) in zip(feat_cols, _FEATURE_ICONS.items()):
        with col:
            st.markdown(
                f"""
                <div style="border:1px solid #333;border-radius:8px;padding:14px 16px;min-height:110px;text-align:center">
                    <div style="font-size:1.6rem">{icon}</div>
                    <div style="font-weight:600;margin:6px 0 4px">{feature}</div>
                    <div style="font-size:0.8rem;color:#aaa">{_FEATURE_DESC[feature]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.caption("Upload any book CSV using the sidebar uploader — BookLens will auto-detect columns and show relevant charts.")
