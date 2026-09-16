# AI-Based Knowledge Retrieval Platform with Query Resolution System

## SECTION 1 — PROJECT OVERVIEW

### Project Objective

The objective of this project is to provide an AI-powered Knowledge Retrieval Platform that allows users to upload documents (PDF, DOCX, TXT, CSV, JPG, JPEG, PNG) and interactively query them using a Retrieval-Augmented Generation (RAG) approach. The ingestion layer uses native text extraction where available and PaddleOCR for scanned, handwritten, or image-based content. Milestone 2 extended the Milestone 1 RAG pipeline into a multi-agent query-resolution workflow using Query Understanding, Retrieval, and Response Generation agents coordinated by LangGraph. Milestone 3 extends that workflow with Clarification, Conversation Memory, browser-based Voice Input/Text-to-Speech integration, Response Transparency in the conversational UI, and authenticated user-specific workspaces. The current query layer also supports general-knowledge and conversational questions through a direct LLM route while preserving the existing knowledge-base RAG route. Milestone 4 adds query-level analytics, domain-agnostic common query-theme detection, knowledge-gap detection, a database-backed user-specific knowledge base, user-scoped ChromaDB retrieval, and dedicated frontend dashboards for Analytics and Knowledge Gaps while preserving the M1–M3 workflow.

### Problem Statement

Organizations and individuals often struggle to quickly extract meaningful and relevant information from large repositories of unstructured documents. Traditional keyword-based search is limited and lacks semantic understanding, making it difficult to answer complex queries based on specific proprietary data.

### Why Retrieval-Augmented Generation (RAG) is used

RAG bridges the gap between the internal knowledge base of a large language model and external proprietary data. By storing document chunks in a vector database and retrieving semantically matching chunks at query time, RAG provides grounded context for the AI, reducing hallucinations and ensuring responses are derived from uploaded documents.

### Milestone 1 — Core RAG Platform

Milestone 1 established the foundational Retrieval-Augmented Generation (RAG) infrastructure of the platform. It provides the document ingestion, text extraction, chunking, embedding, vector storage, and baseline semantic retrieval capabilities used by the later milestones.

The Milestone 1 pipeline is:

```text
User Uploads Document
        ↓
Document Extraction
        ↓
Text Chunking
        ↓
SentenceTransformer Embeddings
        ↓
ChromaDB Vector Storage
        ↓
Semantic Retrieval
        ↓
Relevant Context
        ↓
Baseline LLM Response
```

### Milestone 1 Components

- **Document Upload:** Supports PDF, DOCX, TXT, CSV, JPG, JPEG, and PNG files.
- **Document Extraction:** Uses native extraction for text-based documents and a hybrid PDF/image OCR pipeline for scanned, handwritten, and image-based content.
- **Chunking:** Splits extracted documents into smaller text chunks for efficient retrieval.
- **Embedding Generation:** Converts chunks into semantic vector representations using the `all-MiniLM-L6-v2` SentenceTransformer model.
- **Vector Storage:** Stores document chunks and embeddings persistently in ChromaDB.
- **Metadata Persistence:** Maintains document metadata and processing status in PostgreSQL; ChromaDB stores document chunks and embeddings for retrieval.
- **Semantic Retrieval:** Retrieves the most semantically relevant document chunks for a user query.
- **Baseline Querying:** Uses the retrieved context to generate answers grounded in the uploaded knowledge base.

### Milestone 1 RAG Flow

```text
Document
    ↓
Extraction
    ↓
Chunking
    ↓
Embedding
    ↓
ChromaDB
    ↓
Semantic Search
    ↓
Relevant Chunks
    ↓
Answer Generation
```

Milestone 1 provides the core RAG infrastructure that is retained throughout the project. Milestone 2 extends this baseline by introducing Query Understanding, deterministic query routing, Retrieval Agent enhancements, reranking, confidence filtering, Response Generation, and LangGraph orchestration.

### Milestone 2 Multi-Agent Resolution

Milestone 2 built the multi-agent resolution layer on top of the existing RAG infrastructure.

The validated Milestone 2 path is:

```text
User Query
    ↓
Query Understanding Agent
    ↓
Query Router
    ↓
Retrieval Agent
    ↓
Response Generation Agent
    ↓
Grounded Answer + Sources + Confidence
```

### Milestone 3 Extensions
Milestone 3 adds four integrated capabilities:

1. **Clarification Agent** — handles ambiguous queries by generating targeted clarification questions and refining the query after the user responds.
2. **Conversation Memory Agent** — stores conversation turns in PostgreSQL and loads prior context using a `conversation_id`, allowing contextual follow-up queries such as `What about its ranking?`.
3. **Voice Input and Text-to-Speech** — the browser performs speech recognition through the Web Speech API and uses browser speech synthesis for spoken responses. The recognized transcript follows the same `/query` workflow as typed text.
4. **Response Transparency** — the frontend displays answer citations, source documents, relevance/confidence information, and retrieved context chunks through the chat UI and Context Inspector.
5. **Authentication and User Isolation** — users can sign up and sign in through the FastAPI authentication API, receive JWT access tokens, restore authenticated sessions, and access only their own conversations.

### Milestone 3 Query Workflow
The primary integrated workflow is:

```text
User Text / Voice Transcript
            ↓
     Conversation Memory
            ↓
Context-aware Query Resolution
            ↓
    Query Understanding Agent
            ↓
       Query Router
       ↙          ↘
 Clarification    Retrieval
      ↓              ↓
 refined query   ranked chunks
      ↓              ↓
      └────→ Retrieval
                    ↓
          Response Generation
                    ↓
          Grounded Response
                    ↓
            Save Conversation
                    ↓
              React Frontend
```

For an ambiguous query that needs user clarification, the first request ends after the clarification question is produced. The follow-up request includes the clarification information and continues through query refinement, Query Understanding, Retrieval, Response Generation, and memory persistence.

### End-to-End Workflow
1. **Upload:** A user uploads a document via the React frontend.
2. **Extraction & Chunking:** The FastAPI backend extracts text and splits it into smaller chunks.
3. **Embedding:** Chunks are converted into semantic vector embeddings using SentenceTransformer.
4. **Storage:** Embeddings and chunks are stored in ChromaDB, while document metadata and processing status are persisted in PostgreSQL.
5. **Conversation Creation:** The frontend creates a conversation and receives a persistent `conversation_id` from the conversation API.
6. **Querying:** The user submits a natural-language query through the chat interface, either typed or produced by browser speech recognition.
7. **Memory Loading:** The workflow loads previous conversation context when a `conversation_id` is supplied.
8. **Contextual Resolution:** Context-dependent follow-ups can be rewritten into standalone queries before the existing Query Understanding Agent processes them.
9. **Query Understanding:** The Query Understanding Agent normalizes the query, extracts entities/keywords/exact terms, and classifies it.
10. **Routing:** LangGraph uses deterministic routing based on the structured query-understanding result.
11. **General LLM Route:** General-knowledge or conversational queries are routed directly to the shared Groq LLM without knowledge-base retrieval.
12. **Clarification:** Ambiguous queries are routed to the Clarification Agent, which generates a targeted question or refines the query after receiving the user's clarification.
13. **Retrieval:** Knowledge-base queries continue through the existing Retrieval Agent, which performs semantic search and optional exact search, merges candidates, reranks them, filters low-confidence candidates, and returns final context.
14. **Response Generation:** Knowledge-base queries use the existing Response Generation Agent to create grounded answers with source citations and confidence. General LLM responses return without knowledge-base sources.
15. **Conversation Persistence:** Completed user/assistant turns are stored in the PostgreSQL-backed conversation memory layer.
16. **Transparency:** For retrieval-backed answers, the frontend displays citations, source references, relevance/confidence, and exact retrieved chunks.
17. **Voice Output:** The browser can read the returned answer aloud using Speech Synthesis; citation markers are not required in the spoken version.

### Overall System Architecture
The frontend remains a React SPA built with Vite. The backend is a FastAPI application. REST requests enter the API layer, and the `/query` endpoint delegates query orchestration to a LangGraph workflow. The agents remain separated by responsibility. Milestone 1 RAG modules continue to provide embeddings, ChromaDB access, extraction and chunking. Milestone 3 adds a PostgreSQL-backed conversation layer and browser-native voice capabilities.

---

## SECTION 2 — TECHNOLOGY STACK

### Backend
| Technology | Description |
|---|---|
| Python 3 | Core backend language |
| FastAPI | HTTP API framework |
| Uvicorn | ASGI server |
| Pydantic | Request and response validation |
| SQLAlchemy | ORM/database session management for conversation memory |
| Psycopg 3 | PostgreSQL database driver |
| Alembic | Database schema migration and versioning |

### Frontend
| Technology | Description |
|---|---|
| React 19 | UI library |
| Vite | Build tool and development server |
| JavaScript | Frontend language |
| Vanilla CSS | Styling system |
| Web Speech API | Browser speech-to-text |
| Speech Synthesis API | Browser text-to-speech |

### AI / Agent Frameworks
| Technology | Description |
|---|---|
| LangChain | LLM integration and related utilities |
| LangGraph | Multi-agent workflow orchestration |
| langchain-groq | LangChain integration for Groq chat models |
| Sentence Transformers | Semantic embedding generation |

### LLM Configuration
| Technology | Description |
|---|---|
| Groq | LLM provider for Query Understanding, Clarification, contextual query resolution, and Response Generation |
| Configured model | Controlled through `GROQ_MODEL` in `backend/.env` |
| Environment variables | `GROQ_API_KEY` and `GROQ_MODEL` are loaded centrally by `app/core/llm.py` |

### Database
| Technology | Description |
|---|---|
| PostgreSQL | Persistent users, conversations/messages, query analytics, and user-specific knowledge-base document metadata |
| SQLAlchemy | Database ORM/session layer |
| Psycopg 3 | PostgreSQL connectivity |
| PostgreSQL | Persistent users, conversations/messages, query analytics, knowledge-gap records, and uploaded-document metadata/status |

### Vector Database
| Technology | Description |
|---|---|
| ChromaDB | Persistent vector storage and semantic retrieval |

### Embedding Model
| Technology | Description |
|---|---|
| all-MiniLM-L6-v2 | Lightweight SentenceTransformer model used for RAG embeddings |
| Analytics theme embeddings | Separate analytics-only `all-MiniLM-L6-v2` model loaded through `app/analytics/theme_embedding.py`; isolated so the RAG model can be optimized independently |

### Document Processing Libraries
| Technology | Description |
|---|---|
| pypdf | General PDF support and compatibility |
| PyMuPDF | Native PDF text extraction and scanned-page rendering |
| python-docx | DOCX extraction |
| pandas | CSV parsing |
| PaddlePaddle | Deep-learning runtime used by PaddleOCR |
| PaddleOCR | OCR for scanned/handwritten/image-based content |
| Pillow | Image processing |
| OpenCV | Image-processing dependency used by the OCR stack |
| image_filter.py | Filters tiny/repeated DOCX images before OCR |
| langchain-text-splitters | Recursive text chunking |

### Development Tools
| Technology | Description |
|---|---|
| Oxlint | Frontend linting |
| npm | Frontend package management |
| XAMPP | Local PostgreSQL development environment |

---

## SECTION 3 — COMPLETE PROJECT STRUCTURE

```text
AI-Based Knowledge Retrieval Platform with Query Resolution System/
│
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 0f628c51b660_initial_schema.py
│   │   │   ├── 7c91f9e3a2b4_milestone4_analytics_and_knowledge_gaps.py
│   │   │   ├── 5a7a6c2b7c8f_add_user_specific_knowledge_base.py
│   │   │   └── e9b7e767c397_add_user_id_to_knowledge_gaps.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                              # FastAPI application entry point
│   │   │
│   │   ├── api/                                 # HTTP/API routers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                          # Registration, login, session and logout endpoints
│   │   │   ├── documents.py                     # Document management endpoints
│   │   │   ├── health.py                        # Health check endpoint
│   │   │   ├── query.py                         # Main M2/M3/M4 /query endpoint + telemetry logging
│   │   │   ├── conversations.py                 # Authenticated conversation management endpoints
│   │   │   ├── upload.py                        # Legacy/original upload and status endpoints
│   │   │   ├── analytics.py                     # M4 analytics router (where applicable)
│   │   │   └── voice.py
│   │   │
│   │   ├── core/                                # Application configuration, auth, and database setup
│   │   │   ├── __init__.py
│   │   │   ├── config.py                        # Paths and application settings
│   │   │   ├── llm.py                           # Centralized Groq LLM setup
│   │   │   ├── database.py                      # SQLAlchemy engine/session/Base + model registration
│   │   │   └── auth.py                          # Password hashing and JWT helpers
│   │   │
│   │   ├── models/                              # API/data models
│   │   │   ├── __init__.py
│   │   │   ├── request_models.py                # Query + M3/M4 request validation
│   │   │   ├── response_models.py               # API response models
│   │   │   ├── auth_models.py                   # Login/register/profile/token models
│   │   │   └── knowledge_base_schemas.py        # M4 knowledge-base API schemas
│   │   │
│   │   ├── rag/                                 # Milestone 1 RAG infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── chromadb_service.py              # ChromaDB operations
│   │   │   ├── chunking.py                      # Text chunking
│   │   │   ├── embedding.py                     # Embedding generation
│   │   │   └── extractor.py                     # Hybrid native-text + OCR document extraction
│   │   │
│   │   ├── dependencies/                        # FastAPI dependency helpers
│   │   │   └── auth.py                          # Bearer/JWT authenticated-user dependency
│   │   │
│   │   ├── services/                            # Backend business services
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py              # Document management logic
│   │   │   ├── knowledge_base_service.py        # M4 user-specific KB lifecycle and processing
│   │   │   ├── metadata_service.py              # Upload-job progress/status persistence
│   │   │   ├── ocr_service.py                   # PaddleOCR service for OCR processing
│   │   │   ├── query_service.py                 # Milestone 1 baseline retained
│   │   │   └── upload_service.py                # Upload validation/processing pipeline
│   │   │
│   │   ├── agents/                              # AI agents
│   │   │   ├── __init__.py
│   │   │   ├── query_understanding/             # Query analysis and classification
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── classifier.py
│   │   │   │   ├── normalizer.py
│   │   │   │   ├── extractor.py
│   │   │   │   └── schemas.py
│   │   │   │
│   │   │   ├── retrieval/                       # Search, ranking and filtering
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── semantic_search.py
│   │   │   │   ├── exact_search.py
│   │   │   │   └── reranker.py
│   │   │   │
│   │   │   ├── response_generation/             # Grounded answer generation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── prompt_builder.py
│   │   │   │   ├── llm_call_groq.py
│   │   │   │   └── schemas.py
│   │   │   │
│   │   │   ├── clarification/                   # Milestone 3 ambiguity handling
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   └── schemas.py
│   │   │   │
│   │   │   └── memory/                          # Milestone 3 conversation memory
│   │   │       ├── __init__.py
│   │   │       ├── agent.py
│   │   │       └── storage.py
│   │   │
│   │   ├── voice/                               # Milestone 3 voice backend contract
│   │   │   ├── __init__.py
│   │   │   ├── input.py                         # Transcript validation/preparation
│   │   │   ├── output.py                        # Speech-ready response preparation
│   │   │   ├── schemas.py                       # Voice request/response schemas
│   │   │   └── service.py                       # Voice module coordinator
│   │   │
│   │   ├── transparency/                        # Milestone 3 response transparency
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py                       # Transparency response schemas
│   │   │   └── service.py                       # Transparency/evidence builder
│   │   ├── analytics/                           # Milestone 4 Query Analytics + Common Query Themes
│   │   │   ├── __init__.py
│   │   │   ├── models.py                         # QueryAnalytics SQLAlchemy model
│   │   │   ├── schemas.py                        # Analytics + theme response schemas
│   │   │   ├── service.py                        # Query logging and aggregate statistics
│   │   │   ├── theme_embedding.py                # Dedicated analytics-only embedding model
│   │   │   ├── theme_service.py                  # Domain-agnostic semantic theme clustering
│   │   │   └── router.py                         # /analytics endpoints
│   │   │
│   │   ├── knowledge_gaps/                       # Milestone 4 Knowledge Gap Detection
│   │   │   ├── __init__.py
│   │   │   ├── models.py                         # KnowledgeGap SQLAlchemy model
│   │   │   ├── schemas.py                        # Gap schemas
│   │   │   ├── service.py                        # Gap detection and aggregation
│   │   │   └── router.py                         # /knowledge-gaps endpoints
│   │   │
│   │   ├── admin/                                # Admin Dashboard
│   │   │   ├── __init__.py
│   │   │   ├── router.py                         # /admin endpoints + Admin role guard
│   │   │   ├── schemas.py                        # Admin response schemas
│   │   │   └── service.py                        # System-wide admin analytics and summaries
│   │   ├── test/                                 # Application-level tests
│   │   │   └── test_memory.py                    # Conversation memory integration test
│   │   │
│   │   ├── orchestration/                       # LangGraph orchestration
│   │   │   ├── __init__.py
│   │   │   ├── state.py                         # Shared workflow state
│   │   │   ├── nodes.py                         # Workflow node implementations
│   │   │   ├── query_router.py                  # Deterministic route selection
│   │   │   └── workflow.py                      # LangGraph graph construction/runner
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── image_filter.py                  # Filters tiny/repeated DOCX images before OCR
│   │
│   ├── chroma_db/                               # Local ChromaDB data (ignored)
│   ├── metadata/                                # Local metadata/state (ignored)
│   ├── uploads/                                 # Local uploaded files (ignored)
│   ├── .env                                     # Local secrets/config (ignored)
│   ├── .env.example                             # Environment variable template
│   └── requirements.txt                         # Python dependencies
│
├── frontend/
│   ├── public/                                  # Static public assets
│   ├── src/
│   │   ├── assets/                              # Frontend assets
│   │   ├── components/                          # Reusable UI components
│   │   │   ├── ChatBubble.jsx
│   │   │   ├── CitationDisplay.jsx              # If included in integrated UI
│   │   │   ├── FileUploader.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── GroundingEvidenceView.jsx        # If included in integrated UI
│   │   │   ├── Sidebar.jsx                      # Main navigation with Admin-only entry
│   │   │   ├── VoiceInput.jsx                   # Voice UI component, if used
│   │   │   └── speechtotext.jsx                 # Speech helper, if retained
│   │   ├── hooks/
│   │   │   └── useSpeechRecognition.js          # Web Speech API hook
│   │   ├── context/
│   │   │   └── Authcontext.jsx                  # Authentication/session context
│   │   ├── pages/
│   │   │   ├── AuthPage.jsx                     # Sign in / sign up UI
│   │   │   ├── ChatPage.jsx                     # Chat + voice + transparency UI
│   │   │   ├── UploadPage.jsx                   # Document upload UI
│   │   │   ├── AdminDashboard.jsx               # Admin overview with system statistics
│   │   │   ├── AdminUsers.jsx                   # Admin user management/list view
│   │   │   ├── AdminUserDetail.jsx              # Admin user details view
│   │   │   ├── AdminDocuments.jsx               # Admin document management and deletion
│   │   │   ├── AdminAnalytics.jsx               # Admin query analytics and frequent queries
│   │   │   └── AdminDashboard.css               # Admin Dashboard styling
│   │   ├── services/
│   │   │   └── api.js                           # REST API communication, including Admin APIs
│   │   ├── App.css
│   │   ├── App.jsx                              # Existing tab-based app navigation, including Admin views
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .env                                     # Local frontend API URL (ignored)
│   ├── .env.example                             # Frontend environment template
│   ├── .gitignore
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── PROJECT_GUIDE.md
└── README.md
```

### Integration Boundary
The repository contains one authoritative backend under `backend/`. The frontend is under `frontend/` and communicates with the backend through the REST API. The old standalone frontend-side backend copy from the frontend team's source package is not part of the integrated architecture.

### Orchestration Design Decision
Milestone 3 intentionally separates shared workflow state and node logic from the graph definition:

```text
orchestration/
├── state.py
├── nodes.py
├── query_router.py
└── workflow.py
```

`workflow.py` is responsible primarily for graph construction, conditional transitions, compilation, and the public runner. `nodes.py` coordinates agent calls and state updates. Agent business logic remains inside the respective agent packages.

---

## SECTION 4 — HIGH LEVEL ARCHITECTURE

```mermaid
graph TD
    U([User]) --> FE[React Frontend]
    FE --> STT[Web Speech API]
    STT --> FE
    FE --> AUTH[JWT Authentication]
    AUTH --> API[FastAPI API]
    API --> DB[(PostgreSQL Conversation Memory)]
    API --> WF[LangGraph Workflow]
    WF --> MEM[Conversation Memory Agent]
    MEM --> DB
    WF --> QUA[Query Understanding Agent]
    QUA --> RT[Query Router]
    RT --> GEN[General LLM Response]
    RT --> CL[Clarification Agent]
    CL --> QUA
    RT --> RA[Retrieval Agent]
    RA --> SS[Semantic Search]
    RA --> ES[Optional Exact Search]
    RA --> RR[Query-aware Reranker]
    RR --> LF[Low-confidence Filter]
    LF --> RG[Response Generation Agent]
    RG --> LLM[Shared Groq LLM]
    RA --> VDB[(ChromaDB)]
    VDB --> RA
    RG --> WF
    WF --> MEM
    WF --> API
    API --> FE
    FE --> TTS[Browser Speech Synthesis]
```

---

## SECTION 5 — FRONTEND ARCHITECTURE

The React frontend remains responsible for presentation and browser capabilities. Milestone 3 adds microphone interaction, conversation state, clarification display, and response transparency without moving RAG/agent logic into the browser.

### Folder Structure
- `src/components/`: Reusable UI components.
- `src/hooks/`: React hooks such as `useSpeechRecognition.js`.
- `src/pages/`: Page-level screens.
- `src/services/`: REST API communication.
- `src/assets/`: Static media.

### Current Frontend Responsibilities
- `AuthPage.jsx`: Provides sign-in and account-creation forms and displays authentication errors/status.
- `Authcontext.jsx`: Centralizes authenticated user state, JWT/session persistence, sign in, registration, session restoration and logout.
- `ChatPage.jsx`: Sends user questions, maintains the current conversation ID, loads persisted conversations, handles voice transcription, displays responses, clarification questions, citations, confidence and retrieved context.
- `useSpeechRecognition.js`: Uses browser Web Speech API for speech-to-text and returns transcript/listening/error state to `ChatPage`.
- `ChatBubble.jsx`: Displays user/bot messages and source information.
- `UploadPage.jsx`: Uploads documents and manages document status.
- `FileUploader.jsx`: Handles multipart upload and progress. Internal processing stages remain available to the workflow, but chunk, embedding, and vector counts are hidden from the user-facing upload UI.
- `api.js`: Centralizes document, query, and conversation REST calls.

### Voice Input Responsibilities
The frontend microphone flow is browser-based:

```text
Microphone
    ↓
Web Speech API
    ↓
Transcript
    ↓
ChatPage
    ↓
api.sendChatMessage()
    ↓
POST /query
```

The provided `useSpeechRecognition.js` hook checks for `window.SpeechRecognition` / `window.webkitSpeechRecognition`, handles listening state, interim results, language configuration, microphone errors and cleanup. The transcript is delivered through the hook's `onResult` callback.

### Text-to-Speech Responsibilities
Speech synthesis is performed in the browser. Backend voice helpers only prepare clean speech-ready text where applicable; they do not access the microphone or synthesize audio. Citation markers such as `[1]` can be removed from the speech version while the display answer retains citations.

### Conversation State
`ChatPage.jsx` maintains the active `conversation_id`. Opening the chatbot loads the current authenticated user's saved conversations and can restore the most recent conversation. A new chat resets the frontend conversation state; the backend conversation is created when the first real user message is submitted. Subsequent messages use the same `conversation_id`.

### Clarification UI
When `/query` returns:

```text
clarification_required = true
clarification_question = "..."
```

the frontend displays the clarification question instead of attempting to read `response.answer` from a null response object.

### Milestone 3 Integration Note
The integrated frontend communicates only with the FastAPI backend. It does not call Groq, ChromaDB, embeddings, SQLAlchemy, or agent modules directly.

### Frontend-to-Backend Query Flow

```text
ChatPage.jsx
    ↓
frontend/src/services/api.js
    ↓
POST /query
    ↓
FastAPI query.py
    ↓
LangGraph workflow
    ↓
Memory → Query Understanding → Router
                             ↙       ↘
                      Clarification  Retrieval
                             ↓          ↓
                         refinement → Response Generation
                                         ↓
                                  Save Conversation
                                         ↓
                                    JSON response
                                         ↓
                                      ChatPage
```

### Source-to-Context Mapping
`response.sources[*].chunk_id` is matched against `retrieval.results[*].chunk_id` to open the exact retrieved chunk in the Context Inspector. Filename matching remains a fallback when a source does not provide a `chunk_id`.

### Response Transparency
The current conversational UI provides response transparency through:

- Source references associated with the generated answer.
- Per-source relevance information.
- Overall response confidence.
- Retrieved chunk content.
- Chunk ID and metadata in the Context Inspector.
- Semantic score information for inspected chunks.

This is the implemented response-transparency behavior; it is not a separate LLM or retrieval stage.

### Frontend Environment
The frontend uses:

```text
frontend/.env
```

Example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The frontend must never contain `GROQ_API_KEY`, PostgreSQL credentials, or other backend-only secrets.

---

## SECTION 6 — BACKEND ARCHITECTURE

### `app/api/`
The presentation layer. Routers validate HTTP requests and delegate work to services/workflow components.

- `documents.py`: Document listing and deletion endpoints.
- `health.py`: Health endpoint.
- `query.py`: Delegates `/query` to `run_workflow()` and supplies the database session for memory-enabled requests.
- `conversations.py`: Creates, lists, reads and deletes persistent conversations and their messages/context.
- `upload.py`: Upload and upload-status endpoints.

### `app/core/`
- `config.py`: Paths, file limits and application constants.
- `llm.py`: Centralized shared LLM initialization from `backend/.env`.
- `database.py`: SQLAlchemy engine, declarative base and database session dependency.

### Authentication and User Isolation
The authentication layer is implemented as a real backend-backed login/signup flow rather than a frontend-only mock.

#### `app/core/auth.py`
- Hashes passwords with bcrypt.
- Verifies supplied passwords against stored password hashes.
- Creates and decodes JWT access tokens.
- Uses the authenticated user's database ID as the JWT subject.

#### `app/dependencies/auth.py`
- Reads the Bearer access token from the request.
- Decodes and validates the JWT.
- Loads the authenticated `User` from PostgreSQL.
- Returns `401 Unauthorized` for missing/invalid/expired authentication.

#### `app/api/auth.py`
Provides:
- `POST /auth/register` — create an account and issue a token.
- `POST /auth/login` — authenticate an existing account and issue a token.
- `GET /auth/me` — return the authenticated user's profile.
- `POST /auth/logout` — complete the logout request; the frontend removes the stored token because JWT access tokens are stateless.

#### Database ownership
`User` is the parent entity for conversations. Every conversation stores a non-null `user_id` foreign key. Conversation endpoints filter by the authenticated user, so a user can list, read, save turns to, and delete only their own conversations. Attempts to access another user's conversation are rejected as not found/unauthorized by the ownership check.

#### Frontend authentication
`Authcontext.jsx` is the single authentication state provider. `AuthPage.jsx` uses the real backend `/auth/register` and `/auth/login` endpoints. `App.jsx` gates the workspace behind authentication, and `main.jsx` provides `AuthProvider`. The Sidebar exposes the authenticated user's profile and logout action below the AI Chatbot navigation.

#### Authentication environment
The backend `.env` contains JWT configuration alongside the existing Groq and PostgreSQL settings:

```env
JWT_SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

The JWT secret must never be committed to GitHub.

### `app/analytics/`
Milestone 4 analytics is isolated from the core RAG execution path.

- `models.py`: Stores per-query telemetry in `QueryAnalytics`.
- `schemas.py`: Defines analytics request/response schemas and `QueryThemeResponse`.
- `service.py`: Persists query analytics and calculates aggregate metrics.
- `theme_embedding.py`: Loads the dedicated analytics-only `all-MiniLM-L6-v2` model.
- `theme_service.py`: Performs domain-agnostic two-stage semantic clustering, filters trivial conversational inputs, calculates theme-level unanswered/low-confidence metrics, and derives a theme gap score without making Groq/LLM calls.
- `router.py`: Exposes authenticated analytics endpoints, including `/analytics/query-themes`.

The theme-analysis model is deliberately separate from `app/rag/embedding.py`. Both currently use `all-MiniLM-L6-v2`, but changing the RAG embedding model later does not require changing the analytics theme model.

### `app/services/`
- `document_service.py`: Document listing/deletion business logic.
- `metadata_service.py`: Upload-job progress and processing status.
- `ocr_service.py`: PaddleOCR initialization and OCR operations for images and scanned PDF pages.
- ``query_service.py`: Retained as the Milestone 1 baseline for comparison/backward compatibility; it is not the main Milestone 3 orchestration entry point.
- `upload_service.py`: Document ingestion pipeline.

### `app/agents/query_understanding/`
Responsibilities:
- Query normalization.
- Search-query normalization.
- Entity extraction.
- Keyword extraction.
- Exact-term extraction.
- Query classification into factual, procedural, comparative, general, or ambiguous.
- Structured `QueryUnderstandingResult` output.

### `app/agents/retrieval/`
Responsibilities:
- Semantic candidate generation.
- Optional exact candidate generation.
- Candidate merging/deduplication.
- Query-aware relevance ranking.
- Exact-term/keyword evidence scoring.
- Low-confidence filtering.
- Final Top-K context selection.

The Retrieval Agent does not require an LLM API call.

### `app/agents/response_generation/`
Responsibilities:
- Grounded prompt construction.
- Shared Groq LLM invocation.
- Citation extraction.
- Source metadata preservation.
- Retrieval-aware confidence estimation.
- Validated `LLMResponse` output.

### `app/agents/clarification/`
Responsibilities:
- Detect/process clarification-required cases as directed by orchestration.
- Generate focused clarification questions.
- Accept the user's clarification response.
- Produce a refined query suitable for the existing Query Understanding/Retrieval pipeline.

The Clarification Agent owns clarification logic; orchestration only decides when to invoke it and how its result changes workflow state.

### `app/agents/memory/`
Responsibilities:
- Load conversation context using `conversation_id`.
- Store completed user/assistant turns.
- Provide context to contextual follow-up resolution.
- Isolate conversation persistence from the rest of the agent layer.

The memory layer uses SQLAlchemy sessions backed by PostgreSQL. `conversation_id` is the persistent identifier for a conversation.

### `app/voice/`
The Voice folder is a module, not an AI agent. It therefore belongs directly under `app/`, not `app/agents/`.

Responsibilities:
- Validate transcript data received from the browser.
- Prepare transcript text for the existing query workflow.
- Build speech-ready response data.
- Provide voice request/response schemas.

The current integrated frontend uses the transcript as an ordinary `/query` request rather than requiring a separate audio-processing backend. The backend does not perform microphone capture or speech recognition.

### `app/transparency/`
The Response Transparency module is a backend service layer, not an AI agent and not a separate retrieval pipeline. It converts the existing retrieval output into a presentation-ready evidence object.

- `schemas.py`: Defines `SourceChunk` and `TransparencyResponse` models containing source document, optional page, chunk ID, content, relevance score, citation, overall confidence, and confidence level.
- `service.py`: Extracts chunks and metadata from the existing retrieval result, normalizes common content/metadata shapes, generates human-readable citations, calculates transparency confidence from available relevance scores, and assigns `High`, `Medium`, or `Low` confidence levels.
- `__init__.py`: Exposes `build_transparency()` for the API layer.

The service is invoked after the existing M3 workflow completes. `query.py` adds the resulting `transparency` object to the `/query` response while preserving the existing `response` and `retrieval` fields. The transparency service does not replace Response Generation's existing confidence value and does not change retrieval ranking/filtering.

The integrated transparency flow is:

```text
Retrieval Result
      ↓
transparency.service.build_transparency()
      ↓
TransparencyResponse
      ├── sources
      │    ├── document
      │    ├── page
      │    ├── chunk_id
      │    ├── content
      │    ├── relevance_score
      │    └── citation
      ├── confidence
      └── confidence_level
      ↓
query.py
      ↓
`transparency` in `/query` response
      ↓
React Context Inspector / transparency UI
```

There is no mandatory standalone `/transparency` API route in the current integrated architecture. Keeping transparency behind `/query` avoids an unnecessary second client request and keeps the endpoint contract aligned with the existing RAG workflow.

### `app/orchestration/`

#### `state.py`
Defines the shared LangGraph `WorkflowState`, including:
- `query`
- `k`
- `query_analysis`
- `route`
- `route_reason`
- `retrieval_result`
- `response`
- `error`
- `conversation_id`
- `memory_context`
- `clarification_required`
- `clarification_question`
- `clarification_answer`
- `original_query`
- `refined_query`
- `user_id` for authenticated user-scoped retrieval
- internal database session (`_db`)

#### `nodes.py`
Contains orchestration-only node functions:
- `memory_node()`
- `query_understanding_node()`
- `routing_node()`
- contextual follow-up query resolution
- `clarification_node()`
- `retrieval_node()`
- `response_generation_node()`
- `general_response_node()`
- `save_memory_node()`

#### `query_router.py`
Contains deterministic route selection:

```text
factual       → retrieval
procedural    → retrieval
comparative   → retrieval
general       → general LLM
ambiguous     → clarification
```

Unexpected query types have a safe retrieval fallback.

#### `workflow.py`
Builds and compiles the LangGraph workflow and exposes `run_workflow()` with support for:
- `query`
- `k`
- `conversation_id`
- `clarification_answer`
- `clarification_question`
- `original_query`
- authenticated `user_id`
- SQLAlchemy `db` session

The workflow preserves the existing Milestone 2 retrieval and response-generation path and adds memory/clarification branches around it.

---

## SECTION 7 — APPLICATION FLOW

### Application Startup
```mermaid
sequenceDiagram
    participant OS
    participant FastAPI
    participant LLM
    participant EmbeddingModel
    participant ChromaDB
    participant PostgreSQL
    OS->>FastAPI: Run `uvicorn app.main:app --reload`
    FastAPI->>LLM: Load shared Groq configuration
    FastAPI->>EmbeddingModel: Load embedding model when retrieval is initialized
    FastAPI->>ChromaDB: PersistentClient(path)
    FastAPI->>PostgreSQL: SQLAlchemy engine/session configuration
    FastAPI-->>OS: Listening on port 8000
```

### Document Upload & Processing
The Milestone 1 ingestion flow remains unchanged:

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant UploadService
    participant RAG
    User->>Frontend: Selects file
    Frontend->>API: POST /upload
    API->>UploadService: create_upload_job()
    UploadService-->>API: Job ID
    API-->>Frontend: 202 Accepted
    Frontend->>API: Poll upload status
    UploadService->>RAG: extract_document()
    RAG->>RAG: chunk_text()
    RAG->>RAG: embed_chunks()
    RAG->>RAG: add_documents()
    UploadService-->>API: completed
```

### Milestone 3 New Conversation
```mermaid
sequenceDiagram
    participant Frontend
    participant API
    participant PostgreSQL
    Frontend->>API: POST /conversations
    API->>PostgreSQL: Create Conversation
    PostgreSQL-->>API: conversation_id
    API-->>Frontend: conversation_id
```

### Milestone 3 Query Processing
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Memory
    participant Workflow
    participant QUA as Query Understanding
    participant Clarification
    participant RA as Retrieval
    participant RGA as Response Generation
    participant PostgreSQL

    User->>Frontend: Types or speaks query
    Frontend->>API: POST /query + conversation_id
    API->>Workflow: run_workflow(query, conversation_id, db)
    Workflow->>Memory: Load context
    Memory->>PostgreSQL: Read conversation history
    PostgreSQL-->>Memory: Previous turns
    Memory-->>Workflow: memory_context
    Workflow->>Workflow: Contextual query resolution when needed
    Workflow->>QUA: run(resolved query)
    QUA-->>Workflow: QueryUnderstandingResult
    Workflow->>Workflow: route_query()

    alt General query
        Workflow->>Workflow: Route to direct General LLM response
        Workflow-->>API: General answer, no KB sources
    else Ambiguous query
        Workflow->>Clarification: Generate clarification question
        Clarification-->>Workflow: clarification question
        Workflow-->>API: clarification_required=true
        API-->>Frontend: Clarification question
    else Knowledge-base query
        Workflow->>RA: run(QueryUnderstandingResult, k)
        RA-->>Workflow: Ranked/filtered chunks
        Workflow->>RGA: generate_response(question, chunks)
        RGA-->>Workflow: LLMResponse
        Workflow->>Memory: Store completed turn
        Memory->>PostgreSQL: INSERT user + assistant messages
        Workflow-->>API: Final workflow state
        API-->>Frontend: Answer + sources + confidence
    end
```

### Contextual Follow-up Resolution
A context-dependent query can be resolved before normal Query Understanding:

```text
Previous conversation:
User: What does the Retrieval Agent do?
Assistant: The Retrieval Agent performs semantic search...

Current query:
What about its ranking?

Contextual resolution:
What is the ranking process used by the Retrieval Agent?

↓
Existing Query Understanding Agent
↓
Retrieval
↓
Response Generation
```

This preserves the existing Query Understanding Agent interface, which expects a query string.

---

## SECTION 8 — REQUEST FLOW

### Standard typed query
1. Frontend sends a `QueryRequest` through `services/api.js`.
2. FastAPI validates the request.
3. `query.py` calls `run_workflow()` with the query, optional `conversation_id`, clarification fields, and database session.
4. Memory context is loaded when a conversation ID exists.
5. Query Understanding produces structured query information.
6. `query_router.py` selects general LLM, retrieval, or clarification.
7. General queries go directly to the shared Groq LLM; knowledge-base queries return ranked context from the existing Retrieval Agent.
8. Retrieval-backed queries use Response Generation for the grounded answer, citations and confidence.
9. The completed turn is persisted when `conversation_id` exists.
10. `query.py` builds the Response Transparency object from the existing retrieval result; general responses have no knowledge-base transparency evidence.
11. FastAPI returns the final JSON response.

### Voice query
1. Browser microphone captures speech.
2. Web Speech API produces a transcript.
3. `ChatPage.jsx` places the transcript into the normal query input.
4. `api.sendChatMessage()` sends the transcript through `POST /query` with the current conversation ID.
5. The backend follows the same M3 workflow as a typed query.
6. The answer is displayed in the chat.
7. Browser Speech Synthesis can read the answer aloud.

### Clarification query
1. An ambiguous query is submitted.
2. Router selects `clarification`.
3. Clarification Agent generates a question.
4. Frontend displays `clarification_question`.
5. User responds.
6. Frontend resubmits the response with the same conversation ID and clarification information where required.
7. Clarification Agent refines the original query.
8. Refined query returns to Query Understanding → Router → Retrieval → Response Generation.
9. Final turn is saved to memory.

---

## SECTION 9 — FRONTEND COMPONENT FLOW

```text
App
├── Sidebar
└── Main Content
    ├── UploadPage
    │   ├── FileUploader
    │   └── Footer
    └── ChatPage
        ├── ChatBubble list
        ├── Voice / microphone interaction
        ├── Clarification display
        └── Context Inspector
            ├── source document
            ├── chunk ID
            ├── relevance
            ├── semantic score
            └── retrieved chunk content
```

### ChatPage Responsibilities
`ChatPage.jsx` maintains:
- current messages
- current input
- listening state through `useSpeechRecognition.js`
- `conversationId`
- retrieved results
- selected source
- loading state
- speech errors

The page sends the conversation ID through `api.sendChatMessage()` and handles both normal answers and clarification responses.

---

## SECTION 10 — BACKEND ROUTERS

| Router | Method | Route | Input | Purpose |
|---|---|---|---|---|
| Health | GET | `/` | None | Health check |
| Documents | GET | `/documents` | None | List indexed documents |
| Documents | DELETE | `/documents/{id}` | Path `document_id` | Delete indexed document |
| Authentication | POST | `/auth/register` | Registration payload | Create account and issue JWT |
| Authentication | POST | `/auth/login` | Login payload | Authenticate user and issue JWT |
| Authentication | GET | `/auth/me` | Bearer token | Return authenticated user profile |
| Authentication | POST | `/auth/logout` | Bearer token | Complete logout request |
| Query | POST | `/query` | `QueryRequest` | Run the M2/M3 workflow and record M4 analytics/gap telemetry after execution |
| Conversations | POST | `/conversations` | Conversation creation data | Create an authenticated user's conversation and return `conversation_id` |
| Conversations | GET | `/conversations` | Bearer token | List the authenticated user's saved conversations |
| Conversations | GET | `/conversations/{id}` | Path `conversation_id` + Bearer | Get one owned conversation and messages |
| Conversations | GET | `/conversations/{id}/context` | Path `conversation_id` + Bearer | Get owned conversation memory context |
| Conversations | DELETE | `/conversations/{id}` | Path `conversation_id` + Bearer | Delete an owned conversation |
| Upload | POST | `/upload` | Multipart file | Upload document |
| Upload | GET | `/upload/status/{id}` | Path `job_id` | Check upload status |
| Knowledge Base | POST | `/knowledge-base/documents` | Multipart file + Bearer token | Upload a user-specific knowledge-base document; processing starts in background |
| Knowledge Base | GET | `/knowledge-base/documents` | Bearer token | List documents belonging only to the authenticated user |
| Knowledge Base | GET | `/knowledge-base/documents/{id}` | Path `document_id` + Bearer | Read one owned knowledge-base document |
| Knowledge Base | DELETE | `/knowledge-base/documents/{id}` | Path `document_id` + Bearer | Delete one owned document and its Chroma vectors |
| Knowledge Base | POST | `/knowledge-base/search` | Search request + Bearer token | Stand-alone semantic search restricted to the authenticated user's KB |
| Analytics | POST | `/analytics/log` | `QueryAnalyticsCreate` | Persist one query analytics event |
| Analytics | GET | `/analytics/overview` | Bearer token or route configuration | Return aggregate query totals/status/confidence/response-time metrics |
| Analytics | GET | `/analytics/query-types` | Bearer token or route configuration | Return query counts grouped by query type |
| Analytics | GET | `/analytics/query-themes` | Bearer token | Return domain-agnostic semantic query themes and theme-level knowledge-gap signals |
| Knowledge Gaps | GET | `/knowledge-gaps` | Backend route | List detected knowledge gaps |
| Knowledge Gaps | GET | `/knowledge-gaps/top` | Backend route | Return top/repeated knowledge gaps |
| Knowledge Gaps | GET | `/knowledge-gaps/statistics` | Backend route | Return gap aggregate statistics |

The current integrated voice frontend uses `POST /query`; a separate audio-processing endpoint is not required because voice recognition occurs in the browser.

---

## SECTION 11 — SERVICE / AGENT LAYER

### Milestone 1 baseline
`query_service.py` remains available as the original retrieval implementation for comparison and backward compatibility.

### Milestone 2 agent layer
The main query execution path uses the LangGraph workflow rather than calling `query_service.process_query()` directly.

### Milestone 3 additions
The main execution path now adds:

```text
Memory Agent
    ↓
Contextual query resolution
    ↓
Query Understanding
    ↓
Router
    ├── Clarification Agent
    └── Retrieval Agent
              ↓
       Response Generation
              ↓
         Memory Agent
```

This keeps:
- API concerns in `app/api/`
- orchestration concerns in `app/orchestration/`
- agent logic in `app/agents/`
- voice contract logic in `app/voice/`
- database setup in `app/core/database.py`
- RAG infrastructure in `app/rag/`

---

## SECTION 11A — GENERAL LLM QUERY HANDLING

The integrated chatbot supports two distinct answer paths so that general questions do not fail merely because the knowledge base does not contain the requested fact.

### Query Routing

```text
factual / procedural / comparative
                ↓
          Knowledge-base query
                ↓
             Existing RAG

          general query
                ↓
          Shared Groq LLM

         ambiguous query
                ↓
       Clarification Agent
```

### General Query Examples

Queries such as:

```text
What is a calculator?
What is a machine?
What is artificial intelligence?
What is the capital of Russia?
Who is the Prime Minister of India?
Hello
How are you?
```

can be classified as `general` and answered directly by the LLM without calling the knowledge-base Retrieval Agent.

### Knowledge-base Preservation
A query that is intended to use uploaded project/company/document information continues through the existing retrieval path. The system does not use `no retrieval results -> general LLM` as a fallback, because that could cause an unsupported general answer to be presented as a knowledge-base answer.

### General Response Characteristics
- General responses do not fabricate document sources.
- `response.sources` is empty for direct general answers.
- Knowledge-base retrieval statistics are not presented as the basis of a general answer.
- General answers can still be persisted in authenticated conversation memory.

---

## SECTION 11B — DOCUMENT INGESTION & OCR

The ingestion pipeline preserves the original RAG flow while adding OCR where native text extraction is insufficient.

### Hybrid extraction strategy

```text
PDF
 ↓
Native PyMuPDF text extraction
 ↓
Enough readable text?
 ├── Yes → use native text
 └── No  → render page → PaddleOCR → OCR text

DOCX
 ↓
Native paragraph extraction
 ↓
Embedded images
 ↓
Optional image filtering
 ↓
PaddleOCR

JPG / JPEG / PNG
 ↓
PaddleOCR

TXT / CSV
 ↓
Native text/tabular extraction

All extracted content
 ↓
Chunking → Embeddings → ChromaDB
```

### OCR modules

- `app/rag/extractor.py`: Selects the extraction strategy by file type and performs hybrid PDF extraction.
- `app/services/ocr_service.py`: Runs PaddleOCR for rendered PDF pages, standalone images and embedded DOCX images.
- `app/utils/image_filter.py`: Filters tiny or repeated DOCX images before OCR to avoid unnecessary processing.
- `app/services/upload_service.py`: Maintains PostgreSQL document metadata and connects extraction/OCR to the existing chunking, embedding and ChromaDB pipeline.

Normal text-based PDF pages are not forced through OCR. OCR is used as a fallback when a page contains little or no native text. This reduces unnecessary OCR processing while preserving support for scanned and handwritten documents.

## SECTION 12 — RAG PIPELINE

The underlying RAG infrastructure from Milestone 1 is retained:

```mermaid
graph LR
    E[extractor.py] --> OCR[PaddleOCR fallback for scanned/image content]
    OCR --> C[chunking.py]
    E --> C
    C --> EMB[embedding.py]
    EMB --> DB[chromadb_service.py]
    DB --> SR[Semantic Retrieval]
```

### Retrieval Agent Pipeline

```text
QueryUnderstandingResult
        ↓
search_query
        ↓
Semantic Search
        +
Optional Exact Search
        ↓
Merge / Deduplicate
        ↓
Query-aware Reranking
        ↓
Low-confidence Filtering
        ↓
Diversification
        ↓
Top-K Context
```

Milestone 3 does not replace this retrieval pipeline. Clarification and conversation memory feed into the existing pipeline rather than creating a separate RAG implementation.

---

## SECTION 13 — CONVERSATION MEMORY

### Purpose
Conversation Memory allows each user's conversation to be identified by a persistent `conversation_id` and stores user/assistant turns in PostgreSQL.

### Database Flow

```text
Frontend
   ↓
POST /conversations
   ↓
conversation_id
   ↓
POST /query
   ↓
Memory Agent
   ├── get_context()
   └── store_turn()
   ↓
PostgreSQL
```

### Conversation Context
A follow-up query can use previous turns to resolve references such as:
- `it`
- `its`
- `this`
- `that`
- `they`
- `them`
- `the above`
- `the previous answer`

Example:

```text
User: What does the Retrieval Agent do?
Assistant: The Retrieval Agent performs semantic search...

User: What about its ranking?
```

The contextual query-resolution step can turn the follow-up into a standalone query before Query Understanding.

### PostgreSQL Requirements
PostgreSQL must be running before using conversation endpoints or memory-enabled queries. XAMPP can be used to run PostgreSQL locally.

Conversation tables are created automatically at application startup through SQLAlchemy model metadata. No separate table-creation script is required.

### Backward Compatibility
A query without `conversation_id` remains usable as an M2-compatible single-query request. A query with `conversation_id` enables memory features.

---

## SECTION 14 — CLARIFICATION

### Clarification Routing
The Milestone 3 deterministic router uses:

```text
factual       → retrieval
procedural    → retrieval
comparative   → retrieval
general       → general LLM
ambiguous     → clarification
```

### Clarification First Pass

```text
User query
   ↓
Query Understanding
   ↓
query_type = ambiguous
   ↓
Query Router
   ↓
Clarification Agent
   ↓
clarification_question
   ↓
Frontend
```

The workflow terminates that request after producing the clarification question because the user must provide the missing information.

### Clarification Follow-up
The follow-up request carries the relevant clarification information. The Clarification Agent refines the original query, and the workflow sends the refined query back through Query Understanding and the normal retrieval/response path.

### Important Separation
The Clarification Agent owns the question/refinement logic. `query_router.py` only decides whether the query enters retrieval or clarification. `workflow.py`/`nodes.py` only orchestrate the transition.

---

## SECTION 15 — VOICE MODULE

### Architecture
The Voice module is **not an AI agent**. It is a backend contract/helper module directly under `app/voice/`.

The browser performs the actual speech work:

```text
Microphone
    ↓
Browser Web Speech API
    ↓
Transcript
    ↓
Normal POST /query
    ↓
M3 workflow
    ↓
Answer
    ↓
Browser Speech Synthesis API
```

### Backend Voice Responsibilities
- Validate the transcript.
- Normalize/prep the transcript before the normal query pipeline.
- Preserve `conversation_id` when a voice query participates in a conversation.
- Prepare a speech-friendly version of the answer by removing citation markers where needed.

### Frontend Hook
`frontend/src/hooks/useSpeechRecognition.js` handles:
- browser support detection
- microphone start/stop
- interim transcripts
- language selection
- listening state
- microphone/network/no-speech errors
- cleanup on component unmount

### Voice and Memory
A voice query uses the same conversation ID as typed queries. Therefore a user can alternate between text and voice in the same conversation:

```text
Typed query
   ↓
conversation_id = ABC
   ↓
Voice query
   ↓
conversation_id = ABC
   ↓
Memory context is shared
```

### Voice and Clarification
A voice-generated transcript can also enter the clarification path because the transcript is treated as ordinary text by the workflow.

---

## SECTION 16 — RESPONSE TRANSPARENCY

### Purpose
Response Transparency makes the evidence behind an answer inspectable without introducing a separate retrieval or generation pipeline. The Milestone 3 transparency service consumes the same retrieval results already produced by the Retrieval Agent.

### Implemented Transparency
The current `/query` response and conversational UI expose:

```text
Generated Answer
    ↓
Citation References
    ↓
Sources Used
    ↓
Response Confidence
    ↓
Transparency Evidence
    ├── Source Document
    ├── Optional Page
    ├── Chunk ID
    ├── Retrieved Content
    ├── Relevance Score
    └── Human-readable Citation
    ↓
Context Inspector
```

### Transparency Backend Module
The dedicated module is:

```text
backend/app/transparency/
├── __init__.py
├── schemas.py
└── service.py
```

`service.py` accepts the existing retrieval result structure and supports common chunk representations. It extracts:

- source document name from common metadata fields such as `source`, `file_name`, `filename`, or `document`
- optional page number from `page`, `page_number`, or `page_num`
- canonical `chunk_id` from chunk/metadata IDs with a safe fallback when no ID exists
- retrieved content from `page_content`, `content`, or `text`
- relevance score from `score`, `relevance_score`, or `similarity`, normalized to the range 0–1

It then builds a `TransparencyResponse` containing `sources`, `confidence`, and `confidence_level`.

### Transparency Schemas
`schemas.py` defines:

```text
SourceChunk
├── document
├── page
├── chunk_id
├── content
├── relevance_score
└── citation

TransparencyResponse
├── confidence
├── confidence_level
└── sources[]
```

### Confidence Separation
The platform intentionally preserves two related but separate values:

```text
response.confidence
→ existing Response Generation confidence shown with the generated answer

transparency.confidence
→ transparency-service confidence derived from retrieved relevance scores
```

The transparency service does not overwrite the existing Response Generation value.

### Query API Integration
`query.py` remains the single public query endpoint. After `run_workflow()` returns, it calls `build_transparency(retrieval_result)` and appends the resulting object under the `transparency` key. Existing M2/M3 fields such as `response`, `retrieval`, `conversation_id`, `route`, and clarification information remain unchanged.

### Canonical Source Mapping
`chunk_id` remains the canonical identifier connecting retrieval evidence to the generated response and the frontend Context Inspector:

```text
Retrieval Result
      ↕
Response Source
      ↕
Transparency SourceChunk
      ↕
Frontend Context Inspector
```

### Human-readable Citation
When a page number is available, the transparency service creates a citation in the form:

```text
<document>, page <number>
```

When no page number is available, the document name is used as the citation.

### Confidence Level
The transparency service maps its numerical confidence to a simple label:

```text
confidence >= 0.80 → High
confidence >= 0.60 → Medium
otherwise          → Low
```

The confidence-level label is intended for user-facing transparency and is not a guarantee of factual correctness.

### Architectural Decision
The current integrated design does not require a standalone `/transparency` request. Transparency is generated from the already available `/query` workflow result, avoiding duplicated retrieval work.

---

## SECTION 17 — DATA STORAGE

### Document Storage
- `uploads/`: Temporary raw upload storage.
- `chroma_db/`: Persistent ChromaDB vector data containing document chunks and embeddings for retrieval.
- PostgreSQL: Persistent document metadata, ownership, file information, and processing status.

### Conversation Storage
Conversation data is stored in PostgreSQL, with SQLAlchemy managing sessions and ORM persistence.

The storage systems have separate responsibilities:

```text
ChromaDB
→ document chunks + embeddings + retrieval

PostgreSQL
→ users + document metadata/status + conversations + conversation messages + analytics
```

The Conversation Memory Agent does not replace ChromaDB and does not store document embeddings.

---

## SECTION 18 — CONFIGURATION

### Backend Environment

Create:

```text
backend/.env
```

The application and Alembic both use this same file. There is **no separate `.env` inside `backend/alembic/`**.

Example:

```env
GROQ_API_KEY=<your-key>
GROQ_MODEL=<configured-model>

DATABASE_URL=postgresql+psycopg://postgres:<your-postgres-password>@localhost:5432/querynest


JWT_SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### PostgreSQL configuration

The current persistent database is PostgreSQL.

```text
Host: localhost
Port: 5432
Database: querynest
Username: postgres
```

PostgreSQL stores:

```text
users
conversations
conversation_messages
alembic_version
```

ChromaDB remains responsible for vector/document retrieval storage.

### Frontend Environment

Create:

```text
frontend/.env
```

Example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Environment Security

Never commit:

- `backend/.env`
- `frontend/.env`
- Groq API keys
- PostgreSQL passwords
- JWT secrets
- other backend-only secrets

Use `.env.example` files only for safe placeholder configuration.

### Database URL note

The backend uses the SQLAlchemy PostgreSQL URL:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

If the PostgreSQL password contains URL-reserved characters such as `@`, `#`, `:`, `/`, or `?`, encode those characters in the URL.

### Alembic configuration

`backend/alembic/env.py` loads `backend/.env` and uses:

```text
DATABASE_URL
```

`backend/alembic.ini` does not store database credentials.

## SECTION 19 — MODELS

### Query Request
The M3 `QueryRequest` preserves M2 compatibility and supports:

```text
query: string
k: integer = 3
conversation_id: optional string
clarification_answer: optional string
clarification_question: optional string
original_query: optional string
```

This lets the same `/query` endpoint support normal, memory-enabled, and clarification follow-up requests.

### Query Understanding Result

```text
original_query
normalized_query
search_query
query_type
entities
keywords
exact_terms
```

### Retrieval Result

```text
chunk_id
content
metadata
distance
matched_terms
semantic_score
keyword_score
lexical_score
synergy_score
evidence_score
relevance_score
```

`chunk_id` is the canonical retrieved-chunk identifier. `document_id` remains the source document identifier inside metadata.

### Response Generation Result

```text
answer
sources
confidence
```

Each source may preserve:

```text
source
reference
chunk_id
relevance_score
metadata
```

### Voice Request

```text
transcript
conversation_id
language
is_voice
```

### Voice Response

```text
answer
conversation_id
sources
confidence
clarification_required
clarification_question
```

A clean `speech_text` representation may also be prepared for browser speech synthesis.

---

## SECTION 19A — POSTGRESQL DATABASE & ALEMBIC

### Database architecture

The persistent database architecture is:

```text
FastAPI
    ↓
SQLAlchemy
    ↓
Psycopg 3
    ↓
PostgreSQL
```

The current application tables are:

```text
users
conversations
conversation_messages
```

with the ownership relationships:

```text
users.id
   ↓
conversations.user_id

conversations.id
   ↓
conversation_messages.conversation_id
```

### Why Alembic is used

Alembic is the database schema migration tool for this project. It is the source of truth for schema changes after the initial baseline.

FastAPI startup does not create or modify database tables.

### Alembic project structure

```text
backend/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    ├── README
    └── versions/
        ├── 0f628c51b660_initial_schema.py
        ├── 7c91f9e3a2b4_milestone4_analytics_and_knowledge_gaps.py
        ├── 5a7a6c2b7c8f_add_user_specific_knowledge_base.py
        └── e9b7e767c397_add_user_id_to_knowledge_gaps.py
```

### Initial migration

The revision:

```text
0f628c51b660
```

is the initial schema migration and creates:

```text
users
conversations
conversation_messages
```

for a fresh database.

The migration contains the schema definition only; it does **not** contain application seed data.

The existing PostgreSQL development database was migrated from the historical PostgreSQL database and then stamped at this revision. Its existing application rows are therefore preserved without being re-created.

### Fresh developer database

For a new teammate:

1. Install PostgreSQL and pgAdmin 4.
2. Create an empty database named `querynest`.
3. Create local `backend/.env`.
4. Install Python dependencies.
5. Run:

```bash
cd backend
alembic upgrade head
```

6. Start FastAPI:

```bash
uvicorn app.main:app --reload
```

7. Start the React frontend.
8. Register a new account.

No manual SQL table creation is required.

### Alembic commands

Check the current revision:

```bash
alembic current
```

Show migration history:

```bash
alembic history
```

Check for model/schema differences:

```bash
alembic check
```

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe the change"
```

Apply all pending migrations:

```bash
alembic upgrade head
```

Move to a specific revision only when intentionally performing a controlled migration:

```bash
alembic upgrade <revision>
```

### Reviewing autogenerated migrations

Never blindly run an autogenerated migration.

After:

```bash
alembic revision --autogenerate -m "describe the change"
```

open the generated file in:

```text
backend/alembic/versions/
```

and review the `upgrade()` and `downgrade()` operations before applying them.

### Database migration history

The project previously used PostgreSQL for conversation persistence during earlier development. The application has since been migrated to PostgreSQL.

The one-time historical PostgreSQL-to-PostgreSQL migration was performed by a maintainer. It transferred existing development data into PostgreSQL and corrected the `conversation_messages.id` sequence.

That historical migration is **not part of normal teammate onboarding**. A fresh teammate database contains no application data.

### Important database rules

- Do not manually create application tables on a fresh developer database.
- Do not commit `backend/.env`.
- Do not put database passwords in `alembic.ini`.
- Do not use `Base.metadata.create_all()` as the production schema-migration mechanism.
- Keep the Alembic migration files under version control.
- Each developer may use their own local PostgreSQL `querynest` database.
- Application data is local to each database unless an intentional shared environment is configured.


## SECTION 20 — API DOCUMENTATION

| Method | Route | Purpose | Request Body / Input |
|---|---|---|---|
| GET | `/` | Health Check | None |
| GET | `/documents` | List indexed documents | None |
| DELETE | `/documents/{id}` | Delete indexed document | Path parameter |
| POST | `/query` | Run Milestone 3 workflow | `QueryRequest` |
| POST | `/conversations` | Create conversation | Optional conversation data |
| GET | `/conversations` | List conversations | None |
| GET | `/conversations/{id}` | Get conversation messages | Path parameter |
| GET | `/conversations/{id}/context` | Get memory context | Path parameter |
| DELETE | `/conversations/{id}` | Delete conversation | Path parameter |
| POST | `/upload` | Upload document | Multipart form-data |
| GET | `/upload/status/{id}` | Check upload status | Path parameter |

### `/query` Normal Request

```json
{
  "query": "What does the Retrieval Agent do?",
  "k": 3
}
```

### `/query` Memory Request

```json
{
  "query": "What about its ranking?",
  "k": 3,
  "conversation_id": "<conversation-id>"
}
```

### `/query` Clarification Follow-up

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

### `/query` Response
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

The `transparency` object is built from the existing retrieval result and preserves source evidence without changing the core M2/M3 retrieval or response-generation path.

For a normal resolved query, `response` contains:

```text
answer
sources
confidence
```

For a clarification-first response, `clarification_required` is true and `clarification_question` contains the next question. `response` may be `null` because no final RAG answer has been generated yet.

---

## SECTION 21 — DOCUMENT PROCESSING LIFECYCLE

```mermaid
graph TD
    A[Upload Endpoint] --> B[Validation]
    B --> C[Save Temporary File]
    C --> D[Extraction]
    D --> E[Chunking]
    E --> F[SentenceTransformer Embedding]
    F --> G[ChromaDB]
    G --> H[PostgreSQL Document Metadata/Status]
    H --> I[Processing Completed]
```

---

## SECTION 22 — MILESTONE 3 QUERY LIFECYCLE

```mermaid
graph TD
    A[User Text or Voice Transcript] --> B[Conversation Memory]
    B --> C[Contextual Follow-up Resolution]
    C --> D[Query Understanding Agent]
    D --> E[Query Router]
    E -->|ambiguous| F[Clarification Agent]
    F --> G[Clarification Question]
    G --> H[User Clarification]
    H --> I[Refined Query]
    I --> D
    E -->|clear| J[Retrieval Agent]
    J --> K[Semantic Search]
    J --> L[Optional Exact Search]
    K --> M[Merge + Rerank]
    L --> M
    M --> N[Low-Confidence Filtering]
    N --> O[Top-K Context]
    O --> P[Response Generation Agent]
    P --> Q[Grounded Answer + Sources + Confidence]
    Q --> R[Save Conversation Memory]
    R --> S[FastAPI JSON]
    S --> T[React Frontend]
    T --> U[Browser Speech Synthesis]
```

---

## SECTION 23 — VALIDATION / TESTING

### Query Understanding
Validated with factual, procedural, comparative and ambiguous classification scenarios and structured outputs containing query type, keywords and exact terms.

### Retrieval Agent
Validated with:
- identifier/entity queries such as `What is the email of Name_1?`
- unsupported queries where the knowledge base contains no relevant policy/information
- generic project-document questions such as `What does the Retrieval Agent do?`
- semantic-only queries where `exact_terms = []`

### Response Generation
Validated with:
- grounded answer generation
- source citation extraction
- real chunk IDs and metadata
- retrieval-aware confidence

### Clarification
Validated with an ambiguous query such as:

```text
Tell me more about that.
```

The workflow returns:

```text
route = clarification
clarification_required = true
clarification_question = <generated question>
```

### Conversation Memory
Validated end-to-end with a persistent `conversation_id` and a contextual follow-up:

```text
User:
What does the Retrieval Agent do?

Assistant:
The Retrieval Agent performs semantic search...

User:
What about its ranking?
```

The follow-up was contextually resolved into a standalone query equivalent to:

```text
What is the ranking process used by the Retrieval Agent?
```

The refined query was classified as factual, routed to retrieval, answered with relevant PDF chunks, and returned with citations and confidence.

### Database Memory
Conversation tables are created and evolved through Alembic migrations. FastAPI startup does not create database tables. Memory-enabled API queries were validated using the same conversation ID across multiple requests.

### Frontend + Backend Integration
Validated end-to-end through the React frontend:
- conversation creation
- typed query submission
- persistent `conversation_id`
- contextual follow-up queries
- generated answer display
- source citations
- confidence display
- retrieved chunks in Context Inspector
- voice microphone UI and transcript integration
- browser-based voice input path into the normal query API

### Response Transparency
Validated that:
- the transparency service consumes the existing retrieval result without changing retrieval behavior
- source document, optional page, chunk ID, retrieved content and relevance information are exposed as transparency evidence
- human-readable citations are generated from available source metadata
- transparency confidence and confidence level are returned separately from the existing response confidence
- the `/query` response includes a dedicated `transparency` object without removing existing M2/M3 fields
- the Context Inspector can continue to inspect the corresponding retrieved chunk

### New agent
Create a new package under `app/agents/` with its own implementation and schemas.

### New orchestration behavior
Modify `app/orchestration/query_router.py`, `nodes.py`, `state.py`, or `workflow.py` as appropriate. Do not add agent business logic to FastAPI routers.

### New API endpoint
Add a router under `app/api/` and keep it focused on HTTP/database dependency concerns.

### New LLM configuration
Update `app/core/llm.py` / `.env` rather than initializing provider credentials inside individual agents.

### New frontend API integration
Add the API wrapper to `frontend/src/services/api.js`.

### New browser capability
Keep microphone and browser speech synthesis logic in the frontend. Backend code should receive text transcripts rather than browser-specific audio/session objects.

### Database changes
Update the SQLAlchemy model layer and create an Alembic migration. Apply schema changes with `alembic upgrade head`; do not use application startup to create tables.

---

## SECTION 26 — CODING STANDARDS

- FastAPI routers remain thin.
- `workflow.py` contains graph construction and public orchestration entry points, not agent business logic.
- `nodes.py` coordinates agents and state transitions.
- `query_router.py` contains deterministic routing.
- Each AI agent owns its domain logic.
- `app/voice/` is a module, not an agent package.
- `app/core/database.py` owns SQLAlchemy session/engine setup.
- `app/core/llm.py` owns shared LLM initialization.
- Absolute Python imports begin with `app.`.
- Python uses `snake_case`; classes use `PascalCase`.
- React components use `.jsx`; hooks use `.js`/`.jsx` according to project convention.
- Secrets are stored in `.env` and never committed.
- Do not duplicate backend implementations inside `frontend/`.

---

## SECTION 27 — SETUP INSTRUCTIONS

### Backend prerequisites

Install:

```text
Python 3
PostgreSQL 18
pgAdmin 4
```

Node.js/npm are required for the frontend.

For Windows, PostgreSQL Server, pgAdmin 4, and Command Line Tools are recommended. XAMPP/PostgreSQL is not required by the current project.

### Backend setup

1. Create the Python environment:

Windows:

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

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create an empty PostgreSQL database in pgAdmin:

```text
Database: querynest
Owner: postgres
Host: localhost
Port: 5432
```

Do not manually create `users`, `conversations`, or `conversation_messages`.

4. Create the local environment file:

```text
backend/.env
```

Example:

```env
GROQ_API_KEY=<your-key>
GROQ_MODEL=<configured-model>

DATABASE_URL=postgresql+psycopg://postgres:<your-postgres-password>@localhost:5432/querynest


JWT_SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

5. Run the initial/future schema migrations:

```bash
alembic upgrade head
```

6. Verify the migration state:

```bash
alembic current
```

Expected on a newly provisioned database:

```text
5a7a6c2b7c8f (head)
```

7. Check that the models and database schema agree:

```bash
alembic check
```

Expected:

```text
No new upgrade operations detected.
```

8. Start FastAPI:

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

### Frontend setup

1. Create:

```text
frontend/.env
```

2. Add:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

3. Install and run:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

### First-run database behavior

A fresh teammate database has:

```text
users                    0 rows
conversations            0 rows
conversation_messages   0 rows
```

after `alembic upgrade head`.

The teammate should then register a new user through the application. No application data from another developer is copied into the new database.

### Application startup responsibility

FastAPI startup does not create database tables. Alembic owns schema management.

```text
Developer changes SQLAlchemy model
            ↓
alembic revision --autogenerate
            ↓
Review migration
            ↓
alembic upgrade head
            ↓
PostgreSQL schema updated
```

## SECTION 28 — RECOMMENDED END-TO-END TEST SEQUENCE

### Fresh PostgreSQL developer setup

1. Start PostgreSQL.
2. Confirm the local `querynest` database exists.
3. Confirm `backend/.env` points to PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://postgres:<your-postgres-password>@localhost:5432/querynest
```

4. Run:

```bash
cd backend
alembic upgrade head
```

5. Confirm:

```bash
alembic current
```

shows:

```text
5a7a6c2b7c8f (head)
```

6. Run:

```bash
alembic check
```

7. Start FastAPI:

```bash
uvicorn app.main:app --reload
```

8. Start the React frontend.
9. Open the application and register a new account.
10. Confirm sign in and session restoration.
11. Upload the project PDF or another supported document.
12. Wait for document processing to complete.
13. Ask a knowledge-base question:

```text
What does the Retrieval Agent do?
```

14. Confirm answer, citations, confidence and source chunks.
15. Ask:

```text
What about its ranking?
```

16. Confirm the follow-up remains in the same conversation and uses prior memory.
17. Ask:

```text
Tell me more about that.
```

18. Confirm that a clarification question is displayed.
19. Test microphone input and verify the browser transcript appears in the chat.
20. Submit the voice transcript through `/query`.
21. Use the Context Inspector to inspect a retrieved chunk.
22. Ask a general question such as:

```text
What is a calculator?
```

23. Confirm the general question is handled by the direct LLM route without fabricated knowledge-base sources.
24. Test a knowledge-base question and confirm Retrieval + Response Generation are used.
25. Create two accounts and verify each account can see only its own conversations.
26. Sign out and verify the protected workspace requires authentication.
27. In pgAdmin, verify the PostgreSQL tables and application rows.

### Database verification queries

For a local PostgreSQL `querynest` database:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM conversations;
SELECT COUNT(*) FROM conversation_messages;
SELECT COUNT(*) FROM query_analytics;
SELECT COUNT(*) FROM knowledge_gaps;
SELECT COUNT(*) FROM knowledge_base_documents;
```

Check Alembic state:

```sql
SELECT * FROM public.alembic_version;
```

Check for broken foreign-key references:

```sql
SELECT COUNT(*) AS orphan_conversations
FROM public.conversations c
LEFT JOIN public.users u ON u.id = c.user_id
WHERE u.id IS NULL;
```

Expected:

```text
0
```

Check for orphaned messages:

```sql
SELECT COUNT(*) AS orphan_messages
FROM public.conversation_messages m
LEFT JOIN public.conversations c
    ON c.id = m.conversation_id
WHERE c.id IS NULL;
```

Expected:

```text
0
```

### Team onboarding verification

A new teammate should be able to complete the project setup with:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

and a separate frontend terminal:

```bash
cd frontend
npm install
npm run dev
```

No manual SQL table creation is part of the onboarding procedure.


---

## SECTION 28A — MILESTONE 4: QUERY ANALYTICS, KNOWLEDGE GAP DETECTION, AND USER-SPECIFIC KNOWLEDGE BASE

Milestone 4 extends the validated M3 platform without replacing the existing multi-agent, memory, clarification, voice, transparency, authentication, or RAG workflow.

The internship project specification defines Milestone 4 as:
1. Query Analytics and Knowledge Gap Detection — track unanswered queries, low-confidence responses, and common query themes to identify knowledge-base gaps.
2. End-to-end testing across a minimum of three distinct knowledge-base domains.
3. Optimization of retrieval quality, prompt design, agent routing accuracy, and voice interaction reliability.
4. Technical documentation, project report, and final demonstration. fileciteturn27file2L155-L165

### 28A.1 M4 Backend Components

The following backend modules were added while preserving the M1–M3 architecture:

```text
backend/app/
├── analytics/
│   ├── models.py
│   ├── schemas.py
│   ├── service.py
│   └── router.py
│
├── knowledge_gaps/
│   ├── models.py
│   ├── schemas.py
│   ├── service.py
│   └── router.py
│
├── api/
│   └── knowledge_base.py
│
├── services/
│   └── knowledge_base_service.py
│
└── models/
    └── knowledge_base_schemas.py
```

`core/models.py` was extended with the SQLAlchemy `KnowledgeBaseDocument` model while preserving the existing `User`, `Conversation`, and `ConversationMessage` models.

### 28A.2 Query Analytics

`QueryAnalytics` stores one telemetry record per processed query.

Core fields include:

```text
id
user_id
conversation_id
query_text
query_type
response_status
confidence_score
response_time
created_at
```

The backend query endpoint records the authenticated user's ID, original query, classified query type, answered/unanswered status, confidence score, and response time. A clarification-only request is recorded as `unanswered`, because it has not yet produced a resolved answer.

The M4 telemetry operation is deliberately isolated from the core query path. If analytics persistence fails, the code rolls back the telemetry transaction so that the already-working M3 query response is not taken down by an analytics problem.

This implements the required query logging, low-confidence/unanswered tracking, and statistics foundation.

#### Common Query Themes

Milestone 4 also analyzes the authenticated user's stored `QueryAnalytics` rows for recurring semantic themes. This is a separate analytics concern and does not participate in document retrieval or response generation.

```text
QueryAnalytics rows for current user
        ↓
analytics-only all-MiniLM-L6-v2
        ↓
Initial semantic/lexical clustering
        ↓
Centroid-based second-pass cluster merging
        ↓
Domain-agnostic theme labels
        ↓
Unanswered + low-confidence metrics
        ↓
Theme gap score
```

The theme detector contains no predefined AI, finance, healthcare, education, legal, or other domain topic lists. Themes are derived from the observed query clusters.

Trivial conversational inputs such as `yes`, `ok`, `thanks`, and `hello` are ignored for theme analysis. They remain available in normal query analytics.

Current generic tuning parameters are:

```text
PAIR_THRESHOLD = 0.62
BRIDGE_THRESHOLD = 0.56
LEXICAL_THRESHOLD = 0.22
LOW_CONFIDENCE_THRESHOLD = 0.50
GAP_SCORE_THRESHOLD = 0.35
MIN_COMMON_THEME_QUERIES = 2
```

A theme-level knowledge gap is reported only when a theme contains at least two meaningful queries and its calculated gap score reaches the configured threshold. Individual one-off problematic queries remain handled by the existing Knowledge Gap Detection module.

The theme service makes **no Groq/LLM request**. It uses only the dedicated analytics embedding model, so refreshing the Analytics dashboard does not consume additional Groq API requests for theme analysis.

Endpoint:

```text
GET /analytics/query-themes
```

Response fields:

```text
theme
query_count
query_share_pct
unanswered_count
low_confidence_count
average_confidence
gap_score
knowledge_gap
representative_query
queries
```

### 28A.3 Analytics API

```text
POST /analytics/log
GET  /analytics/overview
GET  /analytics/query-types
GET  /analytics/query-themes
```

`GET /analytics/overview` provides:

```text
total_queries
answered_queries
unanswered_queries
average_confidence
average_response_time
```

`GET /analytics/query-types` returns query counts grouped by the stored `query_type`.

The current frontend Analytics page transforms these real backend values into:

```text
Total Queries
Answered
Knowledge Gaps / Unanswered
Average Confidence
Average Response Time
Query Type Distribution
Answer Rate
```

The frontend no longer relies on the earlier teammate mock analytics payload. The teammate's original `analytics.js` contained locally generated values and synthetic trends; the integrated M4 frontend uses the real backend analytics contract instead. 

### Analytics Theme Flow

The common-theme feature remains outside the core RAG path:

```text
Authenticated Query
        ↓
QueryAnalytics
        ↓
GET /analytics/query-themes
        ↓
Analytics-only all-MiniLM-L6-v2
        ↓
Domain-agnostic clustering
        ↓
Common Query Themes
        ↓
Theme-level gap signals
```

RAG retrieval continues to use `app/rag/embedding.py` and ChromaDB independently.

### 28A.4 Knowledge Gap Detection

Knowledge-gap detection runs from the retrieval path rather than from general-knowledge LLM requests.

Current detection logic marks a retrieval request as a gap when one or more of the implemented detection conditions is satisfied, including:

```text
unanswered response
OR zero retrieved chunks
OR confidence below the configured threshold
```

Detected gap records contain the query text, query type, reason, confidence score, occurrence information, and timestamps as supported by the implemented model/schema.

Repeated occurrences of the same query are accumulated through the knowledge-gap service instead of being treated as unrelated independent gap definitions.

General LLM queries are intentionally excluded from knowledge-gap creation because a direct LLM route is an explicit M3 behavior and should not be interpreted as missing KB coverage.

### 28A.5 Knowledge Gap API

The current M4 dashboard consumes:

```text
GET /knowledge-gaps
GET /knowledge-gaps/top
GET /knowledge-gaps/statistics
```

The implementation does not require a gap-resolution endpoint. No `PATCH /knowledge-gaps/{id}/resolve` operation is part of the current internship scope.

The dashboard displays backend-detected gap records with fields such as:

```text
Query
Type
Reason
Confidence
Occurrences
Detected
```

### 28A.6 User-Specific Knowledge Base

Milestone 4 adds a second, authenticated document-management path specifically for private per-user knowledge bases.

The main database table is:

```text
knowledge_base_documents
```

Core fields:

```text
id
user_id
filename
original_filename
file_type
file_size
status
created_at
updated_at
```

The document row belongs to the authenticated user through `user_id`.

The ingestion service:
1. Validates the uploaded file.
2. Saves a temporary local copy.
3. Creates a PostgreSQL `KnowledgeBaseDocument` record with `processing` status.
4. Extracts text using the existing M1 extractor.
5. Chunks the text using the existing M1 chunker.
6. Generates embeddings using the existing SentenceTransformer infrastructure.
7. Stores vectors in ChromaDB with metadata containing:
   - `document_id`
   - `filename`
   - `chunk_index`
   - `user_id`
8. Updates PostgreSQL status to `completed` or `failed`.
9. Cleans up the temporary uploaded file.

### 28A.7 User-Specific Knowledge Base API

```text
POST /knowledge-base/documents
GET  /knowledge-base/documents
GET  /knowledge-base/documents/{document_id}
DELETE /knowledge-base/documents/{document_id}
POST /knowledge-base/search
```

All user-specific document operations use the authenticated user identity.

For example, listing documents applies:

```text
KnowledgeBaseDocument.user_id == current_user.id
```

Deleting a document first removes its user-scoped Chroma vectors and then removes the PostgreSQL metadata row.

The stand-alone search endpoint also filters ChromaDB by the authenticated `user_id`.

### 28A.8 User-Specific Retrieval Integration

M4 does not create a second RAG engine.

The existing M2/M3 retrieval pipeline remains:

```text
Query Understanding
       ↓
Semantic Search
       +
Optional Exact Search
       ↓
Merge
       ↓
Rerank
       ↓
Low-confidence Filtering
       ↓
Top-K Context
       ↓
Response Generation
```

The M4 change is that authenticated requests now carry the current `user_id` through workflow state.

```text
FastAPI /query
      ↓
run_workflow(..., user_id=current_user.id)
      ↓
WorkflowState.user_id
      ↓
RetrievalAgent
      ↓
Semantic / Exact search
      ↓
ChromaDB filter:
user_id == authenticated user
```

The retrieval modules retain backward compatibility: when no user ID is supplied, the legacy shared search functions remain available; authenticated application queries use the user-scoped functions.

This prevents one authenticated user's uploaded vectors from being retrieved for another user.

### 28A.9 User-Isolation Validation

The user-specific KB implementation was validated with two authenticated users:

```text
User A
  uploads document
      ↓
User A /knowledge-base/documents → document visible
User A /query → document retrievable

User B
  /knowledge-base/documents → empty for User A's document
  /knowledge-base/search → no User A results
  /query → User A document not retrieved
```

This validates isolation at both the document metadata and vector-retrieval levels.

### 28A.10 M4 Frontend Integration

The frontend now includes:

```text
src/pages/AnalyticsPage.jsx
src/pages/KnowledgeGapPage.jsx
src/pages/HistoryPage.jsx
src/pages/HistoryPage.css
src/pages/Milestone4.css
src/services/analytics.js
```

The existing application navigation was extended with:

```text
Upload Documents
AI Chatbot
History & Statistics
Analytics
Knowledge Gaps
```

`App.jsx` mounts the M4 pages while preserving the existing Upload, Chat, Auth and History functionality.

The updated `api.js` retains compatibility aliases for the earlier frontend document methods while adding the authenticated `/knowledge-base/*` API.

`Authcontext.jsx` remains the central authentication provider. During a normal login attempt, its request does not toggle the global initial-session `loading` state, preventing the temporary “Loading QueryNest… / Verifying your session” screen from obscuring login errors. Initial JWT session restoration still uses the loading screen.

The Analytics UI uses real backend data. It displays query totals, query-type distribution, and domain-agnostic common query themes derived from the authenticated user's stored analytics. It does not display synthetic daily trends or unsupported grounding percentages.

### 28A.11 M4 Database Migrations

The M4 database work was applied through Alembic.

Migration chain:

```text
0f628c51b660
      ↓
7c91f9e3a2b4_milestone4_analytics_and_knowledge_gaps
      ↓
5a7a6c2b7c8f_add_user_specific_knowledge_base_
      ↓
e9b7e767c397_add_user_id_to_knowledge_gaps
```

The first M4 migration adds the analytics and knowledge-gap tables.

The subsequent migration adds:

```text
knowledge_base_documents
```

The current development database was successfully upgraded with:

```bash
alembic upgrade head
```

and the resulting schema contains the M3 tables plus the M4 analytics, gap-detection, and user-specific KB tables.

### 28A.12 M4 End-to-End Flow

```text
Authenticated User
        ↓
React Upload / Chat
        ↓
FastAPI
        ├── User-specific KB APIs
        │       ↓
        │   PostgreSQL metadata
        │       +
        │   ChromaDB user-scoped vectors
        │
        └── POST /query
                ↓
          Existing M3 Workflow
                ↓
        Memory / Context Resolution
                ↓
          Query Understanding
                ↓
             Query Router
          ↙       ↓        ↘
 General LLM  Clarification  Retrieval
                              ↓
                     User-scoped RAG
                              ↓
                    Response Generation
                              ↓
                      Save Conversation
                              ↓
                    M4 Telemetry Logging
                         ↙          ↘
                 Query Analytics   Gap Detection
                         ↓              ↓
                 Analytics UI    Knowledge Gap UI
```

### 28A.13 M4 Frontend Validation

The integrated M4 frontend was validated through the following runtime flow:

```text
Login
  ↓
Upload a supported document
  ↓
Wait until INDEXED
  ↓
Ask a question about the uploaded document
  ↓
Verify grounded answer + source
  ↓
Open Analytics
  ↓
Verify query count changes after another query
  ↓
Open Knowledge Gaps
  ↓
Verify detected historical gap records
```

A successful analytics check is demonstrated when a new chatbot query increases the total query count and, for an answered request, the answered-query count also increases. Repeated or semantically related queries should also be reflected by `GET /analytics/query-themes`.

### 28A.14 Three-Domain Test Requirement

The internship PDF explicitly requires end-to-end validation across a minimum of three distinct knowledge-base domains. fileciteturn27file2L159-L161

A suitable validation matrix is:

```text
Domain 1: Technology / AI
Domain 2: Finance / Business
Domain 3: Science / General Knowledge
```

For each domain, record:

```text
document uploaded
document indexed
factual query
procedural query
comparative query where applicable
unanswerable query
retrieved source
confidence
knowledge-gap behavior
multi-turn follow-up
voice query
```

The application code should not claim that the three-domain requirement is complete merely because the dashboard exists; the actual test evidence must be recorded separately.

### 28A.15 M4 Optimization and Documentation Requirement

The internship PDF also requires optimization and documentation. fileciteturn27file2L162-L165

The current implementation provides technical foundations for:

```text
Retrieval Quality Optimization
- existing hybrid retrieval
- reranking
- low-confidence filtering
- user-scoped retrieval

Prompt / Response Optimization
- existing grounded response-generation prompts
- retrieval-aware context selection

Agent Routing Optimization
- deterministic query routing
- explicit general / clarification / retrieval paths

Voice Reliability Testing
- browser Web Speech API
- transcript submission through normal /query
- browser Speech Synthesis
```

These capabilities should be backed by recorded test results in the final project report rather than by unsupported percentage claims.


## SECTION 28B — ADMIN DASHBOARD

The Admin Dashboard adds a role-protected administration layer on top of the authenticated QueryNest application. It is implemented in `backend/app/admin/` and registered from `backend/app/main.py` through `admin_router`.

### 28B.1 Admin Authorization Model

Every Admin endpoint requires a Bearer JWT belonging to a user whose database role is exactly:

```text
Admin
```

The Admin router reuses the existing JWT dependency and adds the Admin role check. Therefore:

```text
Valid Admin JWT       → allowed
Valid non-Admin JWT   → 403 Forbidden
Missing/invalid JWT   → 401 Unauthorized
```

The frontend may hide Admin navigation for non-admin users, but frontend visibility is not the security boundary. The backend role check remains authoritative.

### 28B.2 Admin Module Structure

```text
backend/app/admin/
├── __init__.py
├── router.py
├── schemas.py
└── service.py
```

Responsibilities:

- `router.py` — exposes Admin endpoints and enforces the `Admin` role.
- `schemas.py` — defines Admin overview, user-summary, user-detail and document response models.
- `service.py` — calculates system-wide Admin statistics and per-user/document summaries.

### 28B.3 Admin API Contract

```text
GET    /admin/overview
GET    /admin/users
GET    /admin/users/{user_id}
GET    /admin/documents
DELETE /admin/documents/{document_id}
GET    /admin/analytics/queries-per-user
GET    /admin/analytics/frequent-queries?limit=10
```

#### `GET /admin/overview`

Returns system-wide statistics:

```json
{
  "total_users": 0,
  "total_documents": 0,
  "total_queries": 0,
  "answered_queries": 0,
  "unanswered_queries": 0,
  "average_confidence": null,
  "average_response_time": null,
  "total_knowledge_gaps": 0,
  "most_common_gap_reason": null
}
```

This endpoint aggregates across the entire application rather than using only the currently authenticated Admin user's personal query statistics.

#### `GET /admin/users`

Returns all users with document/query usage summary:

```json
{
  "users": [
    {
      "id": "...",
      "email": "...",
      "full_name": "...",
      "role": "...",
      "document_count": 0,
      "query_count": 0,
      "created_at": "..."
    }
  ],
  "total_users": 1
}
```

#### `GET /admin/users/{user_id}`

Returns one user's profile information, usage counts and document list.

#### `GET /admin/documents`

Returns all documents system-wide with owner information:

```json
[
  {
    "id": "...",
    "filename": "...",
    "original_filename": "...",
    "file_type": "...",
    "file_size": 0,
    "status": "...",
    "created_at": "...",
    "owner_id": "...",
    "owner_email": "..."
  }
]
```

#### `DELETE /admin/documents/{document_id}`

Admin override delete for any user's document.

```text
204 No Content → successful deletion
404 Not Found  → document does not exist
```

The frontend should confirm destructive actions and refresh the affected document list/counts after a successful deletion.

#### `GET /admin/analytics/queries-per-user`

Returns:

```json
[
  {
    "user_id": "...",
    "email": "...",
    "query_count": 0
  }
]
```

#### `GET /admin/analytics/frequent-queries?limit=10`

Returns repeated query text and occurrence counts:

```json
[
  {
    "query_text": "...",
    "occurrence_count": 0
  }
]
```

### 28B.4 Admin Frontend Pages

Suggested frontend page routes:

```text
/admin
/admin/users
/admin/users/:userId
/admin/documents
/admin/analytics
```

Suggested navigation:

```text
Admin
├── Overview
├── Users
│   └── User Detail
├── Documents
└── Analytics
```

The Overview page should present the system-wide totals, query status, confidence/response-time metrics and knowledge-gap summary. The Users page should support drill-down to an individual user. The Documents page should show owner information and provide an Admin delete action. The Analytics page should provide queries-per-user and frequent-query views.

### 28B.5 Admin User Behavior

An Admin remains a normal authenticated `User` record in the application. The `Admin` role adds access to system-level Admin APIs; it does not inherently disable the normal user workspace.

Therefore an Admin can still use the normal frontend to upload documents and ask chatbot questions. Those operations are associated with the Admin user's `user_id` and are included in system-wide Admin statistics.

For example:

```text
Dr. Vance logs in
      ↓
Normal QueryNest workspace
      ↓
Uploads document / asks query
      ↓
Records use Dr. Vance's user_id
      ↓
/admin/overview includes the activity
/admin/users shows the per-user counts
```

### 28B.6 Admin Validation Sequence

Validate the Admin backend in this order:

```text
1. Login as an Admin user
2. Obtain a valid JWT
3. Call GET /admin/overview
4. Call GET /admin/users
5. Call GET /admin/users/{user_id}
6. Call GET /admin/documents
7. Call GET /admin/analytics/queries-per-user
8. Call GET /admin/analytics/frequent-queries?limit=10
9. Test DELETE /admin/documents/{document_id} on a disposable test document
10. Repeat an Admin request using a normal User token and confirm 403
11. Repeat without/with an invalid token and confirm 401
```

### 28B.7 Admin and M4 Relationship

The Admin Dashboard does not replace the existing M4 Analytics or Knowledge Gap modules. It consumes their stored data at a system-wide level.

```text
Authenticated /query activity
        ↓
QueryAnalytics + KnowledgeGap records
        ↓
       Admin services
        ↓
  ┌─────┼─────────┐
  ↓     ↓         ↓
Overview Users  Analytics
  ↓     ↓         ↓
Knowledge Gaps / Documents
```

The Admin overview therefore provides a global operational view, while the existing `/analytics/*` and `/knowledge-gaps/*` endpoints remain user-facing/application features.

### 28B.8 Admin Migration and Schema Notes

The current Alembic chain includes the migration:

```text
e9b7e767c397_add_user_id_to_knowledge_gaps.py
```

This migration completes the `KnowledgeGap` ownership relationship by adding the foreign key from `knowledge_gaps.user_id` to `users.id` with `ON DELETE CASCADE`. The `user_id` column and index are expected to be present in the final schema, and the SQLAlchemy model should declare the matching indexes for `created_at` and `updated_at`.

On a fresh database, developers should run:

```bash
alembic upgrade head
```

No manual creation of the `knowledge_gaps.user_id` column or foreign key is required.

---

## SECTION 29 — CURRENT MILESTONE STATUS

### Milestone 1 — Completed
- Document upload for PDF, DOCX, TXT, CSV, JPG, JPEG and PNG.
- Hybrid document extraction with native text processing and OCR fallback.
- PaddleOCR support for scanned PDFs, handwritten documents and standalone images.
- Extraction and chunking.
- SentenceTransformer embeddings.
- ChromaDB persistence.
- Metadata/status persistence.
- Baseline RAG querying.

### Milestone 2 — Completed
- Query Understanding Agent.
- Deterministic Query Router.
- Retrieval Agent.
- Semantic + optional exact retrieval.
- Query-aware reranking.
- Low-confidence filtering.
- Response Generation Agent.
- Grounded citations.
- Confidence indicator.
- LangGraph orchestration.
- Frontend/API integration.

### Admin Dashboard — Backend Integrated / Frontend Pending
- Admin router, schemas and service integrated under `backend/app/admin/`.
- System-wide Admin overview endpoint implemented.
- All-users usage summary endpoint implemented.
- Per-user detail endpoint implemented.
- System-wide document listing implemented.
- Admin override document deletion endpoint implemented.
- Queries-per-user Admin analytics endpoint implemented.
- Frequent-query Admin analytics endpoint implemented.
- Admin authorization enforced through the existing JWT dependency plus `role == "Admin"`.
- Backend Admin endpoints tested locally in Swagger.
- Dedicated Admin frontend pages remain to be integrated.

### Milestone 4 — Integrated / Partially Validated
- Query Analytics SQLAlchemy model and persistence.
- Query-level logging from the authenticated `/query` path.
- Tracking of answered/unanswered response status.
- Tracking of confidence scores and response time.
- Query-type aggregation endpoint.
- Domain-agnostic common query-theme detection using a separate analytics-only embedding model.
- Common-theme endpoint and theme-level unanswered/low-confidence/gap scoring.
- Knowledge-gap detection for retrieval failures, zero results and low-confidence retrieval.
- Repeated knowledge-gap occurrence tracking.
- Knowledge-gap list, top-gap and statistics endpoints.
- User-specific `KnowledgeBaseDocument` PostgreSQL model.
- Authenticated user-specific document upload, listing, retrieval, deletion and stand-alone search endpoints.
- Background extraction, chunking, embedding and ChromaDB indexing for user-specific documents.
- ChromaDB metadata now includes `user_id` for private vector filtering.
- Authenticated `user_id` propagated through workflow state into Retrieval Agent.
- User-scoped semantic and exact retrieval functions while retaining legacy shared-search compatibility.
- Frontend Analytics Dashboard connected to real backend analytics.
- Frontend Knowledge Gap Dashboard connected to real backend gap records.
- Frontend History & Statistics page integrated.
- M4 navigation integrated into the authenticated React workspace.
- Analytics query distribution display updated to show values such as `17 queries · 58.6%`.
- Login error UX corrected so failed credentials remain visible on the login page while initial session-verification loading behavior is preserved.

### Milestone 4 Validation Status
- Core M4 analytics runtime behavior: validated.
- Common query-theme runtime behavior: validated with authenticated user-scoped analytics.
- Core knowledge-gap runtime behavior: validated.
- User-specific knowledge-base upload/index/retrieval isolation: validated.
- Frontend M4 dashboards: validated.
- Three-domain end-to-end evidence: should be recorded as a separate final test artifact.
- Retrieval/prompt/routing/voice optimization evidence: should be recorded in the final report.
- Final technical documentation/demo: this guide and README now include the M4 implementation details; final demo evidence remains a project-delivery activity.

### Milestone 3 — Integrated / Validated
- Clarification Agent and conditional clarification routing.
- Clarification question generation.
- Clarification-based query refinement path.
- PostgreSQL-backed Conversation Memory Agent.
- Persistent `conversation_id`.
- Loading conversation context.
- Context-aware follow-up query resolution.
- Saving user/assistant conversation turns.
- Browser Web Speech API speech-to-text.
- Browser Speech Synthesis text-to-speech integration path.
- Voice transcript submission through the normal `/query` workflow.
- Response transparency through source citations, relevance evidence, transparency confidence, and Context Inspector.
- Dedicated `app/transparency/` service integrated into `/query` without replacing the existing M3 response confidence.
- Frontend handling of clarification responses and conversation IDs.
- Backend JWT authentication with bcrypt password hashing.
- Sign up, sign in, `/auth/me`, and logout flow.
- Authenticated workspace gating in the React app.
- User-specific conversation ownership and isolation.
- General-knowledge/conversational queries routed directly to the shared LLM.
- Knowledge-base queries remaining on the existing RAG/retrieval path.
- Removal of chunk/embedding/vector implementation counts from the user-facing upload UI while retaining backend processing.

### Not part of the currently validated core flow
The following remain future/optional enhancements unless separately integrated and tested:
- advanced conversation search/summarization
- learned retrieval rerankers
- advanced automated analytics/knowledge-gap visualizations beyond the currently implemented M4 dashboards
- production-grade observability and distributed logging
- Dockerized deployment

---

## SECTION 30 — PROJECT SUMMARY

### Architecture
The platform uses a decoupled React + FastAPI architecture with a LangGraph orchestration layer and persistent PostgreSQL conversation memory.

### Backend
The backend separates:

```text
HTTP API
    ↓
LangGraph orchestration
    ↓
Agents + Memory
    ↓
RAG infrastructure / PostgreSQL
```

### Milestone 4
The platform now adds authenticated user-specific knowledge-base handling and telemetry around the M3 workflow:

```text
User-scoped document ingestion
        ↓
PostgreSQL document ownership + ChromaDB user_id metadata
        ↓
User-scoped Retrieval
        ↓
M3 Answer
        ↓
Query Analytics
        ↓
Knowledge Gap Detection
        ↓
Analytics / Knowledge Gap Dashboards
```

The M4 additions do not replace the M3 agents, memory, clarification, voice or transparency modules.

### Milestone 3
The primary validated conversation flow is:

```text
Authentication
   ↓
Memory
   ↓
Contextual Query Resolution
   ↓
Query Understanding
   ↓
Query Routing
   ├── General LLM
   ├── Clarification
   └── Existing RAG Retrieval
   ↓
Response
   ↓
Save Memory
```

### Voice
Voice is a browser capability layered onto the same conversation workflow:

```text
Web Speech API
    ↓
Transcript
    ↓
Existing /query workflow
    ↓
Answer
    ↓
Browser Speech Synthesis
```

### Retrieval
The system retains the Milestone 1 semantic/ChromaDB infrastructure while adding query-aware reranking, low-confidence filtering and final context selection.

### Response Generation
The system generates grounded answers from retrieved context and exposes source citations and confidence.

### Conversation Memory
Conversation state is keyed by `conversation_id` and persisted in PostgreSQL. Memory context can be used to resolve follow-up references without requiring the user to restate the earlier subject.

### Frontend Integration
The validated demo combines document ingestion, the M2 multi-agent workflow, M3 clarification and memory, browser voice interaction, and response transparency through the FastAPI REST API.

### Maintainability
Agent responsibilities, orchestration, API concerns, database concerns, voice module responsibilities, frontend responsibilities and RAG infrastructure remain separated, allowing each layer to be developed and tested independently.


---

## SECTION 31 — POSTGRESQL TEAM ONBOARDING SUMMARY

For a new developer, the required database process is:

```text
Install PostgreSQL
      ↓
Create empty querynest database
      ↓
Create backend/.env
      ↓
pip install -r requirements.txt
      ↓
alembic upgrade head
      ↓
Run FastAPI
      ↓
Run React
      ↓
Register a new user
      ↓
Upload a user-specific KB document
      ↓
Test Chat + Analytics + Knowledge Gaps
```

The developer does **not** need:

```text
❌ XAMPP
❌ MySQL/XAMPP
❌ PyMySQL
❌ manual application table creation
❌ another Alembic .env file
❌ another developer's application data
```

The developer does need:

```text
✅ PostgreSQL
✅ pgAdmin 4 (recommended)
✅ Psycopg 3
✅ Alembic
✅ local backend/.env
```

The repository should contain the Alembic configuration and migration files, while real environment files remain ignored by Git.
