# Data Directory

This directory contains all data assets for the Agentic AI system.

## Structure

```
data/
├── chroma_db/           # ChromaDB persistent storage
│   └── test_collection/ # Vector database collection
│
├── embeddings/          # Pre-computed embeddings (optional)
│   └── bge_embeddings.pkl
│
└── raw_docs/           # Source documents for knowledge base
    ├── doxa_docs/      # Doxa documentation
    ├── faqs/           # FAQ documents
    └── manuals/        # User manuals
```

## ChromaDB Storage

The `chroma_db/` directory contains the persistent ChromaDB collections with:
- Document chunks
- BGE-M3 embeddings
- Metadata (source, timestamp, etc.)

**Current collections:**
- `test_collection`: Main Doxa knowledge base

## Raw Documents

Place source documents in `raw_docs/` for:
1. Initial knowledge base creation
2. Periodic updates
3. Version control of documentation

**Supported formats:**
- PDF
- Markdown
- Text files
- HTML

## Embeddings Cache

The `embeddings/` directory can store pre-computed embeddings for:
- Faster initialization
- Backup purposes
- Transfer between environments

## Usage

### Loading ChromaDB Collection

```python
from chromadb import PersistentClient

client = PersistentClient(path='data/chroma_db')
collection = client.get_collection(name="test_collection")
```

### Adding Documents

See `scripts/ingest_documents.py` for examples of adding new documents to the knowledge base.

## Notes

- This directory should NOT be committed to git (see .gitignore)
- Use version control for raw_docs only
- Back up chroma_db regularly
- Keep embeddings in sync with documents
