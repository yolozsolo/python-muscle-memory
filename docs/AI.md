# AI Project Context

Use this file as compact context for GPT or other AI assistants discussing this project.

## Project Purpose

Python Muscle Memory is a tiny standard-library CLI for practicing transferable Python, pandas, and PySpark syntax patterns through repetition. It is meant to act like a focused tutor: small prompts, exact answers, progress tracking, and repeated recall of patterns that should become automatic.

## Repository Shape

- `main.py` contains the CLI, JSON loading, drill selection, answer checking, progress updates, template generation, and command dispatch.
- `data/drills/` contains static drill packs.
- `data/templates/` contains drill templates.
- `data/generated/` contains generated drill variants.
- `data/drills.json` is the legacy/default drill file fallback.
- `data/progress.json` stores local user progress and should not be treated as shared source data.
- `README.md` contains user-facing usage notes.
- `AGENTS.md` contains coding-agent instructions.

There is intentionally no package directory yet. Keep changes in `main.py` unless the file becomes genuinely hard to navigate.

## Commands

Use `uv` for local execution:

```bash
uv run python main.py drill
uv run python main.py drill --hide
uv run python main.py drill --pack pandas_basic
uv run python main.py drill --all-packs
uv run python main.py drill --level beginner
uv run python main.py drill --topic python.list_comprehension
uv run python main.py weak
uv run python main.py recall
uv run python main.py recall --pack pyspark_basic
uv run python main.py list
uv run python main.py list --all-packs
uv run python main.py generate --pack python_basic --limit 100 --seed 42
```

Check syntax before finishing code changes:

```bash
uv run python -m py_compile main.py
```

## Current Behavior

- `drill` chooses incomplete drills from the selected pack. Without `--pack`, it defaults to `python_basic`.
- `drill --level` filters by exact difficulty. If omitted, all difficulties in the selected pack are eligible.
- `drill --topic` filters by exact topic.
- `drill` avoids serving the same `pattern_focus` more than two times in a row when another incomplete pattern is available.
- `weak` chooses drills with recorded wrong attempts and runs one attempt at a time.
- `recall` chooses from completed drills. By default it recalls across all known packs; `recall --pack ...` restricts it to one pack.
- `recall` uses shuffled pack and drill queues so one pack or a few tasks do not dominate a session while other completed options exist.
- `list` prints pack, ID, topic, difficulty, progress, wrong attempts, and line count.
- `generate` expands templates into generated drill JSON and can shuffle deterministically with `--seed`.

## Answer Checking And Prompts

Answers are checked with exact string matching after `ast.parse()` confirms valid Python syntax. This means variable names matter.

To make exact matching fair, prompts print required identifiers derived from the expected answer, for example:

```text
Required identifiers: result, df, value
```

Do not assume the learner should memorize arbitrary variable names that are not visible in the prompt. If exact matching requires a name, the prompt should reveal it through the description, starter context, or required-identifiers line.

## Data And Progress

Drill records include:

- `id`
- `topic`
- `description`
- `pattern_focus`
- `starter_context`
- `expected`
- `acceptable_answers`
- `times_required`
- `difficulty`
- `lines_allowed`

Progress keys include the pack name, for example `python_basic:list_comprehension_transform`. Old un-prefixed progress keys are still read for the default `python_basic` pack.

Avoid tests or examples that depend on a user's real `data/progress.json`. Prefer pure helper checks or temporary progress dictionaries.

## Development Constraints

- Use Python 3.12+ and the standard library only.
- Preserve simple JSON storage.
- Avoid frameworks, databases, web UI, generated assets, or new dependencies unless explicitly requested.
- Keep changes small and learning-oriented.
- Prefer direct, readable helper functions over clever abstractions.
- When behavior, commands, data layout, drill selection, prompt display, or workflow changes, update this file in the same change.

## Discussion Style For AI Assistants

When helping with this project, act as a senior pair programmer and tutor. Explain key design decisions, tie concepts to the current codebase, summarize what changed and why, and suggest a small manual exercise when useful.
