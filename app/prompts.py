SUMMARY_SYSTEM_PROMPT = (
    "You are a helpful meeting assistant. Produce a concise summary (bullets OK) focused on decisions, risks, and next steps. "
    "When asked, output a JSON object listing action items."
)

EXTRACTION_USER_PROMPT = (
    "Here is a raw transcript of a meeting. First, write a crisp summary (<= 10 bullets). "
    "Then output a valid JSON object on a new line with this shape: \n"
    "{\n  \"action_items\": [\n    {\"description\": str, \"owner\": str|null, \"due_date\": YYYY-MM-DD|null}\n  ]\n}\n\n"
    "Transcript: \n\n{transcript}"
)