# MCP Tool Catalog

## Server information

| Property | Value |
|---|---|
| Server name | Alarm Management MCP Server |
| Transport | SSE |
| Local endpoint | `http://127.0.0.1:9000/sse` |
| Docker endpoint | `http://alarm-mcp:9000/sse` |
| Source system | Alarm Management API Simulator |

The MCP server calls the Alarm API through
`connectors/alarm_api_client.py`.

The copilot backend does not call the Alarm API directly. It discovers and
invokes MCP tools through the MCP client.

## Common tool behavior

All tools provide:

- Typed input arguments
- Input validation
- Bearer authentication propagation
- Trace metadata propagation
- Timeout handling
- Retry handling
- External API error mapping
- Structured responses
- Safe errors without secrets

Configured authentication headers include:

```http
Authorization: Bearer <configured-token>
trace_id: <generated-or-provided-trace-id>
x-client-id: alarm-copilot-mcp
x-metadata-tag: copilot
```

---

## 1. `asset_search`

### Purpose

Search plant assets by name, type, or description.

### Input schema

```json
{
  "query": "Boiler Feed Pump 101",
  "limit": 10
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `query` | string | Yes | Asset search text |
| `limit` | integer | No | Maximum number of results; 1–100 |

### Underlying API

```http
GET /assets/search?query={query}&limit={limit}
```

### Example invocation

```json
{
  "query": "Boiler Feed Pump 101",
  "limit": 10
}
```

### Example response

```json
{
  "results": [
    {
      "asset_id": "asset-bfp-101",
      "asset_name": "Boiler Feed Pump 101",
      "site": "NorthPlant",
      "unit": "Unit 1",
      "asset_type": "pump",
      "criticality": "high"
    }
  ],
  "count": 1
}
```

### Errors

- Empty query: validation error
- Limit outside 1–100: validation error
- Invalid token: authentication error
- API unavailable: service-unavailable error
- Timeout: timeout error

---

## 2. `asset_metadata`

### Purpose

Retrieve asset metadata and related assets.

### Input schema

```json
{
  "asset_id": "asset-bfp-101"
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `asset_id` | string | Yes | Unique asset identifier |

### Underlying API

```http
GET /assets/{asset_id}/metadata
```

### Example response

```json
{
  "asset": {
    "asset_id": "asset-bfp-101",
    "asset_name": "Boiler Feed Pump 101",
    "site": "NorthPlant",
    "unit": "Unit 1",
    "asset_type": "pump",
    "criticality": "high"
  },
  "related_assets": [
    {
      "asset_id": "asset-motor-101",
      "asset_name": "Motor 101",
      "asset_type": "motor"
    }
  ]
}
```

### Errors

- Empty asset ID: validation error
- Unknown asset: not-found error
- Invalid token: authentication error
- API timeout: timeout error

---

## 3. `alarm_retrieval`

### Purpose

Retrieve active or historical alarms for an asset.

### Input schema

```json
{
  "asset_id": "asset-bfp-101",
  "status": "active",
  "page": 1,
  "page_size": 50
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `asset_id` | string | Yes | Asset identifier |
| `status` | string | No | `active` or `historical` |
| `page` | integer | No | Page number |
| `page_size` | integer | No | Records per page; 1–200 |

### Underlying API

```http
GET /alarms
```

### Example response

```json
{
  "data": [
    {
      "alarm_id": "alarm-bfp101-low-flow-001",
      "asset_id": "asset-bfp-101",
      "asset_name": "Boiler Feed Pump 101",
      "alarm_name": "Boiler Feed Pump Low Flow",
      "severity": "critical",
      "status": "active",
      "occurrence_count": 12
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 1,
    "has_next": false
  }
}
```

### Errors

- Invalid page: validation error
- Invalid page size: validation error
- Invalid token: authentication error
- API unavailable: service-unavailable error
- Timeout: timeout error

---

## 4. `alarm_priority_score`

### Purpose

Calculate the priority of an alarm using severity and recurrence frequency.

### Input schema

```json
{
  "alarm_id": "alarm-bfp101-low-flow-001"
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `alarm_id` | string | Yes | Unique alarm identifier |

### Underlying API

```http
POST /alarms/priority-score
```

### Example response

```json
{
  "alarm_id": "alarm-bfp101-low-flow-001",
  "priority_score": 100,
  "priority": "urgent",
  "reason": "Severity and recurrence frequency"
}
```

### Errors

- Empty alarm ID: validation error
- Unknown alarm: not-found error
- API timeout: timeout error
- API unavailable: service-unavailable error

---

## 5. `operator_recommendations`

### Purpose

Retrieve likely causes, immediate operator actions, and safety guidance.

### Input schema

```json
{
  "alarm_id": "alarm-bfp101-low-flow-001"
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `alarm_id` | string | Yes | Unique alarm identifier |

### Underlying API

```http
POST /recommendations/operator-actions
```

### Example response

```json
{
  "alarm_id": "alarm-bfp101-low-flow-001",
  "likely_causes": [
    "Insufficient suction flow",
    "Blocked suction strainer",
    "Instrument error"
  ],
  "recommended_actions": [
    "Verify the local flow indication.",
    "Check pump suction and discharge pressure.",
    "Inspect valves and suction strainers."
  ],
  "safety_note": "Do not bypass interlocks."
}
```

### Errors

- Empty alarm ID: validation error
- Unknown alarm: not-found error
- API timeout: timeout error
- API unavailable: service-unavailable error

---

## 6. `alarm_correlation`

### Purpose

Correlate alarms across an asset and its related assets.

### Input schema

```json
{
  "asset_ids": [
    "asset-bfp-101",
    "asset-motor-101"
  ]
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `asset_ids` | array of strings | Yes | One or more related asset IDs |

### Underlying API

```http
POST /alarms/correlation
```

### Example response

```json
{
  "trace_id": "trace-123",
  "correlations": [
    {
      "alarm_name": "Boiler Feed Pump Low Flow",
      "asset_id": "asset-bfp-101",
      "support": 12,
      "confidence": 0.62,
      "likely_factor": "Low suction flow or restriction"
    }
  ]
}
```

### Errors

- Empty asset list: validation error
- Unknown assets: empty result or not-found response
- API timeout: timeout error
- API unavailable: service-unavailable error

---

## Multi-step chaining

The main copilot flow uses the following chain:

```text
asset_search
    |
    v
asset_metadata
    |
    v
alarm_retrieval
    |
    v
alarm_priority_score
    |
    v
operator_recommendations
    |
    v
alarm_correlation
    |
    v
RAG retrieval
    |
    v
Grounded answer with citations
```

Example data flow:

```text
asset_search.results[0].asset_id
    -> asset_metadata(asset_id)
    -> alarm_retrieval(asset_id)
```

Then:

```text
alarm_retrieval.data[0].alarm_id
    -> alarm_priority_score(alarm_id)
    -> operator_recommendations(alarm_id)
```

Related assets returned by `asset_metadata` are passed to:

```text
alarm_correlation(asset_ids)
```

## Timeout and retry behavior

The connector applies a configured request timeout and retries transient
failures. Client errors such as invalid authentication, invalid input, and
not-found responses are not retried.

## Traceability

The GUI displays:

- Tool name
- Tool arguments
- Tool status
- Tool duration
- Error information for failed calls

The MCP server and connector must not log bearer tokens or other secrets.
