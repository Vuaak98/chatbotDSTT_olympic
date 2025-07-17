"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import field
from typing import Optional

from app.rag.config.base_config import BaseConfiguration

from . import prompts


class RAGConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    generate_queries_system_prompt: Optional[str] = field(
        default=prompts.GENERATE_QUERIES_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used by the retriever to generate queries based on a step in the research plan."
        },
    )
    combined_template: Optional[str] = field(
        default=prompts.COMBINED_TEMPLATE,
        metadata={
            "description": "The full combined template that defines the structure and flow.",
        },
    )
    base_instructions: Optional[str] = field(
        default=prompts.BASE_INSTRUCTIONS,
        metadata={
            "description": "Basic instructions that serve as a foundation for the template's execution.",
        },
    )
    user_info: Optional[str] = field(
        default=prompts.USER_INFO,
        metadata={
            "description": "Information about the user that will be incorporated into the template.",
        },
    )
    current_time: Optional[str] = field(
        default=prompts.CURRENT_TIME,
        metadata={
            "description": "Current local time zone that will be incorporated into the template.",
        },
    )
    conversation_summary: Optional[str] = field(
        default=prompts.CONVERSATION_SUMMARY,
        metadata={"description": "Summary of the ongoing conversation, if available."},
    )
    formatting_instructions: Optional[str] = field(
        default=prompts.FORMATTING_INSTRUCTIONS,
        metadata={
            "description": "Instructions for how the output should be formatted (e.g., JSON, text).",
        },
    )
    multi_query: Optional[str] = field(
        default=None,
        metadata={
            "description": "Instructions or rules for handling multi-query situations (optional).",
        },
    )
if __name__ == "__main__":
    print("Test import thành công!")