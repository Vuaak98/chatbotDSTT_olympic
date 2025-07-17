from typing import Union

from langchain_core.embeddings import Embeddings

from app.rag.config.base_config import AzureOpenAIConfig


def create_azure_embedding_model(embedding_config: AzureOpenAIConfig):
    from langchain_openai import AzureOpenAIEmbeddings
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(
        model=embedding_config.azure_deployment,
        api_key=embedding_config.api_key.get_secret_value() if hasattr(embedding_config.api_key, 'get_secret_value') else embedding_config.api_key,
        **embedding_config.kwargs,
    )


def create_embedding_model(embedding_config: Union[AzureOpenAIConfig]) -> Embeddings:
    """Connect to the configured text encoder."""
    match embedding_config:
        case AzureOpenAIConfig():
            return create_azure_embedding_model(embedding_config)
        case _:
            raise ValueError(f"Unsupported embedding provider: {type(embedding_config)}")
if __name__ == "__main__":
    print("Test import thành công!")