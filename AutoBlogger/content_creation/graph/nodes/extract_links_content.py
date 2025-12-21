from logging_config import logger
from content_creation.graph.state import ContentState
from typing import Dict
import trafilatura

def extract_links_content(state: ContentState) -> Dict:
    logger.info("\n--- Extract Links Content ---")

    if not state.user_links:
        logger.info("No user links provided → skipping extraction")
        logger.info("No user links provided → skipping extraction")
        return {}

    extracted_texts = []

    logger.info(f"Extracting content from {len(state.user_links)} links...")
    for url in state.user_links:
        try:
            logger.info(f"Fetching: {url}")
            downloaded = trafilatura.fetch_url(url)

            if not downloaded:
                logger.info(f"Failed to download: {url}")
                continue

            text = trafilatura.extract(
                downloaded,
                include_formatting=True,
                include_tables=True,
                include_comments=False,
                output_format="markdown"
            )

            if text and len(text.strip()) > 100:
                extracted_texts.append(
                    f"[SOURCE: {url}]\n{text.strip()}"
                )
            else:
                logger.info(f"Low-quality or empty content: {url}")

        except Exception as e:
            logger.info(f"Error fetching {url}: {e}")

    if not extracted_texts:
        logger.info("No meaningful content extracted from provided links.")
        return {
            "exit_reason": "Unable to extract meaningful content from provided links."
        }

    # Join all link contents into one block
    combined_content = "\n\n---\n\n".join(extracted_texts)
    logger.info("Link content extraction completed.")

    return {
        "link_contents": combined_content
    }
