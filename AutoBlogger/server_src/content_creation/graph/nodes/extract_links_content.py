from logging_config import get_logger
logger = get_logger("ContentCreationServer")

from server_src.content_creation.graph.state import ContentState
from typing import Dict
import trafilatura

def extract_links_content(state: ContentState) -> Dict:
    """
    Fetch and extract readable content from user-provided URLs.

    This node downloads each URL supplied by the user and extracts
    high-quality, Markdown-formatted text using Trafilatura.
    Extracted content is filtered to remove very short or low-signal pages.

    If no meaningful content can be extracted from any link, the graph
    exits early with an appropriate reason.

    Args:
        state (ContentState): Current graph state containing user-provided links.

    Returns:
        dict:
            - {"link_contents": str} containing combined extracted content
            - {"exit_reason": str} if extraction fails or yields no usable content
            - {} if no user links were provided
    """
    logger.info("--- EXTRACT LINKS CONTENT ---")

    # Guard: no user links provided
    if not state.user_links:
        logger.info("No user links provided; skipping link extraction")
        return {}

    extracted_texts = []

    logger.info(f"Extracting content from {len(state.user_links)} links")

    # Process each user-provided URL
    for url in state.user_links:
        try:
            logger.info(f"Fetching URL: {url}")

            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                logger.warning(f"Failed to download content from URL: {url}")
                continue

            # Extract readable text as Markdown
            text = trafilatura.extract(
                downloaded,
                include_formatting=True,
                include_tables=True,
                include_comments=False,
                output_format="markdown"
            )

            # Filter out low-quality or empty content
            if text and len(text.strip()) > 100:
                extracted_texts.append(
                    f"[SOURCE: {url}]\n{text.strip()}"
                )
                logger.info(f"Successfully extracted content from: {url}")
            else:
                logger.info(f"Low-quality or empty extracted content from: {url}")

        except Exception as e:
            # Catch and log extraction failures per URL
            logger.exception(f"Error extracting content from {url}: {e}")

    # Guard: no usable content extracted
    if not extracted_texts:
        logger.warning("No meaningful content extracted from provided links")
        return {
            "exit_reason": "Unable to extract meaningful content from provided links."
        }

    # Join all extracted contents into a single block
    combined_content = "\n\n---\n\n".join(extracted_texts)

    logger.info("Link content extraction completed successfully")

    return {
        "link_contents": combined_content
    }
