"""Azure OpenAI client for chat completions."""

import logging
from openai import AzureOpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI."""

    def __init__(self):
        """Initialize Azure OpenAI client."""
        try:
            # Validate required settings
            if not settings.azure_openai_key:
                raise ValueError("AZURE_OPENAI_KEY is not set in environment variables")
            if not settings.azure_openai_endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT is not set in environment variables")
            if not settings.azure_openai_deployment_name:
                raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME is not set in environment variables")
            
            # Debug: Log the values being used
            logger.info(f"Azure OpenAI Configuration:")
            logger.info(f"  Endpoint: {settings.azure_openai_endpoint}")
            logger.info(f"  Deployment: {settings.azure_openai_deployment_name}")
            logger.info(f"  API Version: {settings.azure_openai_api_version}")
            logger.info(f"  API Key (first 20 chars): {settings.azure_openai_key[:20]}...")
            
            # Ensure endpoint doesn't have trailing slash
            endpoint = settings.azure_openai_endpoint
            if endpoint.endswith('/'):
                endpoint = endpoint.rstrip('/')
                logger.info(f"  Removed trailing slash from endpoint: {endpoint}")
            
            self.client = AzureOpenAI(
                api_key=settings.azure_openai_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=endpoint,
            )
            self.deployment_name = settings.azure_openai_deployment_name
            logger.info(f"✓ Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Azure OpenAI client: {str(e)}", exc_info=True)
            raise

    def get_chat_completion(
        self, messages: list[dict], max_tokens: int = None
    ) -> str:
        """
        Get chat completion from Azure OpenAI.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response

        Returns:
            Response text from the model
        """
        if max_tokens is None:
            max_tokens = settings.max_tokens

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=settings.temperature,
                max_completion_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting chat completion: {e}")
            raise

    def get_chat_completion_stream(self, messages: list[dict], max_tokens: int = None):
        """
        Stream chat completion from Azure OpenAI.
        
        Yields chunks of the response as they arrive.
        """
        if max_tokens is None:
            max_tokens = settings.max_tokens

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=settings.temperature,
                max_completion_tokens=max_tokens,
                stream=True,  # Enable streaming
            )
            
            for chunk in response:
                # Check if choices exist and have content
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and hasattr(delta, 'content') and delta.content:
                        yield delta.content
        except Exception as e:
            logger.error(f"Error streaming chat completion: {e}", exc_info=True)
            raise

    def create_context_prompt(
        self, user_query: str, documents: list[dict]
    ) -> str:
        """
        Create a prompt with context from retrieved documents.

        Args:
            user_query: Original user query
            documents: Retrieved documents from Azure Search

        Returns:
            Formatted prompt with context
        """
        context = "\n\n".join(
            [f"Document: {doc}" for doc in documents[:3]]  # Limit to top 3
        )

        prompt = f"""Based on the following documents, answer the user's question:

Documents:
{context}

User Question: {user_query}

Please provide a comprehensive answer based on the documents provided."""

        return prompt
