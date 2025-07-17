from langchain_core.tools import StructuredTool
from langchain_core.vectorstores import VectorStore
from app.rag.config.base_config import BaseConfiguration
from app.rag.factories.embedding_factory import create_embedding_model
from app.rag.factories.vector_store_factory import create_vector_store
from app.rag.config.config_loader import CONFIG
import logging

# --- Thêm Pydantic BaseModel vào ---
from pydantic.v1 import BaseModel, Field
# ====================================

logger = logging.getLogger(__name__)

# --- Định nghĩa Schema cho các đối số của Tool ---
class RetrieverInputSchema(BaseModel):
    """Input schema for the retriever tool."""
    query: str = Field(description="The query to search for relevant documents.")
# ============================================

async def search_documents(query: str, retriever: VectorStore) -> tuple[str, list]:
    """
    Search for documents using the provided retriever.
    
    Args:
        query: The query string to search for.
        retriever: The vector store retriever instance.
        
    Returns:
        A tuple containing the formatted context string and a list of source documents.
    """
    logger.info(f"Searching for documents with query: '{query}'")
    docs = await retriever.ainvoke(query)
    
    context = "\n\n".join(doc.page_content for doc in docs)
    artifacts = [doc.metadata for doc in docs if doc.metadata]
    
    logger.info(f"Found {len(docs)} documents.")
    return context, artifacts

def create_custom_retriever_tool(
    knowledge_retriever: VectorStore,
    name: str = "retrieve_knowledge",
    description: str = "Retrieve relevant documents from the knowledge base.",
) -> StructuredTool:
    """
    Creates a structured tool for retrieving documents from a vector store.
    """
    async def tool_func(query: str):
        """The function that the tool will execute."""
        return await search_documents(query, knowledge_retriever)

    return StructuredTool.from_function(
        func=tool_func,
        name=name,
        description=description,
        # === Sử dụng Pydantic Model đã định nghĩa ở trên ===
        args_schema=RetrieverInputSchema,
        # ================================================
        return_direct=False,
    )

def create_knowledge_retriever(
    vector_store: VectorStore, config: BaseConfiguration
) -> VectorStore:
    """Creates a knowledge retriever from the vector store."""
    return vector_store.as_retriever(
        search_type=config.search_type, search_kwargs=config.search_kwargs
    )

# --- Khởi tạo các thành phần ---
config = BaseConfiguration()
embedding_model = create_embedding_model(config.embedding_model_config)
vector_store = create_vector_store(configuration=config, embedding_model=embedding_model)
knowledge_retriever = create_knowledge_retriever(vector_store=vector_store, config=config)

# Lấy cấu hình tên và mô tả từ config.yaml
if CONFIG is not None:
    tool_name = CONFIG.get("retriever_tool_config", {}).get("name", "retrieve_knowledge")
    tool_description = CONFIG.get("retriever_tool_config", {}).get("description", "Retrieve relevant documents.")
else:
    tool_name = "retrieve_knowledge"
    tool_description = "Retrieve relevant documents."

# --- Tạo Tool cuối cùng ---
retriever_tool = create_custom_retriever_tool(
    knowledge_retriever=knowledge_retriever,
    name=tool_name,
    description=tool_description
)