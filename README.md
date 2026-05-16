# Python Muscle Memory

A tiny standard-library CLI for drilling transferable Python syntax patterns through repetition.

## Requirements

- Python 3.12+
- uv

## Usage

Start a new drill:

```bash
uv run python main.py drill
```

Hide the expected answer while drilling:

```bash
uv run python main.py drill --hide
```

Drill by difficulty:

```bash
uv run python main.py drill --level beginner
```

Drill by topic:

```bash
uv run python main.py drill --topic python.list_comprehension
```

Practice drills where you have made mistakes:

```bash
uv run python main.py weak
```

Hide the expected answer in weak mode:

```bash
uv run python main.py weak --hide
```

Practice a completed drill from memory:

```bash
uv run python main.py recall
```

List progress:

```bash
uv run python main.py list
```

Progress is stored in `data/progress.json`. Drills are stored in `data/drills.json`, so adding or editing practice items is just JSON editing.

The interactive commands `drill`, `recall`, and `weak` continue selecting drills until you type `:done`.

For multiline drills, type your answer and then enter a line containing only `:done`.
