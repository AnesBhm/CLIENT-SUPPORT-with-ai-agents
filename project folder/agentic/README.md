# Doxa Agentic AI Service

This is the agentic AI service for the Doxa complaint handling system. It uses a team of 13 AI agents to classify, process, and validate responses with a feedback loop mechanism.

## Quick Testing

### CLI Tool (Recommended for Testing)

**Easy way (PowerShell script):**
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run with environment variables loaded
.\run_cli.ps1
```

**Manual way:**
```bash
# Set environment variables manually
$env:MISTRAL_API_KEY=///
$env:GEMINI_API_KEY=///

# Run the CLI
python cli.py
```

The CLI will:
- Prompt you for a question
- Show classification result (spam, aggressive, sensitive, out_of_scope, ambiguous, doxa_related)
- Run enhanced RAG pipeline with feedback loop
- Show retry history if queries were refined
- Display final response or escalation message

### Example Session

```
DOXA RAG SYSTEM - Terminal Interface
====================================

Enter your question: How do I create a project?

📝 Processing query: 'How do I create a project?'
🔍 Step 1: Classifying query...
✅ Classification: doxa_related

🤖 Step 2: Running Enhanced RAG Pipeline with Feedback Loop...
   📊 RAG Status: safe
   🔄 Attempts: 1

📋 RAG Response:
============================================================
To create a project in Doxa, navigate to the Projects page...
============================================================
```

## Running the Service

### Start the FastAPI Server

**Easy way (PowerShell script):**
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run server with environment variables loaded
.\run_server.ps1
```

**Manual way:**
```bash
# Set environment variables
$env:MISTRAL_API_KEY=
$env:GEMINI_API_KEY=

# Start server
uvicorn src.main:app --reload --port 8001
```

The service will be available at `http://localhost:8001`

## Architecture

The service follows a clean FastAPI architecture similar to the main backend:

```
agentic/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API endpoints
│   │   └── complaints.py    # Complaint processing endpoints
│   ├── services/            # Business logic
│   │   ├── classification_service.py  # Query classification
│   │   ├── rag_service.py            # RAG pipeline
│   │   └── complaint_service.py      # Main complaint orchestration
│   ├── agents/              # AI agents
│   │   └── classification_agents.py  # Classification agent definitions
│   ├── models/              # Database models (if needed)
│   ├── schemas/             # Pydantic schemas
│   │   └── complaint.py     # Request/response models
│   └── config/              # Configuration
│       └── settings.py      # App settings
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Features

### 1. Query Classification
The service uses a team of specialized agents to classify queries:
- **Spam Detection**: Filters out gibberish and nonsense
- **Aggression Detection**: Identifies hostile language
- **Sensitive Data Detection**: Flags personal information
- **Out-of-Scope Detection**: Filters non-Doxa queries
- **Ambiguity Detection**: Identifies vague queries
- **RAG Agent**: Validates Doxa-related queries

### 2. RAG Pipeline
For valid Doxa-related queries:
- Uses BGE-M3 embeddings for semantic search
- Retrieves relevant documents from ChromaDB
- Generates responses using Gemini 2.5 Flash

## Setup

### 1. Create Virtual Environment
```bash
cd agentic
python -m venv venv
```

### 2. Activate Virtual Environment
**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the `agentic/` directory:
```
GEMINI_API_KEY=your_gemini_api_key
MISTRAL_API_KEY=your_mistral_api_key
BACKEND_API_URL=http://localhost:8000
```

### 5. Run the Service
```bash
# From the agentic/ directory
uvicorn src.main:app --reload --port 8001
```

The service will be available at `http://localhost:8001`

## API Endpoints

### 1. Process Complaint
**POST** `/api/v1/complaints/process`

Process a complaint through the full agentic pipeline (classification + RAG if applicable).

**Request:**
```json
{
  "user_id": 123,
  "complaint_text": "How do I create a project in Doxa?",
  "category": null,
  "priority": null
}
```

**Response:**
```json
{
  "complaint_id": 123,
  "classification": "doxa_related",
  "response": "To create a project in Doxa...",
  "rag_used": true
}
```

### 2. Direct RAG Query
**POST** `/api/v1/complaints/query-rag`

Query the RAG system directly (bypasses classification).

**Request:**
```json
{
  "query": "What are the pricing plans?"
}
```

**Response:**
```json
{
  "query": "What are the pricing plans?",
  "answer": "Doxa offers the following pricing plans...",
  "relevant_docs_count": 6
}
```

### 3. Health Check
**GET** `/health`

Check service health.

## Integration with Main Backend

### Option 1: Mono-Repo (Current Setup) ✅ **RECOMMENDED**

**Pros:**
- Shared repository, easier version control
- Single deployment pipeline
- Shared documentation and issues
- Better for small teams

**How it works:**
1. Main backend runs on port 8000
2. Agentic service runs on port 8001
3. Each service has its own virtual environment
4. Services communicate via HTTP REST API

**Backend Integration Example:**
```python
# In app/services/ai_service.py (existing backend)
import httpx

async def process_complaint_with_agents(complaint_text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1/complaints/process",
            json={"complaint_text": complaint_text}
        )
        return response.json()
```

### Option 2: Multi-Repo (Alternative)

**Pros:**
- Complete separation of concerns
- Independent deployment cycles
- Different teams can own each repo
- Better for microservices at scale

**Structure:**
- Repo 1: `TC-DOXA` (main backend)
- Repo 2: `TC-DOXA-Agentic` (agentic AI)

**Not recommended for your case** because:
- Small team
- Tightly coupled services
- More overhead in maintenance

## Dependencies

Key libraries:
- `fastapi`: Web framework
- `langchain_community==0.4.1`: LangChain community integrations
- `chromadb==1.3.7`: Vector database
- `google.generativeai==0.8.5`: Gemini AI
- `pandas==2.2.2`: Data manipulation
- `langchain_text_splitters==1.1.0`: Text processing
- `FlagEmbedding==1.3.5`: BGE embeddings
- `agno`: Agent framework
- `python-dotenv`: Environment variables
- `pydantic-settings`: Settings management
- `httpx`: HTTP client

## Development

### Running Tests
```bash
pytest
```

### Code Style
```bash
black src/
flake8 src/
```

### Type Checking
```bash
mypy src/
```

## Deployment

Both services can be deployed together or separately:

### Docker Compose (Recommended)
```yaml
version: '3.8'
services:
  backend:
    build: ./app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
  
  agentic:
    build: ./agentic
    ports:
      - "8001:8001"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - BACKEND_API_URL=http://backend:8000
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Gemini API key | Required |
| `MISTRAL_API_KEY` | Mistral API key | Optional |
| `BACKEND_API_URL` | Main backend URL | `http://localhost:8000` |
| `CHROMA_PERSIST_PATH` | ChromaDB storage path | `chroma_archive` |
| `BGE_MODEL_NAME` | BGE model name | `BAAI/bge-m3` |

## Troubleshooting

### Issue: Virtual environment not activating
**Solution:** Use the correct activation script for your shell

### Issue: Module import errors
**Solution:** Ensure you're in the virtual environment and dependencies are installed

### Issue: ChromaDB collection not found
**Solution:** Ensure `chroma_archive` directory exists with the `test_collection`

### Issue: Port already in use
**Solution:** Change the port in the uvicorn command: `--port 8002`

## Contributing

1. Make changes in your branch
2. Test locally with both services running
3. Submit PR for review
4. Do NOT modify files in `app/` directory (main backend)

## License

Proprietary - Doxa Platform
