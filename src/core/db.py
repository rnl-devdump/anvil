# src/core/db.py
import os

import chromadb
import ollama

from src.core.config import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL, RAG_TOP_K
from src.core.file import File


class Db:

    def __init__(self):

        os.makedirs(CHROMA_PATH, exist_ok=True)

        self.client = chromadb.PersistentClient(path=CHROMA_PATH)

        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

        self._current_source: str | None = None


    def _embed_text(self, text: str) -> list[float]:

        response = ollama.embed(model=EMBED_MODEL, input=text)

        return response["embeddings"][0]


    def clear_document(self, source: str) -> None:
        """Remove prior chunks for the same source before re-embedding."""

        existing = self.collection.get(where={"source": source})

        if existing["ids"]:

            self.collection.delete(ids=existing["ids"])


    def embed(self, file_instance: File) -> int:

        chunks = file_instance.get_chunks()

        if not chunks:

            return 0


        source = file_instance.display_name

        self.clear_document(source)

        self._current_source = source


        embedded = 0

        for i, (page_num, text) in enumerate(chunks):

            cleaned_text = " ".join(text.replace("\n", " ").split()).strip()

            if len(cleaned_text) < 10:
                continue


            vector = self._embed_text(cleaned_text)

            unique_id = f"{source}_chunk_{i}"


            self.collection.upsert(
                ids=[unique_id],
                embeddings=[vector],
                documents=[cleaned_text],
                metadatas=[{"page": page_num, "source": source}],
            )

            embedded += 1


        return embedded


    def query(self, question: str, n_results: int = RAG_TOP_K) -> list[str]:

        if self.collection.count() == 0:

            return []


        query_vector = self._embed_text(question)

        where = {"source": self._current_source} if self._current_source else None


        results = self.collection.query(
            query_embeddings=[query_vector],

            n_results=min(n_results, self.collection.count()),
            where=where,
        )


        documents = results.get("documents") or [[]]

        return [doc for doc in documents[0] if doc]


    @property

    def chunk_count(self) -> int:

        return self.collection.count()


    @property

    def current_source(self) -> str | None:

        return self._current_source
