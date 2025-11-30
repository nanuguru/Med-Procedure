# Med Procedure

AI-agent system designed to support nurses and certified home-health caregivers in executing clinical procedures safely and efficiently.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Environment Modes](#environment-modes)
- [Important Notes](#important-notes)
- [License](#license)

## Features

### Multi-Agent System
- **LLM-powered agents**: Search, Validation, and Synthesis agents
- **Parallel agents**: Concurrent execution of search and memory retrieval
- **Sequential agents**: Ordered workflow execution
- **Loop agents**: Iterative agent execution with conditions

### Tools
- **Google Search**: SerpAPI integration for procedure research (English-only results)
- **Groq**: Llama models (llama-3.3-70b-versatile) for fast procedure generation
- **DuckDuckGo Search**: Free search for procedure information (English-only results)
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

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Med-Procedure
   ```

2. **Navigate to Backend directory**
   ```bash
   cd Backend
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**
   ```bash
   # Create a .env file in the Backend directory
   touch .env
   ```

## Configuration

Create a `.env` file in the `Backend` directory with the following variables:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
SERPAPI_API_KEY=your_serpapi_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
```

### API Keys

- **GROQ_API_KEY** (Required): Get your free API key at [https://console.groq.com/](https://console.groq.com/)
  - Used for fast procedure generation using Llama models

- **SERPAPI_API_KEY** (Optional): Google Search API key via SerpAPI. Get it at [https://serpapi.com/](https://serpapi.com/)
  - Provides access to Google Search results
  - Free tier available with limited requests (100 searches/month)
  - This is the Google API key used by the system for Google Search integration
  - Sign up at SerpAPI to get your Google Search API access

- **LANGCHAIN_API_KEY** (Optional): LangSmith API key for observability and tracing. Get it at [https://smith.langchain.com/](https://smith.langchain.com/)
  - Used for monitoring and debugging agent workflows

## Usage

### Start the Server

**Option 1: Using the run script**
```bash
cd Backend
python run.py
```

**Option 2: Using main.py directly**
```bash
cd Backend
python main.py
```

**Option 3: Using uvicorn directly**
```bash
cd Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

The server will start on `http://localhost:8080`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:8080/docs` (Swagger UI)
- **Alternative API docs**: `http://localhost:8080/redoc` (ReDoc)

## API Documentation

### Base URL
```
http://localhost:8080
```

### Endpoints

#### 1. Get Procedures

Request clinical procedures for a given service.

**Endpoint:** `POST /procedures`

**Request Body:**
```json
{
  "user_text": "wound dressing",
  "setting": "Hospital"
}
```

**Parameters:**
- `user_text` (string, required): Name of the service/procedure
- `setting` (string, required): Either "Home" or "Hospital"

**Response:**
```json
{
  "session_id": "uuid-string",
  "service_name": "wound dressing",
  "setting": "Hospital",
  "procedures": {},
  "status": "processing",
  "message": "Request is being processed. Use session_id to check status."
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8080/procedures" \
  -H "Content-Type: application/json" \
  -d '{
    "user_text": "wound dressing",
    "setting": "Hospital"
  }'
```

#### 2. Check Session Status

Get the status and results of a processing session.

**Endpoint:** `GET /sessions/{session_id}`

**Path Parameters:**
- `session_id` (string, required): The session ID returned from the procedures endpoint

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "completed",
  "progress": 1.0,
  "result": {
    "procedures": {
      "detailed_procedure": "...",
      "references": [...]
    }
  }
}
```

**Status Values:**
- `processing`: Request is being processed
- `completed`: Processing completed successfully
- `error`: An error occurred during processing
- `paused`: Processing is paused

**Example using curl:**
```bash
curl "http://localhost:8080/sessions/{session_id}"
```

#### 3. Pause Operation

Pause a long-running agent operation.

**Endpoint:** `POST /sessions/{session_id}/pause`

**Path Parameters:**
- `session_id` (string, required): The session ID to pause

**Response:**
```json
{
  "status": "paused",
  "session_id": "uuid-string"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8080/sessions/{session_id}/pause"
```

#### 4. Resume Operation

Resume a paused agent operation.

**Endpoint:** `POST /sessions/{session_id}/resume`

**Path Parameters:**
- `session_id` (string, required): The session ID to resume

**Response:**
```json
{
  "status": "resumed",
  "session_id": "uuid-string"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8080/sessions/{session_id}/resume"
```

#### 5. Get Metrics

Get application metrics.

**Endpoint:** `GET /metrics`

**Response:**
```json
{
  "total_requests": 100,
  "successful_requests": 95,
  "failed_requests": 5,
  ...
}
```

**Example using curl:**
```bash
curl "http://localhost:8080/metrics"
```

## Project Structure

```
Med-Procedure/
├── Backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent_orchestrator.py    # Multi-agent coordination
│   │   ├── agent_evaluation.py      # Agent output evaluation
│   │   ├── a2a_protocol.py          # Agent-to-agent communication
│   │   ├── base_agent.py             # Base agent class
│   │   ├── search_agent.py           # Search agent
│   │   ├── validation_agent.py       # Validation agent
│   │   ├── synthesis_agent.py        # Synthesis agent
│   │   └── context_compaction.py     # Context compaction
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search_tools.py           # Search tools (Google, Groq, DuckDuckGo)
│   │   └── custom_tools.py           # Custom validation tools
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py        # Session management
│   │   └── memory_bank.py            # Memory storage
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── logging.py                # Structured logging
│   │   ├── metrics.py                # Metrics collection
│   │   └── tracing.py                # Distributed tracing
│   ├── main.py                       # FastAPI application
│   ├── run.py                        # Run script
│   ├── config.py                     # Configuration settings
│   └── requirements.txt              # Python dependencies
└── README.md
```

## Environment Modes

### Hospital Mode
Procedures executed in clinical departments (ICU, ER, wards, labs, OT) with full equipment and support staff. This mode assumes:
- Full access to medical equipment
- Support staff available
- Standard clinical protocols
- Comprehensive documentation systems

### Home Healthcare Mode
Procedures performed at patient's residence with minimal equipment and environmental variation. This mode considers:
- Limited equipment availability
- Environmental constraints
- Single caregiver scenarios
- Adaptations for home settings

## Important Notes

⚠️ **Medical Disclaimer:**
- The system does **NOT** provide medical diagnoses or prescriptions
- The system does **NOT** require image or document uploads
- Focus is on workflow coordination, safety protocol adherence, and intelligent care navigation
- Always follow your institution's protocols and guidelines
- Consult official clinical guidelines for complete and verified procedures


