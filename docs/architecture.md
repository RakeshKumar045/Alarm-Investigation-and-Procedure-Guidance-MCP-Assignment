# Architecture

## Overview

The Alarm Investigation and Procedure Guidance Copilot combines structured alarm
data obtained through MCP with procedure and maintenance evidence retrieved
through document RAG.

## Architecture diagram

```text
User
 |
 v
Streamlit GUI
 |
 v
Copilot Backend / Orchestrator
 |
 +--> MCP Client
 |       |
 |       v
 |   Alarm MCP Server
 |       |
 |       v
 |   Alarm API Simulator
 |
 +--> RAG Retrieval Service
         |
         +--> Document Store
         |       |
         |       v
         |   Operating Procedures
         |   Maintenance Manuals
         |
         +--> TF-IDF Retrieval Index
 |
 v
Grounded Investigation Answer
with Citations and MCP Execution Trace
```

## Main components

### Streamlit frontend

Location:

```text
apps/frontend/app.py
```

Responsibilities:

- Natural-language investigation input
- Alarm summary display
- Priority score display
- Likely causes and recommended actions
- Safety guidance
- Procedure and maintenance citations
- Operational visualizations
- MCP execution trace
- Raw response inspection
- Loading, empty, and error states
- Links to API documentation

### Copilot backend

Location:

```text
apps/backend/
```

Responsibilities:

- Receive the user question
- Identify the asset query
- Connect to the MCP server
- Discover available MCP tools
- Invoke tools using typed arguments
- Chain results between multiple tools
- Call the RAG retrieval service
- Combine structured and unstructured evidence
- Produce the final grounded response
- Return citations and execution trace

### MCP client

The backend uses the MCP Python SDK with SSE transport.

The client performs:

1. MCP session initialization
2. Tool discovery
3. Tool availability validation
4. Schema-aware tool invocation
5. Multi-step tool chaining
6. Tool duration measurement
7. Success and failure trace recording

### Alarm MCP server

Location:

```text
mcp_servers/alarm_management/server.py
```

The MCP server exposes these tools:

- `asset_search`
- `asset_metadata`
- `alarm_retrieval`
- `alarm_priority_score`
- `operator_recommendations`
- `alarm_correlation`

The MCP server is responsible for:

- Input validation
- Authentication propagation
- Trace metadata propagation
- Timeout handling
- Retry handling
- External API error mapping
- Safe tool responses

### Alarm API simulator

Location:

```text
alarm_api/
```

The FastAPI simulator represents the enterprise Alarm Management source
system. It contains synthetic assets and alarms and supports authentication,
pagination, metadata, alarm retrieval, priority scoring, recommendations,
summaries, and correlation.

### API connector

Location:

```text
connectors/alarm_api_client.py
```

The connector is used by the MCP server to call the Alarm API simulator.

It handles:

- Base URL configuration
- Bearer token authentication
- Trace headers
- Client identification
- Request timeout
- Retry behavior
- HTTP error mapping
- Response parsing

### RAG retrieval service

Location:

```text
rag/
```

The RAG service:

1. Loads Markdown documents.
2. Extracts document metadata.
3. Splits documents into sections and chunks.
4. Builds a TF-IDF retrieval index.
5. Calculates cosine-similarity scores.
6. Filters low-confidence results.
7. Returns relevant passages with citations.

## End-to-end request flow

1. The user submits a natural-language alarm investigation question.
2. The Streamlit GUI calls the copilot backend.
3. The backend connects to the Alarm MCP server.
4. The backend discovers the available MCP tools.
5. The `asset_search` tool resolves the asset name to an asset ID.
6. The `alarm_retrieval` tool retrieves active or historical alarms.
7. The `asset_metadata` tool retrieves asset context and related assets.
8. The `alarm_priority_score` tool calculates alarm priority.
9. The `operator_recommendations` tool returns likely causes and actions.
10. The `alarm_correlation` tool analyses related assets.
11. The RAG service retrieves relevant operating procedures and maintenance manuals.
12. The backend combines Alarm API evidence with RAG evidence.
13. The backend generates a grounded response.
14. The GUI displays the answer, alarm data, citations, visualizations, and MCP trace.

## Combined MCP and RAG workflow

The primary acceptance scenario is:

```text
Investigate active alarms for Boiler Feed Pump 101
and recommend immediate actions.
```

The workflow produces:

- Resolved asset identifier
- Active alarm details
- Alarm priority score
- Likely causes
- Recommended actions
- Related asset information
- Operating procedure evidence
- Maintenance manual evidence
- Source citations
- MCP tool execution trace

MCP and RAG are therefore part of the same business workflow rather than
independent demonstrations.

## Authentication and security boundaries

- API tokens are loaded from environment variables.
- Secrets are not hard-coded in application responses.
- Secrets are not displayed in the GUI.
- The copilot backend does not call the Alarm API directly.
- Alarm API calls are made by the MCP server.
- Retrieved documents are treated as untrusted evidence.
- Retrieved text cannot execute tools or override safety rules.
- No operational write operation is exposed.
- Recommendations require operator verification against approved procedures.
- User input is validated before tool invocation.
- External API errors are mapped to safe application errors.

## Observability

The implementation exposes or records:

- MCP tool name
- Tool arguments
- Tool execution status
- Tool duration
- API service activity
- Trace metadata
- Retrieved document identifiers
- Retrieval relevance scores
- Final citations
- Partial failure information

Sensitive tokens and credentials must not be logged.

## Deployment

### Local deployment

The application can be run as four local processes:

| Service | Port |
|---|---:|
| Alarm API simulator | 8000 |
| Alarm MCP server | 9000 |
| Copilot backend | 8080 |
| Streamlit frontend | 8501 |

### Docker deployment

Docker Compose starts:

- Alarm API simulator
- Alarm MCP server
- Copilot backend
- Streamlit frontend

Inside Docker, services communicate using Docker service names. Browser users
must use `localhost` URLs.

For example:

```text
Browser:  http://localhost:8080/docs
Container: http://copilot-backend:8080
```

The Docker hostname `copilot-backend` is not resolvable from the host browser.

## Configuration

Configuration is provided through environment variables:

```env
ALARM_API_BASE_URL=http://127.0.0.1:8000
ALARM_API_TOKEN=demo-token
MCP_SERVER_URL=http://127.0.0.1:9000/sse
COPILOT_BACKEND_URL=http://127.0.0.1:8080
DOCUMENT_PATH=./rag/documents
REQUEST_TIMEOUT_SECONDS=10
```

Docker uses internal service URLs:

```env
ALARM_API_BASE_URL=http://alarm-api:8000
MCP_SERVER_URL=http://alarm-mcp:9000/sse
DOCUMENT_PATH=/app/rag/documents
```

## Limitations

- The Alarm API data is synthetic.
- Alarm data is stored in memory.
- The RAG corpus is small and synthetic.
- TF-IDF retrieval is used instead of a production embedding model.
- No production identity provider is integrated.
- No persistent conversation history is implemented.
- No operational write action is available.
- Recommendations are decision-support output only.
- Docker execution requires a running Docker Engine.
- MCP uses SSE transport with MCP SDK 1.2.0.

## Future improvements

- Implement and test the remaining Postman endpoints.
- Add real alarm trend visualizations.
- Add site, unit, date-range, and severity filters.
- Add alarm flood heatmaps.
- Add historical recurrence analysis.
- Add related-asset dependency graphs.
- Add semantic embeddings and vector database retrieval.
- Add hybrid keyword and vector search.
- Add document version and approval filtering.
- Add reranking and confidence calibration.
- Add prompt-injection scanning.
- Add configurable LLM providers.
- Add role-based access control.
- Add audit logging and conversation persistence.
- Add OpenTelemetry tracing and metrics.
- Add CMMS or ticketing integration with explicit approval.
- Add PDF investigation report export.
- Add automated notifications for critical alarms.
- Add performance and load testing.
- Add high-availability deployment.
