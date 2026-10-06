from rag.retrieval import RagRetriever


def test_rag_retrieves_pump_procedure():
    retriever = RagRetriever("./rag/documents")

    results = retriever.search(
        "boiler feed pump low flow suction strainer procedure",
        top_k=3,
    )

    assert results
    assert any(
        "BFP" in result["document_id"]
        for result in results
    )


def test_rag_returns_empty_for_unknown_query():
    retriever = RagRetriever("./rag/documents")

    results = retriever.search(
        "quantum spaceship navigation",
        top_k=3,
    )

    assert results == []
