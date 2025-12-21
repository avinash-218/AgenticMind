from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class ContentState(BaseModel):
    """
    State object for the content creation pipeline.
    """
    title: str = Field(
        ...,
        description="Mandatory user-provided title or topic for the content to be generated."
    )

    user_hints: Optional[List[str]] = Field(
        None,
        description=(
            "Optional free-form hints, notes, or guidance provided by the user. "
            "Used to steer relevance checks, keyword generation, and final content tone."
        )
    )

    user_links: Optional[List[str]] = Field(
        None,
        description=(
            "Optional list of URLs supplied by the user. These links are fetched and summarized "
            "to extract relevant background information related to the title."
        )
    )

    title_hints_relevant: Optional[bool] = Field(
        None,
        description=(
            "Result of semantic relevance check between the title and user hints. "
            "False indicates insufficient relevance and triggers early exit."
        )
    )

    title_links_relevant: Optional[bool] = Field(
        None,
        description=(
            "Result of semantic relevance check between the title and extracted link contents. "
            "False indicates links are not useful for the given title and triggers early exit."
        )
    )

    exit_reason: Optional[str] = Field(
        None,
        description=(
            "Human-readable explanation for early termination of the graph execution, "
            "used when a validation step fails."
        )
    )

    link_contents: Optional[str] = Field(
        None,
        description=(
            "Condensed textual summary extracted from user-provided links. "
            "This is generated after fetching and summarizing external web pages."
        )
    )

    search_keywords: Optional[List[str]] = Field(
        None,
        description=(
            "List of concise search keywords generated from the title, user hints, "
            "and link contents. Used for web search and retrieval."
        )
    )

    tavily_results: Optional[str] = Field(
        None,
        description=(
            "Aggregated and summarized content retrieved from web search "
            "(via Tavily or free scraping alternatives)."
        )
    )

    images: Optional[List[Dict[str, str]]] = None

    compiled_context: Optional[str] = Field(
        None,
        description=(
            "Unified context assembled from user hints, extracted link content, "
            "and web search results. Acts as the single source of truth for generation."
        )
    )

    content: Optional[str] = Field(
        None,
        description=(
            "Final generated content (e.g., blog post or article) produced by the "
            "content generation model."
        )
    )
