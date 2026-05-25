# Python Muscle Memory

A tiny standard-library CLI for drilling transferable syntax patterns through repetition.

By default, `drill` uses the `python_basic` pack plus standard custom sets in `data/sets/`. Pandas, PySpark, and broader data-pattern built-in packs are included when you request them with `--pack` or `--all-packs`. By default, `recall` chooses from completed drills across built-in packs and standard custom sets. Opt-in custom sets such as `fastapi-basics` appear only when requested with `--set`.

## Requirements

- Python 3.12+
- uv

## Available Packs And Sets

Built-in packs, selected with `--pack`:

| Pack | Focus |
| --- | --- |
| `python_basic` | Core Python syntax patterns and default practice pack |
| `python_data_patterns` | Common data-cleaning and transformation patterns |
| `pandas_basic` | Basic pandas expressions |
| `pyspark_basic` | Basic PySpark expressions |
| `ai_tooling_core` | Python shapes for AI tooling, RAG, tools, and structured LLM applications |

Custom sets, selected with `--set`:

| Set | Focus | Availability |
| --- | --- | --- |
| `online-retail` | Online retail data practice | Included in standard custom-set practice |
| `fastapi-basics` | FastAPI and Pydantic syntax practice | Opt-in only |

## Usage

Start a basic Python drill:

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

Use the opt-in FastAPI basics set:

```bash
uv run python main.py drill --set fastapi-basics
uv run python main.py recall --set fastapi-basics
```

Include every built-in pack and standard custom set intentionally:

```bash
uv run python main.py drill --all-packs
```

Drill by difficulty:

```bash
uv run python main.py drill --pack python_basic --level beginner
```

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
```

Hide the expected answer in weak mode:

```bash
uv run python main.py weak --hide
```

Practice a completed drill from memory:

```bash
uv run python main.py recall
uv run python main.py recall --pack pyspark_basic
```

List progress:

```bash
uv run python main.py list
uv run python main.py list --all-packs
```

Generate drills from templates:

```bash
uv run python main.py generate --pack python_basic --limit 100 --seed 42
```

Progress is stored in `data/progress.json`. Drill packs live in `data/drills/`, templates in `data/templates/`, and generated drills in `data/generated/`.

Custom sets live in `data/sets/`. A set name maps directly to a JSON file stem, so `--set online-retail` loads `data/sets/online-retail.json`. The `fastapi-basics` set is opt-in, so it is excluded from default practice and `--all-packs`.

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

Progress tracks both general wrong attempts and recall-specific wrong attempts. `weak` uses only recall-specific misses, so mistakes during `drill` do not make a drill weak. After three correct attempts in weak mode, the recall miss is cleared and the drill drops out of weak mode.

The interactive commands `drill`, `recall`, and `weak` continue selecting drills until you type `:done`.

For multiline drills, type your answer and then enter a line containing only `:done`.
