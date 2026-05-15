# MarkItDown MCP Server - Quick Start Guide

Get started with the MarkItDown MCP Server in minutes!

## Quick Install

```bash
# Clone or navigate to the markitdown-tool directory
cd markitdown-tool

# Install with all dependencies
pip install -e ".[all]"
```

## Run the Server

### Option 1: Streamable HTTP (Recommended)

```bash
markitdown-mcp --mode streamable-http --port 8000
```

Server will be available at:
- Health: http://localhost:8000/health
- Info: http://localhost:8000/
- MCP Endpoint: http://localhost:8000/mcp

### Option 2: Server-Sent Events (SSE)

```bash
markitdown-mcp --mode sse --port 8000
```

SSE endpoint: http://localhost:8000/sse

### Option 3: Standard I/O (stdio)

```bash
markitdown-mcp --mode stdio
```

## Quick Test

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok"}
```

### Server Info

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "ok",
  "transport": "streamable-http",
  "server": "markitdown-mcp",
  "tools": 3
}
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `convert_to_markdown` | Convert from URI | `uri` (string) - http:, https:, file:, data: URI |
| `convert_local_file` | Convert local file | `file_path` (string) - Path to local file |
| `convert_stream` | Convert from stream | `content` (string), `file_extension` (optional) |

## MCP Client Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "markitdown": {
      "type": "streamable-http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Generic MCP Client (stdio)

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "markitdown-mcp",
      "args": ["--mode", "stdio"]
    }
  }
}
```

## Docker Quick Start

### Build

```bash
docker build -t markitdown-mcp .
```

### Run

```bash
# Default port 8000
docker run -p 8000:8000 markitdown-mcp

# Custom port
docker run -e PORT=3001 -p 3001:3001 markitdown-mcp

# With local file access
docker run -v /path/to/docs:/workdir -p 8000:8000 markitdown-mcp
```

## Example Usage

### Convert a PDF from URL

```python
# Via MCP tool
{
  "tool": "convert_to_markdown",
  "arguments": {
    "uri": "https://example.com/document.pdf"
  }
}
```

### Convert Local Word Document

```python
{
  "tool": "convert_local_file",
  "arguments": {
    "file_path": "/path/to/report.docx"
  }
}
```

### Convert HTML Content

```python
{
  "tool": "convert_stream",
  "arguments": {
    "content": "<html><body><h1>Hello</h1></body></html>",
    "file_extension": ".html"
  }
}
```

## Supported File Formats

✅ PDF  
✅ PowerPoint (.pptx)  
✅ Word (.docx)  
✅ Excel (.xlsx, .xls)  
✅ Images (PNG, JPG, GIF) - with OCR  
✅ Audio (MP3, WAV) - with transcription  
✅ HTML  
✅ CSV, JSON, XML  
✅ ZIP files  
✅ EPub  
✅ YouTube URLs  

## Environment Variables

- `MARKITDOWN_ENABLE_PLUGINS` - Enable plugins (true/false, default: false)
- `PORT` - Server port (Docker only, default: 8000)

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'markitdown'"

**Solution:** Install with optional dependencies
```bash
pip install -e ".[all]"
```

### Issue: Server won't start

**Solution:** Check if port is already in use
```bash
# Try a different port
markitdown-mcp --mode streamable-http --port 3001
```

### Issue: "Tool registration failed"

**Solution:** Ensure all dependencies are installed
```bash
pip install -e ".[all]"
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [mcp.example.json](mcp.example.json) for configuration examples
- Run tests: `pytest tests/test_mcp_server.py -v`
- Explore the [Microsoft MarkItDown documentation](https://github.com/microsoft/markitdown)

## Getting Help

- GitHub Issues: https://github.com/microsoft/markitdown/issues
- MCP Documentation: https://modelcontextprotocol.io/

---

**Status:** ✅ Production-ready  
**Version:** 0.1.0  
**Transport Modes:** Streamable HTTP, SSE, stdio  
**Tools:** 3/3 operational
