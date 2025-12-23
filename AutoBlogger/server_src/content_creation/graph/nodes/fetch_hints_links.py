import json
from logging_config import get_logger

logger = get_logger("ContentCreationServer")
import os
from server_src.content_creation.graph.state import ContentState

def fetch_hints_links(state: ContentState):
    INPUT_FILE = os.path.join(os.curdir, os.getenv("INPUT_FILE"))
    logger.info('---FETCH HINTS, LINKS, IMAGES---')

    if not os.path.exists(INPUT_FILE):
        return {"exit_reason": f"Input file not found: {INPUT_FILE}"}

    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    state.user_hints = data.get("hints", [])
    state.user_links = data.get("links", [])
    raw_images = data.get("images", [])
    state.images = [
        {
            "url": url,
            "source": "user"
        }
        for url in raw_images
        if isinstance(url, str) and url.strip()
    ]

    if not all([state.user_hints, state.user_links, state.images]):
        return {"exit_reason": "Input file contains no usable content"}

    return state