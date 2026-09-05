# agnes-2.5-flash-mcp — Image / Video (agnes-image/video-2.5-flash)

**English** | [中文](#中文说明)

> 2.5-flash-only MCP edition. If you need 2.0/2.1 or `agnes-video-v2.0`,
> use `agnes-mcp` (MSWEIMZ) instead. This package targets only
> `agnes-image-2.5-flash` + `agnes-video-2.5-flash` with Flash-strict validation.
>
> 仅做 2.5-flash 专版。如需 2.0/2.1 或 v2.0，请用社区 `agnes-mcp`。

Any MCP-compatible IDE works:
Cursor / Claude Desktop / VSCode / Cline / Windsurf / Cherry Studio / Opencode.

Models & endpoints (see official docs):
- Image: `POST https://apihub.agnes-ai.com/v1/images/generations`, model `agnes-image-2.5-flash`
- Video: `POST /v1/videos` create + `GET /agnesapi?video_id=&model_name=agnes-video-2.5-flash` poll, model `agnes-video-2.5-flash` (size fixed `720P`)

## Install / 安装

```bash
pip install agnes-2.5-flash-mcp
# or from source:
pip install -e .
```

Requires Python ≥ 3.10.

## API key / 配置 Key

Recommended: put the key in your MCP client config (per-project or global),
do NOT commit real keys. Priority:
tool arg `api_key` > MCP `environment.AGNES_API_KEY` > system env > `.env` file.

```json
{ "mcp": { "agnes-2-5-flash": { "environment": { "AGNES_API_KEY": "YOUR_KEY" } } } }
```

Alternatives:

```bash
setx AGNES_API_KEY "YOUR_KEY"
copy .env.example .env
```

> Proxy note: if `ALL_PROXY=socks5://...` breaks `httpx` (`socksio is not installed`),
> keep `ALL_PROXY/all_proxy` empty in `opencode.json.example`, or use
> `HTTP_PROXY=http://127.0.0.1:10808`, or `pip install "httpx[socks]" "httpcore[socks]"`.

## Connect / 接入各 IDE (stdio)

### Cursor (`.cursor/mcp.json` or global)

```json
{
  "mcpServers": {
    "agnes-2-5-flash": {
      "command": "agnes-2.5-flash-mcp",
      "args": [],
      "env": { "AGNES_API_KEY": "YOUR_KEY" }
    }
  }
}
```

Without install: `command: python`, `args: ["-m", "agnes_2_5_flash_mcp.server"]`,
`cwd: "<repo>/mcps/agnes"`, `env: { "PYTHONPATH": "src" }`.

### Claude Desktop (`claude_desktop_config.json`)

Same as above.

### Opencode (`opencode.json`, see `opencode.json.example`)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "agnes-2-5-flash": {
      "type": "local",
      "command": ["agnes-2.5-flash-mcp"],
      "enabled": true,
      "environment": {
        "AGNES_API_KEY": "YOUR_API_KEY_HERE",
        "ALL_PROXY": "",
        "all_proxy": ""
      }
    }
  }
}
```

Without install: `command: ["python", "-m", "agnes_2_5_flash_mcp.server"]`
with `cwd` pointing at `mcps/agnes`.

### VSCode / Cline / Windsurf / Cherry Studio

Same stdio server: command=`agnes-2.5-flash-mcp`
(or `python -m agnes_2_5_flash_mcp.server`), workdir `mcps/agnes`.

## Tools / 工具一览

> Video default is **async**: `create_video` → `query_video`.
> `generate_video` is compat-only (blocking, may hit client timeouts).

| Tool | Use | Returns |
|---|---|---|
| `generate_image` | 文生图 / 图生图 / 多图合成，**返回 URL** (`save_path` 可选落盘) / text-to-image, image-to-image, compose | `{ url, size, ratio, saved_to }` or `{ b64_json, ... }` |
| `create_video` | **(RECOMMENDED)** 异步创建视频任务 / async create | `{ video_id, task_id, status }` |
| `query_video` | 按 `video_id` 轮询进度/结果 / poll by `video_id` | `{ status, progress, video_url?, error? }` |
| `generate_video` | (compat) 同步阻塞一键生成，仅短视频用 / sync blocking, short clips only | `{ video_url, video_id, ... }` |

Intent routing (no extra layer needed — LLM picks by description):
- 用户说「agnes生图 / 生成图片 / 做张图 / 文生图 / 图生图」→ `generate_image`
- 用户说「生视频 / 生成视频 / 做个视频 / 首尾帧 / 参考图视频」→ `create_video` (+`query_video`)

### Image spec / 图片规格 (default `2K` + `16:9`)

- `size`: `1K` (fast/cheap) / `2K` (default, 16:9 ≈ 2624x1472) / `3K` / `4K` (max)
- `ratio`: `16:9` (default) / `1:1` / `9:16` / `3:4` / `4:3` / `2:3` / `3:2` / `21:9`
- Pass `images` (public URL or Data URI) for image-to-image / compose; omit for pure text-to-image.

### Video constraints / 视频约束 (Flash-only, validated locally)

- `size` fixed `720P`; `seconds` string `"4"`–`"12"` (default `"5"`); aspect `16:9` (default) / `21:9` / `4:3` / `1:1` / `3:4` / `9:16`
- `text` forbids all media; `keyframe` needs first/last frame ≥1; `reference` needs `images`(≤5)/`audios`(≤3) ≥1 with `<Picture N>` / `<Audio N>` in prompt; `videos` unsupported
- `generate_video` default `poll_interval=2s`, `timeout_seconds=600s`; on timeout reuse `video_id` with `query_video`

## Usage examples / 调用示例

- “用 generate_image 生成一张 2K 16:9 的赛博朋克夜景壁纸”
- “把这张图（URL）改成雨夜霓虹风格，保持构图，size 用 2K”
- “用 create_video 生成 5 秒 16:9 的未来城市街道视频，再用 query_video 帮我轮询”
- "Generate a 5s 16:9 future-city video via create_video, then poll with query_video"

## Test / 测试

```bash
python -m pytest tests -q
```

`tests/test_validation.py` is pure-local (no API cost).

---

## 中文说明

本包是 **2.5-flash 专版**：只支持 `agnes-image-2.5-flash` 与
`agnes-video-2.5-flash`，自带 Flash 强校验（`size must be 720P` /
`images≤5` / `audios≤3` / `videos不支持`）。视频默认走**异步**
`create_video` + `query_video`，避免 `generate_video` 阻塞导致
Cursor/Claude 60s 超时。工具描述首行已内置「生图 / 生视频」中文触发词，
Agent 会自动选工具，无需额外路由层。

安装 `pip install agnes-2.5-flash-mcp`，Key 写入 MCP 配置
`environment.AGNES_API_KEY`（见 `opencode.json.example`），重启即生效。
