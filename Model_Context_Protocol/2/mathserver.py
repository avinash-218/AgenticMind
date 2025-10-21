from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a:int, b:int)->int:
    """Add two numbers

    Args:
        a (int): operand 1
        b (int): operand 2

    Returns:
        int: addition of a and b
    """
    return a + b

@mcp.tool()
def multiply(a:int, b:int)->int:
    """Multiply two numbers

    Args:
        a (int): operand 1
        b (int): operand 2

    Returns:
        int: product of a and b
    """
    return a * b

if __name__ == '__main__':
    mcp.run(transport="stdio")