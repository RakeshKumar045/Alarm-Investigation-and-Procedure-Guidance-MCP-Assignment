# ABB Alarm Intelligence Copilot

Alarm Investigation and Procedure Guidance Copilot for the ABB technical
assessment.

## Use case

The application investigates plant alarms by combining:

- Asset search and metadata
- Active and historical alarm retrieval
- Related asset information
- Alarm priority scoring
- Operator recommendations
- Alarm correlation
- Alarm summaries and trends
- Flood analysis
- Rationalization candidates
- KPI calculations
- Operating procedures
- Maintenance manuals
- RAG citations
- MCP execution traceability

The source system is a synthetic Alarm Management API simulator.

> This application is decision support only. Operators must verify all
> recommendations against approved site procedures, safety requirements, and
> qualified engineering judgement.

## Architecture

```text
Streamlit GUI
     |
     v
Copilot Backend / Orchestrator
     |
     v
MCP Client
     |
     v
Alarm MCP Server
     |
     v
Alarm API Simulator

Copilot Backend
     |
     v
RAG Retrieval Service
     |
     v
Operating Procedures and Maintenance Manuals
```

The backend accesses the Alarm API only through MCP. RAG retrieval participates
in the same investigation workflow and provides cited document evidence.

Architecture documentation:

- `docs/architecture.md`
- `docs/architecture-diagram.png`
- `docs/design-decisions.md`

## Technology stack

- Python 3.12+
- FastAPI
- Uvicorn
- MCP Python SDK `1.2.0`
- Streamlit
- Pydantic
- HTTPX
- scikit-learn TF-IDF retrieval
- pandas
- pytest
- Docker Compose

## MCP tools

The Alarm MCP server exposes:

- `asset_search`
- `asset_metadata`
- `alarm_retrieval`
- `alarm_priority_score`
- `operator_recommendations`
- `alarm_correlation`

The MCP client performs tool discovery and invokes tools through typed
arguments. Alarm API calls are made by the MCP server, not directly by the
copilot backend.

See:

```text
docs/mcp-tool-catalog.md
```

## RAG corpus

The sample corpus contains:

```text
rag/documents/boiler_feed_pump_procedure.md
rag/documents/pump_maintenance_manual.md
```

The retrieval workflow includes:

1. Markdown document loading
2. Metadata extraction
3. Section-based chunking
4. TF-IDF indexing
5. Cosine-similarity retrieval
6. Low-confidence filtering
7. Source citation construction

See:

```text
docs/rag-design.md
```

## Repository structure

```text
.
├── alarm_api/
│   ├── data.py
│   └── main.py
├── apps/
│   ├── backend/
│   │   ├── main.py
│   │   └── orchestrator.py
│   └── frontend/
│       └── app.py
├── connectors/
│   └── alarm_api_client.py
├── mcp_servers/
│   └── alarm_management/
│       └── server.py
├── rag/
│   ├── retrieval.py
│   └── documents/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
├── scripts/
├── screenshots/
├── postman/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── .env.example
```

## Configuration

Create local configuration:

```powershell
Copy-Item .env.example .env
```

Example configuration:

```env
ALARM_API_BASE_URL=http://127.0.0.1:8000
ALARM_API_TOKEN=demo-token
MCP_SERVER_URL=http://127.0.0.1:9000/sse
COPILOT_BACKEND_URL=http://127.0.0.1:8080
DOCUMENT_PATH=./rag/documents
REQUEST_TIMEOUT_SECONDS=10
```

Do not commit `.env`.

## Local execution

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the following services in separate terminals.

### Terminal 1 — Alarm API simulator

```powershell
python -m uvicorn alarm_api.main:app --port 8000
```

URLs:

```text
API:     http://localhost:8000
Swagger: http://localhost:8000/docs
Health:  http://localhost:8000/health
```

### Terminal 2 — MCP server

```powershell
python -m mcp_servers.alarm_management.server
```

MCP endpoint:

```text
http://localhost:9000/sse
```

### Terminal 3 — Copilot backend

```powershell
python -m uvicorn apps.backend.main:app --port 8080
```

URLs:

```text
Backend:  http://localhost:8080
Swagger:  http://localhost:8080/docs
Health:   http://localhost:8080/health
```

### Terminal 4 — Streamlit frontend

```powershell
python -m streamlit run apps/frontend/app.py
```

Open:

```text
http://localhost:8501
```

## Docker execution

Ensure Docker Desktop or another Docker Engine is running:

```powershell
docker info
```

Build and start all services:

```powershell
docker compose up --build
```

Services:

| Service | URL |
|---|---|
| Frontend | http://localhost:8501 |
| Copilot backend | http://localhost:8080 |
| Backend Swagger | http://localhost:8080/docs |
| Alarm API | http://localhost:8000 |
| Alarm API Swagger | http://localhost:8000/docs |
| Backend health | http://localhost:8080/health |
| Alarm API health | http://localhost:8000/health |

Stop services:

```powershell
docker compose down
```

View logs:

```powershell
docker compose logs copilot-backend --tail=100
docker compose logs alarm-mcp --tail=100
docker compose logs alarm-api --tail=100
docker compose logs frontend --tail=100
```

The Docker hostname below is available only inside the Docker network:

```text
http://copilot-backend:8080
```

From a browser, use:

```text
http://localhost:8080/docs
```

## Example questions

### Successful investigation

```text
Investigate active alarms for Boiler Feed Pump 101 and recommend immediate actions.
```

### Pump motor investigation

```text
Show active critical alarms for Boiler Feed Pump 102 and recommend immediate actions.
```

### Compressor investigation

```text
Investigate active alarms for Compressor 201 and identify likely causes.
```

### Maintenance guidance

```text
What maintenance checks should be performed for recurring low flow on Boiler Feed Pump 101?
```

### Degraded scenario

```text
Investigate active alarms for Unknown Pump 999.
```

Expected result:

```text
No matching asset was found.
```

## GUI features

The Streamlit application displays:

- Investigation overview
- Asset metadata
- Alarm details
- Severity and priority score
- Likely causes
- Immediate operator actions
- Safety guidance
- Procedure and maintenance citations
- Operational visualizations
- MCP tool execution trace
- Tool arguments and duration
- Raw response data
- API documentation links
- Loading, empty, and error states

## API simulator endpoints

The simulator implements:

- `GET /health`
- `GET /assets/search`
- `GET /assets/{asset_id}/metadata`
- `GET /alarms`
- `GET /alarms/{alarm_id}`
- `POST /alarms/summary`
- `POST /alarms/trends`
- `POST /alarms/correlation`
- `POST /alarms/flood-analysis`
- `POST /alarms/rationalization-candidates`
- `POST /alarms/priority-score`
- `POST /recommendations/operator-actions`
- `POST /calculation-code/generate`
- `POST /calculation-code/execute`
- `GET /analytics/kpi-definitions`

The API supports:

- Bearer authentication
- Trace headers
- Pagination
- Timeout and retry handling through the connector
- Structured error responses
- Multi-step API chaining

Reference Postman collections are available under:

```text
postman/
```

Additional API documentation:

```text
docs/api-integration.md
```

## Testing

Run dependency validation:

```powershell
python -m pip check
```

Run the complete test suite:

```powershell
python -m pytest -q
```

Current verified result:

```text
13 passed, 1 warning
```

The warning is a non-blocking dependency deprecation warning.

Run unit RAG tests:

```powershell
python -m pytest tests/unit/test_rag.py -q
```

Run API tests:

```powershell
python -m pytest tests/integration/test_api.py -q
```

Run API chaining tests:

```powershell
python -m pytest tests/integration/test_chaining.py -q
```

Run MCP discovery tests while the MCP server is running:

```powershell
python -m pytest tests/integration/test_mcp_connection.py -q
```

Run the combined MCP and RAG E2E test while the Alarm API and MCP server are
running:

```powershell
python -m pytest tests/e2e/test_mcp_rag_workflow.py -q
```

## Combined acceptance workflow

The primary acceptance scenario is:

```text
Natural-language question
    -> MCP tool discovery
    -> Asset resolution
    -> Alarm retrieval
    -> Asset metadata
    -> Priority scoring
    -> Operator recommendations
    -> Related asset correlation
    -> RAG document retrieval
    -> Grounded answer
    -> Citations and MCP trace
    -> GUI presentation
```

This demonstrates that MCP and RAG participate in the same business workflow.

## Security and safety

- Tokens are loaded from environment variables.
- `.env` is excluded from source control.
- Secrets are not displayed in the GUI.
- The backend does not bypass MCP.
- Retrieved documents are treated as untrusted evidence.
- Retrieved text cannot execute tools.
- No alarm acknowledgement or equipment control operation is exposed.
- Recommendations require operator verification.
- No ticket or write operation occurs without an explicit future approval flow.
- API errors are mapped to safe application errors.

## Known limitations

- Alarm data is synthetic and stored in memory.
- The RAG corpus is small and synthetic.
- TF-IDF is used instead of production embeddings.
- No external LLM is required.
- No production SSO or role-based authorization is implemented.
- No conversation persistence is implemented.
- Docker Compose is for demonstration, not production high availability.
- Recommendations are decision-support output only.
- The MCP server uses SSE transport with MCP SDK `1.2.0`.

See:

```text
docs/known-limitations.md
```

## Future enhancements

- Real alarm historian integration
- Real-time alarm trends
- Alarm flood heatmaps
- Historical recurrence analysis
- Semantic embeddings and vector database
- Hybrid retrieval and reranking
- Document version and approval filtering
- Stronger intent classification
- Confidence scoring
- Conversational history
- Role-based access control
- OpenTelemetry tracing
- Prometheus metrics
- CMMS and ticketing integration with explicit approval
- PDF investigation report export
- Notifications for critical alarms
- Kubernetes deployment
- Load and performance testing
- High-availability deployment
- Scheduled RAG index refresh
- Automated prompt-injection detection

## Documentation

- `docs/architecture.md`
- `docs/architecture-diagram.png`
- `docs/mcp-tool-catalog.md`
- `docs/rag-design.md`
- `docs/api-integration.md`
- `docs/design-decisions.md`
- `docs/known-limitations.md`

## Demo evidence

Screenshots are available in:

```text
screenshots/
```

Included evidence:

1. `01-successful-investigation.png` — successful alarm investigation
2. `02-mcp-trace.png` — MCP discovery and tool execution
3. `03-rag-citations.png` — RAG document citations
4. `04-visualizations.png` — operational visualizations
5. `05-unknown-asset.png` — degraded/no-result scenario
6. `06-api-docs.png` — backend API documentation
7. `07-docker-services.png` — Docker Compose services
8. `architecture-diagram.png` — architecture diagram

The architecture diagram is also available at:

```text
docs/architecture-diagram.png
```

## CI

GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

The workflow runs:

- Python source compilation
- Alarm API startup validation
- MCP startup validation
- Automated tests
- Docker Compose image build

## Demo video

Not included at this stage as advised by HR; available upon request.

## Final verification

The following have been verified locally and through Docker Compose:

- Alarm API simulator starts successfully.
- MCP server starts successfully.
- MCP tool discovery succeeds.
- Copilot backend starts successfully.
- RAG retrieval tests pass.
- API tests pass.
- Multi-step chaining tests pass.
- Combined MCP and RAG E2E test passes.
- GUI displays alarm details, citations, visualizations, and trace.
- Unknown asset handling works.
- Docker Compose services start successfully.
- Backend and Alarm API health endpoints return HTTP 200.
- `python -m pip check` reports no broken requirements.
