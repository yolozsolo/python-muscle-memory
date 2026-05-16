# Python Muscle Memory

A tiny standard-library CLI for drilling transferable syntax patterns through repetition.

By default, the CLI always uses the `python_basic` pack. Pandas, PySpark, and broader data-pattern drills are only included when you request them with `--pack` or `--all-packs`.

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

Include every known pack intentionally:

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

Progress keys include the pack name, for example `python_basic:list_comprehension_transform`. Old un-prefixed progress keys are still read for the default `python_basic` pack.

The interactive commands `drill`, `recall`, and `weak` continue selecting drills until you type `:done`.

For multiline drills, type your answer and then enter a line containing only `:done`.
