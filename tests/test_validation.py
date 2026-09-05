import pytest

from agnes_2_5_flash_mcp.validation import validate_image, validate_video


def test_image_defaults_valid():
    validate_image("2K", "16:9", None, "url")


def test_image_bad_size():
    with pytest.raises(ValueError):
        validate_image("720P", "16:9", None, "url")


def test_image_bad_ratio():
    with pytest.raises(ValueError):
        validate_image("2K", "auto", None, "url")


def test_video_text_ok():
    validate_video("text", "5", "720P", "16:9", None, None, None, None, None)


def test_video_flash_size_rejected():
    with pytest.raises(ValueError, match="size must be 720P"):
        validate_video("text", "5", "1080P", "16:9", None, None, None, None, None)


def test_video_images_limit():
    with pytest.raises(ValueError, match="images length must not exceed 5"):
        validate_video("reference", "5", "720P", "16:9", None, None, ["u"] * 6, None, None)


def test_video_audios_limit():
    with pytest.raises(ValueError, match="audios length must not exceed 3"):
        validate_video("reference", "5", "720P", "16:9", None, None, None, ["a"] * 4, None)


def test_video_videos_unsupported():
    with pytest.raises(ValueError, match="videos is not supported"):
        validate_video("reference", "5", "720P", "16:9", None, None, ["img"], None, [{"url": "x"}])


def test_video_keyframe_needs_frame():
    with pytest.raises(ValueError):
        validate_video("keyframe", "5", "720P", "16:9", None, None, None, None, None)


def test_video_reference_needs_media():
    with pytest.raises(ValueError):
        validate_video("reference", "5", "720P", "16:9", None, None, None, None, None)


def test_video_seconds_must_be_string_range():
    with pytest.raises(ValueError):
        validate_video("text", "30", "720P", "16:9", None, None, None, None, None)
