import sys
import click

from server1 import main as server1_main
from server2 import main as server2_main

@click.command()
@click.option(
    "--server",
    type=click.Choice(["server1", "server2"]),
    required=True,
    help="Select which server to run (server1 or server2)",
)
@click.option(
    "--log-level",
    default="DEBUG",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Set logging level for the server (default: DEBUG)",
)

def main(server: str, log_level: str):
    """
    Entry point for selecting and starting one MCP server.
    Passes selected log level to the appropriate server.
    """
    # Convert server and log-level options into a format Click expects
    args = ["--log-level", log_level]

    if server == "server1":
        sys.exit(server1_main(args=args, standalone_mode=False))
    elif server == "server2":
        sys.exit(server2_main(args=args, standalone_mode=False))
    else:
        print("Invalid server option. Use --server with either 'server1' or 'server2'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
