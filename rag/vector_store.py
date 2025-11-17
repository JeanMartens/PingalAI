"""
Vector Store Wrapper
TODO: Implement ChromaDB wrapper
"""

import chromadb


class VectorStore:
    """Wrapper for ChromaDB - to be implemented"""
    
    def __init__(self, persist_directory: str, collection_name: str):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
    
    # TODO: Implement vector store methods
