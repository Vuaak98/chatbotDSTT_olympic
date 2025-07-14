import re
import html
from typing import Any, Dict, List, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)

def sanitize_text(text: str) -> str:
    """Sanitize text input to prevent injection attacks.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # HTML escape to prevent XSS
    sanitized = html.escape(text)
    
    # Remove any potentially dangerous patterns
    # This is a basic example - adjust based on your specific needs
    sanitized = re.sub(r'[\r\n]+', '\n', sanitized)  # Normalize newlines
    sanitized = re.sub(r'[\u0000-\u001F\u007F-\u009F]', '', sanitized)  # Remove control chars
    
    return sanitized

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal attacks.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return ""
    
    # Remove path components
    sanitized = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    # Remove any leading/trailing dots or spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure the filename is not empty after sanitization
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized

def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize all string values in a dictionary.
    
    Args:
        data: The dictionary to sanitize
        
    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        # Sanitize the key if it's a string
        sanitized_key = sanitize_text(key) if isinstance(key, str) else key
        
        # Recursively sanitize the value
        if isinstance(value, dict):
            result[sanitized_key] = sanitize_dict(value)
        elif isinstance(value, list):
            result[sanitized_key] = sanitize_list(value)
        elif isinstance(value, str):
            result[sanitized_key] = sanitize_text(value)
        else:
            result[sanitized_key] = value
    
    return result

def sanitize_list(data: List[Any]) -> List[Any]:
    """Recursively sanitize all string values in a list.
    
    Args:
        data: The list to sanitize
        
    Returns:
        Sanitized list
    """
    if not isinstance(data, list):
        return data
    
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append(sanitize_dict(item))
        elif isinstance(item, list):
            result.append(sanitize_list(item))
        elif isinstance(item, str):
            result.append(sanitize_text(item))
        else:
            result.append(item)
    
    return result

def validate_mime_type(content_type: str, allowed_types: List[str]) -> bool:
    """Validate that a MIME type is in the list of allowed types.
    
    Args:
        content_type: The MIME type to validate
        allowed_types: List of allowed MIME types
        
    Returns:
        True if the MIME type is allowed, False otherwise
    """
    if not content_type or not allowed_types:
        return False
    
    # Normalize content type (lowercase, remove parameters)
    normalized = content_type.lower().split(';')[0].strip()
    
    # Check if the normalized content type is in the allowed types
    return normalized in [t.lower() for t in allowed_types]