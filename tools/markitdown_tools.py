"""MarkItDown tools for MCP server."""
import os
from typing import Any
from tools.toolhandler import ToolHandler


# Import MarkItDown from src/markitdown
try:
    from markitdown import MarkItDown
except ImportError:
    # Fallback to local path if not installed
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from markitdown import MarkItDown


class ConvertToMarkdownTool(ToolHandler):
    """Tool to convert documents to Markdown using MarkItDown."""

    def __init__(self):
        super().__init__("convert_to_markdown")
        self.enable_plugins = self._check_plugins_enabled()

    def _check_plugins_enabled(self) -> bool:
        """Check if plugins are enabled via environment variable."""
        return os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").strip().lower() in (
            "true",
            "1",
            "yes",
        )

    async def run_tool(self, arguments: dict[str, Any]) -> Any:
        """Convert a resource to Markdown.
        
        Args:
            arguments: Dictionary with 'uri' key containing http:, https:, file:, or data: URI
            
        Returns:
            Dictionary with the converted markdown content
        """
        uri = arguments.get("uri")
        if not uri:
            return {"error": "Missing required parameter: uri"}

        try:
            markitdown = MarkItDown(enable_plugins=self.enable_plugins)
            result = markitdown.convert_uri(uri)
            
            return {
                "markdown": result.markdown,
                "uri": uri,
                "title": getattr(result, 'title', None),
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "uri": uri,
                "success": False
            }

    def get_tool_description(self) -> dict[str, Any]:
        """Get the tool description for MCP registration."""
        return {
            "name": self.name,
            "description": (
                "Convert a resource described by an http:, https:, file: or data: URI to Markdown. "
                "Supports PDF, PowerPoint, Word, Excel, images (with OCR), audio (with transcription), "
                "HTML, CSV, JSON, XML, ZIP files, YouTube URLs, EPubs, and more."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "uri": {
                        "type": "string",
                        "description": (
                            "URI of the resource to convert. Supported schemes: http:, https:, file:, data:. "
                            "Examples: 'https://example.com/document.pdf', 'file:///path/to/doc.docx'"
                        )
                    }
                },
                "required": ["uri"]
            }
        }


class ConvertLocalFileTool(ToolHandler):
    """Tool to convert local files to Markdown."""

    def __init__(self):
        super().__init__("convert_local_file")
        self.enable_plugins = self._check_plugins_enabled()

    def _check_plugins_enabled(self) -> bool:
        """Check if plugins are enabled via environment variable."""
        return os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").strip().lower() in (
            "true",
            "1",
            "yes",
        )

    async def run_tool(self, arguments: dict[str, Any]) -> Any:
        """Convert a local file to Markdown.
        
        Args:
            arguments: Dictionary with 'file_path' key containing path to local file
            
        Returns:
            Dictionary with the converted markdown content
        """
        file_path = arguments.get("file_path")
        if not file_path:
            return {"error": "Missing required parameter: file_path"}

        try:
            if not os.path.exists(file_path):
                return {
                    "error": f"File not found: {file_path}",
                    "file_path": file_path,
                    "success": False
                }

            markitdown = MarkItDown(enable_plugins=self.enable_plugins)
            result = markitdown.convert_local(file_path)
            
            return {
                "markdown": result.markdown,
                "file_path": file_path,
                "title": getattr(result, 'title', None),
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "file_path": file_path,
                "success": False
            }

    def get_tool_description(self) -> dict[str, Any]:
        """Get the tool description for MCP registration."""
        return {
            "name": self.name,
            "description": (
                "Convert a local file to Markdown. Supports PDF, PowerPoint, Word, Excel, images, "
                "audio files, HTML, CSV, JSON, XML, ZIP files, EPubs, and more."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": (
                            "Absolute or relative path to the local file to convert. "
                            "Examples: '/path/to/document.pdf', './data/report.xlsx'"
                        )
                    }
                },
                "required": ["file_path"]
            }
        }


class ConvertStreamTool(ToolHandler):
    """Tool to convert data from a string to Markdown."""

    def __init__(self):
        super().__init__("convert_stream")
        self.enable_plugins = self._check_plugins_enabled()

    def _check_plugins_enabled(self) -> bool:
        """Check if plugins are enabled via environment variable."""
        return os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").strip().lower() in (
            "true",
            "1",
            "yes",
        )

    async def run_tool(self, arguments: dict[str, Any]) -> Any:
        """Convert stream data to Markdown.
        
        Args:
            arguments: Dictionary with 'content' (string data) and optional 'file_extension'
            
        Returns:
            Dictionary with the converted markdown content
        """
        content = arguments.get("content")
        file_extension = arguments.get("file_extension", None)
        
        if not content:
            return {"error": "Missing required parameter: content"}

        try:
            from io import BytesIO
            
            markitdown = MarkItDown(enable_plugins=self.enable_plugins)
            
            # Convert string to bytes if needed
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            stream = BytesIO(content_bytes)
            result = markitdown.convert_stream(stream, file_extension=file_extension)
            
            return {
                "markdown": result.markdown,
                "file_extension": file_extension,
                "title": getattr(result, 'title', None),
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "file_extension": file_extension,
                "success": False
            }

    def get_tool_description(self) -> dict[str, Any]:
        """Get the tool description for MCP registration."""
        return {
            "name": self.name,
            "description": (
                "Convert content from a string or stream to Markdown. "
                "Useful for converting in-memory data or clipboard content."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to convert to Markdown (as string or base64-encoded data)"
                    },
                    "file_extension": {
                        "type": "string",
                        "description": (
                            "Optional file extension hint for content type detection "
                            "(e.g., '.pdf', '.html', '.json'). If omitted, MarkItDown will attempt auto-detection."
                        )
                    }
                },
                "required": ["content"]
            }
        }


def register_all_tools() -> list[ToolHandler]:
    """Register all MarkItDown tools.
    
    Returns:
        List of all tool handlers
    """
    return [
        ConvertToMarkdownTool(),
        ConvertLocalFileTool(),
        ConvertStreamTool(),
    ]
