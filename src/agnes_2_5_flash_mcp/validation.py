"""Agnes API validation rules (Flash-only constraints from official docs)."""

from __future__ import annotations

IMAGE_SIZES = ("1K", "2K", "3K", "4K")
IMAGE_RATIOS = ("1:1", "3:4", "4:3", "16:9", "9:16", "2:3", "3:2", "21:9")
IMAGE_RESPONSE_FORMATS = ("url", "b64_json")

VIDEO_MODEL = "agnes-video-2.5-flash"
VIDEO_SIZES = ("720P",)
VIDEO_ASPECT_RATIOS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16")
VIDEO_SECONDS = tuple(str(s) for s in range(4, 13))  # "4".."12"
VIDEO_MODES = ("text", "keyframe", "reference")

# Approximate output pixels for the default 16:9 ratio (from docs).
SIZE_PIXELS_16_9 = {
    "1K": "1312x736",
    "2K": "2624x1472",
    "3K": "3936x2208",
    "4K": "5248x2944",
}


def validate_image(
    size: str,
    ratio: str,
    images: list[str] | None,
    response_format: str,
) -> None:
    if size not in IMAGE_SIZES:
        raise ValueError(f"size must be one of {list(IMAGE_SIZES)}, got {size!r}")
    if ratio not in IMAGE_RATIOS:
        raise ValueError(f"ratio must be one of {list(IMAGE_RATIOS)}, got {ratio!r}")
    if response_format not in IMAGE_RESPONSE_FORMATS:
        raise ValueError(
            f"response_format must be one of {list(IMAGE_RESPONSE_FORMATS)}, got {response_format!r}"
        )
    if images is not None:
        if not isinstance(images, list) or not images:
            raise ValueError("images must be a non-empty list when provided")
        if len(images) > 10:
            raise ValueError("images: too many reference images (max 10)")
        for img in images:
            if not isinstance(img, str) or not img.strip():
                raise ValueError("images: each entry must be a non-empty URL or Data URI string")


def validate_video(
    mode: str,
    seconds: str,
    size: str,
    aspect_ratio: str,
    first_frame: str | None,
    last_frame: str | None,
    images: list[str] | None,
    audios: list[str] | None,
    videos: list[dict] | None,
) -> None:
    if mode not in VIDEO_MODES:
        raise ValueError(f"mode must be one of {list(VIDEO_MODES)}, got {mode!r}")
    if seconds not in VIDEO_SECONDS:
        raise ValueError(f'seconds must be a string "4".."12", got {seconds!r}')
    if size not in VIDEO_SIZES:
        raise ValueError("size must be 720P")  # exact Flash error text
    if aspect_ratio not in VIDEO_ASPECT_RATIOS:
        raise ValueError(f"aspect_ratio must be one of {list(VIDEO_ASPECT_RATIOS)}, got {aspect_ratio!r}")

    has_first = bool(first_frame and first_frame.strip())
    has_last = bool(last_frame and last_frame.strip())
    has_images = bool(images)
    has_audios = bool(audios)
    has_videos = bool(videos)

    if has_videos:
        raise ValueError("videos is not supported")  # exact Flash error text
    if images is not None and len(images) > 5:
        raise ValueError("images length must not exceed 5")  # exact Flash error text
    if audios is not None and len(audios) > 3:
        raise ValueError("audios length must not exceed 3")  # exact Flash error text

    if mode == "text":
        if has_first or has_last or has_images or has_audios or has_videos:
            raise ValueError('mode="text" forbids first_frame/last_frame/images/audios/videos')
    elif mode == "keyframe":
        if not (has_first or has_last):
            raise ValueError('mode="keyframe" requires at least one of first_frame/last_frame')
        if has_images or has_audios or has_videos:
            raise ValueError('mode="keyframe" forbids images/audios/videos')
    elif mode == "reference":
        if not (has_images or has_audios):
            raise ValueError('mode="reference" requires at least one of images/audios')
        if has_first or has_last:
            raise ValueError('mode="reference" forbids first_frame/last_frame')
