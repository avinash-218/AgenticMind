import sys
import os

# Add project root to PYTHONPATH to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from logging_config import get_logger
# Initialize logger for Hashnode MCP server
logger = get_logger("HashnodeServer")
logger.info("HashnodeServer started")

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from server_src.hashnode_graphql_queries import (
    ME_QUERY,
    CREATE_DRAFT_QUERY,
    GET_PUBLICATION_QUERY,
    PUBLICATION_POSTS_QUERY,
    PUBLICATION_QUERY,
    PUBLISH_DRAFT_QUERY,
    REMOVE_POST_QUERY,
    UPDATE_POST_QUERY,
)

# Load environment variables (API URL and token)
load_dotenv()
HASHNODE_API_URL = os.getenv("HASHNODE_API_URL")
HASHNODE_TOKEN = os.getenv("HASHNODE_TOKEN")

# Initialize MCP server
mcp = FastMCP("Hashnode_Server")

async def fetch_from_api(query: str, variables: dict = None) -> dict:
    """
    Execute a GraphQL request against the Hashnode API.

    Parameters
    ----------
    query : str
        GraphQL query or mutation string.
    variables : dict, optional
        Variables required by the GraphQL query.

    Returns
    -------
    dict
        Parsed JSON response from the API.

    Raises
    ------
    httpx.HTTPStatusError
        If the API returns a non-2xx status code.
    """
    headers = {
        "Authorization": HASHNODE_TOKEN,
        "Content-Type": "application/json",
    }

    # Use an async HTTP client to avoid blocking the event loop
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Send POST request with GraphQL query and optional variables
        response = await client.post(
            HASHNODE_API_URL,
            json={"query": query, "variables": variables},
            headers=headers,
        )

        # Raise an exception if the HTTP response is not 2xx
        response.raise_for_status()

        # Log successful response receipt (without dumping payload)
        logger.debug("Received successful response from Hashnode API")

        # Return parsed JSON body
        return response.json()

def format_section(title: str, content: str) -> str:
    """
    Format a section for consistent, readable terminal output.

    Parameters
    ----------
    title : str
        Section header.
    content : str
        Body content of the section.

    Returns
    -------
    str
        Formatted section string.
    """
    divider = "-" * len(title)
    return f"\n{title}\n{divider}\n{content.strip()}\n"

@mcp.tool()
async def get_authenticated_user() -> str:
    """
    Fetch details of the authenticated Hashnode user.

    Returns
    -------
    str
        Structured user profile information or an error message.
    """
    try:
        # Log start of user profile fetch
        logger.info("Fetching authenticated user details.")

        # Call Hashnode API to retrieve current authenticated user
        data = await fetch_from_api(ME_QUERY)

        # Safely extract the user object from the GraphQL response
        me = data.get("data", {}).get("me", {})

        # Handle missing or invalid authentication
        if not me:
            logger.warning("No authenticated user found in Hashnode response.")
            return "No authenticated user found. Please check your HASHNODE_TOKEN."

        # Build a list of user's publications
        pub_list = [
            f"  - {p.get('node', {}).get('title', 'Untitled')} "
            f"(id: {p.get('node', {}).get('id', 'N/A')})"
            for p in me.get("publications", {}).get("edges", [])
        ] or ["  None"]

        # Extract and format the user's tech stack
        tech_stack = ", ".join(
            [t.get("name") for t in me.get("techStack", {}).get("nodes", [])]
        ) or "None"

        # Extract available social media links
        socials = me.get("socialMediaLinks", {}) or {}
        social_links = ", ".join(
            [f"{k}: {v}" for k, v in socials.items() if v]
        ) or "None"

        # Assemble core user profile information into a formatted block
        user_info = f"""
Name: {me.get('name', 'N/A')}
Username: {me.get('username', 'N/A')}
Bio: {me.get('bio', {}).get('text', 'N/A')}
Location: {me.get('location', 'N/A')}
Role: {me.get('role', 'N/A')}
Joined: {me.get('dateJoined', 'N/A')}
Followers: {me.get('followersCount', 0)}
Following: {me.get('followingsCount', 0)}
Tagline: {me.get('tagline', 'N/A')}
Profile Picture: {me.get('profilePicture', 'N/A')}
"""

        # Group all formatted sections for final output
        sections = [
            format_section("USER DETAILS", user_info),
            format_section("TECH STACK", tech_stack),
            format_section("SOCIAL LINKS", social_links),
            format_section("PUBLICATIONS (First 5)", "\n".join(pub_list)),
        ]

        # Log successful user profile retrieval
        logger.info("Authenticated user details fetched successfully.")

        # Return combined output as a single formatted string
        return "\n".join(sections).strip()

    except Exception as e:
        # Log unexpected errors for debugging and observability
        logger.error("Failed to fetch authenticated user details.", exc_info=True)
        return f"Error: {str(e)}"

@mcp.tool()
async def create_draft_article(
    title: str,
    content_markdown: str,
    subtitle: str = "",
    tags: str = ""
) -> str:
    """
    Create a new draft article in the user's primary publication.

    Parameters
    ----------
    title : str
        Article title.
    content_markdown : str
        Markdown content for the article body.
    subtitle : str, optional
        Optional subtitle.
    tags : str, optional
        Comma-separated list of tags.

    Returns
    -------
    str
        Draft creation status and metadata.
    """
    try:
        # Log start of draft creation flow
        logger.info("Creating draft article.")

        # Fetch publication details to determine publication ID
        pub_data = await fetch_from_api(GET_PUBLICATION_QUERY)

        # Safely extract publication edges from the response
        edges = (
            pub_data.get("data", {})
            .get("me", {})
            .get("publications", {})
            .get("edges", [])
        )

        # If no publications exist, draft creation cannot proceed
        if not edges:
            logger.warning("No publication found for authenticated user.")
            return "No publication found. Please ensure your Hashnode account has a publication."

        # Use the first publication as the default target
        publication_id = edges[0]["node"]["id"]

        # Convert comma-separated tags into Hashnode-compatible tag objects
        tag_objects = [
            {"name": t.strip(), "slug": t.strip().lower().replace(" ", "-")}
            for t in tags.split(",") if t.strip()
        ]

        # Build input payload for draft creation mutation
        input_data = {
            "publicationId": publication_id,
            "title": title,
            "subtitle": subtitle,
            "contentMarkdown": content_markdown,
            "tags": tag_objects,
        }

        # Execute GraphQL mutation to create the draft
        response = await fetch_from_api(CREATE_DRAFT_QUERY, {"input": input_data})

        # Extract draft object from API response
        draft = response.get("data", {}).get("createDraft", {}).get("draft", {})

        # Handle unexpected failure where draft is not returned
        if not draft:
            logger.error("Draft creation failed. No draft returned by API.")
            return "Failed to create draft."

        # Format draft metadata for output
        content = f"""
ID: {draft.get('id', 'N/A')}
Title: {draft.get('title', 'N/A')}
Slug: {draft.get('slug', 'N/A')}
Publication: {draft.get('publication', {}).get('title', 'N/A')}
Author: {draft.get('author', {}).get('name', 'N/A')} (@{draft.get('author', {}).get('username', '')})
Read Time: {draft.get('readTimeInMinutes', 'N/A')} mins
Tags: {', '.join([t['name'] for t in draft.get('tags', [])]) or 'None'}
Updated: {draft.get('updatedAt', 'N/A')}
"""

        # Log successful draft creation
        logger.info(f"Draft created successfully (id={draft.get('id')}).")

        # Return formatted response section
        return format_section("DRAFT CREATED SUCCESSFULLY", content)

    except Exception as e:
        # Log unexpected errors with full traceback for debugging
        logger.error("Error occurred while creating draft article.", exc_info=True)
        return f"Error: {str(e)}"

@mcp.tool()
async def publish_draft_article(draft_id: str) -> str:
    """
    Publish an existing draft article.

    Parameters
    ----------
    draft_id : str
        Draft identifier.

    Returns
    -------
    str
        Publication result and post metadata.
    """
    try:
        # Log the start of draft publishing process
        logger.info(f"Publishing draft article (draft_id={draft_id}).")

        # Call Hashnode API to publish the draft
        response = await fetch_from_api(
            PUBLISH_DRAFT_QUERY,
            {"input": {"draftId": draft_id}}
        )

        # Safely extract the published post object
        post = response.get("data", {}).get("publishDraft", {}).get("post", {})

        # Handle failure when API does not return a post
        if not post:
            logger.error(f"Draft publish failed for draft_id={draft_id}.")
            return "Failed to publish draft."

        # Format published post metadata for output
        content = f"""
Post ID: {post.get('id', 'N/A')}
Title: {post.get('title', 'N/A')}
Slug: {post.get('slug', 'N/A')}
Publication: {post.get('publication', {}).get('title', 'N/A')}
Author: {post.get('author', {}).get('name', 'N/A')} (@{post.get('author', {}).get('username', '')})
Tags: {', '.join([t['name'] for t in post.get('tags', [])]) or 'None'}
Read Time: {post.get('readTimeInMinutes', 'N/A')} mins
Published: {post.get('publishedAt', 'N/A')}
Updated: {post.get('updatedAt', 'N/A')}
Views: {post.get('views', 0)}
Featured: {'Yes' if post.get('featured') else 'No'}
URL: {post.get('url', 'N/A')}
"""

        # Log successful publication
        logger.info(f"Draft published successfully (post_id={post.get('id')}).")

        # Return formatted success response
        return format_section("DRAFT PUBLISHED SUCCESSFULLY", content)

    except Exception as e:
        # Log unexpected errors with traceback for debugging
        logger.error(f"Error occurred while publishing draft (draft_id={draft_id}).", exc_info=True)
        return f"Error: {str(e)}"

@mcp.tool()
async def update_post_article(
    post_id: str,
    title: str = None,
    content_markdown: str = None,
    subtitle: str = None,
    tags: str = None,
    canonical_url: str = None
) -> str:
    """
    Update an existing published post.

    Parameters
    ----------
    post_id : str
        Post identifier.
    title : str, optional
        Updated title.
    content_markdown : str, optional
        Updated markdown content.
    subtitle : str, optional
        Updated subtitle.
    tags : str, optional
        Comma-separated list of tags.
    canonical_url : str, optional
        Canonical URL for SEO.

    Returns
    -------
    str
        Update result and post metadata.
    """
    try:
        # Log start of post update operation
        logger.info(f"Updating post (post_id={post_id}).")

        # Initialize mutation input with mandatory post ID
        input_data = {"id": post_id}

        # Conditionally include only provided fields in update payload
        if title:
            input_data["title"] = title
        if content_markdown:
            input_data["contentMarkdown"] = content_markdown
        if subtitle:
            input_data["subtitle"] = subtitle
        if canonical_url:
            input_data["canonicalUrl"] = canonical_url
        if tags:
            # Convert comma-separated tags into Hashnode-compatible format
            input_data["tags"] = [
                {"name": t.strip(), "slug": t.strip().lower().replace(" ", "-")}
                for t in tags.split(",") if t.strip()
            ]

        # Execute GraphQL mutation to update the post
        response = await fetch_from_api(UPDATE_POST_QUERY, {"input": input_data})

        # Safely extract updated post object from API response
        post = response.get("data", {}).get("updatePost", {}).get("post", {})

        # Handle failure when API does not return updated post
        if not post:
            logger.error(f"Post update failed (post_id={post_id}).")
            return "Failed to update post."

        # Format updated post metadata for output
        content = f"""
ID: {post.get('id')}
Title: {post.get('title')}
Slug: {post.get('slug')}
Updated: {post.get('updatedAt')}
Publication: {post.get('publication', {}).get('title', 'N/A')}
Author: {post.get('author', {}).get('name')} (@{post.get('author', {}).get('username', '')})
Tags: {', '.join([t['name'] for t in post.get('tags', [])]) or 'None'}
URL: {post.get('url', 'N/A')}
"""

        # Log successful post update
        logger.info(f"Post updated successfully (post_id={post.get('id')}).")

        # Return formatted success response
        return format_section("POST UPDATED SUCCESSFULLY", content)

    except Exception as e:
        # Log unexpected errors with full traceback for debugging
        logger.error(f"Error occurred while updating post (post_id={post_id}).", exc_info=True)
        return f"Error: {str(e)}"

@mcp.tool()
async def remove_post_article(post_id: str) -> str:
    """
    Permanently remove a published post.

    Parameters
    ----------
    post_id : str
        Post identifier.

    Returns
    -------
    str
        Removal confirmation details.
    """
    try:
        # Log start of post removal operation
        logger.info(f"Removing post (post_id={post_id}).")

        # Call Hashnode API to remove the specified post
        response = await fetch_from_api(
            REMOVE_POST_QUERY,
            {"input": {"id": post_id}}
        )

        # Safely extract removed post object from API response
        post = response.get("data", {}).get("removePost", {}).get("post", {})

        # Handle failure when API does not return a post
        if not post:
            logger.error(f"Post removal failed (post_id={post_id}).")
            return "Failed to remove post."

        # Format removed post metadata for output
        content = f"""
Post ID: {post.get('id')}
Title: {post.get('title')}
Slug: {post.get('slug')}
Publication: {post.get('publication', {}).get('title', 'N/A')}
Author: {post.get('author', {}).get('name')} (@{post.get('author', {}).get('username', '')})
Status: Deleted Permanently
"""

        # Log successful post removal
        logger.info(f"Post removed successfully (post_id={post.get('id')}).")

        # Return formatted success response
        return format_section("POST REMOVED SUCCESSFULLY", content)

    except Exception as e:
        # Log unexpected errors with traceback for debugging
        logger.error(f"Error occurred while removing post (post_id={post_id}).", exc_info=True)
        return f"Error: {str(e)}"

@mcp.tool()
async def get_publication_info(host: str) -> str:
    """
    Fetch metadata for a Hashnode publication.

    Parameters
    ----------
    host : str
        Publication host (e.g., blog.domain.com).

    Returns
    -------
    str
        Publication details.
    """
    try:
        # Log start of publication metadata fetch
        logger.info(f"Fetching publication info for host: {host}")

        # Call Hashnode API to retrieve publication details by host
        response = await fetch_from_api(PUBLICATION_QUERY, {"host": host})

        # Safely extract publication object from response
        publication = response.get("data", {}).get("publication", {})

        # Handle case where no publication exists for the given host
        if not publication:
            logger.warning(f"No publication found for host: {host}")
            return f"No publication found for host: {host}"

        # Format publication metadata for output
        content = f"""
Host: {host}
Title: {publication.get('title', 'N/A')}
Type: {'Team Publication' if publication.get('isTeam') else 'Personal Publication'}
About:
{publication.get('about', {}).get('markdown', 'No description available.')}
"""

        # Log successful publication metadata retrieval
        logger.info(f"Publication info fetched successfully for host: {host}")

        # Return formatted publication information
        return format_section("PUBLICATION INFO", content)

    except Exception as e:
        # Log unexpected errors with traceback for debugging
        logger.error(f"Error occurred while fetching publication info for host: {host}", exc_info=True)
        return f"Error: {str(e)}"

@mcp.tool()
async def get_publication_posts(host: str, limit: int = 10) -> str:
    """
    Fetch recent posts from a publication.

    Parameters
    ----------
    host : str
        Publication host.
    limit : int, optional
        Number of posts to retrieve.

    Returns
    -------
    str
        List of recent posts.
    """
    try:
        # Log start of publication posts fetch
        logger.info(f"Fetching recent posts for publication host: {host}")

        # Call Hashnode API to retrieve recent posts for the given publication
        response = await fetch_from_api(
            PUBLICATION_POSTS_QUERY,
            {"host": host, "limit": limit}
        )

        # Safely extract publication object from API response
        publication = response.get("data", {}).get("publication", {})

        # Handle case where publication does not exist
        if not publication:
            logger.warning(f"No publication found for host: {host}")
            return f"No publication found for host: {host}"

        # Extract list of post edges
        posts = publication.get("posts", {}).get("edges", [])

        # Handle case where publication has no posts
        if not posts:
            logger.info(f"No posts found for publication host: {host}")
            return f"No posts found for publication: {host}"

        # Build a human-readable list of recent posts
        post_list = []
        for i, p in enumerate(posts, start=1):
            # Extract individual post node safely
            node = p.get("node", {})

            # Append formatted post summary to list
            post_list.append(
                f"{i}. {node.get('title', 'Untitled')}\n"
                f"   {node.get('brief', '').strip()}\n"
                f"   URL: {node.get('url', 'N/A')}"
            )

        # Format publication and post details for output
        content = f"""
Host: {host}
Title: {publication.get('title', 'N/A')}
Type: {'Team Publication' if publication.get('isTeam') else 'Personal Publication'}
Recent Posts ({len(posts)}):
{chr(10).join(post_list)}
"""

        # Log successful retrieval of publication posts
        logger.info(f"Fetched {len(posts)} posts for publication host: {host}")

        # Return formatted output
        return format_section("PUBLICATION POSTS", content)

    except Exception as e:
        # Log unexpected errors with traceback for debugging
        logger.error(f"Error occurred while fetching posts for publication host: {host}", exc_info=True)
        return f"Error: {str(e)}"

if __name__ == "__main__":
    """
    Entry point for starting the Hashnode MCP Server.
    """
    logger.info("Starting Hashnode MCP Server...")
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8001
    mcp.run(transport="sse")
