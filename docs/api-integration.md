# API Integration

## Overview

The Alarm API simulator represents the enterprise Alarm Management source
system. It is implemented with FastAPI and is called by the Alarm MCP server
through the reusable API connector.

The copilot backend does not call the Alarm API directly.

```text
Copilot backend
      |
      v
MCP client
      |
      v
Alarm MCP server
      |
      v
Alarm API connector
      |
      v
Alarm API simulator
```

## Base URLs

### Local

```text
http://localhost:8000
```

### Docker

```text
http://alarm-api:8000
```

The Docker hostname is available only inside the Docker network.

## Authentication

Protected endpoints require:

```http
Authorization: Bearer demo-token
```

The configured token is read from:

```env
ALARM_API_TOKEN=demo-token
```

The health endpoint does not require authentication.

## Trace and metadata headers

Trace-aware operations support:

```http
trace_id: <trace-id>
x-client-id: <client-id>
x-metadata-tag: <metadata-tag>
```

The MCP connector sends:

```http
trace_id: <generated-trace-id>
x-client-id: alarm-copilot-mcp
x-metadata-tag: copilot
```

Trace identifiers are returned in responses where supported.

## Implemented endpoints

### Health

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "alarm-api-simulator"
}
```

### Asset search

```http
GET /assets/search?query=Boiler%20Feed%20Pump%20101&limit=10
```

Example response:

```json
{
  "results": [
    {
      "asset_id": "asset-bfp-101",
      "asset_name": "Boiler Feed Pump 101",
      "site": "NorthPlant",
      "unit": "Unit 1",
      "asset_type": "pump"
    }
  ],
  "count": 1
}
```

### Asset metadata

```http
GET /assets/{asset_id}/metadata
```

Example:

```http
GET /assets/asset-bfp-101/metadata
```

### Alarm retrieval

```http
GET /alarms
```

Supported query parameters include:

- `asset_id`
- `site`
- `unit`
- `status`
- `page`
- `page_size`
- `sort_by`
- `sort_order`

Example:

```http
GET /alarms?asset_id=asset-bfp-101&status=active&page=1&page_size=50
```

The response includes:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 0,
    "has_next": false
  }
}
```

### Alarm detail

```http
GET /alarms/{alarm_id}
```

### Alarm summary

```http
POST /alarms/summary
```

Example request:

```json
{
  "asset_ids": [
    "asset-bfp-101"
  ],
  "severity": [
    "high",
    "critical"
  ],
  "group_by": [
    "alarm_name"
  ],
  "kpis": [
    "alarm_count",
    "recurring_rate",
    "avg_ack_delay"
  ]
}
```

### Alarm correlation

```http
POST /alarms/correlation
```

Example request:

```json
{
  "asset_ids": [
    "asset-bfp-101",
    "asset-motor-101"
  ],
  "correlation_method": "cooccurrence",
  "lag_window_minutes": 15,
  "severity_threshold": "medium",
  "min_support": 1
}
```

### Priority score

```http
POST /alarms/priority-score
```

Example request:

```json
{
  "alarm_id": "alarm-bfp101-low-flow-001"
}
```

### Operator recommendations

```http
POST /recommendations/operator-actions
```

Example request:

```json
{
  "alarm_id": "alarm-bfp101-low-flow-001",
  "include_related": true,
  "include_asset_context": true,
  "include_historical_pattern": true
}
```

## Error behavior

The simulator uses standard HTTP status codes:

| Status | Meaning |
|---:|---|
| 200 | Successful request |
| 401 | Missing or invalid bearer token |
| 404 | Asset or alarm not found |
| 422 | Invalid request or query parameters |
| 503 | Source service unavailable |
| 504 | Timeout |

The MCP connector maps API errors to understandable MCP errors.

## Pagination

Alarm retrieval supports:

```text
page
page_size
```

The response contains:

```json
{
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 12,
    "has_next": false
  }
}
```

The MCP tool validates page and page-size values before forwarding requests.

## Retry and timeout behavior

The API connector:

- Uses a configured request timeout.
- Retries transient failures.
- Does not retry validation errors.
- Does not retry authentication errors.
- Maps timeout failures to a timeout response.
- Maps connection failures to an unavailable-service response.

Configuration:

```env
REQUEST_TIMEOUT_SECONDS=10
```

## MCP integration boundary

The application intentionally separates responsibilities:

| Component | Responsibility |
|---|---|
| GUI | User interaction and evidence presentation |
| Copilot backend | Planning and orchestration |
| MCP client | Tool discovery and invocation |
| MCP server | Tool contracts and source-system access |
| API connector | HTTP, authentication, retry, timeout |
| Alarm API | Synthetic source-system behavior |
| RAG service | Document retrieval and citations |

The backend never bypasses the MCP server for Alarm API access.

## Testing

API tests cover:

- Health endpoint
- Authentication
- Asset search
- Pagination
- Asset-to-alarm chaining
- Priority scoring
- Error responses

Run:

```powershell
python -m pytest tests/integration/test_api.py -q
python -m pytest tests/integration/test_chaining.py -q
```

## Postman validation

The reference Postman collections are located in:

```text
postman/
```

They define authentication, trace headers, request payloads, endpoint paths,
and multi-step chaining behavior.

Use the collections against:

```text
http://localhost:8000
```

with:

```text
auth_token=demo-token
```

## Limitations

The API simulator is synthetic and in-memory. It is not intended to represent
a production database, production authentication provider, or real plant
control system.

Any endpoint not implemented in the simulator must be explicitly documented
as a known limitation rather than presented as production-ready.
