import os
import pickle
import numpy as np
import logging
from utils.embeddings import EmbeddingHelper

logger = logging.getLogger(__name__)

# Constants
VECTOR_STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vector_store'))
FAISS_INDEX_PATH = os.path.join(VECTOR_STORE_DIR, 'faiss_index.bin')
STORED_TEXTS_PATH = os.path.join(VECTOR_STORE_DIR, 'stored_texts.pkl')
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

class FAISSVectorStore:
    def __init__(self):
        self.index = None
        self.metadata_store = []
        self._ensure_store_dir()
        self._load_store()

    def _ensure_store_dir(self):
        """Create the vector store directory if it doesn't exist."""
        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

    def _load_store(self):
        """Load the FAISS index and metadata pickle from disk or create them."""
        import faiss

        # Load metadata first
        if os.path.exists(STORED_TEXTS_PATH):
            try:
                with open(STORED_TEXTS_PATH, 'rb') as f:
                    self.metadata_store = pickle.load(f)
                logger.info(f"Loaded {len(self.metadata_store)} history items from pickle.")
            except Exception as e:
                logger.error(f"Error loading pickle store, starting fresh: {e}")
                self.metadata_store = []
        else:
            self.metadata_store = []

        # Load FAISS Index
        if os.path.exists(FAISS_INDEX_PATH):
            try:
                self.index = faiss.read_index(FAISS_INDEX_PATH)
                logger.info("Loaded FAISS index from disk.")
            except Exception as e:
                logger.error(f"Error reading FAISS index, creating a new one: {e}")
                self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
        else:
            self.index = faiss.IndexFlatL2(EMBEDDING_DIM)

    def _save_store(self):
        """Save the FAISS index and metadata store to disk."""
        import faiss
        try:
            # Save metadata pickle
            with open(STORED_TEXTS_PATH, 'wb') as f:
                pickle.dump(self.metadata_store, f)
            
            # Save FAISS Index
            faiss.write_index(self.index, FAISS_INDEX_PATH)
            logger.info("Saved FAISS index and metadata store to disk.")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")

    def add_content(self, topic: str, content_type: str, tone: str, generated_content: str, keywords: str = ""):
        """
        Embed the generated content and save it with metadata to FAISS and Pickle storage.
        """
        # We will embed the topic and content combined to capture semantic meaning
        text_to_embed = f"Topic: {topic}. Content Type: {content_type}. Tone: {tone}. Content: {generated_content}"
        
        # Get embedding
        embedding = EmbeddingHelper.get_embedding(text_to_embed)
        embedding_np = np.array([embedding]).astype('float32')

        # Add to FAISS Index
        self.index.add(embedding_np)

        # Add to metadata store
        from datetime import datetime
        metadata = {
            'topic': topic,
            'content_type': content_type,
            'tone': tone,
            'generated_content': generated_content,
            'keywords': keywords,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.metadata_store.append(metadata)

        # Save to disk
        self._save_store()

    def search_similar(self, query_text: str, top_k: int = 3):
        """
        Search FAISS index for similar generated content.
        Returns a list of metadata dictionaries.
        """
        if self.index is None or self.index.ntotal == 0:
            logger.info("FAISS index is empty. No similarity search possible.")
            return []

        # Embed query text
        query_embedding = EmbeddingHelper.get_embedding(query_text)
        query_embedding_np = np.array([query_embedding]).astype('float32')

        # Search index
        # Cap top_k to the number of total elements
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding_np, k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.metadata_store):
                continue
            item = self.metadata_store[idx].copy()
            item['distance'] = float(distances[0][i])
            results.append(item)

        return results

    def get_all_history(self):
        """Get all stored content metadata sorted by timestamp descending."""
        # Reverse to show newest first
        return self.metadata_store[::-1]

    def clear_history(self):
        """Clear all database history and FAISS index."""
        import faiss
        self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
        self.metadata_store = []
        
        # Delete files from disk if they exist
        if os.path.exists(FAISS_INDEX_PATH):
            try:
                os.remove(FAISS_INDEX_PATH)
            except Exception as e:
                logger.error(f"Error removing FAISS index file: {e}")
        if os.path.exists(STORED_TEXTS_PATH):
            try:
                os.remove(STORED_TEXTS_PATH)
            except Exception as e:
                logger.error(f"Error removing stored texts file: {e}")
        
        logger.info("Cleared history and reset vector store.")
