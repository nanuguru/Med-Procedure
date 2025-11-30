# Quick Start Guide

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `OPENAI_API_KEY` (required for procedure generation)
- `SERPAPI_API_KEY` (optional, for Google Search)
- `LANGCHAIN_API_KEY` (optional, for LangSmith observability)

3. **Run the server:**
```bash
python run.py
```

Or:
```bash
uvicorn main:app --reload
```

## API Usage

### Request Procedure

```bash
POST http://localhost:8000/api/v1/procedures
Content-Type: application/json

{
  "user_text": "wound dressing",
  "setting": "Hospital"
}
```

### Check Status

```bash
GET http://localhost:8000/api/v1/sessions/{session_id}
```

### Example with curl

```bash
# Make request
curl -X POST http://localhost:8000/api/v1/procedures \
  -H "Content-Type: application/json" \
  -d '{
    "user_text": "wound dressing",
    "setting": "Hospital"
  }'

# Check status (replace {session_id} with actual ID)
curl http://localhost:8000/api/v1/sessions/{session_id}
```

## Testing

Run the example script:
```bash
python example_usage.py
```

## Architecture

The system uses a multi-agent workflow:

1. **Search Agent** (Parallel) - Searches for procedures using Google Search and OpenAI
2. **Validation Agent** (Sequential) - Validates and enhances procedures
3. **Synthesis Agent** (Sequential) - Synthesizes final output

All agents communicate via A2A Protocol and are evaluated for quality.

## Features Implemented

✅ Multi-agent system (parallel, sequential, loop)
✅ LLM-powered agents
✅ Tools (Google Search, OpenAI, custom tools)
✅ Sessions & Memory (InMemorySessionService, Memory Bank)
✅ Context compaction
✅ Observability (logging, metrics, tracing)
✅ Long-running operations (pause/resume)
✅ Agent evaluation
✅ A2A Protocol
✅ FastAPI backend

