# Design Decisions

## 1. Python-based implementation

Python was selected because it provides mature support for:

- FastAPI
- MCP
- HTTP clients
- Pydantic validation
- Streamlit
- Retrieval and machine-learning libraries
- Automated testing

This enables a complete vertical slice with a small and maintainable codebase.

## 2. FastAPI for the Alarm API simulator

FastAPI was selected because it provides:

- Typed request and response models
- Automatic OpenAPI documentation
- Fast development of REST endpoints
- Easy integration testing
- Native asynchronous support

The simulator exposes Swagger documentation at:

```text
http://localhost:8000/docs
```

## 3. MCP as the integration boundary

The copilot backend accesses alarm data through MCP rather than calling the
Alarm API directly.

This creates a clear boundary:

```text
Copilot backend -> MCP client -> MCP server -> API connector -> Alarm API
```

Benefits include:

- Tool discovery
- Typed tool contracts
- Centralized authentication
- Centralized retry and timeout handling
- Consistent error mapping
- Tool-level observability
- Ability to add additional enterprise systems later

## 4. SSE transport for MCP

The implementation uses SSE transport because it is supported by the selected
MCP SDK version:

```text
mcp==1.2.0
```

The local MCP endpoint is:

```text
http://localhost:9000/sse
```

The Docker MCP endpoint is:

```text
http://alarm-mcp:9000/sse
```

The MCP version is pinned to avoid incompatible SDK changes.

## 5. FastAPI backend for orchestration

The copilot backend is separate from the GUI. This separation allows:

- Independent backend testing
- Multiple future clients
- API-based integration
- Easier deployment
- Clear separation between presentation and orchestration

The backend exposes:

```text
POST /chat
GET  /health
```

Swagger documentation is available at:

```text
http://localhost:8080/docs
```

## 6. Streamlit for the GUI

Streamlit was selected to provide a usable graphical interface quickly while
keeping the focus on integration and orchestration.

The GUI displays:

- Investigation results
- Alarm data
- Priority score
- Recommendations
- Visualizations
- RAG citations
- MCP trace
- Raw response data
- API documentation links

A production implementation could replace Streamlit with React, Angular, or
another enterprise frontend without changing the backend contracts.

## 7. TF-IDF for the initial RAG implementation

TF-IDF was selected because:

- It is deterministic.
- It is easy to run locally.
- It requires no external service or API key.
- It is suitable for the small synthetic corpus.
- It is easy to test and reproduce.

The retrieval layer is isolated in `rag/retrieval.py`, allowing future
replacement with embeddings and a vector database.

## 8. Synthetic documents

Synthetic operating procedures and maintenance manuals were used because the
assignment requires a representative corpus but real industrial documents may
be confidential.

The documents demonstrate:

- Document ingestion
- Metadata extraction
- Chunking
- Retrieval
- Citations
- Safety content
- Procedure alignment

## 9. Read-only operations

The application exposes read and analysis operations only.

It does not:

- Acknowledge alarms
- Suppress alarms
- Reset equipment
- Change set points
- Create maintenance tickets
- Execute control actions

This reduces operational risk and avoids requiring approval workflows for the
demonstration.

## 10. Deterministic response composition

The current response combines structured API results and RAG citations using a
deterministic orchestration flow.

This was selected to ensure:

- Reproducible demonstrations
- Testable outputs
- No external LLM dependency
- No secret API key requirement
- Clear evidence traceability

A future LLM layer can be added behind a provider abstraction while retaining
the same MCP and RAG evidence contracts.

## 11. Environment-based configuration

Runtime configuration is loaded from environment variables.

This avoids hard-coding:

- Service URLs
- API tokens
- Document paths
- Timeout values

Secrets are excluded from source control through `.gitignore`.

## 12. In-memory simulator data

The simulator uses in-memory data to keep setup simple and deterministic.

This is appropriate for:

- Local development
- Automated tests
- Demonstration
- Docker Compose startup

A production implementation would use a persistent database or connect to an
enterprise source system.

## 13. Docker Compose packaging

Docker Compose was selected because it provides a repeatable local deployment
for:

- Alarm API
- MCP server
- Copilot backend
- Streamlit frontend

It also demonstrates service-to-service networking and configuration
separation.

## 14. Explicit traceability

Every investigation response includes:

- MCP tool names
- Tool arguments
- Tool status
- Tool duration
- Retrieved document identifiers
- Relevance scores
- Source paths

This supports debugging, auditability, and evaluator verification.

## 15. Safety and document trust boundary

Retrieved document text is treated as evidence, not executable instructions.

The system does not allow retrieved documents to:

- Invoke tools
- Override application rules
- Change authorization
- Bypass safety controls
- Trigger operational actions

Operators must verify recommendations against approved site procedures.

## 16. Testing strategy

The test suite is divided into:

- Unit tests for RAG retrieval
- API integration tests
- API chaining tests
- MCP discovery tests
- End-to-end MCP and RAG tests

The goal is to validate both individual components and the complete business
workflow.

## 17. Honest scope disclosure

The implementation prioritizes one complete vertical slice rather than claiming
unsupported production functionality.

The primary demonstrated workflow is:

```text
Natural-language request
    -> MCP tool discovery
    -> Asset resolution
    -> Alarm retrieval
    -> Asset metadata
    -> Priority scoring
    -> Recommendations
    -> Correlation
    -> RAG retrieval
    -> Grounded answer
    -> Citations and execution trace
```

Any endpoint or capability not implemented is documented as a limitation or
future enhancement.
