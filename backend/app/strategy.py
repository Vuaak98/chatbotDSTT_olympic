"""
Strategy Pattern Implementation for AI Pipeline Management

This module provides abstract classes and concrete implementations for different AI pipelines:
- GeminiPipeline: Direct Gemini API calls
- RagPipeline: RAG-based pipeline with vector search

The strategy pattern allows easy switching between pipelines via configuration.
"""

import abc
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.rag.orchestrator.graph_builder import GraphBuilder
from app.rag.config.config_loader import CONFIG as RAG_CONFIG

logger = logging.getLogger(__name__)

class PipelineResponse:
    """Standard response format for all pipelines."""
    def __init__(self, content: str, artifacts: Optional[List[Dict]] = None, error: Optional[str] = None):
        self.content = content
        self.artifacts = artifacts or []
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "artifacts": self.artifacts,
            "error": self.error
        }

class PipelineStrategy(abc.ABC):
    """Abstract base class for AI pipeline strategies."""
    @abc.abstractmethod
    async def generate_response(
        self,
        chat_id: str,
        user_message_content: str,
        file_ids: Optional[List[str]],
        db: Session,
        queue: asyncio.Queue
    ) -> PipelineResponse:
        """Generate AI response using the specific pipeline strategy."""
        pass

    @abc.abstractmethod
    async def _prepare_context(self, chat_id: str, db: Session) -> List[Any]:
        """Prepare context from chat history."""
        pass

    @abc.abstractmethod
    async def _process_files(self, file_ids: Optional[List[str]], db: Session) -> List[Any]:
        """Process attached files for the pipeline."""
        pass 

class GeminiPipeline(PipelineStrategy):
    """Pipeline strategy for direct Gemini API calls."""
    def __init__(self, client, types, model_name, system_instruction, crud_service=None, file_service=None):
        self.client = client
        self.types = types
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.crud_service = crud_service
        self.file_service = file_service

    async def _prepare_context(self, chat_id: str, db: Session) -> list:
        """Chuẩn bị context từ lịch sử chat cho Gemini."""
        if not self.crud_service:
            logger.warning("crud_service not provided, returning empty context")
            return []
            
        chat_history_models = self.crud_service.get_messages_for_chat(db, chat_id=int(chat_id))
        gemini_prompt_contents = []
        for msg_model in chat_history_models:
            message_parts = [self.types.Part(text=msg_model.content)]
            # Nếu message có file đính kèm, truyền nội dung file vào prompt
            if hasattr(msg_model, 'files') and msg_model.files:
                for fm in msg_model.files:
                    file_parts = await self._prepare_single_file_for_gemini(fm, db)
                    if file_parts:
                        message_parts.extend(file_parts)
            gemini_prompt_contents.append(
                self.types.Content(
                    role="user" if msg_model.role == "user" else "model",
                    parts=message_parts
                )
            )
        return gemini_prompt_contents

    async def _process_files(self, file_ids: Optional[list], db: Session) -> list:
        # Đã xử lý file trong _prepare_context, nên trả về []
        return []

    async def _prepare_single_file_for_gemini(self, fm, db):
        """Chuẩn bị file cho Gemini API."""
        import os
        try:
            context_part = self.types.Part(text=f"[File đính kèm: {fm.original_filename}, loại: {fm.content_type}]")
            if fm.content_type == 'text/plain':
                with open(fm.local_disk_path, 'r', encoding='utf-8', errors='replace') as f:
                    text_content = f.read()
                return [context_part, self.types.Part(text=text_content)]
            elif fm.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                if self.file_service:
                    text_content = self.file_service.extract_text_from_docx(fm.local_disk_path)
                else:
                    # Fallback nếu không có file_service
                    import docx
                    doc = docx.Document(fm.local_disk_path)
                    text_content = '\n'.join([para.text for para in doc.paragraphs])
                return [context_part, self.types.Part(text=text_content)]
            elif fm.processing_method == 'inline':
                with open(fm.local_disk_path, 'rb') as f_bytes:
                    file_data = f_bytes.read()
                return [context_part, self.types.Part(inline_data={"data": file_data, "mime_type": fm.content_type})]
            elif fm.processing_method == 'files_api' and fm.gemini_api_file_id:
                if self.file_service:
                    gemini_file_id = self.file_service.refresh_gemini_file_if_needed(fm, db)
                else:
                    # Fallback logic
                    gemini_file_id = fm.gemini_api_file_id
                return [context_part, self.types.Part(uri=gemini_file_id, mime_type=fm.content_type)]
            else:
                logger.warning(f"Unknown processing_method '{fm.processing_method}' for file {fm.id}")
                return None
        except Exception as e:
            logger.error(f"Error preparing file {fm.id}: {e}", exc_info=True)
            return None

    async def generate_response(
        self,
        chat_id: str,
        user_message_content: str,
        file_ids: Optional[list],
        db: Session,
        queue: asyncio.Queue
    ) -> PipelineResponse:
        """
        Triển khai logic gọi Gemini API.
        Đã sửa để gửi về các chunk JSON hợp lệ.
        """
        try:
            gemini_prompt_contents = await self._prepare_context(chat_id, db)
            
            logger.info(f"Sending request to Gemini for chat_id {chat_id}")
            response_stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=gemini_prompt_contents,
                config=self.types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7
                )
            )

            ai_response_content = ""
            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    ai_response_content += chunk.text
                    # Đảm bảo luôn gửi JSON string hợp lệ
                    json_chunk = json.dumps({"text": chunk.text})
                    await queue.put(json_chunk)

            logger.info(f"Gemini response generated for chat_id {chat_id}")
            return PipelineResponse(content=ai_response_content.strip())

        except Exception as e:
            logger.error(f"Error in GeminiPipeline: {e}")
            error_message = f"Lỗi từ Gemini pipeline: {e}"
            await queue.put(json.dumps({"error": error_message}))
            return PipelineResponse(content="", error=error_message)

class RagPipeline(PipelineStrategy):
    """Pipeline strategy for RAG (Retrieval-Augmented Generation)."""
    def __init__(self, rag_config=None):
        self.graph_builder = GraphBuilder(config=rag_config)
        self.graph = self.graph_builder.graph
        self.rag_config = rag_config

    async def generate_response(
        self,
        chat_id: str,
        user_message_content: str,
        file_ids: Optional[list],
        db: Session,
        queue: asyncio.Queue
    ) -> PipelineResponse:
        try:
            state = {"messages": [{"role": "user", "content": user_message_content}]}
            content = ""
            artifacts = []
            
            async for event in self.graph.astream(state, {"configurable": {"thread_id": chat_id}}):
                print(f"DEBUG: RAG event = {repr(event)}")
                if "agent" in event and "messages" in event["agent"]:
                    print(f"DEBUG: RAG event['agent']['messages'] = {repr(event['agent']['messages'])}")
                    for msg in event["agent"]["messages"]:
                        print(f"DEBUG: RAG msg type = {type(msg)}, msg = {repr(msg)}")
                        if isinstance(msg, dict) and "content" in msg:
                            chunk_text = msg["content"]
                            print(f"DEBUG: RAG chunk_text = {repr(chunk_text)}")
                            content += chunk_text
                            await queue.put(json.dumps({"text": chunk_text}))
                        elif hasattr(msg, "content"):
                            chunk_text = msg.content
                            print(f"DEBUG: RAG chunk_text (attr) = {repr(chunk_text)}")
                            content += chunk_text
                            await queue.put(json.dumps({"text": chunk_text}))
                        # Xử lý artifact nếu có
                        if isinstance(msg, dict) and "artifact" in msg:
                            artifacts.extend(msg["artifact"])
                            await queue.put(json.dumps({"artifacts": msg["artifact"]}))
                             
            return PipelineResponse(content=content, artifacts=artifacts)
        except Exception as e:
            logger.error(f"Error in RagPipeline: {e}")
            error_message = f"Lỗi từ RAG pipeline: {e}"
            await queue.put(json.dumps({"error": error_message}))
            return PipelineResponse(content="", error=error_message)

    async def _prepare_context(self, chat_id: str, db: Session) -> list:
        return []

    async def _process_files(self, file_ids: Optional[list], db: Session) -> list:
        return []

class PipelineFactory:
    """Factory class để tạo pipeline dựa trên configuration."""
    def __init__(self, client, types, crud_service, file_service, config_service=None, rag_config=None):
        self.client = client
        self.types = types
        self.crud_service = crud_service
        self.file_service = file_service
        self.config_service = config_service
        # Đảm bảo luôn có config hợp lệ cho RAG
        self.rag_config = rag_config if rag_config is not None else RAG_CONFIG
    
    def create_gemini_pipeline(self):
        if not self.config_service:
            model_name = "gemini-1.5-flash"
            system_instruction = "You are a helpful AI assistant."
        else:
            model_name = self.config_service.get_settings().gemini_model_name
            system_instruction = self.config_service.MATH_CHATBOT_SYSTEM_INSTRUCTION
        return GeminiPipeline(
            client=self.client,
            types=self.types,
            model_name=model_name,
            system_instruction=system_instruction,
            crud_service=self.crud_service,
            file_service=self.file_service
        )
    
    def create_rag_pipeline(self):
        # Luôn truyền self.rag_config (không bao giờ None)
        return RagPipeline(rag_config=self.rag_config)
    
    def get_pipeline(self, pipeline_type: str = "gemini"):
        if pipeline_type.lower() == "gemini":
            return self.create_gemini_pipeline()
        elif pipeline_type.lower() == "rag":
            return self.create_rag_pipeline()
        else:
            raise ValueError(f"Unknown pipeline type: {pipeline_type}")

# Helper function để tạo factory

def create_pipeline_factory(client, types, crud_service, file_service, config_service=None, rag_config=None):
    return PipelineFactory(client, types, crud_service, file_service, config_service, rag_config)

# Helper function để lấy pipeline

def get_pipeline(pipeline_type: str = "gemini", config_service=None, rag_config=None):
    from . import services
    from google import genai
    from google.genai import types
    factory = create_pipeline_factory(
        client=services.client,
        types=types,
        crud_service=services.crud,
        file_service=services,
        config_service=config_service,
        rag_config=rag_config
    )
    return factory.get_pipeline(pipeline_type) 