# BookLens

**BookLens** is an interactive Streamlit app for exploring book datasets. Pick one of the bundled datasets or upload your own CSV, then dig in with charts, filters, and AI-powered narrative summaries.

Demo: https://youtu.be/abUJmBCQQGo

## Features

| Tab | What it does |
|-----|-------------|
| **Home** | Dataset cards and feature overview |
| **Overview** | Key stats, missing-value heatmap, and a data snapshot |
| **Profiling** | Column-level breakdown — types, cardinality, nulls, distributions |
| **Visualizations** | Interactive Plotly charts that adapt to your dataset's columns |
| **Explore** | Sort, scroll, and filter the full table, then download the result |
| **AI Insights** | Claude analyzes your dataset and surfaces insights in plain language |

## Bundled Datasets

- **My Personal Library** — 381 books read by Joshua Keith (2016–2025), with series, format, and finish dates
- **Goodreads Dataset** — ~11,000 books with community ratings, review counts, and publication metadata
- **Amazon Top 50 (2009-2019)** — 550 bestseller entries with ratings, review counts, and price
- **Book-Crossing (271K books)** — 271,000 books with aggregated community ratings

You can also upload any book CSV — BookLens auto-detects columns and shows relevant charts.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with your OpenRouter API key to enable AI Insights:

```
OPENROUTER_API_KEY=your_key_here
```

## Run

```bash
streamlit run app.py
```
