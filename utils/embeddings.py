import logging

logger = logging.getLogger(__name__)

class EmbeddingHelper:
    _model = None

    @classmethod
    def get_model(cls):
        """Lazily load the SentenceTransformer model."""
        if cls._model is None:
            logger.info("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer: {e}")
                raise e
        return cls._model

    @classmethod
    def get_embedding(cls, text: str):
        """Generate vector embedding for a single text."""
        model = cls.get_model()
        # model.encode returns a numpy array, convert to list
        embedding = model.encode(text)
        return embedding

    @classmethod
    def get_embeddings(cls, texts: list[str]):
        """Generate vector embeddings for a list of texts."""
        model = cls.get_model()
        embeddings = model.encode(texts)
        return embeddings
