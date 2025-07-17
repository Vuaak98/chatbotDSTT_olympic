from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, models, schemas, services
from ..database import get_db
from ..config import get_settings # For upload limits if needed here

# Lưu ý: Các route message được lồng dưới chat để tổ chức hợp lý,
# nhưng được định nghĩa riêng để dễ bảo trì.
# chat_id sẽ được truyền qua path parameter.
router = APIRouter(
    tags=["Messages"],
    responses={404: {"description": "Không tìm thấy"}},
)

@router.post("/chats/{chat_id}/messages/", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
async def create_new_message_for_chat(
    chat_id: int, 
    message_text: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """Tạo một tin nhắn mới (có thể kèm file) trong một phiên chat cụ thể."""
    db_chat = crud.get_chat(db, chat_id=chat_id)
    if db_chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên chat")

    processed_files_metadata = []
    if files:
        if len(files) > get_settings().max_files_per_prompt: # Tối đa 5 file
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Quá nhiều file. Tối đa {get_settings().max_files_per_prompt} file cho mỗi lần gửi."
            )
        for upload_file in files:
            # Hàm prepare_file_metadata_for_db sẽ kiểm tra kích thước và loại file
            file_meta = await services.prepare_file_metadata_for_db(upload_file, db)
            processed_files_metadata.append(file_meta)

    # 1. Lưu tin nhắn người dùng và file liên quan
    user_message_schema = schemas.MessageCreate(role="user", content=message_text)
    user_db_message = crud.create_chat_message_with_files(
        db=db, 
        message_data=user_message_schema, 
        chat_id=chat_id, 
        file_metadatas=processed_files_metadata
    )

    # 2. Lấy lịch sử chat (loại trừ tin nhắn vừa thêm) để làm ngữ cảnh cho AI
    chat_history_for_ai = crud.get_messages_for_chat(db=db, chat_id=chat_id, limit=50, exclude_message_id=user_db_message.id)

    # 3. Gọi AI để sinh phản hồi
    import asyncio
    import json
    queue = asyncio.Queue()

    # --- Logic chọn pipeline ---
    if message_text.strip().startswith("/rag"):
        pipeline_type = "rag"
        # Cắt '/rag' khỏi message_text khi gửi vào pipeline RAG
        message_for_pipeline = message_text.strip()[4:].lstrip()
    else:
        pipeline_type = "gemini"
        message_for_pipeline = message_text

    await services.generate_ai_response_stream(
        chat_id=str(chat_id),
        user_message_content=message_for_pipeline,
        file_ids=[f.id for f in user_db_message.files] if user_db_message.files else [],
        db=db,
        queue=queue,
        pipeline_type=pipeline_type
    )
    ai_response_content = ""
    while True:
        chunk = await queue.get()
        if chunk == "[DONE]":
            break
        if not chunk or not chunk.strip():
            continue  # Bỏ qua chunk rỗng hoặc chỉ chứa whitespace
        try:
            data = json.loads(chunk)
        except json.JSONDecodeError:
            print(f"Chunk không phải JSON hợp lệ: {repr(chunk)}")
            continue
        if "text" in data:
            ai_response_content += data["text"]

    # 4. Lưu tin nhắn AI vào DB
    ai_message_schema = schemas.MessageCreate(role="model", content=ai_response_content)
    ai_db_message = crud.create_chat_message_with_files(db=db, message_data=ai_message_schema, chat_id=chat_id, file_metadatas=[])

    # 5. Trả về tin nhắn AI (không kèm file)
    return ai_db_message

@router.get("/chats/{chat_id}/messages/", response_model=List[schemas.Message])
def read_messages_for_chat(chat_id: int, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    """Lấy toàn bộ tin nhắn của một phiên chat cụ thể."""
    db_chat = crud.get_chat(db, chat_id=chat_id)
    if db_chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên chat")
    messages = crud.get_messages_for_chat(db, chat_id=chat_id, skip=skip, limit=limit)
    return messages