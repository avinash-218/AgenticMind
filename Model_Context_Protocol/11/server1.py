import click
import logging
import sys
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

@click.command()  # Defines a CLI command
@click.option("--port", default=3000, help="Port number to run the server on")
@click.option("--log-level", default="DEBUG", help="Logging level (e.g., DEBUG, INFO)")

def main(port: int, log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.DEBUG),  # convert string to log level constant
        format="%(asctime)s - %(levelname)s - %(message)s",       # format: timestamp - level - message
    )
    logger = logging.getLogger(__name__)  # Logger instance scoped to this file/module
    logger.info("Launching Stateless Addition/Subtraction MCP Server...")

    mcp = FastMCP(
        "Stateless Arithmetic Server",  # Server name
        host="localhost",               # Bind to localhost only
        port=port,                      # Use port from CLI flag
        stateless_http=True,           # Enforces stateless behavior - Ensures no session memory is kept between requests
    )

    class ArithmeticInput(BaseModel):
        a: float = Field(..., description="First number")
        b: float = Field(..., description="Second number")

    class ArithmeticResult(BaseModel):
        result: float = Field(..., description="The result of the operation")       # Numerical result
        expression: str = Field(..., description="The operation that was performed")  # Explanation as a string

    @mcp.tool(description="Adds two numbers", title="Add Numbers")
    def add_numbers(params: ArithmeticInput) -> ArithmeticResult:
        result = params.a + params.b  # Perform addition
        return ArithmeticResult(      # Return result using structured format
            result=result,
            expression=f"{params.a} + {params.b}"
        )

    @mcp.tool(description="Subtracts number b from a", title="Subtract Numbers")
    def subtract_numbers(params: ArithmeticInput) -> ArithmeticResult:
        result = params.a - params.b  # Perform subtraction
        return ArithmeticResult(      # Return result with explanation
            result=result,
            expression=f"{params.a} - {params.b}"
        )

    try:
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        print("Server exited. Thanks for using MCP!")

if __name__ == "__main__":
    main()