# Agnes 2.5 Flash MCP Server 🚀

<div align="center">
  <p>A Model Context Protocol (MCP) server that seamlessly integrates Agnes AI's latest 2.5-flash Image & Video generation models into your favorite AI IDEs.</p>
  <p>
    <a href="https://pypi.org/project/agnes-2.5-flash-mcp/"><img src="https://img.shields.io/pypi/v/agnes-2.5-flash-mcp.svg" alt="PyPI version"></a>
    <a href="https://www.python.org/downloads/release/python-3100/"><img src="https://img.shields.io/badge/Python-%E2%89%A53.10-blue.svg" alt="Python 3.10+"></a>
    <a href="https://github.com/JasonOracle/agnes-2.5-flash-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
    <img src="https://img.shields.io/badge/Protocol-MCP_stdio-purple.svg" alt="MCP Protocol">
  </p>
  <p><strong>English</strong> | <a href="README.md">中文说明</a></p>
</div>

---

## 🌟 Engineering Highlights (Why this exists)

While Agnes provides excellent free image and video generation models (`agnes-image-2.5-flash` / `agnes-video-2.5-flash`), manually switching contexts between IDEs and web pages disrupts the developer workflow. Originally built as a personal tool to avoid context switching in Opencode, this MCP server is now officially published on PyPI. Any developer can install it out-of-the-box, bringing AI generation capabilities directly into their agentic IDEs like Opencode, Claude Desktop, and Windsurf.

**Key Technical Decisions:**
- **Robust Async Workflow**: Video generation typically takes several minutes, which easily hits the standard timeout of MCP clients like Opencode or Claude Desktop. To solve this, I implemented an asynchronous task polling system (`create_video` → `query_video`), allowing the agent to check progress without blocking or timing out.
- **Strict Parameter Validation**: Implemented local Flash-strict constraints validation (e.g., enforcing `720P` size, validating image/audio attachment counts). This catches invalid requests instantly *before* hitting the API, reducing latency and saving API costs.
- **Intelligent Intent Routing**: Designed tool descriptions using optimized bilingual trigger words. The LLM can automatically infer user intent (e.g., "draw a cyberpunk city", "生一张图") and route to the correct tool without explicit prompt engineering.
- **Plug-and-Play Design**: Fully compliant with the official MCP `stdio` transport layer, ensuring universal compatibility across any MCP-enabled client.

---

## 🚀 Supported Models & Endpoints

> **Note:** This is a dedicated 2.5-flash MCP edition. If you need 2.0/2.1 or `agnes-video-v2.0` support, use the community `agnes-mcp` package instead.

- **Image Generation**: Model `agnes-image-2.5-flash` via `POST /v1/images/generations`
- **Video Generation**: Model `agnes-video-2.5-flash` via `POST /v1/videos` & `GET /agnesapi` (Size fixed at `720P`)

## 📦 Installation

```bash
# Install via pip
pip install agnes-2.5-flash-mcp

# Or install from source
git clone https://github.com/JasonOracle/agnes-2.5-flash-mcp.git
cd agnes-2.5-flash-mcp
pip install -e .
```

*Requires Python ≥ 3.10.*

## 🔑 Configuration (API Key)

Priority of API Key resolution:
`Tool Argument` > `MCP environment.AGNES_API_KEY` > `System Env` > `.env` file.

**Recommended approach:** Configure it directly in your MCP client settings to avoid committing real keys.

```json
{
  "mcpServers": {
    "agnes-2.5-flash-mcp": {
      "command": "agnes-2.5-flash-mcp",
      "args": [],
      "env": {
        "AGNES_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

> **Proxy configuration:** If `ALL_PROXY=socks5://...` breaks `httpx`, leave `ALL_PROXY` empty or use HTTP proxy `HTTP_PROXY=http://127.0.0.1:10808`. Alternatively, install socks support: `pip install "httpx[socks]"`.

## 🔌 IDE Integration

### Cursor / Claude Desktop
Add the following to your `.cursor/mcp.json` or `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agnes-2.5-flash-mcp": {
      "command": "agnes-2.5-flash-mcp",
      "env": { "AGNES_API_KEY": "YOUR_KEY" }
    }
  }
}
```
*(If running without installation: use `command: "python"`, `args: ["-m", "agnes_2_5_flash_mcp.server"]`, and specify `cwd`)*

### Opencode
See `opencode.json.example` for details.

## 🛠️ Tools Reference

| Tool | Description | Return Format |
|---|---|---|
| `generate_image` | Text-to-image, Image-to-image, Compose. <br>*(Returns URL, can optionally save locally)* | `{ url, size, ratio, saved_to }` or `{ b64_json, ... }` |
| `create_video` | **(RECOMMENDED)** Async video creation task. | `{ video_id, task_id, status }` |
| `query_video` | Poll video progress/result by `video_id`. | `{ status, progress, video_url?, error? }` |
| `generate_video` | *(Compat)* Sync blocking generation (Short clips only, may timeout). | `{ video_url, video_id, ... }` |

### 🖼️ Image Constraints (Default: `2K` + `16:9`)
- **Size**: `1K` (fast) / `2K` (default, ≈ 2624x1472) / `3K` / `4K` (max)
- **Ratio**: `16:9` / `1:1` / `9:16` / `3:4` / `4:3` / `2:3` / `3:2` / `21:9`
- **Capabilities**: Pass `images` (URL or Data URI) for image-to-image/compose, or omit for pure text-to-image.

### 🎥 Video Constraints (Validated Locally)
- **Size**: Fixed at `720P`.
- **Duration**: `"4"` to `"12"` seconds (default `"5"`).
- **Ratio**: `16:9` (default) / `21:9` / `4:3` / `1:1` / `3:4` / `9:16`.
- **Validation**: Strict checks applied (e.g., Text mode forbids media, Keyframe mode requires first/last frames ≥ 1).

## 💬 Usage Examples (Talk to your Agent)

- *"Use `generate_image` to create a 2K 16:9 cyberpunk city night wallpaper."*
- *"Modify this image (URL) to a neon rainy night style, keep the composition, size 2K."*
- *"Create a 5s 16:9 futuristic city video using `create_video`, then poll for the result with `query_video`."*

## 🧪 Testing

The test suite (`tests/test_validation.py`) is pure-local and incurs no API costs.
```bash
python -m pytest tests -q
```
