from logging_config import logger
from content_creation.graph.state import ContentState
from content_creation.graph.chains.content_writer_chain import content_writer

def write_content(state: ContentState):
    logger.info('--- WRITE CONTENT ---')

    # Prepare images block for the model
    images_block = ""
    if state.images:
        images_block = "\n".join(
            f"- URL: {img['url']}\n  Description: {img['description']}"
            for img in state.images[:5]  # hard cap for safety
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

