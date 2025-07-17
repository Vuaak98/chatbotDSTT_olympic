from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from app.rag.config.base_config import BaseConfiguration, QdrantConfig

from .embedding_factory import create_embedding_model
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
import logging

logger = logging.getLogger(__name__)


def create_qdrant_vector_store(
    vector_store_config: QdrantConfig, embedding_model: Embeddings
) -> Qdrant:
    """Creates a Qdrant vector store."""
    logger.info("Creating Qdrant vector store")
    
    qdrant_client = QdrantClient(
        url=vector_store_config.url,
        api_key=vector_store_config.api_key.get_secret_value(),
    )
    
    vector_store = Qdrant(
        client=qdrant_client,
        collection_name=vector_store_config.collection_name,
        embeddings=embedding_model,
    )
    
    logger.info("Successfully created Qdrant vector store")
    return vector_store

def create_vector_store(
    configuration: BaseConfiguration, embedding_model: Embeddings
) -> Qdrant:
    """
    Creates a vector store based on the provided configuration.
    """
    # Lấy nhà cung cấp từ cấu hình retrieval, không phải từ vector_store_config
    vector_store_provider = getattr(configuration, 'retrieval_config', None)
    if vector_store_provider is None:
         from app.rag.config.config_loader import CONFIG
         provider_name = CONFIG.get("retrieval_config", {}).get("provider", "qdrant")
    else:
         provider_name = vector_store_provider.provider

    vector_store_config = configuration.vector_store_config
    
    if provider_name == "qdrant":
        return create_qdrant_vector_store(vector_store_config, embedding_model)
    else:
        raise ValueError(f"Unsupported vector store provider: {provider_name}")

if __name__ == "__main__":
    print("Test import thành công!")