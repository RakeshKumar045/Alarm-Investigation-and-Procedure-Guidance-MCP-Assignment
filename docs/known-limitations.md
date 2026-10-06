# Known Limitations and Future Enhancements

## Current limitations

### Synthetic source system

The Alarm Management API is a FastAPI simulator with in-memory synthetic
data. It does not connect to a real industrial control system, historian,
SCADA platform, or production alarm database.

### Limited dataset

The current dataset contains a small number of representative assets and
alarms, including:

- Boiler Feed Pump 101
- Boiler Feed Pump 102
- Compressor 201
- Motor 101

The data is intended to demonstrate integration and orchestration behavior.

### Retrieval implementation

The current RAG implementation uses TF-IDF and cosine similarity. It does not
yet use a production embedding model or managed vector database.

### Deterministic answer generation

The current answer generation is deterministic and combines API responses with
retrieved passages. It does not require an external LLM provider.

### No production authentication

The simulator uses a configured demonstration bearer token:

```text
demo-token
```

Production identity providers, OAuth2, SSO, user roles, and fine-grained
authorization are not implemented.

### No persistent storage

Assets, alarms, and calculations are stored in memory. Data is lost when the
API container restarts.

Conversation history and investigation reports are not persisted.

### No write operations

The application does not acknowledge, suppress, modify, reset, or close alarms.
It exposes read and analysis operations only.

### Safety limitation

The application is decision support only. Recommendations must be verified by
qualified operators and engineers against approved site procedures, safety
rules, permits, and authorization processes.

### Limited natural-language planning

The current orchestration uses lightweight intent and asset-query extraction.
A production implementation should use a configurable planner with stronger
intent classification, confidence scoring, and clarification questions.

### Extended API coverage

The primary vertical slice implements the core assigned-use-case endpoints.
Any extended endpoints from the Postman collections that are not implemented
must be clearly treated as pending work.

The following endpoints require explicit implementation and validation if full
Postman compatibility is claimed:

```text
POST /alarms/trends
POST /alarms/flood-analysis
POST /alarms/rationalization-candidates
POST /calculation-code/generate
POST /calculation-code/execute
GET  /analytics/kpi-definitions
```

### Observability

The demonstration includes tool execution status, duration, and source
traceability. A production deployment would require centralized logging,
metrics, distributed tracing, alerting, and retention policies.

### Deployment

Docker Compose is suitable for local demonstration. It does not provide
production high availability, autoscaling, secret rotation, network policies,
or disaster recovery.

## Security limitations

- Demonstration tokens must be replaced in production.
- No enterprise identity integration is included.
- No role-based MCP authorization is included.
- No external document access control is implemented.
- No malware scanning is implemented for uploaded documents.
- No automated prompt-injection classifier is included.
- No database is used, so SQL-injection protection is not applicable.
- No external write action is exposed.
- Secrets must remain outside source control.

## Future enhancements

### Alarm analytics

- Implement real alarm trend analysis.
- Add date-range filtering.
- Add site, unit, asset, and severity filters.
- Add alarm flood analysis.
- Add nuisance alarm detection.
- Add alarm rationalization candidate analysis.
- Add critical alarm density KPIs.
- Add operator response efficiency KPIs.
- Add historical recurrence charts.
- Add alarm heatmaps.

### Visualizations

- Add time-series alarm trends.
- Add severity distribution charts.
- Add alarm recurrence charts.
- Add flood-window visualization.
- Add related-asset network graphs.
- Add priority-versus-frequency scatter plots.
- Add exportable investigation reports.

### RAG improvements

- Use a production embedding model.
- Add a vector database such as Qdrant, pgvector, or Elasticsearch.
- Add hybrid keyword and semantic retrieval.
- Add reranking.
- Add document version filtering.
- Add document approval-state filtering.
- Add source-system ownership metadata.
- Add scheduled index refresh.
- Add retrieval quality evaluation.
- Add automated prompt-injection detection.
- Add document access control.

### Copilot improvements

- Add a configurable LLM provider abstraction.
- Add stronger intent classification.
- Add clarification questions for ambiguous assets.
- Add confidence scores.
- Add conflicting-evidence detection.
- Add partial-failure explanations.
- Add conversational context and history.
- Add user-selectable analysis depth.
- Add multi-asset investigation.
- Add report export to PDF.

### MCP improvements

- Add MCP authorization policies.
- Add per-tool permissions.
- Add rate limiting.
- Add circuit breakers.
- Add idempotency support.
- Add structured audit events.
- Add output schema validation.
- Add tool versioning.
- Add MCP server health and readiness endpoints.
- Add automated contract testing for every tool.

### Enterprise integrations

- Integrate with a real alarm historian.
- Integrate with SCADA or DCS systems.
- Integrate with CMMS and maintenance systems.
- Integrate with ticketing platforms.
- Require explicit human approval before ticket creation.
- Add notification integrations.
- Add identity and access-management integration.
- Add enterprise document repositories.

### Operations

- Add OpenTelemetry tracing.
- Add Prometheus metrics.
- Add centralized structured logs.
- Add dashboards and alerts.
- Add container image scanning.
- Add dependency vulnerability scanning.
- Add CI/CD deployment.
- Add Kubernetes manifests.
- Add high-availability services.
- Add backup and recovery processes.
- Add performance and load testing.

## Submission disclosure

This submission prioritizes one complete vertical slice:

```text
Natural-language request
    -> MCP discovery
    -> Asset resolution
    -> Alarm retrieval
    -> Metadata and related assets
    -> Priority and recommendations
    -> Correlation
    -> RAG retrieval
    -> Grounded answer
    -> Citations and trace
    -> GUI presentation
```

The implementation favors a smaller, fully integrated MCP-plus-RAG workflow over
a broad but incomplete production platform.
