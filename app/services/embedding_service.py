"""Embedding Service to generate text embeddings locally using Hugging Face transformers.
"""

import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Union
from loguru import logger
from app.core.config import settings


class EmbeddingService:
    """Service to generate dense vector representations from text queries and event summaries."""
    
    _tokenizer = None
    _model = None
    _device = None
    _mock_mode = False

    @classmethod
    def initialize(cls):
        """Pre-initialize and load tokenizer/model in memory."""
        if cls._model is not None or cls._mock_mode:
            return

        if settings.MOCK_MODEL:
            logger.info("Mock model mode is enabled. Skipping weights download and loading for EmbeddingService.")
            cls._mock_mode = True
            return

        model_id = settings.EMBEDDING_MODEL_ID
        logger.info(f"Initializing EmbeddingService with model: {model_id}")
        
        try:
            if torch.cuda.is_available():
                cls._device = "cuda"
            else:
                cls._device = "cpu"
            logger.info(f"EmbeddingService using device: {cls._device}")

            cls._tokenizer = AutoTokenizer.from_pretrained(model_id)
            cls._model = AutoModel.from_pretrained(model_id)
            cls._model.to(cls._device)
            cls._model.eval()
            
            logger.info("EmbeddingService successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingService: {e}")
            logger.warning("Falling back to mock mode for EmbeddingService.")
            cls._mock_mode = True

    @classmethod
    def generate_embeddings(cls, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate L2-normalized dense embeddings for a string or a list of strings."""
        if cls._model is None and not cls._mock_mode:
            cls.initialize()

        is_single = isinstance(texts, str)
        text_list = [texts] if is_single else texts

        # Fallback / Mock mode to prevent heavy downloads during tests or startup failures
        if cls._mock_mode:
            dummy_dim = 1024 if "bge-m3" in settings.EMBEDDING_MODEL_ID.lower() else 384
            # Return simple non-zero dummy vectors of the correct dimension to ensure Qdrant accepts them
            res = []
            for t in text_list:
                # Deterministic mock vector based on string length to simulate similarity for simple unit checks
                val = (len(t) % 100) / 100.0
                vec = [val] * dummy_dim
                res.append(vec)
            return res[0] if is_single else res

        try:
            encoded_input = cls._tokenizer(
                text_list, 
                padding=True, 
                truncation=True, 
                max_length=512, 
                return_tensors="pt"
            )
            
            # Move inputs to target device
            encoded_input = {k: v.to(cls._device) for k, v in encoded_input.items()}

            with torch.no_grad():
                model_output = cls._model(**encoded_input)
                # BGE models use the CLS token representation (first token)
                embeddings = model_output[0][:, 0]
                # L2 normalize embeddings
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                
            embeddings_list = embeddings.cpu().tolist()
            return embeddings_list[0] if is_single else embeddings_list
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            dummy_dim = 1024 if "bge-m3" in settings.EMBEDDING_MODEL_ID.lower() else 384
            res = [[0.0] * dummy_dim for _ in text_list]
            return res[0] if is_single else res
