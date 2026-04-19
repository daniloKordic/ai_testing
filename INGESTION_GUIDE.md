# Document Ingestion Guide

This guide explains how to ingest markdown documents into your Azure Search index.

## Setup

### 1. Ensure Documents Directory Exists

The ingestion script looks for markdown files in the `documents/` directory:

```
sample project/
├── documents/
│   ├── apples.md
│   ├── oranges.md
│   └── ...
├── ingest_documents.py
└── ...
```

### 2. Prepare Your Azure Search Index

Before ingesting, your Azure Search index must have the following fields:

```json
{
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false
    },
    {
      "name": "title",
      "type": "Edm.String",
      "searchable": true,
      "retrievable": true
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "retrievable": true
    },
    {
      "name": "file_path",
      "type": "Edm.String",
      "searchable": false,
      "retrievable": true
    },
    {
      "name": "file_name",
      "type": "Edm.String",
      "searchable": true,
      "retrievable": true
    }
  ]
}
```

### 3. Create Index via Azure Portal or CLI

**Using Azure CLI:**

```bash
az search index create \
  --service-name <your-search-service> \
  --resource-group <your-resource-group> \
  --index-definition @index_schema.json
```

**Using Azure Portal:**
1. Navigate to your Azure Search service
2. Click "Indexes" → "New Index"
3. Add the fields listed above
4. Save

## Ingesting Documents

### 1. Add Markdown Files

Place your markdown files in the `documents/` directory:

```bash
cp apples.md documents/
cp your_document.md documents/
```

### 2. Run the Ingestion Script

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run ingestion script
python ingest_documents.py
```

### 3. Verify Ingestion

Check that documents were successfully ingested:

```bash
# Using Azure CLI
az search documents show \
  --service-name <your-search-service> \
  --resource-group <your-resource-group> \
  --index-name sample_index \
  --id apples
```

## Document Format

Markdown files should contain:
- **Title**: First line should be a level 1 heading (`# Title`)
- **Content**: Well-structured markdown with sections and information
- **Encoding**: UTF-8

### Example:

```markdown
# Apples: Nature's Perfect Fruit

## Overview
Apples are...

## Characteristics
- Red apples...
- Green apples...

## Uses
1. Fresh consumption
2. Cooking
3. Processing
```

## Testing with the Chat API

Once documents are ingested, test them:

```bash
# In another terminal, run the API
.venv\Scripts\python.exe -m uvicorn src.main:app --reload

# Test search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "apple varieties", "top_k": 5}'

# Test chat
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are the different types of apples?"}
    ]
  }'
```

## Troubleshooting

### "unable to infer type for attribute"
- Ensure all fields in the index schema are properly typed
- Check that field names match exactly

### "Index not found"
- Verify `AZURE_SEARCH_INDEX_NAME` in `.env` matches your index name
- Create the index in Azure Search first

### "Authentication failed"
- Check `AZURE_SEARCH_ENDPOINT` and `AZURE_SEARCH_KEY` are correct in `.env`
- Regenerate keys if needed in Azure Portal

### "No results found"
- Verify documents were uploaded: `az search documents show ...`
- Try different search terms
- Ensure the index has documents before querying

## Adding More Documents

1. Create markdown files in the `documents/` directory
2. Run `python ingest_documents.py` again
3. Test via the API

## Next Steps

- Create more markdown documents about different topics
- Enhance the markdown with more detailed information
- Customize the ingestion script for your specific needs
- Implement document versioning or updates

---

For more information on Azure Search, visit: https://docs.microsoft.com/en-us/azure/search/
