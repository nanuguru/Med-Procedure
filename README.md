# NurseSOP Live

AI-agent system designed to support nurses and certified home-health caregivers in executing clinical procedures safely and efficiently.

## Features

### Multi-Agent System
- **LLM-powered agents**: Search, Validation, and Synthesis agents
- **Parallel agents**: Concurrent execution of search and memory retrieval
- **Sequential agents**: Ordered workflow execution
- **Loop agents**: Iterative agent execution with conditions

### Tools
- **Google Search**: SerpAPI integration for procedure research
- **Groq**: Llama models (llama-3.1-70b-versatile) for fast procedure generation
- **DuckDuckGo Search**: Free search for procedure information
- **Custom tools**: Procedure validation, context enhancement, equipment checking
- **Hybrid search**: Combines multiple search sources (Groq + DuckDuckGo + Google)

### Sessions & Memory
- **InMemorySessionService**: Session and state management
- **Memory Bank**: Long-term memory storage and retrieval
- **Context compaction**: Reduces context size while preserving information

### Observability
- **Structured logging**: JSON-formatted logs with structlog
- **Metrics**: Prometheus-compatible metrics
- **Tracing**: OpenTelemetry distributed tracing

### Long-Running Operations
- **Pause/Resume**: Support for pausing and resuming agent operations
- **Session tracking**: Real-time session status updates

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Configure your API keys in `.env`:
- `GROQ_API_KEY`: Your Groq API key (required, get free at https://console.groq.com/)
- `SERPAPI_API_KEY`: Your SerpAPI key (optional, for Google Search)
- `LANGCHAIN_API_KEY`: Your LangSmith API key (optional, for observability)

## Usage

### Start the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

### API Endpoints

#### Get Procedures
```bash
POST /api/v1/procedures
Content-Type: application/json

{
  "user_text": "wound dressing",
  "setting": "Hospital"
}
```

Response:
```json
{
  "session_id": "uuid",
  "service_name": "wound dressing",
  "setting": "Hospital",
  "procedures": {},
  "status": "processing",
  "message": "Request is being processed. Use session_id to check status."
}
```

#### Check Session Status
```bash
GET /api/v1/sessions/{session_id}
```

#### Pause Operation
```bash
POST /api/v1/sessions/{session_id}/pause
```

#### Resume Operation
```bash
POST /api/v1/sessions/{session_id}/resume
```

#### Get Metrics
```bash
GET /api/v1/metrics
```

## Project Structure

```
NurseSOP-Live/
├── agents/
│   ├── agent_orchestrator.py    # Multi-agent coordination
│   ├── base_agent.py            # Base agent class
│   ├── search_agent.py          # Search agent
│   ├── validation_agent.py      # Validation agent
│   ├── synthesis_agent.py       # Synthesis agent
│   └── context_compaction.py    # Context compaction
├── tools/
│   ├── search_tools.py          # Search tools (Google, OpenAI)
│   └── custom_tools.py          # Custom validation tools
├── services/
│   ├── session_service.py       # Session management
│   └── memory_bank.py           # Memory storage
├── observability/
│   ├── logging.py               # Structured logging
│   ├── metrics.py               # Metrics collection
│   └── tracing.py               # Distributed tracing
├── main.py                      # FastAPI application
├── config.py                    # Configuration
└── requirements.txt             # Dependencies
```

## Environment Modes

### Hospital Mode
Procedures executed in clinical departments (ICU, ER, wards, labs, OT) with full equipment and support staff.

### Home Healthcare Mode
Procedures performed at patient's residence with minimal equipment and environmental variation.

## Important Notes

- The system does NOT provide medical diagnoses or prescriptions
- The system does NOT require image or document uploads
- Focus is on workflow coordination, safety protocol adherence, and intelligent care navigation

## License

MIT
