# AI Project Context

Use this file as compact context for GPT or other AI assistants discussing this project.

## Project Purpose

Python Muscle Memory is a tiny standard-library CLI for practicing transferable Python, pandas, PySpark, and FastAPI syntax patterns through repetition. It is meant to act like a focused tutor: small prompts, exact answers, progress tracking, and repeated recall of patterns that should become automatic.

## Repository Shape

- `main.py` contains the CLI, JSON loading, drill selection, answer checking, progress updates, and command dispatch.
- `data/drills/` contains static drill packs.
- `data/sets/` contains custom named drill sets. Plain `drill`, `recall`, and `weak` expose them in an interactive collection menu.
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
uv run python main.py drill --set online-retail
uv run python main.py drill --set fastapi-basics
uv run python main.py drill --all-packs
uv run python main.py drill --level beginner
uv run python main.py drill --pack pyspark_basic --level advanced
uv run python main.py drill --topic python.list_comprehension
uv run python main.py weak
uv run python main.py weak --pack pandas_basic
uv run python main.py weak --set online-retail
uv run python main.py weak --all-packs
uv run python main.py recall
uv run python main.py recall --pack pyspark_basic
uv run python main.py recall --set online-retail
uv run python main.py recall --set fastapi-basics
uv run python main.py recall --all-packs
uv run python main.py list
uv run python main.py list --all-packs
```

Check syntax before finishing code changes:

```bash
uv run python -m py_compile main.py
```

## Current Behavior

- `drill`, `weak`, and `recall` prompt for a numbered built-in pack, custom set, or all-collections selection when no selection flag is supplied. Entering `:done` at that menu exits before a session starts.
- `drill` chooses incomplete drills from the selected collection.
- `--pack` selects one built-in pack. `--set` selects one custom drill set. They are mutually exclusive.
- `--all-packs` selects every built-in pack and every discovered custom set, including `fastapi-basics`.
- `fastapi-basics` is a custom set for A-level FastAPI, Pydantic, type annotation, route signature, validator, HTTPException, and TestClient drills.
- `python_basic`, `python_data_patterns`, and `pyspark_basic` each contain 60 curated drills: 20 `beginner`, 20 `intermediate`, and 20 `advanced`.
- Their content targets routinely used Python application, standard-library data workflow, and PySpark DataFrame/performance patterns rather than specialized edge cases.
- `drill --level` filters by exact difficulty (`beginner`, `intermediate`, or `advanced`). If omitted, all difficulties in the selected pack are eligible.
- `drill --topic` filters by exact topic.
- `drill` avoids serving the same `pattern_focus` more than two times in a row when another incomplete pattern is available.
- `weak` chooses completed drills that were missed during `recall` and runs one attempt at a time. `--pack`, `--set`, and `--all-packs` bypass the collection menu. Generic wrong attempts from `drill` do not make a drill weak. Three correct weak-mode attempts clear the recall miss and remove the drill from weak mode; a weak-mode wrong answer resets that correct streak.
- `recall` chooses from completed drills and prints the source pack or set for each prompt. `recall --pack ...`, `recall --set ...`, and `recall --all-packs` bypass the collection menu.
- `recall` uses shuffled pack and drill queues so one pack or a few tasks do not dominate a session while other completed options exist.
- `list` prints pack, ID, topic, difficulty, progress, general wrong attempts, recall wrong attempts, and line count.
- Custom set names are discovered from `data/sets/*.json` and are not hardcoded.
- Missing, malformed, or internally duplicated custom sets should fail with a clear error.
- Drill tasks are loaded from static pack and set JSON files only. There is no template-generation command or generated-drill loading path.

## Answer Checking And Prompts

Answers are checked with exact string matching after `ast.parse()` confirms valid Python syntax. The `expected` answer is always accepted, and `acceptable_answers` can add extra exact alternatives. This means variable names and literal values matter.

To make exact matching fair, prompts print required identifiers and literals derived from the expected answer, for example:

```text
Required identifiers: result, df, value
Required literals: "reason", "invalid_amount"
```

Do not assume the learner should memorize arbitrary variable names, dictionary keys, indexes, format strings, or expected string values that are not visible in the prompt. If exact matching requires a name or literal, the prompt should reveal it through the description, starter context, required-identifiers line, or required-literals line.

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

The expanded 60-drill `python_basic`, `python_data_patterns`, and `pyspark_basic` catalogs give revised exercises fresh IDs (for example, `practical_assignment_generic`) so historical completion is not applied to changed prompts. Stored historical records remain untouched.

Custom set progress uses the same prefix style, for example `online-retail:parse_strict_datetime`.

Progress records default missing fields at load/use time for compatibility. They include `completed_count`, generic `wrong_attempts`, recall-only `recall_wrong_attempts`, weak-mode `weak_correct_attempts`, and `last_wrong`. `weak` selection is based on `recall_wrong_attempts > 0`.

To create another custom set, add a JSON list of drill records to `data/sets/<name>.json`, then run it with:

```bash
uv run python main.py drill --set <name>
uv run python main.py recall --set <name>
```

Avoid tests or examples that depend on a user's real `data/progress.json`. Prefer pure helper checks or temporary progress dictionaries.

## Development Constraints

- Use Python 3.12+ and the standard library only.
- Preserve simple JSON storage.
- Avoid frameworks, databases, web UI, generated assets, or new dependencies unless explicitly requested.
- Keep changes small and learning-oriented.
- Prefer direct, readable helper functions over clever abstractions.
- Keep the `Available Packs And Sets` section of `README.md` updated whenever a static pack in `data/drills/` or custom set in `data/sets/` is added, renamed, or removed.
- When behavior, commands, data layout, drill selection, prompt display, or workflow changes, update this file in the same change.

## Discussion Style For AI Assistants

When helping with this project, act as a senior pair programmer and tutor. Explain key design decisions, tie concepts to the current codebase, summarize what changed and why, and suggest a small manual exercise when useful.
