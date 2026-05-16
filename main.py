import ast
import argparse
import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).parent
DRILLS_PATH = BASE_DIR / "data" / "drills.json"
PROGRESS_PATH = BASE_DIR / "data" / "progress.json"
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


def load_drills():
    return load_json(DRILLS_PATH, [])


def load_progress():
    return load_json(PROGRESS_PATH, {})


def save_progress(progress):
    save_json(PROGRESS_PATH, progress)


def get_progress_record(progress, drill_id):
    record = progress.setdefault(drill_id, {})
    record.setdefault("completed_count", 0)
    record.setdefault("wrong_attempts", 0)
    record.setdefault("last_wrong", "")
    return record


def completed_count(progress, drill_id):
    return int(get_progress_record(progress, drill_id)["completed_count"])


def wrong_attempts(progress, drill_id):
    return int(get_progress_record(progress, drill_id)["wrong_attempts"])


def record_correct(progress, drill_id):
    record = get_progress_record(progress, drill_id)
    record["completed_count"] += 1


def record_wrong(progress, drill_id, answer):
    record = get_progress_record(progress, drill_id)
    record["wrong_attempts"] += 1
    record["last_wrong"] = answer.strip()


def is_completed(progress, drill):
    return completed_count(progress, drill["id"]) >= drill["times_required"]


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
        if wrong_attempts(progress, drill["id"]) > 0
        and not is_completed(progress, drill)
    ]
    if not weak_drills:
        return None

    highest_wrong = max(
        wrong_attempts(progress, drill["id"]) for drill in weak_drills
    )
    most_wrong = [
        drill
        for drill in weak_drills
        if wrong_attempts(progress, drill["id"]) == highest_wrong
    ]
    return random.choice(most_wrong)


def choose_completed_drill(drills, progress):
    completed = [drill for drill in drills if is_completed(progress, drill)]
    if not completed:
        return None
    return random.choice(completed)


def print_context(drill, show_answer):
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
    drill_id = drill["id"]
    count = completed_count(progress, drill_id)
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
            record_wrong(progress, drill_id, answer)
            save_progress(progress)
            print_result(result)
            continue

        print_result(result)
        record_correct(progress, drill_id)
        save_progress(progress)
        count = completed_count(progress, drill_id)
        print(f"Progress: {count} / {required}")

    print("Drill completed")
    return True


def run_drill(show_answer=True, level=None, topic=None):
    drills = filter_drills(load_drills(), level=level, topic=topic)
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


def run_weak(show_answer=True, level=None, topic=None):
    drills = filter_drills(load_drills(), level=level, topic=topic)
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


def run_recall():
    drills = load_drills()
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
            record_wrong(progress, drill["id"], answer)
            save_progress(progress)

        print("Expected:")
        print(drill["expected"])


def run_list():
    drills = load_drills()
    progress = load_progress()

    for drill in drills:
        drill_id = drill["id"]
        count = completed_count(progress, drill["id"])
        required = drill["times_required"]
        print(
            f"{drill_id} | {drill['topic']} | {drill['difficulty']} | "
            f"{count}/{required} | wrong: {wrong_attempts(progress, drill_id)} | "
            f"lines: {drill['lines_allowed']}"
        )


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

    subparsers.add_parser("recall")
    subparsers.add_parser("list")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "drill":
        run_drill(
            show_answer=not args.hide,
            level=args.level,
            topic=args.topic,
        )
    elif args.command == "weak":
        run_weak(
            show_answer=not args.hide,
            level=args.level,
            topic=args.topic,
        )
    elif args.command == "recall":
        run_recall()
    elif args.command == "list":
        run_list()


if __name__ == "__main__":
    main()
