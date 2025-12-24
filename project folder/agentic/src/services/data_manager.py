"""
Data management utilities for ChromaDB operations
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from chromadb import PersistentClient
from FlagEmbedding import BGEM3FlagModel
import json

from ..config.settings import settings


class ChromaDBManager:
    """Manager for ChromaDB operations and data ingestion"""
    
    def __init__(self, persist_path: str = None):
        """
        Initialize ChromaDB manager.
        
        Args:
            persist_path: Path to ChromaDB storage (defaults to settings)
        """
        self.persist_path = persist_path or settings.CHROMA_PERSIST_PATH
        self.client = PersistentClient(path=self.persist_path)
        self.bge_model = BGEM3FlagModel(
            settings.BGE_MODEL_NAME,
            use_fp16=settings.BGE_USE_FP16
        )
    
    def create_collection(self, name: str, metadata: Dict = None) -> None:
        """
        Create a new ChromaDB collection.
        
        Args:
            name: Collection name
            metadata: Optional metadata for the collection
        """
        try:
            collection = self.client.get_collection(name=name)
            print(f"Collection '{name}' already exists")
        except:
            collection = self.client.create_collection(
                name=name,
                metadata=metadata or {}
            )
            print(f"Created collection: {name}")
    
    def delete_collection(self, name: str) -> None:
        """Delete a collection"""
        self.client.delete_collection(name=name)
        print(f"Deleted collection: {name}")
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def get_collection_info(self, name: str) -> Dict:
        """Get information about a collection"""
        collection = self.client.get_collection(name=name)
        count = collection.count()
        metadata = collection.metadata
        
        return {
            "name": name,
            "document_count": count,
            "metadata": metadata
        }
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict] = None,
        ids: List[str] = None
    ) -> None:
        """
        Add documents to a collection with BGE embeddings.
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
        """
        collection = self.client.get_collection(name=collection_name)
        
        # Generate embeddings
        print(f"Generating embeddings for {len(documents)} documents...")
        embeddings_result = self.bge_model.encode(
            documents,
            batch_size=12,
            max_length=settings.BGE_MAX_LENGTH
        )
        embeddings = embeddings_result["dense_vecs"]
        
        # Generate IDs if not provided
        if ids is None:
            start_id = collection.count()
            ids = [f"doc_{start_id + i}" for i in range(len(documents))]
        
        # Add to collection
        collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(documents)} documents to '{collection_name}'")
    
    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = None
    ) -> Dict:
        """
        Query a collection with a text query.
        
        Args:
            collection_name: Name of the collection
            query_text: Query text
            n_results: Number of results (defaults to settings)
            
        Returns:
            Query results dict
        """
        collection = self.client.get_collection(name=collection_name)
        n_results = n_results or settings.CHROMA_N_RESULTS
        
        # Generate query embedding
        query_embedding = self.bge_model.encode(
            [query_text],
            batch_size=1,
            max_length=settings.BGE_MAX_LENGTH
        )["dense_vecs"][0]
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        return results
    
    def update_document(
        self,
        collection_name: str,
        doc_id: str,
        document: str = None,
        metadata: Dict = None
    ) -> None:
        """
        Update a document in the collection.
        
        Args:
            collection_name: Name of the collection
            doc_id: Document ID to update
            document: New document text (optional)
            metadata: New metadata (optional)
        """
        collection = self.client.get_collection(name=collection_name)
        
        update_params = {"ids": [doc_id]}
        
        if document:
            # Generate new embedding
            embedding = self.bge_model.encode(
                [document],
                batch_size=1,
                max_length=settings.BGE_MAX_LENGTH
            )["dense_vecs"][0]
            
            update_params["documents"] = [document]
            update_params["embeddings"] = [embedding.tolist()]
        
        if metadata:
            update_params["metadatas"] = [metadata]
        
        collection.update(**update_params)
        print(f"Updated document '{doc_id}' in '{collection_name}'")
    
    def delete_documents(self, collection_name: str, ids: List[str]) -> None:
        """Delete documents from collection"""
        collection = self.client.get_collection(name=collection_name)
        collection.delete(ids=ids)
        print(f"Deleted {len(ids)} documents from '{collection_name}'")
    
    def export_collection(self, collection_name: str, output_path: str) -> None:
        """
        Export collection to JSON file.
        
        Args:
            collection_name: Name of collection
            output_path: Path to output JSON file
        """
        collection = self.client.get_collection(name=collection_name)
        data = collection.get()
        
        export_data = {
            "collection_name": collection_name,
            "metadata": collection.metadata,
            "documents": data["documents"],
            "metadatas": data["metadatas"],
            "ids": data["ids"]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported '{collection_name}' to {output_path}")
    
    def import_collection(self, json_path: str) -> None:
        """
        Import collection from JSON file.
        
        Args:
            json_path: Path to JSON file
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        collection_name = data["collection_name"]
        
        # Create collection if doesn't exist
        try:
            self.create_collection(collection_name, data.get("metadata"))
        except:
            pass
        
        # Add documents
        self.add_documents(
            collection_name=collection_name,
            documents=data["documents"],
            metadatas=data.get("metadatas"),
            ids=data["ids"]
        )
        
        print(f"Imported '{collection_name}' from {json_path}")


# Global instance
chroma_manager = ChromaDBManager()
