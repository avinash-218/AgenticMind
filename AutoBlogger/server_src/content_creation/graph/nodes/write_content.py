from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.chains.content_writer_chain import content_writer

def write_content(state: ContentState):
    logger.info('--- WRITE CONTENT ---')

    # Prepare images block for the model
    images_block = ""
    if state.images:
        images_block = "\n".join(
            f"- URL: {img.get('url', 'N/A')}\n"
            f"  Description: {img.get('description', 'No description available')}"
            for img in state.images
        )
    logger.info('Invoking content writer model...')
    result = content_writer.invoke(
        {
            "title": state.title,
            "context": state.compiled_context,
            'images': images_block
        }
    )
    logger.info('Content writing completed.')
    return {
        "content": result.content
    }

