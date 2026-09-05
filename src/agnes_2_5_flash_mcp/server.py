"""Agnes Image/Video 2.5 Flash MCP Server (stdio) - 2.5-flash-only edition.

Tools (default async for video to avoid client timeouts):
  - generate_image  : text-to-image / image-to-image / multi-image compose -> returns URL
  - create_video    : async create (RECOMMENDED), returns video_id
  - query_video     : poll a video task, returns video_url when completed
  - generate_video  : compat sync blocking create+poll, prefer create_video+query_video
"""

from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP

from . import agnes_client
from .config import resolve_api_key, resolve_base_url

mcp = FastMCP("agnes-2-5-flash")

ImageSize = Literal["1K", "2K", "3K", "4K"]
ImageRatio = Literal["1:1", "3:4", "4:3", "16:9", "9:16", "2:3", "3:2", "21:9"]
ImageFormat = Literal["url", "b64_json"]
VideoMode = Literal["text", "keyframe", "reference"]
VideoAspect = Literal["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]


@mcp.tool()
def generate_image(
    prompt: str,
    size: ImageSize = "2K",
    ratio: ImageRatio = "16:9",
    images: list[str] | None = None,
    response_format: ImageFormat = "url",
    save_path: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> dict:
    """Generate or edit an image with agnes-image-2.5-flash. Always returns a URL (or base64).

    中文触发：当用户说「agnes生图 / 生成图片 / 做张图 / 文生图 / 图生图 / 改图 / 多图合成」时调用此工具。
    Trigger: agnes generate image / text-to-image / image-to-image / edit image.

    Presets: size 1K(fast/cheap) / 2K(default, wallpaper 16:9=2624x1472) / 3K / 4K(max quality).
    ratio 16:9 default (wallpaper), 1:1 social, 9:16 vertical, 21:9 ultrawide.
    Pass `images` (public URL or Data URI) for image-to-image / multi-image compose;
    omit it for pure text-to-image. save_path is optional: when given, the result
    is also downloaded locally.

    Examples:
      - 纯文生图：prompt="赛博朋克夜景壁纸", size="2K", ratio="16:9"
      - 带图改图：prompt="改成雨夜霓虹风格，保持构图", images=["https://.../a.png"]
    """
    key = resolve_api_key(api_key)
    base = resolve_base_url(base_url)
    result = agnes_client.generate_image(key, base, prompt, size, ratio, images, response_format)
    saved_to = None
    if save_path and result.get("url"):
        saved_to = agnes_client.download_to_file(result["url"], save_path)
    elif save_path and response_format == "b64_json" and result.get("b64_json"):
        import base64

        from pathlib import Path

        p = Path(save_path).expanduser()
        if str(p.parent) not in ("", "."):
            p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(base64.b64decode(result["b64_json"]))
        saved_to = str(p)
    result["saved_to"] = saved_to
    return result


@mcp.tool()
def create_video(
    prompt: str,
    mode: VideoMode = "text",
    seconds: str = "5",
    aspect_ratio: VideoAspect = "16:9",
    first_frame: str | None = None,
    last_frame: str | None = None,
    images: list[str] | None = None,
    audios: list[str] | None = None,
    seed: int | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> dict:
    """Create an async agnes-video-2.5-flash task (RECOMMENDED). Returns video_id; poll with query_video.

    中文触发：当用户说「生视频 / 生成视频 / 做个视频 / 图生视频 / 首尾帧 / 参考图视频」时优先调用此工具（异步默认，避免IDE超时）。
    Trigger: agnes generate video (async) / text-to-video / image-to-video / keyframe.

    mode text: pure text (no media). keyframe: first_frame and/or last_frame required.
    reference: images (<=5) and/or audios (<=3) required; use <Picture N>/<Audio N> in prompt.
    size is fixed 720P. seconds is a string "4".."12" (default "5").

    Examples:
      - 纯文本生视频：prompt="未来城市街道", mode="text", seconds="5"
      - 首尾帧：prompt="街道由白天变为夜晚", mode="keyframe", first_frame="https://.../a.png"
    """
    key = resolve_api_key(api_key)
    base = resolve_base_url(base_url)
    return agnes_client.create_video(
        key, base, prompt, mode, seconds, "720P",
        aspect_ratio, first_frame, last_frame, images, audios, None, seed,
    )


@mcp.tool()
def query_video(
    video_id: str,
    api_key: str | None = None,
    base_url: str | None = None,
) -> dict:
    """Query an agnes-video-2.5-flash task. Returns status/progress and video_url when completed.

    中文触发：视频创建后，用此工具按 video_id 轮询进度（配合 create_video 使用）。
    """
    key = resolve_api_key(api_key)
    base = resolve_base_url(base_url)
    return agnes_client.query_video(key, base, video_id)


@mcp.tool()
def generate_video(
    prompt: str,
    mode: VideoMode = "text",
    seconds: str = "5",
    aspect_ratio: VideoAspect = "16:9",
    first_frame: str | None = None,
    last_frame: str | None = None,
    images: list[str] | None = None,
    audios: list[str] | None = None,
    seed: int | None = None,
    poll_interval: float = 2.0,
    timeout_seconds: float = 600.0,
    api_key: str | None = None,
    base_url: str | None = None,
) -> dict:
    """Create a video task and block-poll until completed/failed (compat; may hit client timeouts).

    ⚠️ 同步阻塞（易超时）：开源推荐用 create_video + query_video；此工具仅为短视频兼容保留。
    中文触发：仅当用户明确说「一步到位 / 直接等视频结果」时才用，否则用 create_video。
    Trigger (compat): agnes generate video sync; prefer async create_video + query_video.

    Same params as create_video plus poll_interval (default 2s) and
    timeout_seconds (default 600s). On timeout, reuse video_id with query_video.
    """
    key = resolve_api_key(api_key)
    base = resolve_base_url(base_url)
    return agnes_client.generate_video_blocking(
        key, base, prompt, mode, seconds, "720P",
        aspect_ratio, first_frame, last_frame, images, audios, seed,
        poll_interval, timeout_seconds,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
