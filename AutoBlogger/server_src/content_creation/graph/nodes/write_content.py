from logging_config import get_logger
logger = get_logger("ContentCreationServer")

from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.chains.content_writer_chain import content_writer

def write_content(state: ContentState):
    """
    Generate the final written content using the compiled context and images.

    This node invokes the content writer LLM chain to produce a complete,
    publication-ready blog post in Markdown format. Images are formatted
    into a structured block to guide proper placement and usage.

    Args:
        state (ContentState): Current graph state containing the title,
                              compiled context, and optional images.

    Returns:
        dict:
            - {"content": str} containing the generated Markdown content
    """
    logger.info("--- WRITE CONTENT ---")

    # Prepare images block for the model
    images_block = ""
    if state.images:
        logger.info(f"Formatting {len(state.images)} images for content generation")
        images_block = "\n".join(
            f"- URL: {img.get('url', 'N/A')}\n"
            f"  Description: {img.get('description', 'No description available')}"
            for img in state.images
        )
    else:
        logger.info("No images provided for content generation")

    # Invoke content writer LLM
    logger.info("Invoking content writer model")

    result = content_writer.invoke(
        {
            "title": state.title,
            "context": state.compiled_context,
            "images": images_block
        }
    )

    logger.info("Content writing completed successfully")

    return {
        "content": result.content
    }
