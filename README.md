# Python Muscle Memory

A tiny standard-library CLI for drilling transferable syntax patterns through repetition.

When run without collection flags, `drill`, `recall`, and `weak` prompt you to choose a built-in pack, a custom set, or all collections. Use `--pack`, `--set`, or `--all-packs` to choose directly without the menu.

## Requirements

- Python 3.12+
- uv

## Available Packs And Sets

Built-in packs, selected with `--pack`:

| Pack | Focus |
| --- | --- |
| `python_basic` | Core Python application patterns; 60 drills, 20 per level |
| `python_data_patterns` | Practical standard-library data cleaning and transformation; 60 drills, 20 per level |
| `pandas_basic` | Basic pandas expressions |
| `pyspark_basic` | PySpark DataFrame and performance patterns; 60 drills, 20 per level |
| `ai_tooling_core` | Python shapes for AI tooling, RAG, tools, and structured LLM applications |

Custom sets, selected with `--set`:

| Set | Focus | Availability |
| --- | --- | --- |
| `online-retail` | Online retail data practice | Included when selected directly or with `--all-packs` |
| `fastapi-basics` | FastAPI and Pydantic syntax practice | Included when selected directly or with `--all-packs` |

## Usage

Start a drill and choose a collection from the numbered menu:

```bash
uv run python main.py drill
```

Hide the expected answer while drilling:

```bash
uv run python main.py drill --hide
```

Use a specific pack:

```bash
uv run python main.py drill --pack python_data_patterns
uv run python main.py drill --pack pandas_basic
uv run python main.py drill --pack pyspark_basic
uv run python main.py drill --pack ai_tooling_core
```

Use a custom set:

```bash
uv run python main.py drill --set online-retail
uv run python main.py recall --set online-retail
```

Use the FastAPI basics set directly:

```bash
uv run python main.py drill --set fastapi-basics
uv run python main.py recall --set fastapi-basics
```

Include every built-in pack and custom set intentionally:

```bash
uv run python main.py drill --all-packs
```

Drill by difficulty:

```bash
uv run python main.py drill --pack python_basic --level beginner
uv run python main.py drill --pack python_data_patterns --level intermediate
uv run python main.py drill --pack pyspark_basic --level advanced
```

The `python_basic`, `python_data_patterns`, and `pyspark_basic` packs each
contain 20 `beginner`, 20 `intermediate`, and 20 `advanced` drills. Their
content favors commonly used application, ETL, and Spark DataFrame workflows
over specialized edge-case techniques.

Drill by topic:

```bash
uv run python main.py drill --pack python_basic --topic python.list_comprehension
```

Practice completed drills that you missed during recall:

```bash
uv run python main.py weak
```

Practice weak drills from a specific pack:

```bash
uv run python main.py weak --pack pandas_basic
uv run python main.py weak --set online-retail
uv run python main.py weak --all-packs
```

Hide the expected answer in weak mode:

```bash
uv run python main.py weak --hide
```

Practice a completed drill from memory:

```bash
uv run python main.py recall
uv run python main.py recall --pack pyspark_basic
uv run python main.py recall --all-packs
```

Recall prompts show the source pack or set before each drill description.

List progress:

```bash
uv run python main.py list
uv run python main.py list --all-packs
```

Validate drill data:

```bash
uv run python main.py validate
```

Progress is stored locally in ignored `data/progress.json`. Drill packs live in `data/drills/`.

Custom sets live in `data/sets/`. A set name maps directly to a JSON file stem, so `--set online-retail` loads `data/sets/online-retail.json`. Plain `drill`, `recall`, and `weak` show the collection menu; their selection flags remain useful for direct and scripted sessions.

Custom set files reuse the normal drill schema:

```json
{
  "id": "parse_strict_datetime",
  "topic": "online_retail.datetime",
  "description": "Parse text as a strict online retail timestamp.",
  "pattern_focus": "datetime.strptime(value, format)",
  "starter_context": "from datetime import datetime",
  "expected": "parsed_at = datetime.strptime(text, \"%Y-%m-%d %H:%M:%S\")",
  "acceptable_answers": [
    "parsed_at = datetime.strptime(text, \"%Y-%m-%d %H:%M:%S\")"
  ],
  "times_required": 3,
  "difficulty": "intermediate",
  "lines_allowed": 1
}
```

Prompts automatically show required identifiers and literals from `expected`, so exact-match drills should not require memorizing hidden variable names, dictionary keys, indexes, or string values.

Progress keys include the pack name, for example `python_basic:list_comprehension_transform`. Old un-prefixed progress keys are still read for the default `python_basic` pack.

Revised exercises in the expanded 60-drill packs use fresh identifiers, so
completion of an earlier prompt is not incorrectly applied to updated
practice material. Existing progress data is not deleted.

Progress tracks both general wrong attempts and recall-specific wrong attempts. `weak` uses only recall-specific misses, so mistakes during `drill` do not make a drill weak. A recall miss resets that drill's `weak_correct_streak`; after three correct weak-mode attempts, the recall miss is cleared, the streak resets, and the drill drops out of weak mode.

`validate` checks every drill JSON file for schema shape, duplicate IDs, parseable expected and acceptable answers, difficulty values, repetition counts, line limits, and whether `expected` is included in `acceptable_answers`.

The interactive commands `drill`, `recall`, and `weak` accept `:done` at the collection menu to quit, and continue selecting drills until you type `:done` during a session.

For multiline drills, type your answer and then enter a line containing only `:done`.
