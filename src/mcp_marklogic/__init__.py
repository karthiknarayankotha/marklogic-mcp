from . import server
import asyncio
import argparse
import os


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description='MarkLogic MCP Server')
    parser.add_argument('--host', 
                       default=os.environ.get("MARKLOGIC_HOST", "localhost"),
                       help='MarkLogic host')
    parser.add_argument('--port', 
                       type=int,
                       default=int(os.environ.get("MARKLOGIC_PORT", "8000")),
                       help='MarkLogic port')
    parser.add_argument('--username', 
                       default=os.environ.get("MARKLOGIC_USERNAME", "python-user"),
                       help='MarkLogic username')
    parser.add_argument('--password', 
                       default=os.environ.get("MARKLOGIC_PASSWORD", "pyth0n"),
                       help='MarkLogic password')
    
    args = parser.parse_args()
    asyncio.run(server.main(args.host, args.port, args.username, args.password))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
