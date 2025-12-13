import click
import logging
import sys
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

@click.command()  # Defines a CLI command
@click.option("--port", default=3001, help="Port number to run the server on")
@click.option("--log-level", default="DEBUG", help="Logging level (e.g., DEBUG, INFO)")

def main(port: int, log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.DEBUG),  # convert string to log level constant
        format="%(asctime)s - %(levelname)s - %(message)s",       # format: timestamp - level - message
    )
    logger = logging.getLogger(__name__)  # Logger instance scoped to this file/module
    logger.info("Starting Stateless Multiplication/Division MCP Server...")

    mcp = FastMCP(
        "Stateless Math Server",   # Server name
        host="localhost",          # Bind to localhost only
        port=port,                 # Use port from CLI flag
        stateless_http=True,      # Enforces stateless behavior
    )

    class ArithmeticInput(BaseModel):
        a: float = Field(..., description="First number")
        b: float = Field(..., description="Second number")

    class ArithmeticResult(BaseModel):
        result: float = Field(..., description="Calculation result")             # Numerical result
        expression: str = Field(..., description="Math expression performed")    # Explanation as a string

    @mcp.tool(description="Multiply two numbers", title="Multiply Numbers")
    def multiply_numbers(params: ArithmeticInput) -> ArithmeticResult:
        result = params.a * params.b  # Perform multiplication
        return ArithmeticResult(      # Return result with expression
            result=result,
            expression=f"{params.a} * {params.b}"
        )

    @mcp.tool(description="Divide a by b", title="Divide Numbers")
    def divide_numbers(params: ArithmeticInput) -> ArithmeticResult:
        if params.b == 0:
            raise ValueError("Division by zero is not allowed.")  # Handle division by 0 error
        result = params.a / params.b  # Perform division
        return ArithmeticResult(      # Return result with expression
            result=result,
            expression=f"{params.a} / {params.b}"
        )

    try:
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        print("Server exited.")

if __name__ == "__main__":
    main()