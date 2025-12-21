from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from langchain_tavily import TavilySearch
from typing import Dict
from content_creation.graph.state import ContentState

web_search_tool = TavilySearch(
    max_results=1,
    search_depth="basic",
    include_raw_content=False,
    include_images=True,
    include_image_descriptions=True,
)

def web_search(state: ContentState) -> Dict:
    logger.info('--- WEB SEARCH (Tavily) ---')

    if not state.search_keywords:
        logger.info("No search keywords provided → skipping web search")
        return {}

    aggregated_results = []
    images = []

    for keyword in state.search_keywords:
        try:
            logger.info(f"Searching Tavily for: {keyword}")

            tavily_results = web_search_tool.invoke(
                {"query": keyword}
            )

            # -------- TEXT CONTENT --------
            for res in tavily_results.get("results", []):
                title = res.get("title", "")
                content = res.get("content", "")
                url = res.get("url")

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

            # -------- IMAGES --------
            for img in tavily_results.get("images", []):
                img_url = img.get("url")
                img_desc = img.get("description")

                if img_url and img_desc:
                    images.append(
                        {
                            "url": img_url,
                            "description": img_desc.strip(),
                            "query": keyword
                        }
                    )

        except Exception as e:
            logger.error(f"Tavily search error for '{keyword}': {e}")

    if not aggregated_results and not images:
        logger.info("No meaningful content retrieved from Tavily search.")
        return {
            "exit_reason": "No meaningful content retrieved from Tavily search."
        }

    result: Dict = {}

    if aggregated_results:
        result["tavily_results"] = "\n\n---\n\n".join(aggregated_results)

    if images:
        # remove duplicate images
        seen = set()
        unique_images = []
        for img in images:
            if img["url"] not in seen:
                unique_images.append(img)
                seen.add(img["url"])

        result["images"] = unique_images

    logger.info(f"Tavily search retrieved {len(aggregated_results)} text results and {len(images)} images.")

    return result
