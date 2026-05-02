"""Main FastAPI application for Azure Search + OpenAI chatbot."""

import logging
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.models import SearchQuery, ChatRequest, ChatResponse
from src.azure_search_client import AzureSearchClient
from src.azure_openai_client import AzureOpenAIClient
import json
from fastapi.responses import StreamingResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Azure Search ChatGPT",
    description="Chat with your Azure Search index using Azure OpenAI",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialize clients
search_client = None
openai_client = None


def get_search_client():
    """Get or initialize search client."""
    global search_client
    if search_client is None:
        search_client = AzureSearchClient()
    return search_client


def get_openai_client():
    """Get or initialize OpenAI client."""
    global openai_client
    if openai_client is None:
        openai_client = AzureOpenAIClient()
    return openai_client


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/search")
async def search(query: SearchQuery):
    """
    Search for documents in Azure Search.

    Args:
        query: Search query details

    Returns:
        List of matching documents
    """
    client = get_search_client()
    results = client.search(query.query, top_k=query.top_k)
    return {"results": results, "count": len(results)}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that searches Azure Search and uses Azure OpenAI to generate responses.

    Args:
        request: Chat request with messages and optional search query

    Returns:
        Chat response with AI-generated answer and source documents
    """
    try:
        # Determine search query
        search_query = request.search_query or request.messages[-1].content

        # Search for relevant documents
        search = get_search_client()
        documents = search.search(search_query, top_k=5)

        # Convert documents to list of dicts if they're Pydantic models
        doc_list = []
        for doc in documents:
            if isinstance(doc, dict):
                doc_list.append(doc)
            else:
                # If it's a Pydantic model, convert to dict
                doc_list.append(doc.model_dump() if hasattr(doc, 'model_dump') else doc.__dict__)

        doc_refs = []
        for doc in documents:
            doc_dict = doc if isinstance(doc, dict) else (doc.model_dump() if hasattr(doc, 'model_dump') else doc.__dict__)
            doc_refs.append({
                "id": doc_dict.get("id") or doc_dict.get("document_id") or doc_dict.get("key"),
                "title": doc_dict.get("title") or doc_dict.get("name") or doc_dict.get("filename") or doc_dict.get("metadata_storage_name"),
                "path": doc_dict.get("file_path") or doc_dict.get("metadata_storage_path"),
            })

        # Extract document content for context (limiting to first 3 for prompt)
        doc_contents = [str(doc) for doc in doc_list[:3]]

        # Create context-aware system message
        system_message = {
            "role": "system",
            "content": f"""You are a helpful AI assistant that answers questions based on provided documents.
        
Available documents context:
{chr(10).join([f"- {doc}" for doc in doc_contents])}

Answer questions based on this context. If the information is not in the documents, say so.""",
        }

        # Prepare messages for OpenAI
        messages = [system_message]
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})
        logger.info(f"Prepared messages for OpenAI: {messages}")
        # Get response from Azure OpenAI
        openai = get_openai_client()
        logger.info("Sending request to Azure OpenAI...")
        response_text = openai.get_chat_completion(messages)

        logger.info(f"User Query: {search_query}")
        logger.info(f"Retrieved Documents: {doc_contents}")
        logger.info(f"AI Response: {response_text}")
        
        return ChatResponse(
            response=response_text,
            source_documents=doc_refs,  # Return documents as list of dicts
        )
    except Exception as e:
        import traceback
        error_msg = f"Error in chat endpoint: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint."""
    try:
        search_query = request.search_query or request.messages[-1].content
        search = get_search_client()
        documents = search.search(search_query, top_k=5)
        
        # Prepare documents (same as before)
        doc_list = []
        for doc in documents:
            if isinstance(doc, dict):
                doc_list.append(doc)
            else:
                doc_list.append(doc.model_dump() if hasattr(doc, 'model_dump') else doc.__dict__)

        doc_refs = []
        for doc in documents:
            doc_dict = doc if isinstance(doc, dict) else (doc.model_dump() if hasattr(doc, 'model_dump') else doc.__dict__)
            logger.info(f"Document dict: {doc_dict}")
            doc_refs.append({
                "id": doc_dict.get("id") or doc_dict.get("document_id") or doc_dict.get("key"),
                "title": doc_dict.get("title") or doc_dict.get("name") or doc_dict.get("filename") or doc_dict.get("metadata_storage_name"),
                "path": doc_dict.get("file_path") or doc_dict.get("metadata_storage_path"),
            })
        
        doc_contents = [str(doc) for doc in doc_list[:3]]
        
        system_message = {
            "role": "system",
            "content": f"""You are a helpful AI assistant that answers questions based on provided documents.
Available documents context:
{chr(10).join([f"- {doc}" for doc in doc_contents])}
Answer questions based on this context. If the information is not in the documents, say so.""",
        }
        
        messages = [system_message]
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Create generator function
        async def generate():
            # Send initial metadata
            yield json.dumps({"type": "sources", "data": doc_refs}) + "\n"
            
            # Stream the response
            openai = get_openai_client()
            for chunk in openai.get_chat_completion_stream(messages):
                try:
                    # Handle Azure OpenAI choice objects
                    if hasattr(chunk, 'choices') and chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            # Safely escape and encode
                            yield json.dumps({"type": "content", "data": content}) + "\n"
                    # Fallback for string chunks
                    elif isinstance(chunk, str) and chunk.strip():
                        yield json.dumps({"type": "content", "data": chunk}) + "\n"
                except Exception as e:
                    logger.error(f"Error processing chunk: {e}, chunk: {chunk}")
                    continue
            
            # Send completion signal
            yield json.dumps({"type": "done"}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
    except Exception as e:
        logger.error(f"Error in streaming chat: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Azure Search ChatGPT API",
        "endpoints": {
            "health": "/health",
            "search": "/search (POST)",
            "chat": "/chat (POST)",
            "docs": "/docs",
        },
    }

# To run the app from sample_project directory:
# .venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8002
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
