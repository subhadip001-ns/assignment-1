import os
from typing import List, Dict, Any
from pathlib import Path
import json

from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
try:
    # Newer community path/class name
    from langchain_community.embeddings import VoyageEmbeddings as VoyageAIEmbeddings
except Exception:  # pragma: no cover
    # Fallback for alternate module path
    from langchain_community.embeddings.voyageai import VoyageEmbeddings as VoyageAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RAGService:
    """RAG (Retrieval-Augmented Generation) service for course information"""

    def __init__(self):
        # Single global vector store name
        self.store_name = "admin-vector-store"

        # Create cache directory
        self.cache_dir = Path("data/embeddings_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # JSON persistence file for all docs across the app
        self.persist_path = Path("data") / f"{self.store_name}.json"
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize underlying embeddings (Voyage AI)
        self.underlying_embeddings = VoyageAIEmbeddings(
            voyage_api_key=os.getenv("VOYAGE_AI_API_KEY"),
            model="voyage-3"
        )

        # Create local file store for caching
        self.fs = LocalFileStore(str(self.cache_dir))

        # Create cached embeddings
        self.embeddings = CacheBackedEmbeddings.from_bytes_store(
            self.underlying_embeddings,
            self.fs,
            namespace="course_embeddings"
        )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

        # Initialize in-memory vector store
        self.vector_store = InMemoryVectorStore(embedding=self.embeddings)

        # Load persisted documents (re-embeds via cache if needed)
        self._load_persisted_docs_into_store()

    def _load_persisted_docs_into_store(self) -> None:
        """Load all previously persisted documents into the single admin vector store.

        We persist only page_content + metadata in JSON. On load, we re-add Documents
        to the in-memory store; embeddings are resolved via the cache backend.
        """
        try:
            if self.persist_path.exists():
                with self.persist_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    docs = [Document(page_content=d.get("page_content", ""), metadata=d.get("metadata", {})) for d in data]
                    if docs:
                        self.vector_store.add_documents(docs)
        except Exception as e:
            print(f"Warning: failed loading persisted docs into {self.store_name}: {e}")

    def _append_docs_to_persist(self, docs: List[Document]) -> None:
        """Append newly ingested documents to the JSON persistence file."""
        try:
            existing: List[Dict[str, Any]] = []
            if self.persist_path.exists():
                with self.persist_path.open("r", encoding="utf-8") as f:
                    try:
                        existing = json.load(f) or []
                    except Exception:
                        existing = []

            to_add = [
                {"page_content": d.page_content, "metadata": d.metadata}
                for d in docs
            ]
            existing.extend(to_add)
            with self.persist_path.open("w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: failed persisting docs into {self.store_name}: {e}")

    def ingest_course_document(self, course_id: int, course_name: str, course_description: str):
        """
        Ingest a course document into the vector store

        Args:
            course_id: The course ID
            course_name: The course name
            course_description: The course description
        """
        try:
            # Create document content
            content = f"""
Course Name: {course_name}

Course Description: {course_description}

Course ID: {course_id}
"""

            # Create document
            doc = Document(
                page_content=content,
                metadata={
                    "course_id": course_id,
                    "course_name": course_name,
                    "type": "course",
                    "source": f"course_{course_id}"
                }
            )

            # Split document into chunks
            docs = self.text_splitter.split_documents([doc])

            # Add to single global in-memory vector store and persist to JSON
            if docs:
                self.vector_store.add_documents(docs)
                self._append_docs_to_persist(docs)
                print(f"Successfully ingested course {course_id}: {course_name} -> {self.store_name}")

        except Exception as e:
            print(f"Error ingesting course {course_id}: {e}")
            raise

    def search_courses(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant courses based on the query

        Args:
            query: The search query
            k: Number of results to return

        Returns:
            List of course information dictionaries
        """
        try:
            # Search vector store
            docs = self.vector_store.similarity_search(query, k=k)

            # Format results
            results = []
            for doc in docs:
                metadata = doc.metadata
                content = doc.page_content

                # Extract course information
                lines = content.split('\n')
                course_info = {
                    "course_id": metadata.get("course_id"),
                    "course_name": metadata.get("course_name"),
                    "description": "",
                    "relevance_score": 0  # InMemoryVectorStore doesn't provide scores
                }

                # Extract description from content
                for line in lines:
                    if line.startswith("Course Description:"):
                        course_info["description"] = line.replace("Course Description:", "").strip()
                        break

                results.append(course_info)

            return results

        except Exception as e:
            print(f"Error searching courses: {e}")
            return []

    def get_course_context(self, query: str, max_results: int = 3) -> str:
        """
        Get formatted context about courses for the LLM

        Args:
            query: The search query
            max_results: Maximum number of courses to include

        Returns:
            Formatted context string
        """
        try:
            results = self.search_courses(query, k=max_results)

            if not results:
                return "No relevant course information found."

            context_parts = []
            for i, course in enumerate(results, 1):
                context_parts.append(f"""
Course {i}:
- Name: {course['course_name']}
- ID: {course['course_id']}
- Description: {course['description']}
""")

            return "Here are the most relevant courses:\n" + "\n".join(context_parts)

        except Exception as e:
            return f"Error retrieving course context: {str(e)}"


# Singleton instance
rag_service = RAGService()
