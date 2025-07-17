from typing import Any, Callable, Optional, Sequence, Union
import re
from functools import wraps
import time
import tiktoken

_NoDefault = object()  # Variable to indicate no default value is provided.


def get_value_from_dict(
    key: Union[str, Sequence[str]], data: dict, /, *, default: Optional[Any] = _NoDefault
) -> Callable:
    """Create a factory method that gets a value from a dictionary by a key path.

    Args:
        key: The key path to look up, either as a string or a list of keys.
            If a list of keys is provided, the first key found will be used.
        data: The dictionary in which the key(s) are searched.
    """

    def get_value_fn():
        """Retrieve a value from a dictionary based on a key path."""
        keys = key.split(".") if isinstance(key, str) else key
        res = data
        for k in keys:
            try:
                res = res[k]
            except KeyError:
                if default is _NoDefault:
                    msg = f"Did not find {keys} ({k} not found), please add an correct keys."
                    raise KeyError(msg)
                else:
                    return default
        return res

    return get_value_fn



def clean_text(text: str) -> str:
    """
    Cleans and preprocesses text data.
    :param text: Raw text string.
    :return: Cleaned text string.
    """
    # Remove extra whitespace, newlines, and tabs
    cleaned_text = re.sub(r"\s+", " ", text).strip()
    return cleaned_text




def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()  # Capture the start time
        result = await func(*args, **kwargs)  # Call the wrapped function
        end_time = time.time()  # Capture the end time
        execution_time = end_time - start_time  # Calculate the execution time
        print(f"{func.__name__} took {execution_time:.4f} seconds")
        return result

    return wrapper


from typing import Any, cast

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)


def str_token_counter(text: str) -> int:
    enc = tiktoken.get_encoding("o200k_base")
    return len(enc.encode(text))


# def tiktoken_counter(messages: List[BaseMessage]) -> int: # TODO:
def tiktoken_counter(messages: Any) -> int:
    """Approximately reproduce https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

    For simplicity only supports str Message.contents.
    """
    num_tokens = 3  # every reply is primed with <|start|>assistant<|message|>
    tokens_per_message = 3
    tokens_per_name = 1
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif isinstance(msg, ToolMessage):
            role = "tool"
        elif isinstance(msg, SystemMessage):
            role = "system"
        else:
            raise ValueError(f"Unsupported messages type {msg.__class__}")
        num_tokens += (
            tokens_per_message + str_token_counter(cast(str, role)) + str_token_counter(cast(str, msg.content))
        )
        if msg.name:
            num_tokens += tokens_per_name + str_token_counter(cast(str, msg.name))
    return num_tokens
