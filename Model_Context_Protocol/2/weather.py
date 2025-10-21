from mcp.server.fastmcp import FastMCP
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("weather")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Hardcoded coordinates
LOCATIONS = {
    "madurai": {"lat": 9.9333, "lon": 78.1167},
    "chennai": {"lat": 13.0878, "lon": 80.2785},
    "bangalore": {"lat": 12.9762, "lon": 77.6033}
}

@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Fetch current weather for a given location using OpenWeatherMap Current Weather API.
    """
    loc = location.lower()
    if loc not in LOCATIONS:
        return f"Location {location} not found."

    lat = LOCATIONS[loc]["lat"]
    lon = LOCATIONS[loc]["lon"]

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return f"Failed to fetch weather for {location} (HTTP {response.status})"
            data = await response.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"The current weather in {location.title()} is {desc} with a temperature of {temp}°C."

if __name__ == '__main__':
    mcp.run(transport="streamable-http")
