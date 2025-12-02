import os
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from queries import (
    ME_QUERY,
    CREATE_DRAFT_QUERY,
    GET_PUBLICATION_QUERY,
    PUBLICATION_POSTS_QUERY,
    PUBLICATION_QUERY,
    PUBLISH_DRAFT_QUERY,
    REMOVE_POST_QUERY,
    UPDATE_POST_QUERY,
)

load_dotenv()
HASHNODE_API_URL = os.getenv("HASHNODE_API_URL")
HASHNODE_TOKEN = os.getenv("HASHNODE_TOKEN")

mcp = FastMCP("Hashnode_Server")

async def fetch_from_api(query: str, variables: dict = None) -> dict:
    headers = {
        "Authorization": HASHNODE_TOKEN,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            HASHNODE_API_URL,
            json={"query": query, "variables": variables},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

def format_section(title: str, content: str) -> str:
    """Formats each section for consistent terminal output."""
    divider = "-" * len(title)
    return f"\n{title}\n{divider}\n{content.strip()}\n"

@mcp.tool()
async def get_authenticated_user() -> str:
    """Fetch authenticated Hashnode user details."""
    try:
        data = await fetch_from_api(ME_QUERY)
        me = data.get("data", {}).get("me", {})
        if not me:
            return "No authenticated user found. Please check your HASHNODE_TOKEN."

        pub_list = [
            f"  - {p.get('node', {}).get('title', 'Untitled')} (id: {p.get('node', {}).get('id', 'N/A')})"
            for p in me.get("publications", {}).get("edges", [])
        ] or ["  None"]

        tech_stack = ", ".join(
            [t.get("name") for t in me.get("techStack", {}).get("nodes", [])]
        ) or "None"

        socials = me.get("socialMediaLinks", {}) or {}
        social_links = ", ".join([f"{k}: {v}" for k, v in socials.items() if v]) or "None"

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

        sections = [
            format_section("USER DETAILS", user_info),
            format_section("TECH STACK", tech_stack),
            format_section("SOCIAL LINKS", social_links),
            format_section("PUBLICATIONS (First 5)", "\n".join(pub_list)),
        ]

        return "\n".join(sections).strip()

    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def create_draft_article(title: str, content_markdown: str, subtitle: str = "", tags: str = "") -> str:
    """Create a new draft article."""
    try:
        pub_data = await fetch_from_api(GET_PUBLICATION_QUERY)
        edges = pub_data.get("data", {}).get("me", {}).get("publications", {}).get("edges", [])
        if not edges:
            return "No publication found. Please ensure your Hashnode account has a publication."

        publication_id = edges[0]["node"]["id"]

        tag_objects = [
            {"name": t.strip(), "slug": t.strip().lower().replace(" ", "-")}
            for t in tags.split(",") if t.strip()
        ]

        input_data = {
            "publicationId": publication_id,
            "title": title,
            "subtitle": subtitle,
            "contentMarkdown": content_markdown,
            "tags": tag_objects,
        }

        response = await fetch_from_api(CREATE_DRAFT_QUERY, {"input": input_data})
        draft = response.get("data", {}).get("createDraft", {}).get("draft", {})

        if not draft:
            return "Failed to create draft."

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
        return format_section("DRAFT CREATED SUCCESSFULLY", content)

    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def publish_draft_article(draft_id: str) -> str:
    """Publish a draft article."""
    try:
        response = await fetch_from_api(PUBLISH_DRAFT_QUERY, {"input": {"draftId": draft_id}})
        post = response.get("data", {}).get("publishDraft", {}).get("post", {})

        if not post:
            return "Failed to publish draft."

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
        return format_section("DRAFT PUBLISHED SUCCESSFULLY", content)

    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def update_post_article(
    post_id: str, title: str = None, content_markdown: str = None,
    subtitle: str = None, tags: str = None, canonical_url: str = None
) -> str:
    """Update an existing post."""
    try:
        input_data = {"id": post_id}
        if title:
            input_data["title"] = title
        if content_markdown:
            input_data["contentMarkdown"] = content_markdown
        if subtitle:
            input_data["subtitle"] = subtitle
        if canonical_url:
            input_data["canonicalUrl"] = canonical_url
        if tags:
            input_data["tags"] = [
                {"name": t.strip(), "slug": t.strip().lower().replace(" ", "-")}
                for t in tags.split(",") if t.strip()
            ]

        response = await fetch_from_api(UPDATE_POST_QUERY, {"input": input_data})
        post = response.get("data", {}).get("updatePost", {}).get("post", {})

        if not post:
            return "Failed to update post."

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
        return format_section("POST UPDATED SUCCESSFULLY", content)

    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def remove_post_article(post_id: str) -> str:
    """Remove a published post."""
    try:
        response = await fetch_from_api(REMOVE_POST_QUERY, {"input": {"id": post_id}})
        post = response.get("data", {}).get("removePost", {}).get("post", {})

        if not post:
            return "Failed to remove post."

        content = f"""
Post ID: {post.get('id')}
Title: {post.get('title')}
Slug: {post.get('slug')}
Publication: {post.get('publication', {}).get('title', 'N/A')}
Author: {post.get('author', {}).get('name')} (@{post.get('author', {}).get('username', '')})
Status: Deleted Permanently
"""
        return format_section("POST REMOVED SUCCESSFULLY", content)

    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_publication_info(host: str) -> str:
    """Fetch basic information about a publication."""
    try:
        response = await fetch_from_api(PUBLICATION_QUERY, {"host": host})
        publication = response.get("data", {}).get("publication", {})
        if not publication:
            return f"No publication found for host: {host}"

        content = f"""
Host: {host}
Title: {publication.get('title', 'N/A')}
Type: {'Team Publication' if publication.get('isTeam') else 'Personal Publication'}
About:
{publication.get('about', {}).get('markdown', 'No description available.')}
"""
        return format_section("PUBLICATION INFO", content)

    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_publication_posts(host: str, limit: int = 10) -> str:
    """Fetch recent posts from a publication."""
    try:
        response = await fetch_from_api(PUBLICATION_POSTS_QUERY, {"host": host, "limit": limit})
        publication = response.get("data", {}).get("publication", {})
        if not publication:
            return f"No publication found for host: {host}"

        posts = publication.get("posts", {}).get("edges", [])
        if not posts:
            return f"No posts found for publication: {host}"

        post_list = []
        for i, p in enumerate(posts, start=1):
            node = p.get("node", {})
            post_list.append(
                f"{i}. {node.get('title', 'Untitled')}\n   {node.get('brief', '').strip()}\n   URL: {node.get('url', 'N/A')}"
            )

        content = f"""
Host: {host}
Title: {publication.get('title', 'N/A')}
Type: {'Team Publication' if publication.get('isTeam') else 'Personal Publication'}
Recent Posts ({len(posts)}):
{chr(10).join(post_list)}
"""
        return format_section("PUBLICATION POSTS", content)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("Starting Hashnode MCP Server...")
    mcp.run(transport="stdio")
