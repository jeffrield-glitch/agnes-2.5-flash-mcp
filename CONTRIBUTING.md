# Contributing to agnes-2.5-flash-mcp

Thanks for your interest! This is a 2.5-flash-only MCP edition
(`agnes-image-2.5-flash` + `agnes-video-2.5-flash`).

## Dev setup

```bash
cd mcps/agnes  # or the standalone repo root
pip install -e ".[dev]"
# or minimal:
pip install -e . && pip install pytest ruff
python -m pytest tests -q
```

## Rules

- Keep Flash-only constraints in `src/agnes_2_5_flash_mcp/validation.py`
  (`size must be 720P`, `images<=5`, `audios<=3`, `videos unsupported`).
- Video default stays **async**: `create_video` + `query_video`.
  `generate_video` is compat-only, do not make it the documented default.
- Tool docstrings must keep Chinese trigger words
  （生图 / 生视频） in the first lines so intent routing works.
- Do not commit real API keys. Use `.env` (see `.env.example`)
  or MCP client `environment.AGNES_API_KEY`.

## Release

```bash
python -m build
twine upload dist/*
git tag v0.1.0 && git push --tags
```
