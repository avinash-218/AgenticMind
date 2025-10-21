from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("flight_assistant")

# Prompt: Greeting template
@mcp.prompt()
def greeting_prompt(user_name: str):
    return f"Hello {user_name}! I can help you check flight status and airport info."

# Tool: Check flight status
@mcp.tool()
async def get_flight_status(flight_number: str):
    # Simulated flight status data
    flights = {
        "AI101": "On Time",
        "BA256": "Delayed",
        "DL404": "Cancelled"
    }
    return flights.get(flight_number.upper(), "Flight not found")

@mcp.prompt()
def combined_response(user_message: str):
    """
    Task: 
    - Identify if the user is greeting → call greeting_prompt
    - Identify if the user mentions a flight → call get_flight_status
    - Combine all outputs into a single reply
    """
    return user_message

# Resource: Get airport info
@mcp.resource("airport://{code}")
def airport_info(code: str) -> str:
    airports = {
        "JFK": "John F. Kennedy International Airport, New York",
        "LHR": "London Heathrow Airport",
        "DEL": "Indira Gandhi International Airport, Delhi"
    }
    return airports.get(code.upper(), "Unknown airport")

# Combine into full response
@mcp.tool()
async def flight_report(user_name: str, flight_number: str, airport_code: str):
    greeting = greeting_prompt(user_name)
    status = await get_flight_status(flight_number)
    airport = airport_info(f"{airport_code}")
    
    report = f"""
{greeting}
Flight {flight_number.upper()} is {status}.
Departure: {airport}.
"""
    return report.strip()

if __name__ == "__main__":
    print("Flight Assistant MCP server running...")
    mcp.run(transport="stdio")
