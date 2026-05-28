# Repository Guidelines

## Project Structure & Module Organization

This repository is intentionally small. The CLI lives in `main.py`, static drill packs live in `data/drills/`, custom drill sets live in `data/sets/`, and local user progress lives in `data/progress.json`. Project metadata is in `pyproject.toml`, usage notes are in `README.md`, and AI handoff context lives in `docs/AI.md`.

There is no package directory yet. Keep new functionality in `main.py` unless the file becomes genuinely hard to navigate. Avoid adding frameworks, databases, web UI, or generated assets.

## Build, Test, and Development Commands

Use `uv` for local execution:

```bash
uv run python main.py drill
uv run python main.py drill --hide
uv run python main.py recall
uv run python main.py weak
uv run python main.py list
uv run python main.py validate
```

Check syntax before finishing changes:

```bash
uv run python -m py_compile main.py
```

Validate drill data when editing drill JSON:

```bash
uv run python main.py validate
```

You can still manually try one filtered drill, for example:

```bash
uv run python main.py drill --topic python.list_comprehension
```

## Coding Style & Naming Conventions

Use Python 3.12+ and the standard library only. Prefer small functions with direct names such as `load_progress`, `record_wrong`, and `filter_drills`. Use 4-space indentation, `snake_case` for functions and variables, and uppercase names for constants.

Keep code readable over clever. Preserve the existing flow: load JSON, choose a drill, collect input, validate with `ast.parse()`, update progress, and save JSON.

## Testing Guidelines

There is a minimal standard-library `unittest` suite under `tests/`. For small changes, run `py_compile`, `validate`, and relevant tests.

Avoid tests that depend on a user’s real progress state. Prefer temporary progress data or pure helper-function tests.

## Commit & Pull Request Guidelines

This workspace may not have Git history, so use clear, conventional commit messages such as `Add weak drill mode` or `Track wrong attempts`. Keep commits focused.

Pull requests should describe the behavior change, list the commands run for verification, and note any changes to `data/drills.json` or `data/progress.json`.

## Agent-Specific Instructions

Keep changes small and learning-oriented. Explain key design decisions, preserve simple JSON storage, and avoid adding dependencies unless explicitly requested.

Keep `docs/AI.md` current. Whenever you change code behavior, commands, drill selection, prompt display, data layout, project structure, or important development guidance, update `docs/AI.md` in the same change so future GPT/project discussions have accurate context.

Keep the `Available Packs And Sets` section of `README.md` current. Whenever you add, rename, or remove a static pack in `data/drills/` or a custom set in `data/sets/`, update that README catalog in the same change.
