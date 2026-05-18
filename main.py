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
CUSTOM_SETS_DIR = DATA_DIR / "sets"
TEMPLATES_DIR = DATA_DIR / "templates"
GENERATED_DIR = DATA_DIR / "generated"
PROGRESS_PATH = BASE_DIR / "data" / "progress.json"
DEFAULT_PACK = "python_basic"
MAX_PATTERN_STREAK = 2
REQUIRED_DRILL_FIELDS = [
    "id",
    "topic",
    "description",
    "pattern_focus",
    "starter_context",
    "expected",
    "acceptable_answers",
    "times_required",
    "difficulty",
    "lines_allowed",
]
EXIT_SESSION = "__EXIT_SESSION__"


class DrillLoadError(Exception):
    pass


def load_json(path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise DrillLoadError(
            f"Malformed JSON in {path}: {error.msg} "
            f"at line {error.lineno}, column {error.colno}"
        ) from error


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)
        file.write("\n")


def progress_key(pack, drill_id):
    return f"{pack}:{drill_id}"


def available_builtin_packs():
    packs = sorted(path.stem for path in DRILLS_DIR.glob("*.json"))
    if OLD_DRILLS_PATH.exists() and DEFAULT_PACK not in packs:
        packs.append(DEFAULT_PACK)
        packs.sort()
    return packs


def available_custom_sets():
    if not CUSTOM_SETS_DIR.exists():
        return []
    return sorted(path.stem for path in CUSTOM_SETS_DIR.glob("*.json"))


def validate_no_name_conflicts():
    builtins = set(available_builtin_packs())
    custom_sets = set(available_custom_sets())
    conflicts = sorted(builtins & custom_sets)
    if conflicts:
        names = ", ".join(conflicts)
        raise DrillLoadError(
            f"Custom set name conflicts with a built-in pack: {names}. "
            "Rename the custom set file."
        )


def format_available_sets():
    sets = available_custom_sets()
    if not sets:
        return "none"
    return ", ".join(sets)


def with_pack(drill, pack):
    item = dict(drill)
    item["_pack"] = pack
    return item


def validate_drills(drills, collection_name, path):
    if not isinstance(drills, list):
        raise DrillLoadError(
            f"{path} must contain a JSON list of drill records."
        )

    seen_ids = set()
    for index, drill in enumerate(drills, start=1):
        if not isinstance(drill, dict):
            raise DrillLoadError(
                f"{path} item {index} must be a JSON object."
            )

        missing = [
            field for field in REQUIRED_DRILL_FIELDS if field not in drill
        ]
        if missing:
            fields = ", ".join(missing)
            raise DrillLoadError(
                f"{path} item {index} is missing required fields: {fields}"
            )

        drill_id = drill["id"]
        if drill_id in seen_ids:
            raise DrillLoadError(
                f"{path} has duplicate drill id in {collection_name}: "
                f"{drill_id}"
            )
        seen_ids.add(drill_id)


def load_pack(pack):
    if pack not in available_builtin_packs():
        available = ", ".join(available_builtin_packs()) or "none"
        raise DrillLoadError(
            f"Unknown built-in pack: {pack}. Available packs: {available}"
        )

    static_path = DRILLS_DIR / f"{pack}.json"
    if pack == DEFAULT_PACK and not static_path.exists():
        static_drills = load_json(OLD_DRILLS_PATH, [])
    else:
        static_drills = load_json(static_path, [])

    generated_path = GENERATED_DIR / f"{pack}_generated.json"
    generated_drills = load_json(generated_path, [])
    validate_drills(static_drills + generated_drills, pack, static_path)

    drills = []
    seen_ids = set()
    for drill in static_drills + generated_drills:
        if drill["id"] in seen_ids:
            continue
        seen_ids.add(drill["id"])
        drills.append(with_pack(drill, pack))
    return drills


def load_custom_set(name):
    validate_no_name_conflicts()
    if name not in available_custom_sets():
        raise DrillLoadError(
            f"Unknown custom set: {name}. "
            f"Available sets: {format_available_sets()}"
        )

    path = CUSTOM_SETS_DIR / f"{name}.json"
    drills = load_json(path, [])
    validate_drills(drills, name, path)
    return [with_pack(drill, name) for drill in drills]


def load_collection(name):
    if name in available_builtin_packs():
        return load_pack(name)
    return load_custom_set(name)


def load_drills(collections=None):
    selected_collections = collections or [DEFAULT_PACK]
    drills = []
    for collection in selected_collections:
        drills.extend(load_collection(collection))
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


class RequiredPromptCollector(ast.NodeVisitor):
    def __init__(self):
        self.identifiers = []
        self.seen_identifiers = set()
        self.literals = []
        self.seen_literals = set()

    def add_identifier(self, name):
        if name is None or name in self.seen_identifiers:
            return
        self.seen_identifiers.add(name)
        self.identifiers.append(name)

    def add_literal(self, value):
        if not isinstance(value, (str, int, float, bool, type(None))):
            return
        key = (type(value), value)
        if key in self.seen_literals:
            return
        self.seen_literals.add(key)
        self.literals.append(value)

    def visit_Name(self, node):
        self.add_identifier(node.id)

    def visit_keyword(self, node):
        self.add_identifier(node.arg)
        self.visit(node.value)

    def visit_Constant(self, node):
        self.add_literal(node.value)


def required_prompt_values(drill):
    try:
        tree = ast.parse(drill["expected"])
    except SyntaxError:
        return [], []

    collector = RequiredPromptCollector()
    collector.visit(tree)
    return collector.identifiers, collector.literals


def required_identifiers(drill):
    identifiers, _ = required_prompt_values(drill)
    return identifiers


def required_literals(drill):
    _, literals = required_prompt_values(drill)
    return literals


def format_literal(value):
    if isinstance(value, str):
        return json.dumps(value)
    return repr(value)


def print_required_prompt_values(drill):
    identifiers, literals = required_prompt_values(drill)
    if identifiers:
        print(f"Required identifiers: {', '.join(identifiers)}")
    if literals:
        formatted = ", ".join(format_literal(value) for value in literals)
        print(f"Required literals: {formatted}")


def current_pattern_streak(pattern_history):
    if not pattern_history:
        return 0

    current_pattern = pattern_history[-1]
    streak = 0
    for pattern in reversed(pattern_history):
        if pattern != current_pattern:
            break
        streak += 1
    return streak


def choose_incomplete_drill(drills, progress, pattern_history=None):
    incomplete = [drill for drill in drills if not is_completed(progress, drill)]
    if not incomplete:
        return None

    candidates = incomplete
    if (
        pattern_history
        and current_pattern_streak(pattern_history) >= MAX_PATTERN_STREAK
    ):
        repeated_pattern = pattern_history[-1]
        varied_candidates = [
            drill
            for drill in incomplete
            if drill["pattern_focus"] != repeated_pattern
        ]
        if varied_candidates:
            candidates = varied_candidates

    return random.choice(candidates)


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


def completed_drills_by_pack(drills, progress):
    by_pack = {}
    for drill in drills:
        if is_completed(progress, drill):
            by_pack.setdefault(drill["_pack"], []).append(drill)
    return by_pack


def choose_recall_drill(drills, progress, pack_queue, drill_queues):
    by_pack = completed_drills_by_pack(drills, progress)
    eligible_packs = set(by_pack)
    if not eligible_packs:
        return None

    pack_queue[:] = [pack for pack in pack_queue if pack in eligible_packs]
    if not pack_queue:
        pack_queue.extend(eligible_packs)
        random.shuffle(pack_queue)

    pack = pack_queue.pop()
    pack_drills = by_pack[pack]
    queue = drill_queues.setdefault(pack, [])
    completed_ids = {drill["id"] for drill in pack_drills}
    queue[:] = [drill for drill in queue if drill["id"] in completed_ids]
    if not queue:
        queue.extend(pack_drills)
        random.shuffle(queue)

    return queue.pop()


def print_context(drill, show_answer):
    print(f"Pack: {drill['_pack']}")
    print(f"Topic: {drill['topic']}")
    print(f"Difficulty: {drill['difficulty']}")
    print(f"Description: {drill['description']}")
    print(f"Pattern focus: {drill['pattern_focus']}")

    if drill["starter_context"]:
        print("Starter context:")
        print(drill["starter_context"])

    print_required_prompt_values(drill)

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


def run_single_attempt_session(drill, progress, show_answer):
    record = get_progress_record(progress, drill["id"], drill["_pack"])

    print_context(drill, show_answer)
    print(f"Wrong attempts: {record['wrong_attempts']}")
    if record["last_wrong"]:
        print("Last wrong:")
        print(record["last_wrong"])
    print()

    answer = read_answer(drill["lines_allowed"])
    if answer == EXIT_SESSION:
        return False

    result = check_answer(
        answer,
        drill["acceptable_answers"],
        drill["lines_allowed"],
    )

    print_result(result)
    if result != "correct":
        record_wrong(progress, drill, answer)
        save_progress(progress)
        return True

    if record["completed_count"] < drill["times_required"]:
        record["completed_count"] += 1
    save_progress(progress)
    return True


def run_drill(show_answer=True, level=None, topic=None, packs=None):
    drills = filter_drills(load_drills(packs), level=level, topic=topic)
    progress = load_progress()
    pattern_history = []

    while True:
        if not should_continue_session():
            return

        drill = choose_incomplete_drill(drills, progress, pattern_history)

        if drill is None:
            print("No matching incomplete drill found.")
            return

        pattern_history.append(drill["pattern_focus"])
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

        if not run_single_attempt_session(drill, progress, show_answer):
            return


def run_recall(packs=None):
    drills = load_drills(packs)
    progress = load_progress()
    pack_queue = []
    drill_queues = {}

    while True:
        if not should_continue_session():
            return

        drill = choose_recall_drill(
            drills,
            progress,
            pack_queue,
            drill_queues,
        )

        if drill is None:
            print("No completed drills yet. Use drill first.")
            return

        print(f"Description: {drill['description']}")
        if drill["starter_context"]:
            print("Starter context:")
            print(drill["starter_context"])
        print_required_prompt_values(drill)

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


def default_drill_collections():
    return [DEFAULT_PACK] + available_custom_sets()


def all_practice_collections():
    return available_builtin_packs() + available_custom_sets()


def resolve_set(name):
    validate_no_name_conflicts()
    if name not in available_custom_sets():
        raise DrillLoadError(
            f"Unknown custom set: {name}. "
            f"Available sets: {format_available_sets()}"
        )
    return [name]


def resolve_drill_collections(args):
    if getattr(args, "set", None):
        return resolve_set(args.set)
    if getattr(args, "all_packs", False):
        return all_practice_collections()
    if getattr(args, "pack", None):
        return [args.pack]
    return default_drill_collections()


def resolve_recall_collections(args):
    if getattr(args, "set", None):
        return resolve_set(args.set)
    if getattr(args, "pack", None):
        return [args.pack]
    return all_practice_collections()


def resolve_focused_collections(args):
    if getattr(args, "set", None):
        return resolve_set(args.set)
    if getattr(args, "all_packs", False):
        return all_practice_collections()
    return [getattr(args, "pack", None) or DEFAULT_PACK]


def add_pack_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--pack",
        choices=available_builtin_packs(),
        help="choose one drill pack",
    )
    group.add_argument(
        "--set",
        metavar="NAME",
        help="choose one custom drill set",
    )
    group.add_argument(
        "--all-packs",
        action="store_true",
        help="include every known drill pack and custom set",
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
        choices=available_builtin_packs(),
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

    try:
        if args.command == "drill":
            run_drill(
                show_answer=not args.hide,
                level=args.level,
                topic=args.topic,
                packs=resolve_drill_collections(args),
            )
        elif args.command == "weak":
            run_weak(
                show_answer=not args.hide,
                level=args.level,
                topic=args.topic,
                packs=resolve_focused_collections(args),
            )
        elif args.command == "recall":
            run_recall(packs=resolve_recall_collections(args))
        elif args.command == "list":
            run_list(packs=resolve_focused_collections(args))
        elif args.command == "generate":
            run_generate(pack=args.pack, limit=args.limit, seed=args.seed)
    except DrillLoadError as error:
        print(f"Error: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
