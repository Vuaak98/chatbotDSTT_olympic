from typing import Union

from langchain_core.language_models import BaseChatModel

from app.rag.config.base_config import AzureOpenAIConfig

def create_azure_chat_model(chat_config) -> BaseChatModel:
    from langchain_openai import AzureChatOpenAI
    from langchain_openai import ChatOpenAI
    # Nếu là dict, lấy các trường từ dict
    if isinstance(chat_config, dict):
        provider = chat_config.get("provider")
        if provider == "azure_openai":
            # Ưu tiên AzureChatOpenAI nếu có endpoint, nếu không thì ChatOpenAI
            if chat_config.get("azure_endpoint"):
                return AzureChatOpenAI(
                    api_key=chat_config.get("api_key"),
                    azure_endpoint=chat_config.get("azure_endpoint"),
                    api_version=chat_config.get("api_version"),
                    azure_deployment=chat_config.get("deployment_name"),
                    **(chat_config.get("kwargs") or {}),
                )
            else:
                return ChatOpenAI(
                    api_key=chat_config.get("api_key"),
                    model=chat_config.get("deployment_name", "gpt-4o-mini"),
                    **(chat_config.get("kwargs") or {}),
                )
        else:
            raise ValueError(f"Unsupported chat model provider: {provider}")
    # Nếu là object kiểu AzureOpenAIConfig
    elif isinstance(chat_config, AzureOpenAIConfig):
        return AzureChatOpenAI(
            api_key=chat_config.api_key,
            azure_endpoint=chat_config.azure_endpoint,
            api_version=chat_config.api_version,
            azure_deployment=chat_config.azure_deployment,
            **(chat_config.kwargs if chat_config.kwargs else {}),
        )
    else:
        raise ValueError(f"Unsupported chat config type: {type(chat_config)}")

def create_chat_model(chat_config) -> BaseChatModel:
    """Connect to the configured chat model (Azure)."""
    # Nếu là dict, tự động nhận diện provider
    if isinstance(chat_config, dict):
        provider = chat_config.get("provider")
        if provider == "azure_openai":
            return create_azure_chat_model(chat_config)
        else:
            raise ValueError(f"Unsupported chat model provider: {provider}")
    # Nếu là object kiểu AzureOpenAIConfig
    elif isinstance(chat_config, AzureOpenAIConfig):
        return create_azure_chat_model(chat_config)
    else:
        raise ValueError(f"Unsupported chat config type: {type(chat_config)}")
