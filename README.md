# ds-trainer

Practice data scientist technical assessments — fully offline.

---

## Quick start

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install (editable, so you can add your own questions later)
pip install -e .

# 3. Run a default 5-question session across all domains
ds-trainer train

# 4. Focus on what you need
ds-trainer train --domain sql --difficulty hard --count 3
ds-trainer train --type fill_in_code --domain python
```

> **No install?** If you skip `pip install -e .`, you can still run the tool from inside the `logic` directory using:
> ```bash
> python -m ds_trainer train
> ```
> Note: the dependencies (`rich`, `pandas`, `numpy`) must still be installed for this to work.

---

## Visual Web App

You can also practice and manage questions using the interactive visual web application.

```bash
# Start the FastAPI web server
uv run python web/main.py
```

Then navigate to `http://127.0.0.1:8000` in your browser. 

From the web UI, you can:
- **Configure Training Sessions**: Select your domain, difficulty, and question types.
- **Interactive Practice**: Write code and SQL with syntax highlighting, and instantly grade your solutions against the test cases.
- **Database Management**: From the bottom of the Setup View, you can access tools to manage the database:
  - **Add Question**: Opens a form to securely evaluate and add new custom questions directly to the SQLite database (`ds_trainer/questions.db`). IDs are generated automatically!
  - **Reset Database**: Wipes all custom questions and safely restores the database back to its original core question set.

---

## What it covers

Companies that hire data scientists typically test these areas:

| Domain | Topics covered |
|---|---|
| **SQL** | JOINs, aggregations, HAVING, window functions (RANK, ROW_NUMBER, moving average), CTEs, correlated subqueries |
| **Python / Pandas** | Boolean indexing, missing data imputation, `groupby`/`transform`, rolling windows, `pivot_table`, MultiIndex |
| **Statistics** | p-values, CLT, A/B test design, two-sample t-test, multiple comparisons, bootstrap CI, bias-variance tradeoff |
| **ML** | Overfitting, class imbalance, cross-validation, feature importance, gradient boosting, Ridge + GridSearchCV, data leakage |
| **Algorithms** | Two-sum, sliding window, binary search, group anagrams, max profit (single pass) |
| **Case Studies** | North Star metric, DAU drops, funnel analysis, churn prediction lifecycle, RFM segmentation, cold-start |
| **Probability** | Bayes' theorem, base-rate fallacy, expected value, independence, Monty Hall, birthday problem, Markov chains, law of total expectation |

**Difficulty levels:** easy / medium / hard (filter with `--difficulty`)

---

## Exercise types

| Type | How to answer |
|---|---|
| `multiple_choice` | Type a letter: `A`, `B`, `C`, or `D` |
| `fill_in_code` | Paste a complete function body; submit with a blank line |
| `sql_challenge` | Write a SQL query; submit with a blank line |
| `explain_concept` | Write your answer in plain text; submit with a blank line |
| `take_home` | A dataset CSV is generated locally; work in your editor, press Enter when done |

Python code and SQL queries are evaluated automatically. Concept questions and take-home projects are self-graded — compare your answer to the model solution shown after you submit.

---

## Navigation keys

During any session:

| Key | Action |
|---|---|
| `h` | Show the next available hint |
| `s` | Skip this question (counts as wrong) |
| `q` | Quit the session early (summary is still shown) |

---

## Full CLI reference

```
ds-trainer train   [--domain DOMAIN] [--difficulty LEVEL] [--type TYPE]
                   [--count N] [--no-shuffle]
ds-trainer list    [--domain DOMAIN] [--difficulty LEVEL] [--type TYPE]
ds-trainer stats
ds-trainer --version
```

**Options:**

| Flag | Values | Default |
|---|---|---|
| `--domain`, `-d` | `sql` `python` `statistics` `ml` `algorithms` `case_studies` `probability` `all` | `all` |
| `--difficulty`, `-l` | `easy` `medium` `hard` `all` | `all` |
| `--type`, `-t` | `multiple_choice` `fill_in_code` `explain_concept` `sql_challenge` `take_home` `all` | `all` |
| `--count`, `-n` | integer | `5` |
| `--no-shuffle` | flag | (shuffle by default) |

**Examples:**

```bash
# See what questions are available before committing
ds-trainer list --domain ml --difficulty medium

# Check how many questions exist per domain × difficulty
ds-trainer stats

# Pure coding interview prep
ds-trainer train --type fill_in_code --count 10

# SQL-only hard grind
ds-trainer train --domain sql --difficulty hard --no-shuffle
```

---

## Architecture

```
ds_trainer/
├── cli.py           # argparse entry point; dispatches train / list / stats
├── models.py        # Question, Session, SessionResult dataclasses + enums
├── registry.py      # load_all(), filter_questions(), sample_questions()
├── runner.py        # interactive loop, render_question(), evaluate(), show_summary()
├── evaluators.py    # eval_code() and eval_sql() — sandboxed execution engines
├── domains/
│   ├── sql.py           # 12 questions
│   ├── python_pandas.py # 10 questions
│   ├── statistics.py    # 10 questions
│   ├── ml.py            # 10 questions
│   ├── algorithms.py    # 8 questions
│   └── case_studies.py  # 9 questions
└── data/
    └── generators.py    # CSV dataset generators for take-home exercises
```

**Key design decisions:**

- **Single flat `Question` dataclass** — no inheritance hierarchy; the `ExerciseType` enum carries the type tag and `__post_init__` validates required fields per type via `match/case`.
- **Sandboxed code execution** — `eval_code` uses `exec()` with a whitelist of ~30 safe builtins (no `open`, no `__import__`). A `threading.Thread` with a 10-second timeout prevents infinite loops.
- **In-memory SQLite** — `eval_sql` runs both the user query and the model answer against a fresh `sqlite3.connect(":memory:")` and compares result sets as `frozenset[tuple]` (order-independent).
- **Marker dicts** — pandas DataFrames and sklearn arrays in test cases are stored as serialisable dicts (`{"__pandas_df__": True, "data": {...}}`) and resolved to real objects just before evaluation.
- **SQLite Database** — questions are stored in `ds_trainer/questions.db` making it fully portable and easy to query or extend.

---

## Development setup

```bash
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=ds_trainer --cov-report=term-missing
```

Python 3.10+ required (uses `match/case` throughout).

---

## Contributing questions

The easiest way to add new questions is through the **Visual Web App**:
1. Run `uv run python web/main.py` and open `http://127.0.0.1:8000`.
2. In the Database Management section at the bottom of the setup screen, click **Add Question**.
3. Fill out the fields. The Question ID will be automatically generated.
4. Click **Test Question**. This runs your model answer against your test cases (or schema) to ensure it is valid.
5. Once the test passes, click **Add to Database** to save it to `ds_trainer/questions.db`.

For **FILL_IN_CODE** questions, always include `test_cases` so the answer can be auto-evaluated. The `model_answer` field is shown to the user after they submit and is also used by the test suite to verify correctness.

For **TAKE_HOME** questions, add a generator to `ds_trainer/data/generators.py` decorated with `@register("your_key")` and reference it via `dataset_generator="your_key"`.

---

## License

MIT
