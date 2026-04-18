#!/usr/bin/env python3
"""
Classifies Amazon bestseller books into detailed genres using Claude.
Run once from the BookLens root:  python scripts/fetch_amazon_genres.py
Saves results to data/amazon_genres.csv, which the app merges automatically.
"""
import json
import os
import sys
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
AMAZON_CSV = ROOT / "data" / "AmazonTop50Bestsellers(2009-19).csv"
OUTPUT_CSV = ROOT / "data" / "amazon_genres.csv"

GENRE_LIST = (
    "Self-Help, Thriller, Mystery, Fantasy, Science Fiction, Literary Fiction, "
    "Romance, Horror, Historical Fiction, Biography, Memoir, History, Business, "
    "Health & Wellness, Children's, Young Adult, Religion & Spirituality, "
    "Cooking, True Crime, Science, Politics, Humor, Graphic Novel"
)


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set. Add it to your .env file.")
        sys.exit(1)

    df = pd.read_csv(AMAZON_CSV)
    books = df[["Name", "Author"]].drop_duplicates().reset_index(drop=True)
    print(f"Classifying {len(books)} unique books with Claude...")

    book_list = "\n".join(
        f'{i + 1}. "{row["Name"]}" by {row["Author"]}'
        for i, row in books.iterrows()
    )

    prompt = f"""You are a librarian classifying books by genre.

Preferred genre labels (use these when they fit, but you may use others if needed):
{GENRE_LIST}

Classify each book below into a single genre. Return a JSON object mapping each
book number (as a string) to its genre. Example: {{"1": "Thriller", "2": "Self-Help"}}
Return ONLY valid JSON — no markdown, no explanation.

{book_list}"""

    client = anthropic.Anthropic(api_key=api_key)
    print("Calling Claude API...")
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw[raw.index("{"):]
    if raw.endswith("```"):
        raw = raw[: raw.rindex("}") + 1]

    genre_map = json.loads(raw)

    rows = []
    for i, row in books.iterrows():
        genre = genre_map.get(str(i + 1), "")
        rows.append({"title": row["Name"], "genre_detail": genre})

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved {len(out_df)} genres to {OUTPUT_CSV}")
    print("\nGenre breakdown:")
    print(out_df["genre_detail"].value_counts().to_string())


if __name__ == "__main__":
    main()
