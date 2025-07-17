"""Define the configurable parameters for the agent."""

from __future__ import annotations

from typing import Annotated, Dict, Literal, Optional, Type, TypeVar, Union, cast

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig, ensure_config
from pydantic import BaseModel, Field, SecretStr, model_validator
from typing_extensions import Self

import os

def from_env(key: str, default=None):
    return os.environ.get(key, default)

def secret_from_env(key: str, default=None):
    return os.environ.get(key, default)

from app.utils import get_value_from_dict
from .config_loader import CONFIG

load_dotenv(override=True)


class AzureOpenAIConfig(BaseModel):
    api_key: SecretStr = Field(default=SecretStr(secret_from_env("OPENAI_API_KEY") or ""))
    # azure_endpoint: str = Field(default_factory=from_env("AZURE_OPENAI_ENDPOINT"))
    # api_version: str = Field(default_factory=from_env("AZURE_OPENAI_API_VERSION"))
    azure_deployment: Optional[str] = None
    kwargs: Dict = Field(default_factory=dict)


class MongoDBConfig(BaseModel):
    url: str = Field(default=from_env("MONGO_URL") or "")
    database_name: str = Field(default=from_env("MONGODB_DATABASE_NAME") or "")
    collection_name: str = Field(default=from_env("MONGODB_COLLECTION_NAME") or "")


class DynamoDBConfig(BaseModel):
    url: str = Field(default=from_env("DYNAMO_URL") or "")
    table_name: str = Field(default=from_env("TABLE_NAME") or "")
    region_name: str = Field(default=from_env("REGION_NAME") or "")


class PortgresDBConfig(BaseModel):
    server: str = Field(default=from_env("POSTGRES_SERVER") or "", description="The hostname or IP address of the PostgreSQL server.")
    port: str = Field(default=from_env("POSTGRES_PORT") or "", description="The port number on which the PostgreSQL server is listening.")
    db: str = Field(default=from_env("POSTGRES_DB") or "", description="The name of the PostgreSQL database to connect to.")
    user: str = Field(default=from_env("POSTGRES_USER") or "", description="The username used for authenticating with the PostgreSQL database.")
    password: SecretStr = Field(default=SecretStr(secret_from_env("POSTGRES_PASSWORD") or ""))
    table_name: str = Field(default=from_env("CONVERSATION_TABLE_NAME") or "")


class QdrantConfig(BaseModel):
    url: str = Field(default=from_env("QDRANT_URL") or "")
    api_key: SecretStr = Field(default=SecretStr(secret_from_env("QDRANT_API_KEY") or ""))
    collection_name: str = Field(default=from_env("QDRANT_COLLECTION_NAME") or "")


class OauthConfig(BaseModel):
    token_url: str = Field(default=from_env("OAUTH_TOKEN_URL") or "", description="The URL to obtain the OAuth token.")


class BaseConfiguration(BaseModel):
    """Configuration class for indexing and retrieval operations.

    This class defines the parameters needed for configuring the indexing and
    retrieval processes, including embedding model selection, retriever provider choice, and search parameters.
    """

    top_k: int = Field(default_factory=get_value_from_dict("chat_model_config.top_k", CONFIG, default=10), description="The number of documents to re-rank. It also is the number of document use as context.")

    search_type: Annotated[
        Literal["similarity", "mmr"],
        {"__template_metadata__": {"kind": "search"}},
    ] = Field(default_factory=get_value_from_dict("retrieval_config.search_type", CONFIG, default="similarity"), description="Type of search")

    search_kwargs: Dict = Field(default_factory=get_value_from_dict("retrieval_config.kwargs", CONFIG, default={}), description="Additional keyword arguments to pass to the search function of the retriever.")

    rrf_k: int = Field(default=get_value_from_dict("retrieval_config.rrf_k", CONFIG, default=60), description="The parameter that controls the influence of each rank position.")

    chat_model_config: AzureOpenAIConfig = Field(default_factory=AzureOpenAIConfig)
    embedding_model_config: AzureOpenAIConfig = Field(default_factory=AzureOpenAIConfig)
    vector_store_config: QdrantConfig = Field(default_factory=QdrantConfig)
    mongo_config: MongoDBConfig = Field(default_factory=MongoDBConfig)
    # dynamo_config: DynamoDBConfig = Field(default_factory=DynamoDBConfig)
    # postgres_config: PortgresDBConfig = Field(default_factory=PortgresDBConfig)
    # oauth_config: OauthConfig = Field(default_factory=OauthConfig)

    @model_validator(mode="after")
    def validate_provider(self) -> Self:
        """Load environment variables based on the provider."""
        chat_model_provider = get_value_from_dict("chat_model_config.provider", CONFIG)()
        embedding_provider = get_value_from_dict("embedding_model_config.provider", CONFIG)()
        retriever_provider = get_value_from_dict("retrieval_config.provider", CONFIG)()

        def get_provider_config(provider_dict: Dict, provider_name: str):
            try:
                return provider_dict[provider_name]()
            except KeyError:
                raise KeyError(f"'{provider_name}' is not supported! Supported: {list(provider_dict.keys())}.")

        def get_model_config(model_type, provider, config_key_prefix):
            model_config = get_provider_config(model_type, provider)
            model_config.azure_deployment = get_value_from_dict(
                f"{config_key_prefix}.deployment_name", CONFIG, default={}
            )()
            model_config.kwargs = get_value_from_dict(f"{config_key_prefix}.kwargs", CONFIG, default={})()
            return model_config

        self.chat_model_config = get_model_config(AVAILABLE_CHAT_MODEL, chat_model_provider, "chat_model_config")
        self.embedding_model_config = get_model_config(
            AVAILABLE_EMBEDDING_MODEL, embedding_provider, "embedding_model_config"
        )

        self.vector_store_config = get_provider_config(AVAILABLE_RETRIEVER, retriever_provider)

        return self

    @classmethod
    def from_runnable_config(cls: Type[T], config: Optional[RunnableConfig] = None) -> T:
        """Create an IndexConfiguration instance from a RunnableConfig object.

        Args:
            cls (Type[T]): The class itself.
            config (Optional[RunnableConfig]): The configuration object to use.

        Returns:
            T: An instance of IndexConfiguration with the specified configuration.
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        return cast(T, update_config(configurable, cls))


def update_config(val, cls):
    if isinstance(val, Dict) and not isinstance(val, cls):
        _fields = {
            f_name: f_info.annotation
            for f_name, f_info in cls.model_fields.items()
            if f_info.init or f_info.init is None
        }
        return cls(**{k: update_config(v, _fields[k]) for k, v in val.items() if k in _fields.keys()})
    return val


AVAILABLE_CHAT_MODEL = {"azure_openai": AzureOpenAIConfig}

AVAILABLE_EMBEDDING_MODEL = {"azure_openai": AzureOpenAIConfig}

AVAILABLE_RETRIEVER = {"qdrant": QdrantConfig}

APP_CONFIG = BaseConfiguration()

T = TypeVar("T", bound=BaseConfiguration)
if __name__ == "__main__":
    print("Test import thành công!")