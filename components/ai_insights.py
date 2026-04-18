import json
import os
import streamlit as st
import pandas as pd
from utils.data_loader import get_summary_stats


def render(df: pd.DataFrame):
    st.header("AI Insights")
    st.markdown(
        "Click the button below to have Claude analyze the dataset and surface key insights in plain language."
    )

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.warning("Set `ANTHROPIC_API_KEY` in your `.env` file to enable AI insights.")
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
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)

            with st.spinner("Analyzing dataset..."):
                result_placeholder = st.empty()
                full_text = ""

                with client.messages.stream(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": user_message,
                                    "cache_control": {"type": "ephemeral"},
                                }
                            ],
                        }
                    ],
                ) as stream:
                    for text in stream.text_stream:
                        full_text += text
                        result_placeholder.markdown(full_text)

        except Exception as e:
            st.error(f"Error calling Claude API: {e}")
