from dataclasses import dataclass
from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    title: str
    document_type: str
    text: str
    source: str


class RagRetriever:
    def __init__(self, document_path: str):
        self.document_path = Path(document_path)
        self.chunks: list[Chunk] = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self.ingest()

    def ingest(self):
        self.chunks.clear()

        for path in self.document_path.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            title = path.stem.replace("_", " ").title()

            document_id_match = re.search(
                r"Document ID:\s*(.+)",
                text,
                flags=re.IGNORECASE,
            )
            document_type_match = re.search(
                r"Document Type:\s*(.+)",
                text,
                flags=re.IGNORECASE,
            )

            document_id = (
                document_id_match.group(1).strip()
                if document_id_match
                else path.stem
            )
            document_type = (
                document_type_match.group(1).strip()
                if document_type_match
                else "Unknown"
            )

            sections = re.split(r"\n## ", text)

            for index, section in enumerate(sections):
                clean = section.strip()

                if len(clean) < 30:
                    continue

                self.chunks.append(
                    Chunk(
                        chunk_id=f"{document_id}-{index}",
                        document_id=document_id,
                        title=title,
                        document_type=document_type,
                        text=clean,
                        source=str(path),
                    )
                )

        if self.chunks:
            self.matrix = self.vectorizer.fit_transform(
                [chunk.text for chunk in self.chunks]
            )

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_type: str | None = None,
    ) -> list[dict]:
        if not self.chunks or self.matrix is None:
            return []

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]

        ranked_indexes = scores.argsort()[::-1]

        results = []

        for index in ranked_indexes:
            chunk = self.chunks[index]

            if document_type and chunk.document_type != document_type:
                continue

            score = float(scores[index])

            if score < 0.05:
                continue

            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "title": chunk.title,
                    "document_type": chunk.document_type,
                    "text": chunk.text,
                    "source": chunk.source,
                    "score": round(score, 4),
                }
            )

            if len(results) >= top_k:
                break

        return results
