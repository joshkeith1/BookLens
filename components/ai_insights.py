import json
import os
import streamlit as st
import pandas as pd
from openai import OpenAI
from utils.data_loader import get_summary_stats

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"


def render(df: pd.DataFrame):
    st.header("AI Insights")
    st.markdown(
        "Click the button below to have an AI analyze the dataset and surface key insights in plain language."
    )

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        st.warning("Set `OPENROUTER_API_KEY` in your `.env` file to enable AI insights.")
        return

    if st.button("Generate Insights", type="primary"):
        stats = get_summary_stats(df)
        stats_json = json.dumps(stats, indent=2, default=str)

        system_prompt = (
            "You are a data analyst assistant helping a non-technical user understand their book dataset. "
            "Write in plain, accessible language. Avoid technical jargon. "
            "Focus on what is interesting, surprising, or useful about the data."
        )

        user_message = (
            "Here are summary statistics about a book dataset:\n\n"
            f"```json\n{stats_json}\n```\n\n"
            "Please provide 3-5 clear, interesting insights about this dataset. "
            "For each insight, explain what it means in plain language and why it might be useful or interesting to someone exploring this data."
        )

        try:
            client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)

            with st.spinner("Analyzing dataset..."):
                result_placeholder = st.empty()
                full_text = ""

                stream = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    max_tokens=1024,
                    stream=True,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_text += delta
                        result_placeholder.markdown(full_text)

        except Exception as e:
            st.error(f"Error calling OpenRouter API: {e}")
