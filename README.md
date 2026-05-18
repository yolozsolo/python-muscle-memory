# Python Muscle Memory

A tiny standard-library CLI for drilling transferable syntax patterns through repetition.

By default, `drill` uses the `python_basic` pack plus any custom sets in `data/sets/`. Pandas, PySpark, and broader data-pattern built-in packs are included when you request them with `--pack` or `--all-packs`. By default, `recall` chooses from completed drills across all built-in packs and custom sets.

## Requirements

- Python 3.12+
- uv

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
```

Use a custom set:

```bash
uv run python main.py drill --set online-retail
uv run python main.py recall --set online-retail
```

Include every known built-in pack and custom set intentionally:

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

Practice drills where you have made mistakes:

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

Custom sets live in `data/sets/`. A set name maps directly to a JSON file stem, so `--set online-retail` loads `data/sets/online-retail.json`.

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

The interactive commands `drill`, `recall`, and `weak` continue selecting drills until you type `:done`.

For multiline drills, type your answer and then enter a line containing only `:done`.
