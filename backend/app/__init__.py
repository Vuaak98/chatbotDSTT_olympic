"""
AI Math Chatbot Application Package
"""
import warnings

# Filter out specific Pydantic warnings
warnings.filterwarnings(
    "ignore", 
    message=".*<built-in function any> is not a Python type.*",
    category=UserWarning
)

# The orm_mode warning is already fixed with from_attributes=True in schemas.py 