"""Script to ingest markdown documents into Azure Search."""

import os
import json
from pathlib import Path
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Azure Search client
endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(key),
)


def read_markdown_file(file_path: str) -> dict:
    """Read markdown file and prepare for indexing."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title from first heading
    lines = content.split("\n")
    title = lines[0].replace("# ", "").strip() if lines[0].startswith("#") else "Untitled"

    # Create document
    doc_id = Path(file_path).stem
    document = {
        "id": doc_id,
        "title": title,
        "content": content,
        "file_path": file_path,
        "file_name": Path(file_path).name,
    }

    return document


def ingest_documents(documents_dir: str = "documents"):
    """Ingest all markdown files from documents directory."""
    documents_path = Path(documents_dir)

    if not documents_path.exists():
        print(f"Documents directory '{documents_dir}' not found.")
        return

    md_files = list(documents_path.glob("*.md"))

    if not md_files:
        print(f"No markdown files found in '{documents_dir}'")
        return

    print(f"Found {len(md_files)} markdown file(s) to ingest...")

    documents = []
    for md_file in md_files:
        print(f"  Processing: {md_file.name}")
        doc = read_markdown_file(str(md_file))
        documents.append(doc)

    # Upload documents to Azure Search
    try:
        result = client.upload_documents(documents)
        print(f"\n✓ Successfully uploaded {len(documents)} document(s)")
        print(f"  Upload result: {result}")
    except Exception as e:
        print(f"\n✗ Error uploading documents: {e}")


if __name__ == "__main__":
    print("Azure Search Document Ingestion Script")
    print("=" * 40)
    print(f"Endpoint: {endpoint}")
    print(f"Index: {index_name}")
    print("=" * 40)

    ingest_documents()
