"""
Vector Store Manager using FAISS
Handles embedding generation and vector indexing
"""

import os
import json
import numpy as np
import pickle
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss

class VectorStoreManager:
    """Manages FAISS vector store for document embeddings"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2', index_dir='data/vector_store'):
        """
        Initialize vector store manager
        
        Args:
            model_name: Name of sentence-transformers model
            index_dir: Directory to store FAISS index and metadata
        """
        self.model_name = model_name
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        self.index = None
        self.documents = []
        self.metadata = []
        
    def create_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Create embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for encoding
            
        Returns:
            numpy array of embeddings
        """
        print(f"Creating embeddings for {len(texts)} documents...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def build_index(self, documents: List[Dict]):
        """
        Build FAISS index from documents
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata'
        """
        print("Building FAISS index...")
        
        # Extract texts and metadata
        texts = [doc['text'] for doc in documents]
        self.documents = texts
        self.metadata = [doc.get('metadata', {}) for doc in documents]
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Create FAISS index
        # Using IndexFlatL2 for exact search (can be changed to IndexIVFFlat for faster approximate search)
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        print(f"Index built with {self.index.ntotal} vectors")
        
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        print("Saving index and metadata...")
        
        # Save FAISS index
        index_path = os.path.join(self.index_dir, 'faiss_index.bin')
        faiss.write_index(self.index, index_path)
        
        # Save documents and metadata
        data_path = os.path.join(self.index_dir, 'documents_metadata.pkl')
        with open(data_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'model_name': self.model_name,
                'embedding_dim': self.embedding_dim
            }, f)
        
        print(f"Index saved to: {index_path}")
        print(f"Metadata saved to: {data_path}")
    
    def load_index(self):
        """Load FAISS index and metadata from disk"""
        print("Loading index and metadata...")
        
        index_path = os.path.join(self.index_dir, 'faiss_index.bin')
        data_path = os.path.join(self.index_dir, 'documents_metadata.pkl')
        
        if not os.path.exists(index_path) or not os.path.exists(data_path):
            raise FileNotFoundError("Index files not found. Please build index first.")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load documents and metadata
        with open(data_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
            saved_model_name = data['model_name']
            
            if saved_model_name != self.model_name:
                print(f"Warning: Loaded index was created with {saved_model_name}, but current model is {self.model_name}")
        
        print(f"Loaded index with {self.index.ntotal} vectors")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict, float]]:
        """
        Search for similar documents
        
        Args:
            query: Query text
            top_k: Number of top results to return
            
        Returns:
            List of tuples (document_text, metadata, similarity_score)
        """
        if self.index is None:
            raise ValueError("Index not loaded. Please load or build index first.")
        
        # Create query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score (inverse)
                similarity = 1 / (1 + distance)
                results.append((
                    self.documents[idx],
                    self.metadata[idx],
                    float(similarity)
                ))
        
        return results
    
    def search_by_filter(self, query: str, filter_func, top_k: int = 20) -> List[Tuple[str, Dict, float]]:
        """
        Search with metadata filtering
        
        Args:
            query: Query text
            filter_func: Function that takes metadata dict and returns True/False
            top_k: Number of results to retrieve before filtering
            
        Returns:
            List of filtered results
        """
        # Get more results than needed
        results = self.search(query, top_k=top_k * 2)
        
        # Apply filter
        filtered_results = [
            (doc, meta, score) 
            for doc, meta, score in results 
            if filter_func(meta)
        ]
        
        return filtered_results[:top_k]


class MultiIndexManager:
    """Manages separate indices for CSV and PDF data"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2', index_dir='data/vector_store'):
        self.csv_store = VectorStoreManager(model_name, os.path.join(index_dir, 'csv'))
        self.pdf_store = VectorStoreManager(model_name, os.path.join(index_dir, 'pdf'))
        
    def build_indices(self, csv_documents_path: str, pdf_documents_path: str):
        """Build both CSV and PDF indices"""
        print("="*60)
        print("BUILDING MULTI-INDEX VECTOR STORE")
        print("="*60)
        
        # Load CSV documents
        if os.path.exists(csv_documents_path):
            print("\nProcessing CSV documents...")
            with open(csv_documents_path, 'r') as f:
                csv_docs = json.load(f)
            self.csv_store.build_index(csv_docs)
            self.csv_store.save_index()
        else:
            print(f"Warning: CSV documents not found at {csv_documents_path}")
        
        # Load PDF documents
        if os.path.exists(pdf_documents_path):
            print("\nProcessing PDF documents...")
            with open(pdf_documents_path, 'r', encoding='utf-8') as f:
                pdf_docs = json.load(f)
            self.pdf_store.build_index(pdf_docs)
            self.pdf_store.save_index()
        else:
            print(f"Warning: PDF documents not found at {pdf_documents_path}")
        
        print("="*60)
        print("MULTI-INDEX BUILD COMPLETE")
        print("="*60)
    
    def load_indices(self):
        """Load both indices"""
        try:
            self.csv_store.load_index()
        except FileNotFoundError:
            print("Warning: CSV index not found")
        
        try:
            self.pdf_store.load_index()
        except FileNotFoundError:
            print("Warning: PDF index not found")
    
    def search_csv(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict, float]]:
        """Search CSV data"""
        return self.csv_store.search(query, top_k)
    
    def search_pdf(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict, float]]:
        """Search PDF data"""
        return self.pdf_store.search(query, top_k)
    
    def search_both(self, query: str, top_k: int = 5) -> Dict[str, List[Tuple[str, Dict, float]]]:
        """Search both indices and return combined results"""
        return {
            'csv': self.csv_store.search(query, top_k),
            'pdf': self.pdf_store.search(query, top_k)
        }


def build_vector_stores():
    """Main function to build all vector stores"""
    processed_dir = 'data/processed'
    
    csv_docs_path = os.path.join(processed_dir, 'documents.json')
    pdf_docs_path = os.path.join(processed_dir, 'pdf_documents.json')
    
    manager = MultiIndexManager()
    manager.build_indices(csv_docs_path, pdf_docs_path)
    
    print("\nVector stores built successfully!")


if __name__ == "__main__":
    build_vector_stores()
