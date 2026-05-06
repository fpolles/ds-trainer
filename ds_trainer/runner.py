"""Interactive training session loop."""
from __future__ import annotations

import dataclasses
import os
import random
import time
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ds_trainer.evaluators import eval_code, eval_sql
from ds_trainer.models import (
    ExerciseType,
    Question,
    Session,
    SessionResult,
)

_HINT_LABEL = "[bold cyan]Hint[/bold cyan]"
_CORRECT_STYLE = "bold green"
_WRONG_STYLE = "bold red"


# ── Helpers ────────────────────────────────────────────────────────────────

def _shuffle_choices(q: Question) -> Question:
    """Return a copy of a MULTIPLE_CHOICE question with choices in random order."""
    choices = list(q.choices or [])
    correct_text = choices[q.answer_index or 0]
    random.shuffle(choices)
    return dataclasses.replace(q, choices=choices, answer_index=choices.index(correct_text))


# ── Rendering ──────────────────────────────────────────────────────────────

def _header(q: Question, index: int, total: int) -> str:
    diff_color = {"easy": "green", "medium": "yellow", "hard": "red"}[q.difficulty.value]
    return (
        f"[dim]Question {index}/{total}[/dim]  "
        f"[bold]{q.domain.value.upper()}[/bold]  "
        f"[{diff_color}]{q.difficulty.value}[/{diff_color}]  "
        f"[dim]{q.exercise_type.value}[/dim]"
    )


def render_question(q: Question, index: int, total: int, console: Console) -> None:
    console.print()
    console.rule(_header(q, index, total))

    match q.exercise_type:
        case ExerciseType.MULTIPLE_CHOICE:
            console.print(Panel(q.prompt, title="Question", border_style="blue"))
            letters = "ABCD"
            for i, choice in enumerate(q.choices or []):
                console.print(f"  [bold]{letters[i]})[/bold] {choice}")

        case ExerciseType.FILL_IN_CODE:
            console.print(Panel(q.prompt, title="Task", border_style="blue"))
            if q.code_template:
                console.print(Syntax(q.code_template, "python", theme="monokai", line_numbers=True))
            console.print(
                "[dim]Paste your complete function body below. "
                "Enter a blank line to submit.[/dim]"
            )

        case ExerciseType.EXPLAIN_CONCEPT:
            console.print(Panel(q.prompt, title="Concept Question", border_style="blue"))
            console.print("[dim]Write your answer below. Enter a blank line to submit.[/dim]")

        case ExerciseType.SQL_CHALLENGE:
            console.print(Panel(q.prompt, title="SQL Challenge", border_style="blue"))
            if q.schema_ddl:
                console.print("[bold]Schema:[/bold]")
                console.print(Syntax(q.schema_ddl.strip(), "sql", theme="monokai"))
            console.print(
                "[dim]Write your SQL query below. Enter a blank line to submit.[/dim]"
            )

        case ExerciseType.TAKE_HOME:
            console.print(Panel(q.prompt, title="Take-Home Project", border_style="magenta"))
            _setup_take_home(q, console)


def _setup_take_home(q: Question, console: Console) -> None:
    from ds_trainer.data.generators import generate
    project_dir = Path(f"ds_trainer_project_{q.id}")
    try:
        csv_path = generate(q.dataset_generator or "", project_dir)
        console.print(
            f"\n[green]Dataset saved to:[/green] [bold]{csv_path}[/bold]"
        )
    except Exception as e:
        console.print(f"[yellow]Warning: could not generate dataset: {e}[/yellow]")

    if q.project_spec:
        console.print(Panel(Markdown(q.project_spec), title="Project Specification", border_style="magenta"))
    console.print(
        "\n[dim]Work on the project in your editor/notebook. "
        "Press Enter when done to see the model solution.[/dim]"
    )


# ── Input helpers ──────────────────────────────────────────────────────────

def _read_multiline(console: Console, prompt: str = ">>> ") -> str:
    console.print(f"[dim]{prompt}[/dim]", end="")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def _inject_pandas_needed(q: Question) -> bool:
    return q.domain.value == "python" or any(
        "pandas" in str(tc.get("args", "")) or "DataFrame" in str(tc.get("args", ""))
        for tc in (q.test_cases or [])
    )


# ── Evaluation ─────────────────────────────────────────────────────────────

def evaluate(q: Question, user_answer: str) -> tuple[bool, str]:
    match q.exercise_type:
        case ExerciseType.MULTIPLE_CHOICE:
            letters = "ABCD"
            normalized = user_answer.strip().upper()
            if normalized in letters:
                idx = letters.index(normalized)
            elif normalized.isdigit():
                idx = int(normalized) - 1
            else:
                return False, f"Invalid answer '{user_answer}'. Enter A/B/C/D."
            correct = idx == q.answer_index
            chosen = (q.choices or [])[idx] if 0 <= idx < len(q.choices or []) else "?"
            if correct:
                return True, f"Correct! You chose [bold]{normalized}) {chosen}[/bold]."
            right_letter = letters[q.answer_index or 0]
            right_text = (q.choices or [])[q.answer_index or 0]
            return False, f"Incorrect. Answer was [bold]{right_letter}) {right_text}[/bold]."

        case ExerciseType.FILL_IN_CODE:
            if not q.test_cases:
                return True, "No automated tests — check the model answer yourself."
            inject = _inject_pandas_needed(q)
            code = user_answer
            if q.code_template:
                # Prepend imports from template if user didn't include them
                imports = [
                    ln for ln in q.code_template.splitlines()
                    if ln.startswith("import ") or ln.startswith("from ")
                ]
                if imports and not any(
                    ln in code for ln in imports
                ):
                    code = "\n".join(imports) + "\n\n" + code
            passed, detail = eval_code(code, q.test_cases, inject_pandas=inject)
            return passed, detail

        case ExerciseType.SQL_CHALLENGE:
            if not q.schema_ddl or not q.expected_query:
                return True, "Cannot auto-evaluate — check the model answer."
            return eval_sql(
                user_answer,
                q.expected_query,
                q.schema_ddl,
                q.seed_data or "",
            )

        case ExerciseType.EXPLAIN_CONCEPT | ExerciseType.TAKE_HOME:
            # Self-graded: always show model answer
            return True, "Self-graded — compare your answer to the model answer below."

        case _:
            return False, "Unknown exercise type."


# ── Session ────────────────────────────────────────────────────────────────

def run_session(questions: list[Question], console: Console) -> Session:
    session = Session()
    total = len(questions)

    console.print(
        Panel(
            f"[bold]Starting session[/bold]  [dim]id={session.id}[/dim]\n"
            f"{total} question(s)  •  [cyan]h[/cyan]=hint  "
            f"[yellow]s[/yellow]=skip  [red]q[/red]=quit",
            border_style="dim",
        )
    )

    for idx, q in enumerate(questions, 1):
        if q.exercise_type == ExerciseType.MULTIPLE_CHOICE:
            q = _shuffle_choices(q)
        render_question(q, idx, total, console)
        hints_used = 0
        start = time.monotonic()
        user_answer = ""
        correct = False

        is_multiline = q.exercise_type in (
            ExerciseType.FILL_IN_CODE,
            ExerciseType.SQL_CHALLENGE,
            ExerciseType.EXPLAIN_CONCEPT,
        )
        is_take_home = q.exercise_type == ExerciseType.TAKE_HOME

        while True:
            if is_take_home:
                input()
                user_answer = "(take-home)"
                correct = True
                detail = "Self-graded — compare your work to the model answer."
                break

            if is_multiline:
                user_input = _read_multiline(console)
            else:
                user_input = Prompt.ask(
                    "\n[bold]Answer[/bold] (or [cyan]h[/cyan]/[yellow]s[/yellow]/[red]q[/red])"
                ).strip()

            match user_input.lower():
                case "h" | "hint":
                    if q.hints and hints_used < len(q.hints):
                        console.print(f"{_HINT_LABEL}: {q.hints[hints_used]}")
                        hints_used += 1
                    else:
                        console.print("[dim]No more hints available.[/dim]")
                    continue

                case "s" | "skip":
                    user_answer = "(skipped)"
                    correct = False
                    detail = "Skipped."
                    break

                case "q" | "quit":
                    console.print("[dim]Session ended early.[/dim]")
                    session.results.append(
                        SessionResult(
                            question_id=q.id,
                            correct=False,
                            hints_used=hints_used,
                            time_seconds=time.monotonic() - start,
                            user_answer="(quit)",
                        )
                    )
                    show_summary(session, console)
                    return session

                case _:
                    user_answer = user_input
                    correct, detail = evaluate(q, user_answer)
                    break

        elapsed = time.monotonic() - start

        # Result feedback
        if q.exercise_type in (ExerciseType.EXPLAIN_CONCEPT, ExerciseType.TAKE_HOME):
            console.print(f"\n[dim]{detail}[/dim]")
        elif correct:
            console.print(f"\n[{_CORRECT_STYLE}]✓ {detail}[/{_CORRECT_STYLE}]")
        else:
            console.print(f"\n[{_WRONG_STYLE}]✗ {detail}[/{_WRONG_STYLE}]")

        # Model answer / explanation
        console.print()
        if q.model_answer:
            console.print(
                Panel(
                    Syntax(q.model_answer, "python", theme="monokai")
                    if q.exercise_type == ExerciseType.FILL_IN_CODE
                    else q.model_answer,
                    title="[bold]Model Answer[/bold]",
                    border_style="green",
                )
            )
        if q.exercise_type == ExerciseType.SQL_CHALLENGE and q.expected_query:
            console.print(
                Panel(
                    Syntax(q.expected_query, "sql", theme="monokai", word_wrap=True),
                    title="[bold]Expected SQL[/bold]",
                    border_style="green",
                )
            )
        if q.explanation:
            console.print(
                Panel(q.explanation, title="[bold]Explanation[/bold]", border_style="dim")
            )

        session.results.append(
            SessionResult(
                question_id=q.id,
                correct=correct,
                hints_used=hints_used,
                time_seconds=elapsed,
                user_answer=user_answer[:200],
            )
        )

        if idx < total:
            Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="", show_default=False)

    show_summary(session, console)
    return session


# ── Summary ────────────────────────────────────────────────────────────────

def show_summary(session: Session, console: Console) -> None:
    console.print()
    console.rule("[bold]Session Summary[/bold]")

    score_pct = session.score * 100
    score_color = "green" if score_pct >= 70 else "yellow" if score_pct >= 50 else "red"

    table = Table(title="Results", show_header=True, header_style="bold")
    table.add_column("Question", style="dim")
    table.add_column("Result", justify="center")
    table.add_column("Hints", justify="right")
    table.add_column("Time (s)", justify="right")

    for r in session.results:
        result_text = Text("✓", style="green") if r.correct else Text("✗", style="red")
        table.add_row(
            r.question_id,
            result_text,
            str(r.hints_used),
            f"{r.time_seconds:.1f}",
        )

    console.print(table)
    console.print(
        f"\n[bold]Score:[/bold] [{score_color}]{session.correct_count}/{len(session.results)} "
        f"({score_pct:.0f}%)[/{score_color}]"
    )

    match True:
        case _ if score_pct >= 90:
            console.print("[green]Excellent work! You're well-prepared.[/green]")
        case _ if score_pct >= 70:
            console.print("[yellow]Good job! Review the missed questions.[/yellow]")
        case _ if score_pct >= 50:
            console.print("[yellow]Keep practicing — focus on the areas you missed.[/yellow]")
        case _:
            console.print("[red]Keep going — repetition is key. Try easier questions first.[/red]")
