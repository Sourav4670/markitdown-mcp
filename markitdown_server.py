"""MarkItDown MCP Server - Document to Markdown conversion service.

This server provides tools for converting various document formats to Markdown
using the MarkItDown library. It supports multiple transport modes:
- Streamable HTTP
- Server-Sent Events (SSE)
- Standard I/O (stdio)
"""

import asyncio
import contextlib
import argparse
import sys
from collections.abc import AsyncIterator
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import Tool

from tools.markitdown_tools import register_all_tools


# Initialize MCP Server
server = Server("markitdown-mcp")

# Storage for registered tools
TOOL_HANDLERS = {}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name=handler.name,
            description=handler.get_tool_description()["description"],
            inputSchema=handler.get_tool_description()["inputSchema"],
        )
        for handler in TOOL_HANDLERS.values()
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[Any]:
    """Handle tool execution."""
    if name not in TOOL_HANDLERS:
        return [{"error": f"Unknown tool: {name}"}]

    handler = TOOL_HANDLERS[name]
    result = await handler.run_tool(arguments if arguments else {})

    # Ensure result is always a list of text content items
    if isinstance(result, dict):
        return [{"type": "text", "text": str(result)}]
    elif isinstance(result, str):
        return [{"type": "text", "text": result}]
    else:
        return [{"type": "text", "text": str(result)}]


def register_all_tools_with_server():
    """Register all MarkItDown tool handlers."""
    global TOOL_HANDLERS
    handlers = register_all_tools()
    TOOL_HANDLERS = {handler.name: handler for handler in handlers}
    print(f"✓ Total tools registered: {len(TOOL_HANDLERS)}")


# Streamable HTTP setup
def create_streamable_http_app() -> Starlette:
    """Create Starlette app for Streamable HTTP transport."""

    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=None,
        json_response=False,
        stateless=False,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        """Handle Streamable HTTP requests."""
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Lifespan context manager for session manager."""
        async with session_manager.run():
            print("✓ Streamable HTTP session manager started")
            try:
                yield
            finally:
                print("✓ Application shutting down...")

    return Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
            Route("/health", endpoint=lambda request: JSONResponse({"status": "ok"})),
            Route(
                "/",
                endpoint=lambda request: JSONResponse(
                    {
                        "status": "ok",
                        "transport": "streamable-http",
                        "server": "markitdown-mcp",
                        "tools": len(TOOL_HANDLERS),
                    }
                ),
            ),
        ],
        lifespan=lifespan,
        middleware=[
            (
                CORSMiddleware,
                {
                    "allow_origins": ["*"],
                    "allow_methods": ["*"],
                    "allow_headers": ["*"],
                },
            )
        ],
    )


# SSE setup
def create_sse_starlette_app() -> Starlette:
    """Create Starlette app for SSE transport."""

    sse = SseServerTransport("/messages")

    async def handle_sse(request: Request) -> None:
        """Handle SSE connections."""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Lifespan context manager."""
        print("✓ SSE transport started")
        try:
            yield
        finally:
            print("✓ Application shutting down...")

    return Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=sse.handle_post_message),
            Route("/health", endpoint=lambda request: JSONResponse({"status": "ok"})),
            Route(
                "/",
                endpoint=lambda request: JSONResponse(
                    {
                        "status": "ok",
                        "transport": "sse",
                        "server": "markitdown-mcp",
                        "tools": len(TOOL_HANDLERS),
                    }
                ),
            ),
        ],
        lifespan=lifespan,
        middleware=[
            (
                CORSMiddleware,
                {
                    "allow_origins": ["*"],
                    "allow_methods": ["*"],
                    "allow_headers": ["*"],
                },
            )
        ],
    )


async def run_stdio():
    """Run the server with stdio transport."""
    print("✓ Starting markitdown-mcp server with stdio transport", file=sys.stderr)
    print(f"✓ Total tools registered: {len(TOOL_HANDLERS)}", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def cli_main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MarkItDown MCP Server - Document to Markdown conversion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with stdio (default)
  markitdown-mcp --mode stdio

  # Start with Streamable HTTP
  markitdown-mcp --mode streamable-http --port 8000

  # Start with SSE
  markitdown-mcp --mode sse --port 8000

Environment Variables:
  MARKITDOWN_ENABLE_PLUGINS   Enable MarkItDown plugins (true/false, default: false)
        """,
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for HTTP/SSE modes (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address for HTTP/SSE modes (default: 127.0.0.1)",
    )

    args = parser.parse_args()

    # Register all tools before starting
    register_all_tools_with_server()

    if args.mode == "stdio":
        asyncio.run(run_stdio())
    elif args.mode == "streamable-http":
        print(f"✓ Starting markitdown-mcp server with Streamable HTTP transport")
        print(f"✓ Listening on http://{args.host}:{args.port}")
        print(f"✓ MCP endpoint: http://{args.host}:{args.port}/mcp")
        app = create_streamable_http_app()
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.mode == "sse":
        print(f"✓ Starting markitdown-mcp server with SSE transport")
        print(f"✓ Listening on http://{args.host}:{args.port}")
        print(f"✓ SSE endpoint: http://{args.host}:{args.port}/sse")
        app = create_sse_starlette_app()
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    cli_main()
