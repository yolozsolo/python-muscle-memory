import ast
import argparse
import itertools
import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OLD_DRILLS_PATH = DATA_DIR / "drills.json"
DRILLS_DIR = DATA_DIR / "drills"
TEMPLATES_DIR = DATA_DIR / "templates"
GENERATED_DIR = DATA_DIR / "generated"
PROGRESS_PATH = BASE_DIR / "data" / "progress.json"
DEFAULT_PACK = "python_basic"
KNOWN_PACKS = [
    "python_basic",
    "python_data_patterns",
    "pandas_basic",
    "pyspark_basic",
]
EXIT_SESSION = "__EXIT_SESSION__"


def load_json(path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)
        file.write("\n")


def progress_key(pack, drill_id):
    return f"{pack}:{drill_id}"


def with_pack(drill, pack):
    item = dict(drill)
    item["_pack"] = pack
    return item


def load_pack(pack):
    static_path = DRILLS_DIR / f"{pack}.json"
    if pack == DEFAULT_PACK and not static_path.exists():
        static_drills = load_json(OLD_DRILLS_PATH, [])
    else:
        static_drills = load_json(static_path, [])

    generated_path = GENERATED_DIR / f"{pack}_generated.json"
    generated_drills = load_json(generated_path, [])

    drills = []
    seen_ids = set()
    for drill in static_drills + generated_drills:
        if drill["id"] in seen_ids:
            continue
        seen_ids.add(drill["id"])
        drills.append(with_pack(drill, pack))
    return drills


def load_drills(packs=None):
    selected_packs = packs or [DEFAULT_PACK]
    drills = []
    for pack in selected_packs:
        drills.extend(load_pack(pack))
    return drills


def load_progress():
    return load_json(PROGRESS_PATH, {})


def save_progress(progress):
    save_json(PROGRESS_PATH, progress)


def get_progress_record(progress, drill_id, pack=DEFAULT_PACK):
    key = progress_key(pack, drill_id)
    if key not in progress and pack == DEFAULT_PACK and drill_id in progress:
        progress[key] = dict(progress[drill_id])

    record = progress.setdefault(key, {})
    record.setdefault("completed_count", 0)
    record.setdefault("wrong_attempts", 0)
    record.setdefault("last_wrong", "")
    return record


def completed_count(progress, drill):
    return int(
        get_progress_record(progress, drill["id"], drill["_pack"])[
            "completed_count"
        ]
    )


def wrong_attempts(progress, drill):
    return int(
        get_progress_record(progress, drill["id"], drill["_pack"])[
            "wrong_attempts"
        ]
    )


def record_correct(progress, drill):
    record = get_progress_record(progress, drill["id"], drill["_pack"])
    record["completed_count"] += 1


def record_wrong(progress, drill, answer):
    record = get_progress_record(progress, drill["id"], drill["_pack"])
    record["wrong_attempts"] += 1
    record["last_wrong"] = answer.strip()


def is_completed(progress, drill):
    return completed_count(progress, drill) >= drill["times_required"]


def check_answer(answer, acceptable_answers, lines_allowed):
    stripped = answer.strip()

    if len(stripped.splitlines()) > lines_allowed:
        return "too_many_lines"

    try:
        ast.parse(stripped)
    except SyntaxError:
        return "syntax_error"

    acceptable = {item.strip() for item in acceptable_answers}
    if stripped not in acceptable:
        return "not_exact"

    return "correct"


def choose_incomplete_drill(drills, progress):
    incomplete = [drill for drill in drills if not is_completed(progress, drill)]
    if not incomplete:
        return None
    return random.choice(incomplete)


def filter_drills(drills, level=None, topic=None):
    filtered = drills

    if level is not None:
        filtered = [
            drill for drill in filtered if drill["difficulty"] == level
        ]

    if topic is not None:
        filtered = [drill for drill in filtered if drill["topic"] == topic]

    return filtered


def choose_weak_drill(drills, progress):
    weak_drills = [
        drill
        for drill in drills
        if wrong_attempts(progress, drill) > 0
        and not is_completed(progress, drill)
    ]
    if not weak_drills:
        return None

    highest_wrong = max(
        wrong_attempts(progress, drill) for drill in weak_drills
    )
    most_wrong = [
        drill
        for drill in weak_drills
        if wrong_attempts(progress, drill) == highest_wrong
    ]
    return random.choice(most_wrong)


def choose_completed_drill(drills, progress):
    completed = [drill for drill in drills if is_completed(progress, drill)]
    if not completed:
        return None
    return random.choice(completed)


def print_context(drill, show_answer):
    print(f"Pack: {drill['_pack']}")
    print(f"Topic: {drill['topic']}")
    print(f"Difficulty: {drill['difficulty']}")
    print(f"Description: {drill['description']}")
    print(f"Pattern focus: {drill['pattern_focus']}")

    if drill["starter_context"]:
        print("Starter context:")
        print(drill["starter_context"])

    if show_answer:
        print("Expected:")
        print(drill["expected"])


def read_answer(lines_allowed):
    if lines_allowed == 1:
        answer = input("Answer: ")
        if answer.strip() == ":done":
            return EXIT_SESSION
        return answer

    print(f"Answer ({lines_allowed} lines max, enter :done when finished):")
    lines = []

    while True:
        line = input()
        if line.strip() == ":done":
            return "\n".join(lines)
        lines.append(line)


def should_continue_session():
    while True:
        answer = input("Press Enter for next drill, or type :done to exit: ")
        if answer.strip() == ":done":
            return False
        if answer.strip() == "":
            return True
        print("Press Enter to continue, or type :done to exit.")


def print_result(result):
    if result == "syntax_error":
        print("Syntax error")
    elif result == "too_many_lines":
        print("Too many lines")
    elif result == "not_exact":
        print("Valid syntax but not exact")
    else:
        print("Correct")


def run_practice_session(drill, progress, show_answer):
    count = completed_count(progress, drill)
    required = drill["times_required"]

    print_context(drill, show_answer)
    print(f"Progress: {count} / {required}")
    print()

    while count < required:
        answer = read_answer(drill["lines_allowed"])
        if answer == EXIT_SESSION:
            return False

        result = check_answer(
            answer,
            drill["acceptable_answers"],
            drill["lines_allowed"],
        )

        if result != "correct":
            record_wrong(progress, drill, answer)
            save_progress(progress)
            print_result(result)
            continue

        print_result(result)
        record_correct(progress, drill)
        save_progress(progress)
        count = completed_count(progress, drill)
        print(f"Progress: {count} / {required}")

    print("Drill completed")
    return True


def run_drill(show_answer=True, level=None, topic=None, packs=None):
    drills = filter_drills(load_drills(packs), level=level, topic=topic)
    progress = load_progress()

    while True:
        if not should_continue_session():
            return

        drill = choose_incomplete_drill(drills, progress)

        if drill is None:
            print("No matching incomplete drill found.")
            return

        if not run_practice_session(drill, progress, show_answer):
            return


def run_weak(show_answer=True, level=None, topic=None, packs=None):
    drills = filter_drills(load_drills(packs), level=level, topic=topic)
    progress = load_progress()

    while True:
        if not should_continue_session():
            return

        drill = choose_weak_drill(drills, progress)

        if drill is None:
            print("No matching weak drill found.")
            return

        if not run_practice_session(drill, progress, show_answer):
            return


def run_recall(packs=None):
    drills = load_drills(packs)
    progress = load_progress()

    while True:
        if not should_continue_session():
            return

        drill = choose_completed_drill(drills, progress)

        if drill is None:
            print("No completed drills yet. Use drill first.")
            return

        print(f"Description: {drill['description']}")
        if drill["starter_context"]:
            print("Starter context:")
            print(drill["starter_context"])

        answer = read_answer(drill["lines_allowed"])
        if answer == EXIT_SESSION:
            return

        result = check_answer(
            answer,
            drill["acceptable_answers"],
            drill["lines_allowed"],
        )

        print_result(result)
        if result != "correct":
            record_wrong(progress, drill, answer)
            save_progress(progress)

        print("Expected:")
        print(drill["expected"])


def run_list(packs=None):
    drills = load_drills(packs)
    progress = load_progress()

    for drill in drills:
        count = completed_count(progress, drill)
        required = drill["times_required"]
        print(
            f"{drill['_pack']} | {drill['id']} | {drill['topic']} | "
            f"{drill['difficulty']} | {count}/{required} | "
            f"wrong: {wrong_attempts(progress, drill)} | "
            f"lines: {drill['lines_allowed']}"
        )


def resolve_packs(args):
    if getattr(args, "all_packs", False):
        return KNOWN_PACKS
    return [getattr(args, "pack", None) or DEFAULT_PACK]


def add_pack_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--pack",
        choices=KNOWN_PACKS,
        help="choose one drill pack",
    )
    group.add_argument(
        "--all-packs",
        action="store_true",
        help="include every known drill pack",
    )


def load_templates(pack):
    path = TEMPLATES_DIR / f"{pack}_templates.json"
    templates = load_json(path, [])
    if isinstance(templates, dict):
        return templates.get("templates", [])
    return templates


def render_template(text, values):
    return text.format(**values)


def generate_from_template(template):
    names = list(template["variables"])
    choices = [template["variables"][name] for name in names]

    for index, combination in enumerate(itertools.product(*choices), start=1):
        values = dict(zip(names, combination))
        expected = render_template(template["expected_template"], values)
        try:
            ast.parse(expected)
        except SyntaxError:
            continue

        yield {
            "id": f"{template['template_id']}_{index}",
            "topic": template["topic"],
            "description": render_template(
                template["description_template"], values
            ),
            "pattern_focus": template["pattern_focus"],
            "starter_context": render_template(
                template.get("starter_context_template", ""), values
            ),
            "expected": expected,
            "acceptable_answers": [expected],
            "times_required": template["times_required"],
            "difficulty": template["difficulty"],
            "lines_allowed": template["lines_allowed"],
        }


def run_generate(pack, limit=None, seed=None):
    templates = load_templates(pack)
    if not templates:
        print(f"No templates found for pack: {pack}")
        return

    generated = []
    seen_expected = set()
    for template in templates:
        generated.extend(generate_from_template(template))

    unique = []
    for drill in generated:
        if drill["expected"] in seen_expected:
            continue
        seen_expected.add(drill["expected"])
        unique.append(drill)

    if seed is not None:
        random.Random(seed).shuffle(unique)

    if limit is not None:
        unique = unique[:limit]

    output_path = GENERATED_DIR / f"{pack}_generated.json"
    save_json(output_path, unique)
    print(f"Generated {len(unique)} drills in {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Drill Python syntax patterns through repetition."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    drill_parser = subparsers.add_parser("drill")
    drill_parser.add_argument(
        "--hide",
        action="store_true",
        help="hide the expected answer during drill mode",
    )
    drill_parser.add_argument(
        "--level",
        choices=["beginner", "intermediate"],
        help="only choose drills with this difficulty",
    )
    drill_parser.add_argument(
        "--topic",
        help="only choose drills with this exact topic",
    )
    add_pack_arguments(drill_parser)

    weak_parser = subparsers.add_parser("weak")
    weak_parser.add_argument(
        "--hide",
        action="store_true",
        help="hide the expected answer during weak mode",
    )
    weak_parser.add_argument(
        "--level",
        choices=["beginner", "intermediate"],
        help="only choose weak drills with this difficulty",
    )
    weak_parser.add_argument(
        "--topic",
        help="only choose weak drills with this exact topic",
    )
    add_pack_arguments(weak_parser)

    recall_parser = subparsers.add_parser("recall")
    add_pack_arguments(recall_parser)

    list_parser = subparsers.add_parser("list")
    add_pack_arguments(list_parser)

    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument(
        "--pack",
        choices=KNOWN_PACKS,
        required=True,
        help="generate drills for this pack",
    )
    generate_parser.add_argument(
        "--limit",
        type=int,
        help="maximum number of generated drills to write",
    )
    generate_parser.add_argument(
        "--seed",
        type=int,
        help="shuffle generated drills deterministically with this seed",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "drill":
        run_drill(
            show_answer=not args.hide,
            level=args.level,
            topic=args.topic,
            packs=resolve_packs(args),
        )
    elif args.command == "weak":
        run_weak(
            show_answer=not args.hide,
            level=args.level,
            topic=args.topic,
            packs=resolve_packs(args),
        )
    elif args.command == "recall":
        run_recall(packs=resolve_packs(args))
    elif args.command == "list":
        run_list(packs=resolve_packs(args))
    elif args.command == "generate":
        run_generate(pack=args.pack, limit=args.limit, seed=args.seed)


if __name__ == "__main__":
    main()
