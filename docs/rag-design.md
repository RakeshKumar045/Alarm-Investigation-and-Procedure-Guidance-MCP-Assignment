# RAG Design

## Purpose

The RAG workflow retrieves relevant operating procedures and maintenance
guidance for the alarm being investigated. Retrieved evidence is combined with
structured Alarm API data in the same copilot response.

## Document corpus

Current synthetic corpus:

| Document | Type | Purpose |
|---|---|---|
| `boiler_feed_pump_procedure.md` | Operating Procedure | Immediate response and safety guidance |
| `pump_maintenance_manual.md` | Maintenance Manual | Recurring low-flow troubleshooting |

Documents are stored in:

```text
rag/documents/
```

## Ingestion workflow

The retrieval service:

1. Reads Markdown files from the configured document directory.
2. Extracts document ID from document metadata.
3. Extracts document type.
4. Captures the document title and source path.
5. Splits content into sections.
6. Creates searchable chunks.
7. Stores metadata for each chunk.
8. Builds a TF-IDF retrieval matrix.

## Chunk metadata

Each chunk contains:

- `chunk_id`
- `document_id`
- `title`
- `document_type`
- `text`
- `source`
- `score`

Example:

```json
{
  "chunk_id": "PROC-BFP-001-1",
  "document_id": "PROC-BFP-001",
  "title": "Boiler Feed Pump Procedure",
  "document_type": "Operating Procedure",
  "text": "Verify pump suction pressure...",
  "source": "rag/documents/boiler_feed_pump_procedure.md",
  "score": 0.2367
}
```

## Retrieval method

The current implementation uses:

- Scikit-learn `TfidfVectorizer`
- English stop-word removal
- Cosine similarity
- Ranked top-K results
- Minimum relevance threshold

This is an equivalent retrieval approach for the synthetic demonstration
corpus. A production implementation should use embeddings and a vector
database.

## Retrieval query

The RAG query is constructed from the alarm context:

```text
alarm name
alarm message
operating procedure
maintenance troubleshooting
safety
```

Example:

```text
Boiler Feed Pump Low Flow Feed water flow below configured limit
operating procedure maintenance troubleshooting safety
```

## Filtering and ranking

Results are:

1. Ranked by cosine similarity.
2. Filtered using a minimum score threshold.
3. Limited to the requested top-K results.
4. Returned with document metadata and source citations.

If no result meets the minimum relevance threshold, the application returns:

```text
No sufficiently relevant documents were found.
```

## Citation construction

The GUI displays:

- Document ID
- Document type
- Document title
- Relevance score
- Retrieved passage
- Source path

Example citation:

```text
[PROC-BFP-001] Boiler Feed Pump Procedure
Source: rag/documents/boiler_feed_pump_procedure.md
Relevance: 0.5024
```

## Combined MCP and RAG workflow

RAG is invoked after MCP has retrieved structured alarm context:

```text
User question
    |
    v
MCP asset search
    |
    v
MCP alarm retrieval
    |
    v
MCP metadata, priority, recommendations, correlation
    |
    v
RAG query using alarm name and message
    |
    v
Combined grounded response
```

This ensures that document retrieval is connected to the actual alarm and asset
being investigated.

## Grounding behavior

The final response uses:

- Alarm severity and status from the Alarm API
- Priority from the priority tool
- Causes and actions from the recommendation tool
- Procedure and maintenance evidence from RAG
- Citations for every retrieved document passage

The application does not claim that an answer is procedure-approved merely
because a document was retrieved. Operators must verify guidance against
approved site procedures.

## Prompt-injection protection

Retrieved documents are treated as untrusted evidence.

The system must:

- Never execute instructions found inside a document.
- Never allow document text to override system or safety rules.
- Never allow retrieved content to invoke tools.
- Keep document content separate from tool arguments.
- Display document content as evidence with citations.

The current deterministic implementation does not execute document instructions.

## Index refresh

The index is rebuilt when the `RagRetriever` is initialized. To refresh the
index:

1. Add or update Markdown documents in `rag/documents/`.
2. Restart the copilot backend or rerun the ingestion process.
3. Verify retrieval using the RAG tests.

## Testing

RAG tests cover:

- Document loading
- Chunk creation
- Metadata extraction
- Relevant retrieval
- Citation metadata
- No-result behavior

Run:

```powershell
python -m pytest tests/unit/test_rag.py -q
```

## Limitations

- The corpus is small and synthetic.
- TF-IDF does not provide semantic understanding comparable to embeddings.
- No external vector database is currently used.
- No document approval workflow is implemented.
- No automatic document versioning is implemented.

## Future improvements

- Add a production embedding model.
- Add a vector database such as Qdrant, pgvector, or Elasticsearch.
- Add hybrid keyword and vector retrieval.
- Add reranking.
- Add document version filtering.
- Add document approval-state filtering.
- Add automated prompt-injection detection.
- Add scheduled index refresh.
- Add document ingestion metrics.
- Add retrieval evaluation datasets.
