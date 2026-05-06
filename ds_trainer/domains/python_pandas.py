from ds_trainer.models import Difficulty, Domain, ExerciseType, Question

QUESTIONS: list[Question] = [
    # ── Easy ──────────────────────────────────────────────────────────────
    Question(
        id="py_e_001",
        domain=Domain.PYTHON,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt="What does `df.loc[df['score'] > 80, 'grade']` return?",
        choices=[
            "All rows where score > 80, all columns",
            "The 'grade' column for rows where score > 80",
            "A boolean mask of shape (n,)",
            "Raises a KeyError",
        ],
        answer_index=1,
        explanation=(
            "df.loc[row_mask, column_label] selects a subset of rows (using the boolean mask) "
            "and a specific column. The result is a Series."
        ),
        hints=["df.loc takes [row_selector, column_selector]."],
        tags=["pandas", "indexing"],
    ),
    Question(
        id="py_e_002",
        domain=Domain.PYTHON,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that returns the percentage of missing values "
            "for each column in a DataFrame, sorted descending."
        ),
        code_template="""\
import pandas as pd

def missing_pct(df: pd.DataFrame) -> pd.Series:
    \"\"\"Return % missing per column, sorted descending (0-100 scale).\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
import pandas as pd

def missing_pct(df: pd.DataFrame) -> pd.Series:
    return (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
""",
        test_cases=[
            {
                "function": "missing_pct",
                "args": [
                    {"__pandas_df__": True,
                     "data": {"a": [1, None, 3], "b": [None, None, None], "c": [1, 2, 3]}}
                ],
                "expected": {"__pandas_series__": True,
                             "values": [100.0, 33.333333333333336, 0.0],
                             "index": ["b", "a", "c"]},
            }
        ],
        explanation=(
            "df.isnull().sum() counts NaN per column. Dividing by len(df) and multiplying "
            "by 100 gives percentage. sort_values(ascending=False) puts worst columns first."
        ),
        hints=[
            "df.isnull() returns a boolean DataFrame.",
            ".sum() collapses rows, giving count of NaN per column.",
        ],
        tags=["pandas", "missing-data"],
    ),
    Question(
        id="py_e_003",
        domain=Domain.PYTHON,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "Which pandas method removes duplicate rows, keeping the first occurrence by default?"
        ),
        choices=["df.drop_duplicates()", "df.unique()", "df.nunique()", "df.duplicated()"],
        answer_index=0,
        explanation=(
            "drop_duplicates() removes duplicate rows (default keep='first'). "
            "duplicated() returns a boolean mask — it marks duplicates but doesn't remove them. "
            "unique() and nunique() operate on Series, not DataFrames."
        ),
        hints=["One of these returns a boolean mask; another actually drops rows."],
        tags=["pandas", "deduplication"],
    ),
    # ── Medium ─────────────────────────────────────────────────────────────
    Question(
        id="py_m_001",
        domain=Domain.PYTHON,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that returns the top-N rows per group by a value column, "
            "using pandas groupby."
        ),
        code_template="""\
import pandas as pd

def top_n_per_group(df: pd.DataFrame, group_col: str, value_col: str, n: int) -> pd.DataFrame:
    \"\"\"Return the top n rows per group_col, ranked by value_col descending.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
import pandas as pd

def top_n_per_group(df: pd.DataFrame, group_col: str, value_col: str, n: int) -> pd.DataFrame:
    return (
        df.sort_values(value_col, ascending=False)
          .groupby(group_col, group_keys=False)
          .head(n)
          .reset_index(drop=True)
    )
""",
        test_cases=[
            {
                "function": "top_n_per_group",
                "args": [
                    {"__pandas_df__": True,
                     "data": {
                         "dept": ["A", "A", "A", "B", "B"],
                         "salary": [100, 200, 150, 80, 90],
                     }},
                    "dept", "salary", 2,
                ],
                "expected": {"__pandas_df__": True,
                             "data": {"dept": ["A", "A", "B", "B"],
                                      "salary": [200, 150, 90, 80]}},
            }
        ],
        explanation=(
            "Sort descending by value, then groupby + head(n) takes the top n per group. "
            "reset_index(drop=True) gives a clean index."
        ),
        hints=[
            "sort_values before groupby so head(n) picks the highest values.",
            "groupby(..., group_keys=False).head(n) is the idiomatic pandas pattern.",
        ],
        tags=["pandas", "groupby", "top-n"],
    ),
    Question(
        id="py_m_002",
        domain=Domain.PYTHON,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that fills missing numeric values with the column median "
            "and missing categorical (object dtype) values with the column mode."
        ),
        code_template="""\
import pandas as pd

def smart_fill(df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"Return a copy with NaN filled: numeric → median, object → mode.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
import pandas as pd

def smart_fill(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna(df[col].mode()[0])
        else:
            df[col] = df[col].fillna(df[col].median())
    return df
""",
        test_cases=[
            {
                "function": "smart_fill",
                "args": [
                    {"__pandas_df__": True,
                     "data": {"age": [25.0, None, 30.0, 35.0], "city": ["NY", None, "LA", "NY"]}}
                ],
                "expected": {"__pandas_df__": True,
                             "data": {"age": [25.0, 30.0, 30.0, 35.0],
                                      "city": ["NY", "NY", "LA", "NY"]}},
            }
        ],
        explanation=(
            "Iterate columns: check dtype to pick the fill strategy. "
            "mode()[0] takes the first mode if there are ties."
        ),
        hints=[
            "df[col].dtype == 'object' identifies string/categorical columns.",
            "df[col].fillna(df[col].median()) for numeric.",
        ],
        tags=["pandas", "missing-data", "imputation"],
    ),
    Question(
        id="py_m_003",
        domain=Domain.PYTHON,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "You call df.groupby('dept')['salary'].transform('mean'). What does this return?"
        ),
        choices=[
            "A DataFrame with one row per department and its mean salary",
            "A Series of the same length as df, with each row replaced by its dept's mean salary",
            "A single scalar: the overall mean salary",
            "A Series with department names as index and mean salaries as values",
        ],
        answer_index=1,
        explanation=(
            "transform() broadcasts the group result back to the original DataFrame shape. "
            "Every row gets the mean salary of its department — useful for creating new features "
            "like 'salary relative to dept average'."
        ),
        hints=["transform keeps the original index/shape, unlike agg."],
        tags=["pandas", "groupby", "transform"],
    ),
    Question(
        id="py_m_004",
        domain=Domain.PYTHON,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain the difference between df.apply() and df.map() (element-wise) "
            "in pandas. When would you use each?"
        ),
        model_answer=(
            "apply() operates on an axis — either row-by-row (axis=1) or column-by-column (axis=0). "
            "It passes each row/column as a Series to the function, making it suitable for "
            "operations that need multiple values at once (e.g., row sum, custom aggregation).\n\n"
            "DataFrame.map() / applymap() (deprecated in pandas 2.1+) operates element-by-element, "
            "passing each scalar value independently. Use it for simple transformations on every cell "
            "(e.g., stripping whitespace, formatting numbers).\n\n"
            "Rule of thumb: if your function works on one cell at a time → df.map(). "
            "If it needs the whole row or column → apply().\n\n"
            "Performance note: both are slower than vectorized operations (df * 2, df['col'].str.strip()). "
            "Prefer vectorized where possible."
        ),
        explanation=(
            "apply() is axis-aware (row or column); map() is element-wise. "
            "Vectorized operations (df * 2, df.str.strip()) are faster than both."
        ),
        hints=[
            "Think about whether the function needs one value or a whole row/column.",
        ],
        tags=["pandas", "apply"],
    ),
    # ── Hard ───────────────────────────────────────────────────────────────
    Question(
        id="py_h_001",
        domain=Domain.PYTHON,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that reads a large CSV in chunks and returns a DataFrame "
            "with the sum of 'revenue' grouped by 'region', aggregated across all chunks."
        ),
        code_template="""\
import pandas as pd

def aggregate_large_csv(filepath: str, chunksize: int = 10_000) -> pd.DataFrame:
    \"\"\"Read filepath in chunks; return total revenue per region as a DataFrame
    with columns ['region', 'revenue'].
    \"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
import pandas as pd

def aggregate_large_csv(filepath: str, chunksize: int = 10_000) -> pd.DataFrame:
    accum = []
    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        accum.append(chunk.groupby('region')['revenue'].sum())
    combined = pd.concat(accum)
    result = combined.groupby(level=0).sum().reset_index()
    result.columns = ['region', 'revenue']
    return result
""",
        explanation=(
            "Chunked reading avoids loading the whole file into RAM. "
            "Aggregate each chunk, collect partial results, then concat + re-aggregate."
        ),
        hints=[
            "pd.read_csv(filepath, chunksize=N) returns an iterator of DataFrames.",
            "Aggregate each chunk, then concat all partial results and aggregate again.",
        ],
        tags=["pandas", "chunked-reading", "memory-efficiency"],
    ),
    Question(
        id="py_h_002",
        domain=Domain.PYTHON,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that pivots a long-format DataFrame to wide format, "
            "then computes a month-over-month percentage change per product."
        ),
        code_template="""\
import pandas as pd

def mom_change(df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"
    df has columns: product, month (str 'YYYY-MM'), revenue.
    Return a DataFrame: rows=products, cols=months, values=MoM % change.
    First month column will be NaN (no prior month).
    \"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
import pandas as pd

def mom_change(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot_table(index='product', columns='month', values='revenue', aggfunc='sum')
    pivot.columns.name = None
    return pivot.pct_change(axis=1) * 100
""",
        test_cases=[
            {
                "function": "mom_change",
                "args": [
                    {"__pandas_df__": True,
                     "data": {
                         "product": ["A", "A", "A", "B", "B", "B"],
                         "month":   ["2024-01", "2024-02", "2024-03",
                                     "2024-01", "2024-02", "2024-03"],
                         "revenue": [100.0, 110.0, 121.0, 200.0, 180.0, 198.0],
                     }}
                ],
                "expected": {"__pandas_df__": True,
                             "data": {
                                 "2024-01": [float("nan"), float("nan")],
                                 "2024-02": [10.0, -10.0],
                                 "2024-03": [10.0, 10.0],
                             }},
            }
        ],
        explanation=(
            "pivot_table reshapes long→wide. pct_change(axis=1) computes period-over-period "
            "change along columns. Multiply by 100 for percentage."
        ),
        hints=[
            "df.pivot_table(index='product', columns='month', values='revenue') reshapes the data.",
            "pct_change(axis=1) works along columns (time axis).",
        ],
        tags=["pandas", "pivot", "time-series"],
    ),
    Question(
        id="py_h_003",
        domain=Domain.PYTHON,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain the pandas MultiIndex. When is it useful, and what are two common ways "
            "to create one from a DataFrame?"
        ),
        model_answer=(
            "A MultiIndex (hierarchical index) allows a DataFrame to be indexed by multiple "
            "levels, enabling efficient grouping and slicing across dimensions.\n\n"
            "It's useful when data has natural hierarchies: (country, city), (year, month), "
            "(company, product). Operations like df.loc[('US', 'NY')] become intuitive.\n\n"
            "Two common ways to create one:\n"
            "1. df.set_index(['col_a', 'col_b']) — promotes columns to index levels.\n"
            "2. df.groupby(['col_a', 'col_b']).agg(...) — groupby naturally produces a MultiIndex.\n\n"
            "Access with .loc[('level0_val', 'level1_val')] or .xs(val, level='name'). "
            "Use .reset_index() to flatten back to a regular DataFrame."
        ),
        explanation="MultiIndex enables hierarchical indexing and efficient cross-section queries.",
        hints=[
            "Think about data with multiple grouping dimensions.",
            "set_index and groupby both produce MultiIndex results.",
        ],
        tags=["pandas", "multiindex"],
    ),
]
