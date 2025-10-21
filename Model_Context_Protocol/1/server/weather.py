from pydoc import cli
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import asyncio

# initialize FastMCP Server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE='https://api.weather.gov'
USER_AGENT="weather-app/1.0"

async def make_nws_request(url):
    """Make a request to the NWS API with proper error handling."""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/geo+json'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except:
            return None

def format_alert(feature):
    """Format an alert feature into readable string."""
    props = feature['properties']

    return f"""
    Event: {props.get('event', 'Unknown')}
    Area: {props.get('areaDesc', 'Unknown')}
    Severity: {props.get('severity', 'Unknown')}
    Description: {props.get('description', 'No description available')}
    Instructions: {props.get('instruction', 'No specific instructions provided')}
    """

@mcp.tool() # creates a mcp service
async def get_alerts(state):
    """Get weather alerts for a US state

    Args:
        state : Two letter US state code(e.g. NY, CA, etc.)
    """
    url = f"{NWS_API_BASE}/alerts/active?area={state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch weather alerts or no alerts found."

    if not data['features']:
        return "No active alerts found for the specified state."

    alerts = [format_alert(feature) for feature in data['features']]
    return "\n---\n".join(alerts)

if __name__ == "__main__":
    mcp.run(transport="stdio")
