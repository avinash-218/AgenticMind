from logging_config import get_logger
logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState
from typing import Dict
import warnings

# Suppress known LangChain tool field shadowing warnings
warnings.filterwarnings(
    "ignore",
    message="Field name .* shadows an attribute in parent .*BaseTool.*"
)

from langchain_tavily import TavilySearch
web_search_tool = TavilySearch( # Tavily web search tool configuration
    max_results=1,
    search_depth="basic",
    include_raw_content=False,
    include_images=True,
    include_image_descriptions=True,
)

def web_search(state: ContentState) -> Dict:
    """
    Perform web search using Tavily based on generated search keywords.

    This node queries Tavily for each keyword, aggregates high-signal
    textual content, and collects relevant images with descriptions.
    Retrieved data is normalized and merged into the graph state.

    Behavior:
    - If no search keywords are provided, the search is skipped.
    - Low-quality or empty results are filtered out.
    - Image results are deduplicated and merged with existing images.
    - If no meaningful content is retrieved, the graph exits early.

    Args:
        state (ContentState): Current graph state containing search keywords
                              and optional existing images.

    Returns:
        dict:
            - {"tavily_results": str} aggregated text content
            - {"images": List[dict]} merged and deduplicated images
            - {"exit_reason": str} if no meaningful content is retrieved
            - {} if search is skipped
    """
    logger.info("--- WEB SEARCH (TAVILY) ---")

    # Guard: no keywords available
    if not state.search_keywords:
        logger.info("No search keywords provided; skipping web search")
        return {}

    aggregated_results = []
    images = []

    # Execute Tavily search per keyword
    for keyword in state.search_keywords:
        try:
            logger.info(f"Searching Tavily for keyword: {keyword}")

            tavily_results = web_search_tool.invoke(
                {"query": keyword}
            )

            # ---------------- TEXT RESULTS ----------------
            for res in tavily_results.get("results", []):
                title = res.get("title", "")
                content = res.get("content", "")
                url = res.get("url")

                # Filter out low-signal text
                if content and len(content.strip()) > 100:
                    block = f"{title}: {content}".strip()

                    if url:
                        aggregated_results.append(
                            f"[QUERY: {keyword}]\n[SOURCE: {url}]\n{block}"
                        )
                    else:
                        aggregated_results.append(
                            f"[QUERY: {keyword}]\n{block}"
                        )

            # ---------------- IMAGE RESULTS ----------------
            for img in tavily_results.get("images", []):
                img_url = img.get("url")
                img_desc = img.get("description")

                if img_url:
                    images.append(
                        {
                            "url": img_url,
                            "description": img_desc.strip() if img_desc else "No Description",
                            "query": keyword,
                            "source": "tavily"
                        }
                    )

        except Exception as e:
            logger.exception(f"Tavily search error for keyword '{keyword}': {e}")

    # Guard: no usable content retrieved
    if not aggregated_results and not images:
        logger.warning("No meaningful content retrieved from Tavily search")
        return {
            "exit_reason": "No meaningful content retrieved from Tavily search."
        }

    result: Dict = {}

    # Attach aggregated text results
    if aggregated_results:
        result["tavily_results"] = "\n\n---\n\n".join(aggregated_results)

    # Merge and deduplicate images
    if images:
        all_images = (state.images or []) + images

        seen = set()
        unique_images = []

        for img in all_images:
            url = img.get("url")
            if not url:
                continue
            if url not in seen:
                unique_images.append(img)
                seen.add(url)

        result["images"] = unique_images

    logger.info(
        f"Tavily search completed: "
        f"{len(aggregated_results)} text blocks, "
        f"{len(images)} images retrieved"
    )

    return result
