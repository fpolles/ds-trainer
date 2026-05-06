"""CLI entry point for ds-trainer."""
from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.table import Table

from ds_trainer import __version__

_DOMAINS = ["sql", "python", "statistics", "ml", "algorithms", "case_studies", "probability", "all"]
_DIFFICULTIES = ["easy", "medium", "hard", "all"]
_TYPES = [
    "multiple_choice", "fill_in_code", "explain_concept",
    "sql_challenge", "take_home", "all",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ds-trainer",
        description="Practice data scientist technical assessments — fully offline.",
    )
    parser.add_argument("--version", action="version", version=f"ds-trainer {__version__}")

    sub = parser.add_subparsers(dest="command")

    # ── train ──────────────────────────────────────────────────────────────
    train = sub.add_parser("train", help="Start an interactive training session (default)")
    _add_filter_args(train)
    train.add_argument(
        "--count", "-n", type=int, default=5,
        help="Number of questions to attempt (default: 5)",
    )
    train.add_argument(
        "--no-shuffle", action="store_true",
        help="Present questions in definition order instead of random",
    )

    # ── list ───────────────────────────────────────────────────────────────
    lst = sub.add_parser("list", help="List questions matching the given filters")
    _add_filter_args(lst)

    # ── stats ──────────────────────────────────────────────────────────────
    sub.add_parser("stats", help="Show question bank statistics")

    return parser


def _add_filter_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--domain", "-d", choices=_DOMAINS, default="all",
        help="Domain to focus on (default: all)",
    )
    p.add_argument(
        "--difficulty", "-l", choices=_DIFFICULTIES, default="all",
        help="Difficulty level (default: all)",
    )
    p.add_argument(
        "--type", "-t", dest="exercise_type", choices=_TYPES, default="all",
        help="Exercise type (default: all)",
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    match args.command:
        case "train" | None:
            _cmd_train(args, console)
        case "list":
            _cmd_list(args, console)
        case "stats":
            _cmd_stats(console)
        case _:
            parser.print_help()


# ── Commands ───────────────────────────────────────────────────────────────

def _cmd_train(args: argparse.Namespace, console: Console) -> None:
    from ds_trainer.registry import filter_questions, load_all, sample_questions
    from ds_trainer.runner import run_session

    all_qs = load_all()
    domain = getattr(args, "domain", "all")
    difficulty = getattr(args, "difficulty", "all")
    exercise_type = getattr(args, "exercise_type", "all")
    count = getattr(args, "count", 5)
    shuffle = not getattr(args, "no_shuffle", False)

    filtered = filter_questions(all_qs, domain, difficulty, exercise_type)

    if not filtered:
        console.print(
            f"[red]No questions found for domain={domain}, "
            f"difficulty={difficulty}, type={exercise_type}.[/red]"
        )
        sys.exit(1)

    selected = sample_questions(filtered, count, shuffle=shuffle)
    run_session(selected, console)


def _cmd_list(args: argparse.Namespace, console: Console) -> None:
    from ds_trainer.registry import filter_questions, load_all

    all_qs = load_all()
    filtered = filter_questions(
        all_qs,
        getattr(args, "domain", "all"),
        getattr(args, "difficulty", "all"),
        getattr(args, "exercise_type", "all"),
    )

    table = Table(title=f"Questions ({len(filtered)} found)", show_header=True)
    table.add_column("ID", style="dim")
    table.add_column("Domain")
    table.add_column("Difficulty")
    table.add_column("Type")
    table.add_column("Prompt (truncated)")

    for q in filtered:
        diff_color = {"easy": "green", "medium": "yellow", "hard": "red"}[q.difficulty.value]
        table.add_row(
            q.id,
            q.domain.value,
            f"[{diff_color}]{q.difficulty.value}[/{diff_color}]",
            q.exercise_type.value,
            q.prompt[:70] + ("…" if len(q.prompt) > 70 else ""),
        )

    console.print(table)


def _cmd_stats(console: Console) -> None:
    from ds_trainer.registry import load_all, stats_table

    all_qs = load_all()
    tbl = stats_table(all_qs)

    table = Table(title=f"Question Bank  ({len(all_qs)} total)", show_header=True)
    table.add_column("Domain", style="bold")
    table.add_column("Easy", justify="right", style="green")
    table.add_column("Medium", justify="right", style="yellow")
    table.add_column("Hard", justify="right", style="red")
    table.add_column("Total", justify="right")

    domain_order = ["sql", "python", "statistics", "ml", "algorithms", "case_studies", "probability"]
    for domain in domain_order:
        counts = tbl.get(domain, {})
        easy = counts.get("easy", 0)
        medium = counts.get("medium", 0)
        hard = counts.get("hard", 0)
        table.add_row(domain, str(easy), str(medium), str(hard), str(easy + medium + hard))

    console.print(table)
