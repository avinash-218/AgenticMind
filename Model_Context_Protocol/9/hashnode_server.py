import os
import json
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from formatters import (
    format_article_creation,
    format_article_update,
    format_search_results,
    format_post_details,
    format_user_info)
from queries import (
    CREATE_ARTICLE_MUTATION,
    PUBLISH_ARTICLE_MUTATION,
    UPDATE_ARTICLE_MUTATION,
    SEARCH_POSTS_OF_PUBLICATION_QUERY,
    GET_PUBLICATION_ID_QUERY,
    GET_POST_BY_ID_QUERY,
    GET_USER_INFO_QUERY,
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
            HASHNODE_API_URL, json={"query": query, "variables": variables}, headers=headers
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def create_article(title: str, body_markdown: str, tags: str = "", published: bool = True) -> str:
    pub_data = await fetch_from_api(GET_PUBLICATION_ID_QUERY)
    edges = pub_data.get("data", {}).get("me", {}).get("publications", {}).get("edges", [])
    if not edges:
        return "No publication found for your account."
    publication_id = edges[0]["node"]["id"]

    input_vars = {
        "title": title,
        "contentMarkdown": body_markdown,
        "publicationId": publication_id,
        "tags": [{"name": t.strip(), "slug": t.strip().lower().replace(" ", "-")} for t in tags.split(",") if t.strip()],
    }
    draft_data = await fetch_from_api(CREATE_ARTICLE_MUTATION, {"input": input_vars})
    draft_id = draft_data.get("data", {}).get("createDraft", {}).get("draft", {}).get("id")

    if not draft_id:
        return f"Draft creation failed: {json.dumps(draft_data, indent=2)}"

    if not published:
        return f"Draft saved with ID {draft_id}"

    pub_result = await fetch_from_api(PUBLISH_ARTICLE_MUTATION, {"draftId": draft_id})
    return format_article_creation(pub_result)

@mcp.tool()
async def update_article(article_id: str, title: str = None, body_markdown: str = None, tags: str = None) -> str:
    input_vars = {"id": article_id}
    if title:
        input_vars["title"] = title
    if body_markdown:
        input_vars["contentMarkdown"] = body_markdown
    if tags:
        input_vars["tags"] = [
            {"name": t.strip(), "slug": t.strip().lower().replace(" ", "-")}
            for t in tags.split(",") if t.strip()
        ]
    data = await fetch_from_api(UPDATE_ARTICLE_MUTATION, {"input": input_vars})
    return format_article_update(data)

@mcp.tool()
async def search_articles(query: str, limit: int = 5) -> str:
    pub_data = await fetch_from_api(GET_PUBLICATION_ID_QUERY)
    edges = pub_data.get("data", {}).get("me", {}).get("publications", {}).get("edges", [])
    if not edges:
        return "No publication found."
    publication_id = edges[0]["node"]["id"]

    variables = {"first": limit, "filter": {"publicationId": publication_id, "query": query}}
    data = await fetch_from_api(SEARCH_POSTS_OF_PUBLICATION_QUERY, variables)
    return format_search_results(data)

@mcp.tool()
async def get_article_details(article_id: str) -> str:
    data = await fetch_from_api(GET_POST_BY_ID_QUERY, {"id": article_id})
    return format_post_details(data)

@mcp.tool()
async def get_user_info(username: str) -> str:
    data = await fetch_from_api(GET_USER_INFO_QUERY, {"username": username})
    return format_user_info(data)

if __name__ == "__main__":
    print("Starting Hashnode MCP Server...")
    mcp.run(transport="stdio")
