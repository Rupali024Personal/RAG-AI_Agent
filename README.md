# 📄 RAG AI Agent

A production-ready Retrieval-Augmented Generation (RAG) application that enables users to upload PDF documents, index their contents into a vector database, and ask natural language questions about the uploaded documents.

The application combines:

- **Google Gemini 2.5 Flash** for answer generation
- **Qdrant** for vector storage and semantic retrieval
- **Inngest** for background workflow orchestration
- **FastAPI** for backend APIs
- **Streamlit** for the user interface
- **LlamaIndex** for document parsing and chunking

---

# 🚀 Features

## PDF Upload & Processing

Users can upload PDF documents through the Streamlit interface.

The backend:

##### 1. Receives the PDF
##### 2. Stores it temporarily
##### 3. Triggers an Inngest workflow
##### 4. Chunks the document
##### 5. Generates embeddings
##### 6. Stores vectors in Qdrant

---

## Retrieval-Augmented Generation (RAG)

Instead of sending entire documents to the LLM:

##### 1. User submits a question
##### 2. Question is converted into an embedding
##### 3. Similar chunks are retrieved from Qdrant
##### 4. Retrieved context is injected into a prompt
##### 5. Gemini generates an answer grounded in the retrieved content

This significantly improves:

- Accuracy
- Context awareness
- Cost efficiency
- Hallucination resistance

---

## Background Processing with Inngest

PDF ingestion runs asynchronously using Inngest.

Benefits:

- Retry support
- Observability
- Rate limiting
- Throttling
- Event-driven architecture
- Production-ready workflow execution

---

## Semantic Search with Qdrant

Document chunks are stored as vectors in Qdrant.

This enables:

- Similarity search
- Semantic retrieval
- Fast querying at scale

---

## Modern UI with Streamlit

The frontend provides:

- PDF uploads
- Question answering
- Query history
- Source attribution
- Simple deployment

---

# 🏗️ Architecture

```text
┌────────────────────┐
│     Streamlit      │
│       Frontend     │
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│      FastAPI       │
│      Backend       │
└───────┬────────────┘
        │
        │ Upload PDF
        ▼
┌────────────────────┐
│      Inngest       │
│ Workflow Engine    │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│ Chunk Documents    │
│ Create Embeddings  │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│      Qdrant        │
│  Vector Database   │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│     Gemini AI      │
│ Answer Generation  │
└────────────────────┘
```


# 📦 Technologies Used

## Backend

- FastAPI
- Inngest
- Google Gemini
- Python

## Frontend

- Streamlit

## Vector Database

- Qdrant

## Document Processing

- LlamaIndex
- PDF Readers

## Infrastructure

- Render
- Inngest Cloud

---

# 📚 Python Packages

```toml
fastapi
google-genai
inngest
llama-index-core
llama-index-readers-file
python-dotenv
qdrant-client
streamlit
uvicorn
```

---

# 🔑 Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_key

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key

INNGEST_EVENT_KEY=your_event_key
INNGEST_SIGNING_KEY=your_signing_key

IS_PRODUCTION=false
```

---

# ⚙️ Local Development Setup

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/rag-ai-agent.git

cd rag-ai-agent
```

---

## 2. Install UV

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Mac/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify:

```bash
uv --version
```

---

## 3. Create Virtual Environment

```bash
uv venv
```

Activate:

### Windows

```bash
.venv\Scripts\activate
```

### Linux/Mac

```bash
source .venv/bin/activate
```

---

## 4. Install Dependencies

```bash
uv sync
```

or

```bash
uv pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create:

```text
.env
```

Add all required API keys.

---

## 6. Start FastAPI Backend

```bash
uv run uvicorn main:app --reload
```

Backend:

```text
http://localhost:8000
```

---

## 7. Start Inngest Dev Server

In a new terminal:

```bash
npx inngest-cli@latest dev
```

Dashboard:

```text
http://localhost:8288
```

---

## 8. Sync Functions

Open:

```text
http://localhost:8288/functions
```

Verify:

- RAG: Ingest PDF

appears.

---

## 9. Start Streamlit

```bash
streamlit run streamlit_app.py
```

Open:

```text
http://localhost:8501
```

---

# 🔄 Workflow Walkthrough

## PDF Ingestion Flow

### Step 1

User uploads a PDF.

```text
Streamlit
   ↓
FastAPI
```

---

### Step 2

FastAPI stores the file.

```python
uploads_dir = Path("/tmp/uploads")
```

---

### Step 3

FastAPI sends an Inngest event.

```python
await inngest_client.send(...)
```

---

### Step 4

Inngest triggers:

```python
rag_ingest_pdf
```

---

### Step 5

PDF is chunked.

```python
load_and_chunk_pdf()
```

---

### Step 6

Embeddings are generated.

```python
embed_texts()
```

---

### Step 7

Vectors are stored.

```python
QdrantStorage().upsert(...)
```
---
# 🧠 RAG Implementation Details

This project uses the classic RAG pipeline:

```text
Document
    ↓
Chunking
    ↓
Embeddings
    ↓
Qdrant Storage
    ↓
Semantic Retrieval
    ↓
Prompt Construction
    ↓
Gemini
    ↓
Answer
```

Benefits:

- Reduced hallucinations
- Lower token usage
- Better factual accuracy
- Scales to large documents

---

# 📊 Why Qdrant?

Qdrant is used because it provides:

- Fast vector search
- Metadata filtering
- Cloud deployment
- Horizontal scalability
- Excellent Python SDK

---

# ⚡ Why Inngest?

Inngest provides:

- Event-driven workflows
- Retry logic
- Workflow observability
- Rate limiting
- Background execution
- Production-ready orchestration

---

# 🌐 Deployment

## Backend

Deploy to:

- Render

Configure:

```env
GEMINI_API_KEY
INNGEST_EVENT_KEY
INNGEST_SIGNING_KEY
QDRANT_URL
QDRANT_API_KEY
```

---

## Frontend

Deploy to:

- Streamlit Community Cloud

Update:

```python
BACKEND_URL
```

to your Render URL.

---

# 🔮 Future Enhancements

## Multi-Document Collections

Support:

- Multiple PDFs
- Folder uploads
- Knowledge bases

---

## Document Management

Add:

- Delete documents
- Re-index documents
- Version tracking

---

## Citation Support

Show:

- Page numbers
- Exact chunk references
- Highlighted source text

---

## Hybrid Search

Combine:

- BM25 keyword search
- Dense vector search

for improved retrieval quality.

---

## Chat Memory

Add:

- Conversation history
- Follow-up questions
- Contextual dialogue

---

## User Authentication

Integrate:

- OAuth
- Google Login
- Role-based access

---

## Streaming Responses

Enable:

- Token streaming
- Real-time answer generation

---

## Evaluation Framework

Track:

- Retrieval quality
- LLM response quality
- Hallucination metrics

---

## Observability

Integrate:

- LangSmith
- OpenTelemetry
- Grafana

---

# 📈 Learning Outcomes

This project demonstrates:

- Retrieval-Augmented Generation (RAG)
- Vector Databases
- Event-Driven Architectures
- LLM Integration
- FastAPI Development
- Streamlit Applications
- Cloud Deployment
- Production AI Engineering

---

# 📝 License

This project is provided for educational and portfolio purposes.

Feel free to fork, modify, and extend it.