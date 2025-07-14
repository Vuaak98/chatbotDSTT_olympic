from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, File, UploadFile, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import json
import asyncio
from pydantic import BaseModel
import os
import logging
import random
from sqlalchemy.orm import Session

from .. import crud, models, schemas, services
from ..crud import file_crud
from ..database import get_db
from ..utils import sanitize_text

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Streaming"],
    responses={404: {"description": "Not found"}},
)

# Global dictionary to store active generation tasks
# This allows us to interrupt them if needed
active_generations: Dict[str, asyncio.Task] = {}

# We're not using chat contexts anymore since we now rebuild from the database each time
# chat_contexts: Dict[str, Any] = {}

# StreamChatRequest is not used by the main /stream endpoint, UserMessageInput is.
# class StreamChatRequest(BaseModel):
#     """Stream chat request schema."""
#     content: str
#     role: Optional[str] = "user"
#     file_id: Optional[str] = None # This was for a single file, UserMessageInput handles multiple file_ids

# UserMessageInput is defined in schemas.py, no need to redefine here.

@router.post("/chats/{chat_id}/stream")
async def stream_chat_response(
    request: Request,
    chat_id: int,
    user_message: schemas.UserMessageInput, # Use the schema from schemas.py
    db: Session = Depends(get_db),
    x_chat_context: Optional[str] = Header(None), # Keep for now, though context handling changed
):
    """
    Stream a response from the AI to the user.
    Receives user message content and a list of file_ids (UUIDs for FileMetadata).
    """
    # Define the streaming response generator
    async def event_generator():
        try:
            # Send the generation ID first
            generation_id_event = f"data: {json.dumps({'generation_id': generation_id})}\n\n"
            logger.info(f"Sending generation ID event: {generation_id_event.strip()}")
            yield generation_id_event

            # Stream the response chunks
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    # Cancel the generation task
                    if not generation_task.done():
                        generation_task.cancel()
                    break

                # Get message from queue
                try:
                    chunk = await asyncio.wait_for(queue.get(), timeout=30.0)
                    # Check for done signal
                    if chunk == "[DONE]":
                        # Send a proper [DONE] marker in SSE format
                        logger.info("Sending [DONE] marker")
                        yield f"data: [DONE]\n\n"
                        break

                    # The chunk is already formatted as "data: {json}\n\n" by the generate_ai_response_stream function
                    # Just pass it through
                    logger.info(f"Sending chunk (length: {len(chunk)})")
                    if chunk.startswith("data:"):
                        yield chunk
                    else:
                        # For backward compatibility, format any unformatted chunks
                        yield f"data: {json.dumps({'text': chunk})}\n\n"
                except asyncio.TimeoutError:
                    # Send a keepalive comment to prevent proxy timeouts
                    logger.debug("Sending keepalive")
                    yield ": keepalive\n\n"
                except Exception as e:
                    # Log full stack trace for debugging event generator errors
                    logger.error(f"Error in event generator: {e}", exc_info=True)
                    # Try to send an error message
                    try:
                        error_chunk = {
                            "error": str(e),
                            "text": "An error occurred while generating the response."
                        }
                        yield f"data: {json.dumps(error_chunk)}\n\n"
                    except:
                        pass
                    break
        except Exception as e:
            logger.error(f"Event generator error: {e}", exc_info=True)
            # Send a final error message
            try:
                error_message = {
                    "error": str(e),
                    "text": "An error occurred while streaming the response."
                }
                yield f"data: {json.dumps(error_message)}\n\n"
            except:
                # If we can't even send the error, just send a plain message
                yield f"data: An error occurred.\n\n"

    try:
        logger.info(f"Received streaming request for chat_id: {chat_id}")
        logger.info(f"User message content: {user_message.content}")
        
        # Validate file_ids and log FileMetadata info (not file paths anymore)
        if user_message.file_ids:
            logger.info(f"File IDs included in request: {user_message.file_ids}")
            valid_file_metadata_for_service = []
            for file_id_str in user_message.file_ids:
                # file_info = crud.get_file_by_id(db=db, file_id=file_id_str) # Old way (filesystem scan)
                file_metadata_entry = file_crud.get_file_metadata_by_id(db=db, file_id=file_id_str) # New way (DB query)
                if file_metadata_entry:
                    # valid_file_metadata_for_service.append(file_metadata_entry) # Pass the whole object or just ID?
                                                                          # Service layer will need to re-fetch or be passed enough info.
                                                                          # For now, service layer takes file_ids and re-fetches.
                    logger.info(f"File metadata found for ID {file_id_str}: Name - {file_metadata_entry.original_filename}, Path - {file_metadata_entry.local_disk_path}")
                else:
                    logger.warning(f"File metadata with ID {file_id_str} not found in database. Skipping this file.")
            # The services.generate_ai_response_stream will receive the original list of file_ids
            # and will be responsible for fetching their metadata and handling missing ones.
        
        # Generate a unique ID for this generation
        generation_id = f"{chat_id}_{random.randint(100, 999)}"
        logger.info(f"Generation ID: {generation_id}")
        
        # Create a queue for passing chunks between tasks
        queue = asyncio.Queue()
        
        # Start the AI response generation in a background task
        logger.info(f"Starting generate_ai_response_stream for generation_id: {generation_id}")
        generation_task = asyncio.create_task(
            services.generate_ai_response_stream(
                chat_id=str(chat_id),
                user_message_content=user_message.content, # Pass content directly
                file_ids=user_message.file_ids,      # Pass the list of UUIDs
                db=db,
                queue=queue,
                # context=None, # context handling has changed
            )
        )
        
        # When the generation task completes, log any exceptions
        def on_generation_done(task):
            try:
                if task.cancelled():
                    logger.info(f"Generation task for {generation_id} was cancelled")
                elif task.exception():
                    logger.error(f"Generation task for {generation_id} raised an exception: {task.exception()}", 
                                exc_info=task.exception())
                elif task.done():
                    # Log completion
                    logger.info(f"Generation task for {generation_id} completed successfully")
            except Exception as e:
                logger.error(f"Error handling generation completion: {e}", exc_info=True)
        
        # Add the callback to the task
        generation_task.add_done_callback(on_generation_done)
        
        # Store in active generations to allow cancellation
        active_generations[generation_id] = generation_task
        
        # Set content type for SSE
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable buffering in Nginx
                "Content-Type": "text/event-stream",
            },
        )
    except Exception as e:
        logger.error(f"Error during streaming: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during streaming: {str(e)}")

# The /chat/{chat_id}/stream-with-file endpoint might be redundant now if UserMessageInput for the main stream endpoint is sufficient.
# Or it could be kept if it serves a slightly different purpose or client interaction pattern.
# For now, let's assume UserMessageInput on the main stream endpoint is the primary path.
# If keeping stream-with-file, it also needs to use schemas.UserMessageInput and ensure file_ids are UUIDs.

@router.post("/chats/{chat_id}/interrupt", response_model=schemas.InterruptResponse)
async def interrupt_chat_stream(
    chat_id: int,
    payload: schemas.InterruptRequest, # Use the new schema for the request body
) -> schemas.InterruptResponse:
    """
    Interrupt a streaming response.
    Expects a JSON body with an optional 'generation_id'.
    """
    try:
        generation_id = payload.generation_id # Get generation_id from the payload
        # If generation_id is provided, use it to find the specific task
        if generation_id and generation_id in active_generations:
            task = active_generations[generation_id]
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled generation {generation_id}")
            # Remove from tracking
            del active_generations[generation_id]
            return schemas.InterruptResponse(status="success", message=f"Generation {generation_id} interrupted")
        
        # If no generation_id, try to cancel all tasks for this chat_id
        prefix = f"{chat_id}_"
        cancelled_count = 0 # Renamed variable to avoid conflict
        for gen_id, task in list(active_generations.items()):
            if gen_id.startswith(prefix) and not task.done():
                task.cancel()
                del active_generations[gen_id]
                cancelled_count += 1
        
        if cancelled_count > 0:
            return schemas.InterruptResponse(status="success", message=f"Interrupted {cancelled_count} active generations for chat {chat_id}")
        else:
            return schemas.InterruptResponse(status="warning", message="No active generations found to interrupt")
    except Exception as e:
        logger.error(f"Error interrupting generation: {e}")
        # Return a valid InterruptResponse even in case of an internal server error
        # The HTTPException will transform this into a 500 response with the detail.
        # However, the endpoint is typed to return InterruptResponse.
        # For clarity, we can raise HTTPException directly without returning, 
        # or ensure the returned object matches if not raising.
        # For now, let's stick to raising HTTPException as it's cleaner.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error interrupting generation: {str(e)}"
        )

# Reset context endpoint - modified to be a no-op since we don't use context anymore
@router.post("/chats/{chat_id}/reset-context", status_code=status.HTTP_204_NO_CONTENT)
async def reset_chat_context(chat_id: int):
    """
    This endpoint is now a no-op since we rebuild context from the database each time.
    
    We keep it for backward compatibility with the frontend.
    """
    logger.info(f"Reset context request received for chat_id: {chat_id} (no action needed)")
    return None