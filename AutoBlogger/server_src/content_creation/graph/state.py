from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class ContentState(BaseModel):
    """
    Central state container for the content creation LangGraph pipeline.

    This Pydantic model defines all inputs, intermediate artifacts, validation
    flags, and final outputs that flow through the graph. Each node in the
    pipeline reads from and writes to this shared state object.
    """

    # User-provided inputs
    title: str = Field(
        ...,
        description=(
            "Mandatory user-provided title or topic for which content "
            "will be generated."
        )
    )

    user_hints: Optional[List[str]] = Field(
        None,
        description=(
            "Optional free-form hints, notes, or guidance provided by the user. "
            "These are used to steer relevance validation, keyword generation, "
            "and the tone or focus of the final content."
        )
    )

    user_links: Optional[List[str]] = Field(
        None,
        description=(
            "Optional list of URLs supplied by the user. "
            "These links are fetched and summarized to extract "
            "background information relevant to the title."
        )
    )

    # Validation flags and exit handling
    title_hints_relevant: Optional[bool] = Field(
        None,
        description=(
            "Indicates whether the user hints are semantically relevant "
            "to the provided title. A value of False triggers early exit."
        )
    )

    title_links_relevant: Optional[bool] = Field(
        None,
        description=(
            "Indicates whether extracted link content is semantically "
            "relevant to the title. A value of False triggers early exit."
        )
    )

    exit_reason: Optional[str] = Field(
        None,
        description=(
            "Human-readable explanation describing why the graph execution "
            "terminated early due to a validation failure."
        )
    )

    # Intermediate artifacts
    link_contents: Optional[str] = Field(
        None,
        description=(
            "Condensed textual summary extracted from user-provided links "
            "after fetching and summarization."
        )
    )

    search_keywords: Optional[List[str]] = Field(
        None,
        description=(
            "List of concise search keywords derived from the title, user hints, "
            "and link contents. Used to drive web search and retrieval."
        )
    )

    tavily_results: Optional[str] = Field(
        None,
        description=(
            "Aggregated and summarized content retrieved from web search "
            "using Tavily or equivalent search providers."
        )
    )

    images: Optional[List[Dict[str, str]]] = Field(
        None,
        description=(
            "Optional list of images provided by the user or discovered during "
            "retrieval. Each image dictionary must include at least a `url` key."
        )
    )

    compiled_context: Optional[str] = Field(
        None,
        description=(
            "Unified context assembled from user hints, extracted link content, "
            "and web search results. This serves as the single source of truth "
            "for final content generation."
        )
    )

    # Final output
    content: Optional[str] = Field(
        None,
        description=(
            "Final generated content (e.g., blog post or article) produced "
            "by the content generation model."
        )
    )
