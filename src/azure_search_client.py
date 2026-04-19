"""Azure Search client for querying documents."""

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from typing import Optional
from src.config import settings


class AzureSearchClient:
    """Client for interacting with Azure Search."""

    def __init__(self):
        """Initialize Azure Search client."""
        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=AzureKeyCredential(settings.azure_search_key),
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Search for documents matching the query.

        Args:
            query: Search query string
            top_k: Number of top results to return

        Returns:
            List of search results
        """
        try:
            results = self.client.search(search_text=query, top=top_k)
            documents = []
            for result in results:
                documents.append(result)
            return documents
        except Exception as e:
            print(f"Error searching Azure Search: {e}")
            return []

    def get_document(self, doc_id: str) -> Optional[dict]:
        """
        Retrieve a specific document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document content or None
        """
        try:
            result = self.client.get_document(key=doc_id)
            return result
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None
