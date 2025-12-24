import json
import os
from logging_config import get_logger
logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.configs.configs import ConfigLoader

def fetch_hints_links(state: ContentState):
    """
    Load user-provided hints, links, and images from a JSON input file.

    This node reads a configured input JSON file and populates the graph
    state with:
    - textual hints
    - reference links
    - image URLs (normalized into a standard structure)

    If the file is missing or contains no usable content, the graph exits
    early with a descriptive reason.

    Args:
        state (ContentState): Current graph state to be populated with
                              user inputs.

    Returns:
        dict | ContentState:
            - Updated ContentState on success
            - {"exit_reason": str} if input validation fails
    """
    logger.info("--- FETCH HINTS, LINKS, AND IMAGES ---")

    # Resolve input file path from config
    config_data = ConfigLoader()    # load config yaml file
    input_file_path = config_data['INPUT_FILE_PATH']
    INPUT_FILE = os.path.join(os.curdir, input_file_path) if input_file_path else None

    # Guard: input file path not configured
    if not INPUT_FILE:
        logger.error("Input file path is invalid")
        return {"exit_reason": "Input file path is invalid"}

    logger.info(f"Input file path: {INPUT_FILE}")

    # Guard: input file does not exist
    if not os.path.exists(INPUT_FILE):
        logger.error(f"Input file not found: {INPUT_FILE}")
        return {"exit_reason": f"Input file not found: {INPUT_FILE}"}

    # Load input JSON
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    # Populate state fields
    state.user_hints = data.get("hints", [])
    state.user_links = data.get("links", [])

    # Normalize image URLs into structured objects
    raw_images = data.get("images", [])
    state.images = [
        {
            "url": url,
            "source": "user"
        }
        for url in raw_images
        if isinstance(url, str) and url.strip()
    ]

    logger.info(
        f"Loaded input: "
        f"{len(state.user_hints)} hints, "
        f"{len(state.user_links)} links, "
        f"{len(state.images)} images"
    )

    # Guard: no usable content provided
    if not any([state.user_hints, state.user_links, state.images]):
        logger.warning("Input file contains no usable hints, links, or images")
        return {"exit_reason": "Input file contains no usable content"}

    return state
