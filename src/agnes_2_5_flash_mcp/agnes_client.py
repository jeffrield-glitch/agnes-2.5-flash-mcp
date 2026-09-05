"""Thin httpx wrapper over the Agnes Image/Video Flash REST APIs."""

from __future__ import annotations

import time

import httpx

from .config import query_base_url
from .validation import VIDEO_MODEL, validate_image, validate_video

IMAGE_MODEL = "agnes-image-2.5-flash"
VIDEO_QUERY_MODEL = VIDEO_MODEL


def _headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def generate_image(
    api_key: str,
    base_url: str,
    prompt: str,
    size: str = "2K",
    ratio: str = "16:9",
    images: list[str] | None = None,
    response_format: str = "url",
    timeout: float = 180.0,
) -> dict:
    """Call POST /v1/images/generations. Returns the first element of `data` + meta."""
    validate_image(size, ratio, images, response_format)
    if not prompt or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")

    body: dict = {"model": IMAGE_MODEL, "prompt": prompt, "size": size, "ratio": ratio}
    extra_body: dict = {}
    if images:
        # Doc坑: 图生图/多图合成走 extra_body.image, 不要 tags:["img2img"]
        extra_body["image"] = images
    if images and response_format == "b64_json":
        extra_body["response_format"] = "b64_json"
    elif response_format == "url":
        # Doc坑: response_format 必须放 extra_body, 不能放顶层
        extra_body["response_format"] = "url"
    elif response_format == "b64_json" and not images:
        body["return_base64"] = True
    if extra_body:
        body["extra_body"] = extra_body

    url = f"{base_url}/images/generations"
    try:
        resp = httpx.post(url, headers=_headers(api_key), json=body, timeout=timeout)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Image API HTTP {e.response.status_code}: {e.response.text[:1000]}") from e
    except httpx.TimeoutException as e:
        raise RuntimeError(f"Image API timeout after {timeout}s (try a smaller size)") from e
    data = resp.json()
    items = data.get("data") or []
    if not items:
        raise RuntimeError(f"Image API returned no data: {str(data)[:1000]}")
    first = items[0]
    return {
        "url": first.get("url"),
        "b64_json": first.get("b64_json"),
        "revised_prompt": first.get("revised_prompt"),
        "created": data.get("created"),
        "size": size,
        "ratio": ratio,
        "response_format": response_format,
    }


def create_video(
    api_key: str,
    base_url: str,
    prompt: str,
    mode: str,
    seconds: str = "5",
    size: str = "720P",
    aspect_ratio: str = "16:9",
    first_frame: str | None = None,
    last_frame: str | None = None,
    images: list[str] | None = None,
    audios: list[str] | None = None,
    videos: list[dict] | None = None,
    seed: int | None = None,
    timeout: float = 60.0,
) -> dict:
    """Call POST /v1/videos. Returns task ids (video_id needed for polling)."""
    validate_video(mode, seconds, size, aspect_ratio, first_frame, last_frame, images, audios, videos)
    if not prompt or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")

    body: dict = {
        "model": VIDEO_MODEL,
        "prompt": prompt,
        "mode": mode,
        "seconds": seconds,
        "size": size,
        "aspect_ratio": aspect_ratio,
    }
    if first_frame:
        body["first_frame"] = first_frame
    if last_frame:
        body["last_frame"] = last_frame
    if images:
        body["images"] = images
    if audios:
        body["audios"] = audios
    if seed is not None:
        body["seed"] = seed
    body["n"] = 1

    url = f"{base_url}/videos"
    try:
        resp = httpx.post(url, headers=_headers(api_key), json=body, timeout=timeout)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Video API HTTP {e.response.status_code}: {e.response.text[:1000]}") from e
    data = resp.json()
    video_id = data.get("video_id") or data.get("id")
    if not video_id:
        raise RuntimeError(f"Video API returned no video_id: {str(data)[:1000]}")
    return {
        "video_id": video_id,
        "task_id": data.get("task_id") or data.get("id"),
        "status": data.get("status", "queued"),
        "model": data.get("model", VIDEO_MODEL),
        "seconds": data.get("seconds", seconds),
        "size": data.get("size", size),
    }


def query_video(
    api_key: str,
    base_url: str,
    video_id: str,
    timeout: float = 30.0,
) -> dict:
    """Call GET /agnesapi?video_id=&model_name=agnes-video-2.5-flash."""
    if not video_id or not video_id.strip():
        raise ValueError("video_id must be a non-empty string")
    root = query_base_url(base_url)
    url = f"{root}/agnesapi"
    try:
        resp = httpx.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            params={"video_id": video_id.strip(), "model_name": VIDEO_QUERY_MODEL},
            timeout=timeout,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Video query HTTP {e.response.status_code}: {e.response.text[:1000]}") from e
    data = resp.json()
    meta = data.get("metadata") or {}
    return {
        "video_id": data.get("video_id", video_id),
        "task_id": data.get("task_id") or data.get("id"),
        "status": data.get("status"),
        "progress": data.get("progress"),
        "video_url": meta.get("url"),
        "completed_at": data.get("completed_at"),
        "error": data.get("error"),
        "raw_model": data.get("model"),
    }


def generate_video_blocking(
    api_key: str,
    base_url: str,
    prompt: str,
    mode: str,
    seconds: str = "5",
    size: str = "720P",
    aspect_ratio: str = "16:9",
    first_frame: str | None = None,
    last_frame: str | None = None,
    images: list[str] | None = None,
    audios: list[str] | None = None,
    seed: int | None = None,
    poll_interval: float = 2.0,
    timeout_seconds: float = 600.0,
) -> dict:
    """Create + poll until completed/failed/timeout. Returns final video_url."""
    created = create_video(
        api_key, base_url, prompt, mode, seconds, size,
        aspect_ratio, first_frame, last_frame, images, audios, None, seed,
    )
    video_id = created["video_id"]
    deadline = time.monotonic() + max(5.0, timeout_seconds)
    last: dict = {}
    interval = max(1.0, min(poll_interval, 10.0))
    while True:
        last = query_video(api_key, base_url, video_id)
        status = last.get("status")
        if status == "completed":
            if not last.get("video_url"):
                raise RuntimeError(f"Video completed but no metadata.url (video_id={video_id})")
            return {
                "video_id": video_id,
                "task_id": last.get("task_id") or created["task_id"],
                "status": "completed",
                "video_url": last["video_url"],
                "seconds": seconds,
                "size": size,
                "aspect_ratio": aspect_ratio,
            }
        if status == "failed":
            err = (last.get("error") or {}).get("message", "Video generation failed")
            raise RuntimeError(f"Video generation failed (video_id={video_id}): {err}")
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Video polling timed out after {timeout_seconds}s "
                f"(video_id={video_id}, last status={status}). Query again with query_video."
            )
        time.sleep(interval)


def download_to_file(url: str, dest_path: str, timeout: float = 120.0) -> str:
    from pathlib import Path

    p = Path(dest_path).expanduser()
    if p.parent and str(p.parent) not in ("", "."):
        p.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=timeout, follow_redirects=True) as r:
        r.raise_for_status()
        with open(p, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return str(p)
