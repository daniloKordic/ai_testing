# 🍎 Fruit & Vegetable Knowledge Chat Application

A FastAPI-based chatbot that leverages Azure Search and Azure OpenAI to answer questions about fruits, vegetables, recipes, and nutrition. The application uses semantic search to find relevant documents and AI-powered responses with streaming capabilities.

## ✨ Features

- **Semantic Search Integration**: Uses Azure Cognitive Search to find relevant documents based on user queries
- **AI-Powered Responses**: Integrates Azure OpenAI GPT models for intelligent, context-aware answers
- **Streaming Responses**: Real-time streaming of AI responses for improved UX
- **Multi-turn Conversations**: Maintains conversation history for contextual follow-up questions
- **Source Document Display**: Shows the documents used to generate each response
- **Modern Web UI**: Clean, responsive frontend with gradient design and real-time updates
- **Comprehensive Knowledge Base**: 15+ documents covering fruits, vegetables, recipes, and nutrition
- **CORS Support**: Ready for cross-origin requests
- **Interactive API Documentation**: Built-in Swagger UI at `/docs`

## 📚 Knowledge Base

### Fruits
- Apples
- Bananas
- Berries (Strawberries, Blueberries, Raspberries, Blackberries, Cranberries)
- Oranges
- Tropical Fruits (Mango, Pineapple, Coconut, Papaya, Passion Fruit, Dragon Fruit)

### Vegetables
- Carrots
- Broccoli
- Tomatoes
- Leafy Greens (Spinach, Lettuce, Kale, Arugula, Swiss Chard)
- Peppers (Sweet and Spicy varieties)

### Recipes
- **Smoothie Recipes** (6 varieties)
- **Salad Recipes** (6 varieties)
- **Main Dish Recipes** (6 varieties)
- **Side Dishes & Snacks** (7 varieties)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Azure Cognitive Search account with API key
- Azure OpenAI account with API key and deployment
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd sample project
```

2. **Install dependencies**

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the project root:
```env
AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_SEARCH_KEY=<your-search-key>
AZURE_SEARCH_INDEX_NAME=fruits-vegetables
AZURE_OPENAI_ENDPOINT=https://<your-openai-instance>.openai.azure.com
AZURE_OPENAI_KEY=<your-openai-key>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

See `.env.example` for reference.

4. **Ingest documents into Azure Search**

```bash
uv run python ingest_documents.py
```

Or without `uv`:
```bash
python ingest_documents.py
```

This will:
- Read all `.md` files from the `documents/` folder
- Split them into chunks
- Upload to Azure Cognitive Search

5. **Start the FastAPI server**

```bash
.venv\Scripts\python -m uvicorn src.main:app --reload --port 8000  # Windows
python -m uvicorn src.main:app --reload --port 8000  # macOS/Linux
```

Server will be available at: `http://localhost:8000`

6. **Open the frontend**

Open `index.html` in your browser or serve it locally:

```bash
python -m http.server 8080 --directory .
```

Then visit: `http://localhost:8080`

## 🔌 API Endpoints

### 1. Health Check
```
GET /health
```
Returns application health status.

**Response:**
```json
{
  "status": "healthy"
}
```

### 2. Search Documents
```
POST /search
```
Search for relevant documents in Azure Search.

**Request Body:**
```json
{
  "query": "health benefits of oranges",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [...],
  "count": 5
}
```

### 3. Chat (Non-Streaming)
```
POST /chat
```
Get a complete AI response with sources.

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What are the health benefits of blueberries?"
    }
  ],
  "search_query": "optional search query"
}
```

**Response:**
```json
{
  "response": "Blueberries are packed with antioxidants...",
  "source_documents": [...]
}
```

### 4. Chat Streaming
```
POST /chat/stream
```
Stream AI responses in real-time (NDJSON format).

**Request Body:** (same as `/chat`)

**Response Stream (NDJSON):**
```json
{"type": "sources", "data": [...]}
{"type": "content", "data": "Blueberries are"}
{"type": "content", "data": " packed with"}
{"type": "content", "data": " antioxidants..."}
{"type": "done"}
```

### 5. Root Endpoint
```
GET /
```
Lists available endpoints and API information.

### Interactive API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🎯 Usage Examples

### Example 1: Ask about a fruit
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Tell me about oranges"}
    ]
  }'
```

### Example 2: Multi-turn conversation
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What vegetables are high in vitamin C?"
    },
    {
      "role": "assistant",
      "content": "Peppers, broccoli, and leafy greens are excellent sources of vitamin C..."
    },
    {
      "role": "user",
      "content": "How do I cook broccoli?"
    }
  ]
}
```

### Example 3: Ask for a recipe
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Give me a green smoothie recipe"
    }
  ],
  "search_query": "green smoothie recipe"
}
```

### Example 4: Stream response (Python)
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/chat/stream",
    json={
        "messages": [
            {"role": "user", "content": "What are the benefits of kale?"}
        ]
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if data["type"] == "content":
            print(data["data"], end="", flush=True)
```

## 🏗️ Project Structure

```
sample project/
├── documents/                 # Knowledge base documents
│   ├── apples.md
│   ├── bananas.md
│   ├── berries.md
│   ├── broccoli.md
│   ├── carrots.md
│   ├── leafy_greens.md
│   ├── main_dish_recipes.md
│   ├── oranges.md
│   ├── peppers.md
│   ├── salad_recipes.md
│   ├── side_snack_recipes.md
│   ├── smoothie_recipes.md
│   ├── tomatoes.md
│   └── tropical_fruits.md
├── src/                       # Backend source code
│   ├── __init__.py
│   ├── main.py               # FastAPI application
│   ├── models.py             # Pydantic data models
│   ├── config.py             # Configuration management
│   ├── azure_search_client.py # Azure Search integration
│   └── azure_openai_client.py # Azure OpenAI integration
├── index.html                # Frontend (single-file SPA)
├── ingest_documents.py       # Document ingestion script
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── README.md                # This file
└── .env.example             # Environment variables template
```

## ⚙️ Configuration

### Azure Search Setup

1. Create an Azure Cognitive Search service
2. Create an index with the following fields:
   - `id` (Edm.String) - key
   - `content` (Edm.String) - searchable
   - `filename` (Edm.String)
   - `source` (Edm.String)

3. Set index name in `.env` as `AZURE_SEARCH_INDEX_NAME`

### Azure OpenAI Setup

1. Create an Azure OpenAI resource
2. Deploy a GPT model (GPT-4 or GPT-3.5-turbo)
3. Get the deployment name and API version
4. Set in `.env` file

### Configuration Options

Edit `src/config.py` to modify:
- `max_tokens`: Maximum response length (default: 2048)
- `temperature`: Response creativity (0-2, default: 0.7)
- `api_version`: Azure OpenAI API version

## 📦 Dependencies

Key packages:
- **fastapi** - Modern web framework
- **uvicorn** - ASGI server
- **openai** - Azure OpenAI SDK
- **azure-search-documents** - Azure Cognitive Search SDK
- **pydantic** - Data validation
- **python-dotenv** - Environment variable management

See `requirements.txt` for full list and versions.

## 🧪 Testing

Run the test suite:
```bash
uv run pytest test_basic.py
```

Or with pip:
```bash
pytest test_basic.py
```

## 🔧 Development

### Adding New Documents

1. Create a new `.md` file in the `documents/` folder
2. Follow the existing format (headings, sections, etc.)
3. Run the ingestion script:
```bash
uv run python ingest_documents.py
```

### Modifying the Frontend

Edit `index.html` directly. Changes reload automatically in the browser.

### Adding New API Endpoints

Add new routes in `src/main.py`:
```python
@app.post("/your-endpoint")
async def your_endpoint(request: YourModel):
    """Your endpoint description."""
    # Your logic here
    return {"result": "..."}
```

## 🐛 Troubleshooting

### "AZURE_OPENAI_KEY is not set"
- Ensure `.env` file exists in the project root
- Check that all required environment variables are set
- Restart the application after updating `.env`

### "No module named 'src'"
- Ensure you're running from the project root directory
- Check that `src/__init__.py` exists

### 405 Method Not Allowed on streaming endpoint
- Ensure using `POST` not `GET` for `/chat/stream`
- Check the frontend is sending the correct HTTP method

### Streaming shows "Thinking..." but no response
- Check Azure OpenAI API is working with non-streaming endpoint
- Verify `stream=True` parameter in `azure_openai_client.py`
- Check browser console for JavaScript errors

### Documents not found in search
- Run `ingest_documents.py` to upload documents
- Verify Azure Search index name matches `.env` configuration
- Check Azure Search service is running and accessible

### "list index out of range" in streaming
- Ensure Azure OpenAI model is properly deployed
- Check API version compatibility in `.env`
- Try non-streaming endpoint to isolate the issue

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_SEARCH_ENDPOINT` | Azure Search service endpoint | `https://myservice.search.windows.net` |
| `AZURE_SEARCH_KEY` | Azure Search API key | `abc123...` |
| `AZURE_SEARCH_INDEX_NAME` | Search index name | `fruits-vegetables` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | `https://my-openai.openai.azure.com` |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key | `xyz789...` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name | `gpt-4` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-02-15-preview` |

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Cognitive Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Last Updated**: April 2026  
**Python Version**: 3.9+  
**Status**: Active Development
