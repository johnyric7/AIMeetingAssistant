import os
from datetime import datetime
from typing import List, Tuple
from openai import OpenAI

from .prompts import SUMMARY_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(filepath: str) -> str:
    """Transcribe an audio file using Whisper."""
    with open(filepath, "rb") as f:
        t = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
        )
    return t.text


def summarize_and_extract(transcript: str) -> Tuple[str, List[dict]]:
    """Use GPT to summarize and extract action items as JSON."""
    # Ask the model to return valid JSON for action items
    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": EXTRACTION_USER_PROMPT.format(transcript=transcript)}
    ]

    # Use Responses API; request two parts: summary text, and JSON action items
    resp = client.responses.create(
        model="gpt-4o-mini",
        input=messages,
    )

    # We guide model to emit a JSON block at the end; parse it
    output = resp.output_text

    # Very defensive JSON extraction: find last JSON object
    import json, re
    candidates = re.findall(r"\{[\s\S]*\}$", output.strip(), flags=re.MULTILINE)
    action_items: List[dict] = []
    summary = output
    if candidates:
        try:
            obj = json.loads(candidates[-1])
            if isinstance(obj, dict) and "action_items" in obj and isinstance(obj["action_items"], list):
                action_items = obj["action_items"]
                # Remove JSON tail from summary
                summary = output[: output.rfind(candidates[-1])].strip()
        except Exception:
            pass

    return summary.strip(), action_items