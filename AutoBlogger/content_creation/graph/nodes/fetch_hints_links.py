from logging_config import get_logger

logger = get_logger("ContentCreationServer")
import os
import re
from content_creation.graph.state import ContentState

def fetch_hints_links(state: ContentState):
    INPUT_FILE=os.path.join(os.curdir, os.getenv("INPUT_FILE"))
    logger.info('---FETCH HINTS AND LINKS---')
    URL_REGEX = re.compile(r"https?://\S+")
    
    if not os.path.exists(INPUT_FILE):
        logger.info(f"Input file not found: {INPUT_FILE}")
        return {
            "exit_reason": f"Input file not found: {INPUT_FILE}"
        }

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f if line.strip()]

    points = []
    links = []

    for line in raw_lines:
        found_links = URL_REGEX.findall(line)

        if found_links:
            links.extend(found_links)

            # remove links from line, keep remaining text as a point if meaningful
            cleaned = URL_REGEX.sub("", line).strip(" -•:")
            if cleaned:
                points.append(cleaned)
        else:
            points.append(line)

    if not points and not links:
        logger.info("Input file contains no usable content")
        return {
            "exit_reason": "Input file contains no usable content"
        }

    if points:
        state.user_hints = points

    if links:
        # de-duplicate while preserving order
        seen = set()
        unique_links = []
        for l in links:
            if l not in seen:
                unique_links.append(l)
                seen.add(l)

        state.user_links = unique_links
    
    return state