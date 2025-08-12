# AI Meeting Assistant – Starter Kit

This project is a minimal AI-powered meeting assistant backend built with FastAPI, OpenAI Whisper & GPT, SQLite, and optional Redis rate limiting.

## Features

- **Audio Transcription**: Uses OpenAI Whisper to transcribe meeting audio.
- **Meeting Summarization**: GPT models generate concise summaries.
- **Action Item Extraction**: Automatically extracts tasks with owners and due dates.
- **Data Persistence**: Stores meetings and action items in SQLite (easy to switch to Postgres).
- **Rate Limiting**: Optional Redis-based rate limiter.
- **Docker Support**: Includes Dockerfile and Compose for app + Redis.
- **Kubernetes Manifests**: For dev/testing deployments.
- **Test Audio Generator**: Simple Python script to create sample meeting audio.

---

## Getting Started

### 1. Clone and Setup

```bash
git clone https://github.com/johnyric7/AIMeetingAssistant.git
cd ai-meeting-assistant
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Fill in your `OPENAI_API_KEY` and adjust other variables as needed.

### 3. Install Requirements (Local)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Locally

```bash
uvicorn app.main:app --reload
```

Open: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 5. Run with Docker Compose

```bash
make up   # or: docker compose up -d --build
```

Open: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints

**POST** `/meetings`

- Upload an audio file (mp3, wav, m4a, webm, mp4) to transcribe, summarize, and extract action items.

**GET** `/meetings/{id}`

- Get summary and transcript preview for a meeting.

**GET** `/meetings/{id}/actions`

- List extracted action items.

**GET** `/health`

- Health check.

---

## Generating Test Audio

You can use the included `generate_test_audio.py` script to create a short `.wav` file.

```python
import pyttsx3

# Meeting text content
text = (
    "This is a test meeting. The first action item is to review the budget by Friday. "
    "The second action item is to prepare the project report by Monday."
)

# Initialize TTS engine
engine = pyttsx3.init()
engine.save_to_file(text, 'test_meeting.wav')
engine.runAndWait()

print("✅ Created 'test_meeting.wav' with spoken meeting content.")
```

**Usage:**

```bash
pip install pyttsx3
python generate_test_audio.py
curl -X POST "http://127.0.0.1:8000/meetings" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@test_meeting.wav"
```

---

## Deployment Notes

- For production, switch to Postgres and managed Redis.
- Update `DATABASE_URL` and `REDIS_URL` in `.env`.
- Use the provided Kubernetes manifests for dev/test clusters.

---
