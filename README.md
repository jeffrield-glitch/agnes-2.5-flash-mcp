# Agnes 2.5 Flash MCP Server 🚀

<div align="center">
  <p>一个 Model Context Protocol (MCP) 服务器，将 Agnes AI 最新发布的 2.5-flash 图像与视频生成模型无缝集成到您最爱的 AI IDE 中。</p>
  <p>
    <a href="https://pypi.org/project/agnes-2.5-flash-mcp/"><img src="https://img.shields.io/pypi/v/agnes-2.5-flash-mcp.svg" alt="PyPI version"></a>
    <a href="https://www.python.org/downloads/release/python-3100/"><img src="https://img.shields.io/badge/Python-%E2%89%A53.10-blue.svg" alt="Python 3.10+"></a>
    <a href="https://github.com/JasonOracle/agnes-2.5-flash-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
    <img src="https://img.shields.io/badge/Protocol-MCP_stdio-purple.svg" alt="MCP Protocol">
  </p>
  <p><strong>中文说明</strong> | <a href="README_en.md">English</a></p>
</div>

---

## 🌟 工程亮点 (致面试官)

虽然 Agnes 提供了非常优秀的免费图像和视频生成模型（`agnes-image-2.5-flash` / `agnes-video-2.5-flash`），但开发者在 IDE 和网页之间频繁切换上下文非常打断心流。最初，这只是为了在 Opencode 中免去切网页烦恼而写的自用工具，现已正式发布至 PyPI，任何开发者均可直接安装，将 AI 生成能力一键接入自己的 Agentic IDE（如 Opencode、Claude Desktop、Windsurf 等）。

**核心技术决策与实现：**
1. **彻底解决客户端超时痛点 (Robust Async Workflow)**：由于视频生成通常耗时数分钟，极易导致 Opencode/Claude 等 MCP 客户端的标准请求超时。为此，我设计了异步的任务轮询系统 (`create_video` → `query_video`)，允许 Agent 非阻塞地检查进度，保证了长耗时任务的稳定性。
2. **前置强校验与防御性编程 (Strict Parameter Validation)**：在本地层面对请求参数进行 Flash 强校验（例如：强制 `720P` 分辨率，校验图文音附件数量等）。这能将无效请求在发起网络调用前瞬间拦截，既降低了网络延迟，又避免了无意义的 API 额度消耗。
3. **自然语言无缝路由 (Intelligent Intent Routing)**：在工具描述（Description）设计中，深度优化了中英双语的触发词（如“生一张图”、“draw a cyberpunk city”）。LLM 能够根据上下文自动推断用户意图，精准路由到正确的工具函数，完全免去了繁杂的 Prompt 设定。
4. **标准化与兼容性 (Plug-and-Play Design)**：完全遵循官方的 MCP `stdio` 传输层规范，实现即插即用，兼容市面上绝大多数支持 MCP 的智能客户端。

---

## 🚀 支持的模型与端点

> **注意：** 本项目为 2.5-flash 专版。如果您需要 2.0/2.1 或 `agnes-video-v2.0` 的支持，请使用社区版的 `agnes-mcp`。

- **图像生成**: `agnes-image-2.5-flash` 模型（接口：`POST /v1/images/generations`）
- **视频生成**: `agnes-video-2.5-flash` 模型（接口：`POST /v1/videos` & `GET /agnesapi`，尺寸固定为 `720P`）

## 📦 安装说明

```bash
# 通过 pip 安装
pip install agnes-2.5-flash-mcp

# 或从源码安装
git clone https://github.com/JasonOracle/agnes-2.5-flash-mcp.git
cd agnes-2.5-flash-mcp
pip install -e .
```

*要求 Python ≥ 3.10.*

## 🔑 配置说明 (API Key)

API Key 解析优先级：
`工具调用参数` > `MCP 环境变量 AGNES_API_KEY` > `系统环境变量` > `.env` 文件。

**推荐方式：** 直接在您的 MCP 客户端配置中设置，避免将 Key 提交到代码库。

```json
{
  "mcpServers": {
    "agnes-2.5-flash-mcp": {
      "command": "agnes-2.5-flash-mcp",
      "args": [],
      "env": {
        "AGNES_API_KEY": "您的_API_KEY"
      }
    }
  }
}
```

> **代理配置：** 如果 `ALL_PROXY=socks5://...` 导致 `httpx` 报错，请将 `ALL_PROXY` 留空，或使用 HTTP 代理 `HTTP_PROXY=http://127.0.0.1:10808`。或者安装 socks 支持：`pip install "httpx[socks]"`。

## 🔌 IDE 接入指引

### Cursor / Claude Desktop
将以下内容添加到您的 `.cursor/mcp.json` 或 `claude_desktop_config.json` 中：

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
*（如果不使用 pip 安装：请使用 `command: "python"`, `args: ["-m", "agnes_2_5_flash_mcp.server"]`, 并指定 `cwd` 目录）*

### Opencode
请参考项目中的 `opencode.json.example` 文件。

## 🛠️ 工具参考 (Tools)

| 工具名称 | 功能描述 | 返回格式 |
|---|---|---|
| `generate_image` | 文生图、图生图、图像合成。<br>*(返回 URL，可选保存至本地)* | `{ url, size, ratio, saved_to }` 或 `{ b64_json, ... }` |
| `create_video` | **(推荐)** 异步创建视频生成任务。 | `{ video_id, task_id, status }` |
| `query_video` | 根据 `video_id` 轮询视频进度及结果。 | `{ status, progress, video_url?, error? }` |
| `generate_video` | *(兼容)* 同步阻塞式生成（仅限短视频，可能触发超时）。 | `{ video_url, video_id, ... }` |

### 🖼️ 图像约束 (默认：`2K` + `16:9`)
- **分辨率 (Size)**: `1K` (快速) / `2K` (默认, ≈ 2624x1472) / `3K` / `4K` (最大)
- **比例 (Ratio)**: `16:9` / `1:1` / `9:16` / `3:4` / `4:3` / `2:3` / `3:2` / `21:9`
- **能力**: 传入 `images` 参数（URL 或 Data URI）可进行图生图/图像合成，省略则为纯文生图。

### 🎥 视频约束 (本地强校验)
- **尺寸 (Size)**: 固定为 `720P`。
- **时长 (Duration)**: `"4"` 至 `"12"` 秒（默认 `"5"`）。
- **比例 (Ratio)**: `16:9` (默认) / `21:9` / `4:3` / `1:1` / `3:4` / `9:16`。
- **校验**: 采用严格校验逻辑（如：文本模式禁止包含媒体附件，关键帧模式首尾帧必须 ≥ 1 等）。

## 💬 使用示例 (直接对 Agent 说)

- *"用 `generate_image` 生成一张 2K 16:9 的赛博朋克城市夜景壁纸。"*
- *"把这张图 (URL) 改成雨夜霓虹风格，保持构图，尺寸用 2K。"*
- *"用 `create_video` 生成 5 秒 16:9 的未来城市街道视频，然后用 `query_video` 帮我轮询结果。"*

## 🧪 本地测试

测试套件 (`tests/test_validation.py`) 是纯本地校验测试，不会产生任何 API 调用计费。
```bash
python -m pytest tests -q
```
