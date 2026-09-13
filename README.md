# AI-Based Knowledge Retrieval Platform with Query Resolution System

An AI-powered Retrieval-Augmented Generation (RAG) platform that enables users to upload knowledge-base documents and query them using natural language. The project combines a multi-agent LangGraph workflow with persistent PostgreSQL conversation memory, clarification handling, browser-based voice input/output, response transparency, authenticated user workspaces, and direct LLM handling for general-knowledge/conversational questions. Milestone 4 adds query analytics, knowledge-gap detection, authenticated user-specific knowledge bases, user-scoped ChromaDB retrieval, and dedicated Analytics and Knowledge Gap dashboards.

> **Detailed Documentation:** See **`PROJECT_GUIDE.md`** for the complete architecture, workflow diagrams, backend/frontend design, API documentation, Milestone 1, Milestone 2 and Milestone 3 implementation details, testing flow, and development guidelines.

## Features

- 📄 Upload PDF, DOCX, TXT, and CSV documents
- 🔍 Semantic document retrieval using ChromaDB and Sentence Transformers
- 🧠 Query Understanding Agent for normalization, entity/keyword extraction and query classification
- 🔎 Hybrid retrieval with semantic search and optional exact-term matching
- 📊 Query-aware relevance ranking and low-confidence filtering
- 🤖 Response Generation Agent for grounded answers
- 📚 Source attribution and retrieval-aware confidence scoring
- 🔗 LangGraph orchestration of the multi-agent workflow
- ❓ Clarification Agent for ambiguous queries and query refinement
- 💬 Persistent multi-turn conversation memory using PostgreSQL and `conversation_id`
- 🧠 Context-aware follow-up resolution such as `What about its ranking?`
- 🎙️ Browser speech-to-text using the Web Speech API
- 🔊 Browser text-to-speech using Speech Synthesis API
- 🔍 Response transparency with citations, source details, confidence and retrieved chunk inspection
- 💻 React-based conversational interface
- 🗂️ Document management (view and delete indexed documents)
- 📈 Background document processing with upload status tracking
- 🔐 User authentication with sign up, sign in, JWT sessions and logout
- 👤 Per-user conversation ownership and isolation
- 🌐 General-knowledge and conversational queries answered directly by the LLM
- 🧩 User-facing upload UI hides internal chunk/embedding/vector counts while processing continues normally
- 📊 Query Analytics Dashboard with real backend query totals, answer rate, confidence, response time and query-type distribution
- ⚠️ Knowledge Gap Detection with backend-detected unanswered, zero-retrieval and low-confidence retrieval records
- 🔐 User-specific Knowledge Base stored with authenticated `user_id` ownership and ChromaDB user-scoped retrieval
- 🗂️ User-specific knowledge-base upload/list/read/delete/search APIs
- 📈 Background processing status for private knowledge-base documents
- 🧭 History & Statistics view for recent query/conversation activity

## Technology Stack

### Frontend

- React 19
- Vite
- JavaScript
- Vanilla CSS
- Web Speech API
- Browser Speech Synthesis API

### Backend

- Python 3
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- Psycopg 3
- Alembic

### AI & Agent Layer

- LangChain
- LangGraph
- langchain-groq
- Groq LLM
- Sentence Transformers (`all-MiniLM-L6-v2`)
- ChromaDB
- Retrieval-Augmented Generation (RAG)

### Document Processing

- pypdf
- python-docx
- pandas
- LangChain text splitters

### API & File Handling

- python-multipart

## Project Structure

The project contains a single authoritative backend at the repository root. Do not place or maintain a second backend copy inside `frontend/`.

```text
AI-Based Knowledge Retrieval Platform with Query Resolution System/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 0f628c51b660_initial_schema.py
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── README
│   ├── alembic.ini
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   ├── health.py
│   │   │   ├── query.py
│   │   │   ├── conversations.py
│   │   │   ├── knowledge_base.py
│   │   │   └── upload.py
│   │   ├── analytics/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── knowledge_gaps/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── llm.py
│   │   │   ├── database.py
│   │   │   └── auth.py
│   │   ├── models/
│   │   │   ├── request_models.py
│   │   │   ├── response_models.py
│   │   │   ├── auth_models.py
│   │   │   └── knowledge_base_schemas.py
│   │   ├── rag/
│   │   │   ├── chromadb_service.py
│   │   │   ├── chunking.py
│   │   │   ├── embedding.py
│   │   │   └── extractor.py
│   │   ├── dependencies/
│   │   │   └── auth.py
│   │   ├── services/
│   │   │   ├── document_service.py
│   │   │   ├── knowledge_base_service.py
│   │   │   ├── metadata_service.py
│   │   │   ├── query_service.py
│   │   │   └── upload_service.py
│   │   ├── agents/
│   │   │   ├── query_understanding/
│   │   │   ├── retrieval/
│   │   │   ├── response_generation/
│   │   │   ├── clarification/
│   │   │   └── memory/
│   │   ├── voice/
│   │   │   ├── input.py
│   │   │   ├── output.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── transparency/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── test/
│   │   │   └── test_memory.py
│   │   └── orchestration/
│   │       ├── state.py
│   │       ├── nodes.py
│   │       ├── query_router.py
│   │       └── workflow.py
│   ├── chroma_db/
│   ├── metadata/
│   ├── uploads/
│   ├── .env
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatBubble.jsx
│   │   │   ├── CitationDisplay.jsx
│   │   │   ├── FileUploader.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── GroundingEvidenceView.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── VoiceInput.jsx
│   │   │   └── speechtotext.jsx
│   │   ├── hooks/
│   │   │   └── useSpeechRecognition.js
│   │   ├── context/
│   │   │   └── Authcontext.jsx
│   │   ├── pages/
│   │   │   ├── AuthPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── UploadPage.jsx
│   │   │   ├── HistoryPage.jsx
│   │   │   ├── HistoryPage.css
│   │   │   ├── AnalyticsPage.jsx
│   │   │   ├── KnowledgeGapPage.jsx
│   │   │   └── Milestone4.css
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── analytics.js
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .env
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
├── PROJECT_GUIDE.md
└── README.md
```

## Milestone 2 Architecture

The validated Milestone 2 path is:

```text
User Query
    ↓
Query Understanding Agent
    ↓
Query Router
    ↓
Retrieval Agent
    ├── Semantic Search
    ├── Optional Exact Search
    ├── Query-aware Reranking
    └── Low-confidence Filtering
    ↓
Response Generation Agent
    ├── Grounded Answer
    ├── Source Citations
    └── Confidence
    ↓
FastAPI JSON Response
    ↓
React Frontend
    └── Context Inspector
```

## Milestone 3 Architecture

Milestone 3 preserves the M2 retrieval/response path and adds memory, clarification, browser voice, authenticated user workspaces, and a separate general-LLM query route:

```text
User Text / Voice Transcript
            ↓
     Conversation Memory
            ↓
Context-aware Follow-up Resolution
            ↓
    Query Understanding Agent
            ↓
       Query Router
       ↙          ↘
 Clarification    Retrieval
      ↓              ↓
 refined query   ranked chunks
      └──────→ Retrieval
                    ↓
          Response Generation
                    ↓
            Save Conversation
                    ↓
              React Frontend
```

### Clarification route

```text
Ambiguous Query
      ↓
Query Router
      ↓
Clarification Agent
      ↓
Clarification Question
      ↓
User Response
      ↓
Query Refinement
      ↓
Query Understanding
      ↓
Retrieval → Response
```

### Conversation Memory
Conversation turns are associated with a persistent `conversation_id` and stored in PostgreSQL.

A contextual follow-up such as:

```text
What does the Retrieval Agent do?
What about its ranking?
```

can be resolved using the previous conversation before the normal retrieval workflow runs.

### Voice
Voice is browser-based:

```text
Microphone
   ↓
Web Speech API
   ↓
Transcript
   ↓
POST /query
   ↓
Same M3 workflow
   ↓
Answer
   ↓
Browser Speech Synthesis
```

The backend receives text, not microphone audio, in the current architecture.

### Authentication and User Isolation
The current application uses backend JWT authentication instead of frontend-only mock authentication.

- `POST /auth/register` creates a user account and issues a JWT.
- `POST /auth/login` authenticates an existing account and issues a JWT.
- `GET /auth/me` restores/returns the authenticated user profile.
- `POST /auth/logout` completes the logout request while the frontend clears the stored token.
- Passwords are hashed with bcrypt before storage.
- Conversations are owned by a `user_id`, and conversation reads/lists/deletes are restricted to the authenticated owner.
- `AuthPage.jsx`, `Authcontext.jsx`, `App.jsx`, and `Sidebar.jsx` provide the sign-in/sign-up, session restoration, workspace gating, user profile and logout experience.

Required backend JWT settings include:

```env
JWT_SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### General LLM Query Handling
General-knowledge and conversational questions are routed directly to the shared LLM instead of forcing every question through knowledge-base retrieval.

Examples include:

```text
What is a calculator?
What is a machine?
What is artificial intelligence?
What is the capital of Russia?
Who is the Prime Minister of India?
Hello
```

Knowledge-base questions continue through the existing Retrieval Agent and Response Generation path. The system does not use an empty-retrieval result as a generic-LLM fallback, which protects grounded knowledge-base answers.

### Response Transparency
The backend also contains a dedicated transparency service at `backend/app/transparency/`. It converts the existing retrieval result into structured evidence containing the source document, optional page, chunk ID, retrieved content, relevance score and a human-readable citation. It also returns a transparency-specific confidence value and `High`/`Medium`/`Low` confidence level.

`query.py` adds this object to the normal `/query` response under `transparency`; it does not replace the existing `response.confidence` or create a separate retrieval pipeline. No standalone `/transparency` request is required in the current architecture.

The frontend exposes:

- generated answer
- citation references
- source documents
- relevance scores
- confidence
- retrieved chunk IDs
- retrieved chunk content
- semantic score information

## Installation & Setup

The current project uses **PostgreSQL 18** for persistent users, conversations, and conversation messages. **Alembic** manages database schema migrations. ChromaDB remains the vector database for document retrieval.

### Prerequisites

Install the following on the development machine:

- Python 3
- PostgreSQL 18 (or another supported PostgreSQL release)
- pgAdmin 4
- Node.js and npm

For Windows, the PostgreSQL installer can install the PostgreSQL Server, pgAdmin 4, and Command Line Tools. XAMPP/PostgreSQL is **not required** by the current project.

### 1. Create a local PostgreSQL database

Open pgAdmin 4 and connect to your PostgreSQL server.

Create only the database:

```text
Database: querynest
Owner: postgres
Host: localhost
Port: 5432
```

**Do not manually create the application tables.** Alembic creates them.

### 2. Backend virtual environment

From the repository root:

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

The current database dependencies are:

```text
SQLAlchemy
psycopg[binary]
alembic
```

### 4. Configure `backend/.env`

Copy the example file:

```text
backend/.env.example
```

to:

```text
backend/.env
```

Set your local values:

```env
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=<configured-model>

DATABASE_URL=postgresql+psycopg://postgres:<your-postgres-password>@localhost:5432/querynest

JWT_SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

The real `backend/.env` is ignored by Git. Keep secrets out of GitHub.

If a PostgreSQL password contains URL-reserved characters such as `@`, `#`, `:`, `/`, or `?`, URL-encode those characters in `DATABASE_URL`. An easy local-development option is to use a strong password that avoids URL-reserved characters.


### Generate `JWT_SECRET_KEY`

The backend requires a secure random value for `JWT_SECRET_KEY`. Generate a new secret locally and paste the generated value into `backend/.env`.

#### PowerShell

Run:

```powershell
$b = New-Object byte[] 64
$rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
$rng.GetBytes($b)
$rng.Dispose()
[Convert]::ToBase64String($b)
```

Copy the generated Base64 string and set:

```env
JWT_SECRET_KEY=<generated-secret>
```

#### Command Prompt (CMD)

You can also run the PowerShell command directly from CMD:

```cmd
powershell -Command "$b = New-Object byte[] 64; $rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider; $rng.GetBytes($b); $rng.Dispose(); [Convert]::ToBase64String($b)"
```

Copy the generated value into:

```env
JWT_SECRET_KEY=<generated-secret>
```

**Security:** Generate your own secret locally. Do not commit `backend/.env` or the generated JWT secret to GitHub. The repository should contain only the placeholder in `backend/.env.example`.

### 5. Run Alembic migrations

For a **fresh developer database**, run:

```bash
alembic upgrade head
```

This creates the schema:

```text
querynest
└── public
    ├── alembic_version
    ├── users
    ├── conversations
    └── conversation_messages
```

The fresh database starts with zero application rows. Each developer creates their own account through the application.

Check the migration state:

```bash
alembic current
```

The current revision should be shown as the latest `head`.

To check whether SQLAlchemy models and the database schema are synchronized:

```bash
alembic check
```

Expected:

```text
No new upgrade operations detected.
```

### 6. Start FastAPI

From `backend/`:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

The FastAPI startup does **not** create database tables. Schema creation and changes are handled by Alembic.

### 7. Configure and start the frontend

Create:

```text
frontend/.env
```

Example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Do not place `GROQ_API_KEY`, PostgreSQL credentials, JWT secrets, or other backend-only secrets in the frontend environment.

Then:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

### 8. First-run application flow

Once PostgreSQL, Alembic, FastAPI, and the frontend are running:

1. Open the frontend.
2. Register a new account.
3. Sign in.
4. Upload a PDF, DOCX, TXT, or CSV document.
5. Wait for document processing to complete.
6. Start a conversation.
7. Ask a knowledge-base question.
8. Try a contextual follow-up such as `What about its ranking?`.
9. Test an ambiguous query to trigger clarification.
10. Test browser voice input.
11. Inspect citations, confidence, and retrieved chunks in the Context Inspector.

### Database development workflow with Alembic

When a SQLAlchemy model changes:

```bash
alembic revision --autogenerate -m "describe the schema change"
```

Review the generated migration file in:

```text
backend/alembic/versions/
```

Then apply it:

```bash
alembic upgrade head
```

Check:

```bash
alembic current
```

Do not use `Base.metadata.create_all()` as the production schema migration mechanism.

### Existing-data migration note

The repository is designed for **fresh developer databases**. The historical PostgreSQL-to-PostgreSQL migration was a one-time maintainer operation used to move existing development data into PostgreSQL. Team members do not need the old PostgreSQL database or its data.

## PostgreSQL & Alembic Reference

### Database responsibilities

```text
PostgreSQL
├── users
├── conversations
├── conversation_messages
└── alembic_version
```

PostgreSQL stores authentication and conversation-memory data. ChromaDB stores document chunks and embeddings for RAG retrieval. The two systems have separate responsibilities.

### Database connection

The backend reads the database connection from:

```text
backend/.env
```

using:

```env
DATABASE_URL=postgresql+psycopg://postgres:<password>@localhost:5432/querynest
```

### Alembic files

```text
backend/
├── alembic.ini
└── alembic/
    ├── env.py
    └── versions/
        └── 0f628c51b660_initial_schema.py
```

`env.py` loads the existing `backend/.env`; there is no separate `.env` inside the `alembic/` directory.

The initial migration is a real bootstrap migration for a fresh database. The current development database was already stamped at this revision after the PostgreSQL-to-PostgreSQL migration.

### Fresh teammate setup

A teammate should create only the `querynest` database and then run:

```bash
cd backend
alembic upgrade head
```

No manual table creation and no personal data import are required.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create account and issue JWT |
| POST | `/auth/login` | Authenticate user and issue JWT |
| GET | `/auth/me` | Get authenticated user profile |
| POST | `/auth/logout` | Logout request |
| GET | `/` | Health check |
| GET | `/documents` | List indexed documents |
| POST | `/upload` | Upload a document |
| GET | `/upload/status/{job_id}` | Check upload status |
| POST | `/query` | Run the Milestone 3 query workflow |
| DELETE | `/documents/{document_id}` | Delete an indexed document |
| POST | `/conversations` | Create an authenticated user's conversation |
| GET | `/conversations` | List the authenticated user's conversations |
| GET | `/conversations/{conversation_id}` | Get an owned conversation and messages |
| GET | `/conversations/{conversation_id}/context` | Get owned conversation memory context |
| DELETE | `/conversations/{conversation_id}` | Delete an owned conversation |

### `/query` normal request

```json
{
  "query": "What does the Retrieval Agent do?",
  "k": 3
}
```

### `/query` memory-enabled request

```json
{
  "query": "What about its ranking?",
  "k": 3,
  "conversation_id": "<conversation-id>"
}
```

### `/query` clarification follow-up

```json
{
  "query": "The Retrieval Agent",
  "k": 3,
  "conversation_id": "<conversation-id>",
  "clarification_answer": "The Retrieval Agent",
  "clarification_question": "Which agent are you referring to?",
  "original_query": "Tell me more about that."
}
```

### `/query` response

A successful response contains:

```text
success
query
conversation_id
query_understanding
route
route_reason
clarification_required
clarification_question
retrieval
response
transparency
```

The `transparency` object is built from the existing retrieval results and contains structured evidence such as source document, optional page, chunk ID, content, relevance score, citation, transparency confidence and confidence level.

For a normal answer:

```text
response.answer
response.sources
response.confidence
```

For an ambiguity-first response:

```text
clarification_required = true
clarification_question = "..."
```

`response` may be `null` until clarification has been completed.

## Conversation Memory Example

Create a conversation:

```text
POST /conversations
```

Use the returned ID for the first query:

```json
{
  "query": "What does the Retrieval Agent do?",
  "k": 3,
  "conversation_id": "1e7cb423-b494-417d-bacc-2b3ca46ead2b"
}
```

Then use the same ID for the follow-up:

```json
{
  "query": "What about its ranking?",
  "k": 3,
  "conversation_id": "1e7cb423-b494-417d-bacc-2b3ca46ead2b"
}
```

Expected behavior:

```text
First query
    ↓
Retrieval + Answer
    ↓
Stored in PostgreSQL

Second query
    ↓
Memory Context
    ↓
Contextual Query Resolution
    ↓
Retrieval + Answer
    ↓
Stored in PostgreSQL
```

## Voice Input Example

The current frontend does not upload audio to FastAPI. It uses the browser Web Speech API to obtain a transcript, then sends that transcript through the ordinary query API.

Example spoken query:

```text
What does the Retrieval Agent do?
```

The backend receives the equivalent of:

```json
{
  "query": "What does the Retrieval Agent do?",
  "k": 3,
  "conversation_id": "<conversation-id>"
}
```

## Supported File Types

- PDF
- DOCX
- TXT
- CSV


## Milestone 4 — Query Analytics, Knowledge Gap Detection & User-Specific Knowledge Base

Milestone 4 builds on the existing M1–M3 implementation rather than replacing it.

The internship specification requires:
- tracking unanswered and low-confidence queries and common query themes
- knowledge-gap detection
- end-to-end testing across at least three distinct knowledge-base domains
- optimization of retrieval, prompts, routing and voice reliability
- documentation, project report and final demonstration. fileciteturn27file2L155-L165

### M4 Backend

#### Query Analytics

Every processed authenticated query can produce a `QueryAnalytics` record containing:

```text
user_id
conversation_id
query_text
query_type
response_status
confidence_score
response_time
created_at
```

The `/query` endpoint records this telemetry after workflow execution. Analytics persistence is isolated with transaction rollback so a telemetry failure does not break the core M3 query response.

Available endpoints:

```text
POST /analytics/log
GET  /analytics/overview
GET  /analytics/query-types
```

The overview returns:

```text
total_queries
answered_queries
unanswered_queries
average_confidence
average_response_time
```

Query types are aggregated from actual stored analytics records.

#### Knowledge Gap Detection

Knowledge gaps are detected for retrieval queries when the implemented rules identify conditions such as:

```text
unanswered response
zero retrieved chunks
low retrieval/response confidence
```

General LLM queries are deliberately excluded from knowledge-gap creation because they are an explicit M3 route and do not represent missing KB coverage.

Available endpoints:

```text
GET /knowledge-gaps
GET /knowledge-gaps/top
GET /knowledge-gaps/statistics
```

The current implementation does not require a separate gap-resolution API.

#### User-Specific Knowledge Base

M4 introduces:

```text
knowledge_base_documents
```

with ownership through `user_id`.

A document upload follows:

```text
POST /knowledge-base/documents
        ↓
PostgreSQL document record
        ↓
background extraction
        ↓
chunking
        ↓
SentenceTransformer embeddings
        ↓
ChromaDB vectors
        ↓
metadata includes user_id
        ↓
status = completed / failed
```

Available endpoints:

```text
POST   /knowledge-base/documents
GET    /knowledge-base/documents
GET    /knowledge-base/documents/{document_id}
DELETE /knowledge-base/documents/{document_id}
POST   /knowledge-base/search
```

Every document-management operation is restricted to the authenticated user's ownership.

### User-Scoped Retrieval

The existing Retrieval Agent remains the RAG engine. M4 passes `user_id` from `/query` through workflow state to semantic/exact retrieval so ChromaDB can filter on:

```text
user_id == authenticated user
```

This prevents one user's private uploaded vectors from being returned to another user's query.

### M4 Frontend

The integrated frontend adds:

```text
src/pages/AnalyticsPage.jsx
src/pages/KnowledgeGapPage.jsx
src/pages/HistoryPage.jsx
src/pages/HistoryPage.css
src/pages/Milestone4.css
src/services/analytics.js
```

The authenticated workspace navigation now includes:

```text
Upload Documents
AI Chatbot
History & Statistics
Analytics
Knowledge Gaps
```

The Analytics dashboard is connected to the actual backend endpoints and does not use the teammate's earlier synthetic local analytics dataset.

The Query Type Distribution UI displays values in the form:

```text
17 queries · 58.6%
6 queries · 20.7%
3 queries · 10.3%
```

### M4 Runtime Validation

The following runtime sequence validates the integration:

```text
Login
   ↓
Upload user-specific document
   ↓
Wait for INDEXED
   ↓
Ask a question about the document
   ↓
Confirm answer + source
   ↓
Open Analytics
   ↓
Run one more query
   ↓
Refresh Analytics
   ↓
Total query count increases
   ↓
Open Knowledge Gaps
   ↓
Verify backend-detected gap records
```

A separate two-user isolation test should verify:

```text
User A uploads document
User A can retrieve it
User B cannot retrieve it
```

### M4 Database Migrations

The applied migration chain is:

```text
0f628c51b660
      ↓
7c91f9e3a2b4_milestone4_analytics_and_knowledge_gaps
      ↓
5a7a6c2b7c8f_add_user_specific_knowledge_base_
```

Run:

```bash
alembic upgrade head
```

on a fresh PostgreSQL database.

The M4 schema adds:

```text
query_analytics
knowledge_gaps
knowledge_base_documents
```

while preserving the existing M3 tables.

### M4 Requirements Status

```text
Query analytics logging                ✅ implemented
Unanswered tracking                   ✅ implemented
Low-confidence tracking               ✅ implemented
Knowledge-gap detection               ✅ implemented
Analytics dashboard                   ✅ integrated
Knowledge-gap dashboard               ✅ integrated
User-specific KB metadata             ✅ implemented
User-scoped ChromaDB retrieval        ✅ implemented
Three-domain E2E test                  ⚠ requires recorded test evidence
Retrieval/prompt/routing optimization  ⚠ requires recorded evaluation evidence
Voice reliability testing              ⚠ requires recorded evaluation evidence
Final documentation/demo              ✅ implementation documented; demo evidence remains delivery work
```


## Milestone 3 Validation

The current Milestone 3 implementation has been validated with:

- ambiguous query → Clarification Agent routing
- clarification question generation
- persistent conversation IDs
- PostgreSQL-backed conversation storage
- multi-turn conversation history
- contextual follow-up resolution
- `What about its ranking?` being resolved in the context of the previous Retrieval Agent discussion
- clear queries continuing through the existing Retrieval and Response Generation path
- grounded responses with source citations and confidence
- `chunk_id` consistency between retrieval results and response sources
- Context Inspector source-to-chunk mapping
- frontend conversation creation
- frontend memory-enabled query submission
- browser Web Speech API integration in ChatPage
- speech transcript submission through the normal `/query` path
- dedicated transparency object generation from existing retrieval results
- transparency source/chunk evidence and confidence-level mapping
- Conversation Memory integration testing through `backend/app/test/test_memory.py`
- user registration and login against the backend
- JWT-authenticated session restoration via `/auth/me`
- logout and client-side session clearing
- per-user conversation isolation
- general-knowledge queries answered directly by the LLM
- knowledge-base queries remaining on the existing RAG retrieval path
- user-facing upload UI no longer displaying chunk, embedding or vector counts
- general-knowledge questions using the direct LLM route without fabricated KB sources

## Troubleshooting

### Sign in or sign up fails
Verify that FastAPI is running, PostgreSQL is running, the `querynest` database is reachable, and the JWT environment variables are configured. A duplicate email returns a conflict response, while incorrect credentials return an authentication error.

### A user can see another user's conversation
This should not occur in the authenticated implementation. Verify that conversation endpoints depend on the authenticated-user dependency and filter conversation records by `user_id`.

### Send and microphone buttons are disabled
The frontend waits for a backend `conversation_id`. Make sure PostgreSQL is running and `POST /conversations` returns `200 OK`.

### `Can't connect to PostgreSQL server on 'localhost'` / `WinError 10061`
Start PostgreSQL from XAMPP and verify that the configured database exists and that the username/password/port in the backend environment match the local PostgreSQL server.

### Retrieval returns no relevant results
Verify that the intended knowledge-base document is uploaded and indexed into the current ChromaDB before changing retrieval thresholds or reranking logic.

### Voice input does not start
Check browser Web Speech API support and microphone permissions. Voice recognition is performed in the browser, not by FastAPI.


### Analytics page shows unsupported/mock data
Verify that `frontend/src/services/analytics.js` calls the real endpoints:

```text
/analytics/overview
/analytics/query-types
```

Do not restore the earlier local mock analytics fallback.

### Knowledge Gaps page shows unsupported/mock values
Verify that the frontend is using:

```text
/knowledge-gaps
/knowledge-gaps/top
/knowledge-gaps/statistics
```

The current backend does not return the teammate's older `summary/topics/insights` mock contract.

### User-specific document is visible to the wrong account
Verify that:
1. document rows are filtered by `user_id`
2. ChromaDB metadata contains `user_id`
3. semantic and exact retrieval use the user-scoped search helpers
4. `/query` passes the authenticated user ID into workflow state

### User-specific document is uploaded but not retrieved
Verify that the document status is `completed`/`INDEXED` and that the ChromaDB vectors were created with the correct `user_id`.

## Security

Authentication and conversation ownership are enforced in the backend. Passwords are stored as bcrypt hashes, JWT access tokens are validated server-side, and conversations are filtered by the authenticated user ID.

### User-specific Conversation Isolation
Each conversation belongs to one authenticated user through `user_id`. Conversation listing, reading, context loading, turn saving and deletion are scoped to the logged-in user. A conversation owned by another account cannot be accessed through the normal authenticated conversation API.

### Upload UI Presentation
Document ingestion still performs extraction, chunking, embedding and vector storage internally. The frontend no longer exposes the internal processing counts such as `11 chunks`, `11 embeddings`, or `11 vectors`; those implementation details remain backend processing concerns.

Do not commit:

- `backend/.env`
- `frontend/.env`
- real Groq API keys
- PostgreSQL passwords
- other backend-only secrets

Use `.env.example` files for safe placeholder configuration only.

## Documentation

For complete technical documentation, architecture diagrams, implementation details, API flow, RAG pipeline, Milestone 3 workflow, conversation memory, clarification, voice integration, response transparency, testing procedures, and development guidelines, refer to:

- **PROJECT_GUIDE.md** — complete architecture, M1–M4 implementation and validation guidance.
- **README.md** — setup, API, milestone and troubleshooting summary.
