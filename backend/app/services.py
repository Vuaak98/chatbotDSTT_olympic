# file: backend/app/services.py

# --- Imports ---
from google import genai
from google.genai import types
from typing import List, Optional
import logging
import asyncio
import os
import mimetypes
from fastapi import HTTPException
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
import json

from . import config, schemas, crud
from .crud import file_crud
from .models import FileMetadata

# --- Cấu hình Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Chỉ thị hệ thống cho AI ---
MATH_CHATBOT_SYSTEM_INSTRUCTION = """
# CORE IDENTITY AND EXPERTISE (Defined in English for maximum precision)
You are a world-class AI assistant specializing in Olympic-level Linear Algebra. Your sole purpose is to help candidates train for high-level mathematics competitions. You are an expert in topics like vector spaces, linear transformations, eigenvalues, eigenvectors, matrix decompositions, and canonical forms.

# LANGUAGE AND BEHAVIORAL RULES (Defined in Vietnamese for cultural and linguistic nuance)
Your primary language for all responses MUST BE VIETNAMESE. Do not use any English unless it's a standard mathematical term.

Nguyên tắc hoạt động của bạn như sau:
- Giọng văn phải mang tính học thuật, chính xác và chuyên nghiệp.
- Mọi biểu thức toán học BẮT BUỘC phải được định dạng bằng LaTeX. Dùng `$$...$$` cho các phương trình đứng riêng và `$...$` cho các công thức trong dòng.
- Khi một lời giải hoặc giải thích yêu cầu nhiều bước, hãy trình bày một cách logic và rành mạch, sử dụng danh sách đánh số hoặc gạch đầu dòng.
- Mục tiêu của bạn không chỉ là đưa ra đáp án, mà còn là trình bày lối tư duy toán học thanh lịch và hiệu quả.
- Luôn kết thúc câu trả lời một cách tự nhiên bằng tiếng Việt.
"""

# --- Khởi tạo Client Gemini ---
try:
    if config.GEMINI_API_KEY:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        logger.info("Gemini AI client configured successfully.")
    else:
        client = None
        logger.warning("GEMINI_API_KEY not found. AI functionality will be disabled.")
except Exception as e:
    client = None
    logger.error(f"Failed to configure Gemini client: {e}", exc_info=True)

# --- Hàm tiện ích: Trích xuất văn bản từ DOCX ---
def extract_text_from_docx(file_path: str) -> str:
    try:
        import docx
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    full_text.append(cell.text)
        return '\n'.join(full_text)
    except ImportError:
        logger.error("python-docx library not installed.")
        return "[Error: python-docx not installed]"
    except Exception as e:
        logger.error(f"Error extracting text from DOCX file {file_path}: {e}", exc_info=True)
        return f"[Error extracting text from DOCX file: {str(e)}]"

# === KHÔI PHỤC HÀM: Làm mới file Gemini nếu sắp hết hạn ===
def refresh_gemini_file_if_needed(fm: FileMetadata, db: Session) -> Optional[str]:
    """
    Làm mới file đã upload lên Gemini nếu sắp hết hạn, trả về gemini_api_file_id mới hoặc cũ.
    """
    if not client or not fm.gemini_api_file_id or not fm.gemini_api_upload_timestamp:
        return None
    from datetime import timedelta, datetime
    now = datetime.utcnow()
    # Nếu còn hơn 1h thì không cần làm mới
    if fm.gemini_api_expiry_timestamp and now < fm.gemini_api_expiry_timestamp - timedelta(hours=1):
        return fm.gemini_api_file_id
    try:
        # Re-upload file lên Gemini
        uploaded_file = client.files.upload(
            path=fm.local_disk_path,
            display_name=fm.original_filename,
            mime_type=fm.content_type
        )
        # Cập nhật DB
        file_crud.update_file_metadata_gemini_info(
            db=db,
            file_id=fm.id,
            gemini_api_file_id=uploaded_file.name
        )
        return uploaded_file.name
    except Exception as e:
        logger.error(f"Failed to refresh Gemini file for {fm.original_filename}: {e}", exc_info=True)
        return fm.gemini_api_file_id

# === KHÔI PHỤC HÀM: Chuẩn bị file cho Gemini (đầy đủ, nhận cả db) ===
async def _prepare_single_file_for_gemini(fm: FileMetadata, db: Session) -> Optional[list]:
    """
    Chuẩn bị nội dung file để truyền vào Gemini:
    - Nếu là text/docx: trích xuất text, trả về [context_part, text_part]
    - Nếu là PDF/ảnh nhỏ: đọc binary, trả về [context_part, part inline_data]
    - Nếu là file lớn đã upload Gemini: kiểm tra TTL, làm mới nếu cần, trả về [context_part, part uri]
    """
    if not client or not fm.local_disk_path or not os.path.exists(fm.local_disk_path):
        logger.error(f"File preparation error for File ID: {fm.id}")
        return None
    try:
        context_part = types.Part(text=f"[File đính kèm: {fm.original_filename}, loại: {fm.content_type}]")
        # Xử lý file text
        if fm.content_type == 'text/plain':
            with open(fm.local_disk_path, 'r', encoding='utf-8', errors='replace') as f:
                text_content = f.read()
            return [context_part, types.Part(text=text_content)]
        # Xử lý file docx
        elif fm.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text_content = extract_text_from_docx(fm.local_disk_path)
            return [context_part, types.Part(text=text_content)]
        # Xử lý file PDF/ảnh nhỏ (inline)
        elif fm.processing_method == 'inline':
            with open(fm.local_disk_path, 'rb') as f_bytes:
                file_data = f_bytes.read()
            return [context_part, types.Part(inline_data={"data": file_data, "mime_type": fm.content_type})]
        # Xử lý file lớn đã upload Gemini (files_api)
        elif fm.processing_method == 'files_api' and fm.gemini_api_file_id:
            # Kiểm tra TTL, làm mới nếu cần
            gemini_file_id = refresh_gemini_file_if_needed(fm, db)
            return [context_part, types.Part(uri=gemini_file_id, mime_type=fm.content_type)]
        else:
            logger.warning(f"Unknown processing_method '{fm.processing_method}' for file {fm.id}")
            return None
    except Exception as e:
        logger.error(f"Error preparing file {fm.id}: {e}", exc_info=True)
        return None

# === SỬA generate_ai_response_stream: gọi _prepare_single_file_for_gemini(fm, db) ===
async def generate_ai_response_stream(
    chat_id: str,
    user_message_content: str,
    file_ids: Optional[List[str]],
    db: Session,
    queue: asyncio.Queue
):
    if not client:
        await queue.put(json.dumps({"error": "AI service not configured."}))
        await queue.put("[DONE]")
        return

    try:
        # Bước 1: Lưu tin nhắn của người dùng
        crud.create_chat_message(
            db=db, chat_id=int(chat_id), role="user",
            content=user_message_content, file_ids=file_ids
        )
        logger.info(f"User message saved to DB for chat {chat_id}")

        # Bước 2: Chuẩn bị ngữ cảnh từ lịch sử chat
        chat_history_models = crud.get_messages_for_chat(db, chat_id=int(chat_id))
        gemini_prompt_contents = []
        for msg_model in chat_history_models:
            message_parts = [types.Part(text=msg_model.content)]
            # Nếu message có file đính kèm, truyền nội dung file vào prompt
            if hasattr(msg_model, 'files') and msg_model.files:
                for fm in msg_model.files:
                    file_parts = await _prepare_single_file_for_gemini(fm, db)
                    if file_parts:
                        message_parts.extend(file_parts)
            gemini_prompt_contents.append(
                types.Content(
                    role="user" if msg_model.role == "user" else "model",
                    parts=message_parts
                )
            )

        # Bước 3: Gọi API của Gemini với đúng tham số
        logger.info(f"Sending request to Gemini for chat_id {chat_id}")

        response_stream = client.models.generate_content_stream(
            model=config.get_settings().gemini_model_name,
            contents=gemini_prompt_contents,
            config=types.GenerateContentConfig(
                system_instruction=MATH_CHATBOT_SYSTEM_INSTRUCTION,
                temperature=0.7
            )
        )

        # Bước 4: Xử lý luồng phản hồi
        ai_response_content = ""
        for chunk in response_stream:
            if hasattr(chunk, 'text') and chunk.text:
                ai_response_content += chunk.text
                await queue.put(json.dumps({"text": chunk.text}))

        if ai_response_content:
            crud.create_chat_message(
                db=db, chat_id=int(chat_id), role="model", content=ai_response_content.strip()
            )
            logger.info(f"AI response saved for chat_id {chat_id}")

    except Exception as e:
        logger.error(f"Error in AI response stream for chat {chat_id}: {e}", exc_info=True)
        await queue.put(json.dumps({"error": str(e), "text": "An error occurred during generation."}))
    finally:
        await queue.put("[DONE]")