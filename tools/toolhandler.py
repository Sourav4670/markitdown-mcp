"""Base class for all tool handlers."""
from abc import ABC, abstractmethod
from typing import Any


class ToolHandler(ABC):
    """Abstract base class for tool handlers."""

    def __init__(self, name: str):
        """Initialize the tool handler.
        
        Args:
            name: The name of the tool
        """
        self.name = name

    @abstractmethod
    async def run_tool(self, arguments: dict[str, Any]) -> Any:
        """Execute the tool with the given arguments.
        
        Args:
            arguments: Dictionary of arguments for the tool
            
        Returns:
            The result of the tool execution
        """
        pass

    @abstractmethod
    def get_tool_description(self) -> dict[str, Any]:
        """Get the tool description for MCP registration.
        
        Returns:
            Dictionary containing tool name, description, and input schema
        """
        pass
