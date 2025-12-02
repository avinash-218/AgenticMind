import json

def format_article_creation(data):
    post = data.get("data", {}).get("publishPost", {}).get("post", {})
    if not post:
        return json.dumps(data, indent=2)
    return f"Published: {post['title']}\nURL: {post['url']}"

def format_article_update(data):
    post = data.get("data", {}).get("updatePost", {}).get("post", {})
    if not post:
        return json.dumps(data, indent=2)
    return f"Updated: {post['title']}\nURL: {post['url']}"

def format_search_results(data):
    edges = data.get("data", {}).get("searchPostsOfPublication", {}).get("edges", [])
    if not edges:
        return "No results found."
    result = "# Search Results\n\n"
    for edge in edges:
        node = edge["node"]
        result += f"**{node['title']}** — {node['author']['name']}\n"
        result += f"Published: {node.get('publishedAt', 'N/A')}\n"
        result += f"{node.get('brief', '')[:200]}...\n\n"
    return result

def format_post_details(data):
    post = data.get("data", {}).get("post", {})
    if not post:
        return "Post not found."
    return f"# {post['title']}\n\n{post['contentMarkdown'][:1000]}..."

def format_user_info(data):
    user = data.get("data", {}).get("user", {})
    if not user:
        return "User not found."
    return f"{user['name']} (@{user['username']})\n{user.get('tagline', '')}\nBlog: {user.get('publicationDomain', '')}"

def format_top_articles(data):
    edges = data.get("data", {}).get("topStoriesFeed", {}).get("edges", [])
    result = "# Top Articles\n\n"
    for edge in edges:
        post = edge["node"]
        result += f"- [{post['title']}]({post['url']})\n"
    return result

def format_articles_by_tag(data):
    edges = data.get("data", {}).get("tag", {}).get("posts", {}).get("edges", [])
    result = "# Articles by Tag\n\n"
    for edge in edges:
        post = edge["node"]
        result += f"- [{post['title']}]({post['url']})\n"
    return result
