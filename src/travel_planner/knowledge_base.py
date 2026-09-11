from __future__ import annotations

import os
from pathlib import Path
import re
import shutil

import httpx
from bs4 import BeautifulSoup
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .source_catalog import SINGAPORE_SOURCES


class TravelKnowledgeBase:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.persist_directory = project_root / "storage" / "chroma"
        self.collection_name = "singapore-travel"
        embedding_model = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001")
        self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
        self.vector_store: Chroma | None = None

    def ensure_ready(self, force_rebuild: bool = False) -> dict[str, int]:
        if force_rebuild and self.persist_directory.exists():
            shutil.rmtree(self.persist_directory)

        if not force_rebuild and self.persist_directory.exists() and any(self.persist_directory.iterdir()):
            self.vector_store = self._create_vector_store()
            return {"source_count": len(SINGAPORE_SOURCES), "chunk_count": 0}

        documents = self._load_documents()
        splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=180)
        chunks = splitter.split_documents(documents)
        self.vector_store = self._create_vector_store()
        self.vector_store.add_documents(chunks)
        return {"source_count": len(SINGAPORE_SOURCES), "chunk_count": len(chunks)}

    def retrieve(self, query: str, limit: int = 6) -> list[Document]:
        if self.vector_store is None:
            self.ensure_ready()
        assert self.vector_store is not None
        return self.vector_store.similarity_search(query, k=limit)

    def _create_vector_store(self) -> Chroma:
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        return Chroma(
            collection_name=self.collection_name,
            persist_directory=str(self.persist_directory),
            embedding_function=self.embeddings,
        )

    def _load_documents(self) -> list[Document]:
        documents: list[Document] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AI-Travel-Planning-Assistant/1.0)"
        }
        with httpx.Client(follow_redirects=True, timeout=30.0, headers=headers) as client:
            for source in SINGAPORE_SOURCES:
                response = client.get(source.url)
                response.raise_for_status()
                text = self._html_to_text(response.text)
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "title": source.title,
                            "url": source.url,
                            "category": source.category,
                        },
                    )
                )
        return documents

    @staticmethod
    def _html_to_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        container = soup.find("main") or soup.find("article") or soup.body or soup
        lines = [line.strip() for line in container.get_text("\n").splitlines()]
        filtered = [line for line in lines if line and len(line.split()) > 2]
        normalized = "\n".join(filtered)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized


def format_retrieved_documents(documents: list[Document]) -> str:
    if not documents:
        return "No destination knowledge was retrieved."

    sections = []
    for index, document in enumerate(documents, start=1):
        metadata = document.metadata
        excerpt = document.page_content[:900].strip()
        sections.append(
            f"Source {index}: {metadata.get('title', 'Unknown')}\n"
            f"URL: {metadata.get('url', 'Unknown')}\n"
            f"Content:\n{excerpt}"
        )
    return "\n\n".join(sections)


def collect_source_references(documents: list[Document]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    references: list[dict[str, str]] = []
    for document in documents:
        title = document.metadata.get("title", "Unknown")
        url = document.metadata.get("url", "Unknown")
        key = (title, url)
        if key in seen:
            continue
        seen.add(key)
        references.append({"title": title, "url": url})
    return references
