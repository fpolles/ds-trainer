"""Evaluation engines for FILL_IN_CODE and SQL_CHALLENGE exercises."""
from __future__ import annotations

import importlib
import math
import sqlite3
import threading
from typing import Any

import builtins as _builtins_module

_ALLOWED_BUILTINS = (
    "abs", "all", "any", "bool", "bytes", "callable", "chr",
    "dict", "dir", "divmod", "enumerate", "filter", "float",
    "frozenset", "getattr", "hasattr", "hash", "int", "isinstance",
    "issubclass", "iter", "len", "list", "map", "max", "min",
    "next", "object", "ord", "pow", "print", "range", "repr",
    "reversed", "round", "set", "setattr", "slice", "sorted",
    "str", "sum", "tuple", "type", "zip",
)

# Modules that sandbox code is allowed to import
_ALLOWED_IMPORT_ROOTS = frozenset({
    "collections", "math", "itertools", "functools", "re", "json",
    "datetime", "statistics", "string", "heapq", "bisect", "operator",
    "pandas", "numpy", "scipy", "sklearn",
})


def _safe_import(name: str, globals=None, locals=None, fromlist=(), level: int = 0) -> Any:
    root = name.split(".")[0]
    if root not in _ALLOWED_IMPORT_ROOTS:
        raise ImportError(f"Module '{name}' is not allowed in the sandbox.")
    return importlib.import_module(name)


SAFE_BUILTINS: dict[str, Any] = {
    name: getattr(_builtins_module, name)
    for name in _ALLOWED_BUILTINS
    if hasattr(_builtins_module, name)
}
SAFE_BUILTINS.update({"None": None, "True": True, "False": False, "__import__": _safe_import})


def _resolve_arg(arg: Any) -> Any:
    """Convert special dict markers to real objects (pandas/sklearn)."""
    if not isinstance(arg, dict):
        return arg

    if arg.get("__pandas_df__"):
        import pandas as pd
        data = arg["data"]
        idx = arg.get("index")
        df = pd.DataFrame(data)
        if idx is not None:
            df.index = idx
        return df

    if arg.get("__pandas_series__"):
        import pandas as pd
        values = arg["values"]
        idx = arg.get("index")
        return pd.Series(values, index=idx)

    if arg.get("__sklearn_dataset__"):
        return _load_sklearn(arg["__sklearn_dataset__"])

    return arg


def _load_sklearn(key: str) -> Any:
    from sklearn import datasets
    match key:
        case "breast_cancer_X":
            return datasets.load_breast_cancer(return_X_y=True)[0]
        case "breast_cancer_y":
            return datasets.load_breast_cancer(return_X_y=True)[1]
        case "diabetes_X":
            return datasets.load_diabetes(return_X_y=True)[0]
        case "diabetes_y":
            return datasets.load_diabetes(return_X_y=True)[1]
        case _:
            raise ValueError(f"Unknown sklearn dataset key: {key}")


def _compare(got: Any, expected: Any) -> bool:
    try:
        import numpy as np
        import pandas as pd
        if isinstance(expected, pd.DataFrame):
            if not isinstance(got, pd.DataFrame):
                return False
            try:
                a = got.reset_index(drop=True)
                b = expected.reset_index(drop=True)
                if a.shape != b.shape or list(a.columns) != list(b.columns):
                    return False
                return bool(np.allclose(a.values, b.values, rtol=1e-4, atol=1e-4, equal_nan=True))
            except Exception:
                return got.reset_index(drop=True).equals(expected.reset_index(drop=True))
        if isinstance(expected, pd.Series):
            if not isinstance(got, pd.Series):
                return False
            try:
                a = got.reset_index(drop=True)
                b = expected.reset_index(drop=True)
                if len(a) != len(b):
                    return False
                return bool(np.allclose(a.values, b.values, rtol=1e-4, atol=1e-4, equal_nan=True))
            except Exception:
                return got.reset_index(drop=True).equals(expected.reset_index(drop=True))
    except ImportError:
        pass

    if isinstance(expected, float) or isinstance(got, float):
        try:
            return math.isclose(float(got), float(expected), rel_tol=0.05, abs_tol=0.05)
        except (TypeError, ValueError):
            return False

    if isinstance(expected, tuple) and isinstance(got, tuple):
        if len(got) != len(expected):
            return False
        return all(_compare(g, e) for g, e in zip(got, expected))

    return got == expected


class _TimeoutError(Exception):
    pass


def _run_with_timeout(fn: Any, timeout_seconds: float = 10.0) -> Any:
    result: list[Any] = [None]
    exc: list[BaseException | None] = [None]

    def target() -> None:
        try:
            result[0] = fn()
        except Exception as e:
            exc[0] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout_seconds)
    if t.is_alive():
        raise _TimeoutError(f"Execution timed out after {timeout_seconds}s")
    if exc[0] is not None:
        raise exc[0]  # type: ignore[misc]
    return result[0]


def eval_code(
    user_code: str,
    test_cases: list[dict],
    inject_pandas: bool = False,
) -> tuple[bool, str]:
    """
    Exec user_code in a restricted namespace and run test_cases against it.

    Returns (all_passed, detail_message).
    test_case schema: {"function": str, "args": list, "expected": Any}
    Marker dicts in args/expected are resolved to real objects before calling.
    """
    globs: dict[str, Any] = {"__builtins__": SAFE_BUILTINS}
    if inject_pandas:
        import numpy as np
        import pandas as pd
        globs.update({"pd": pd, "np": np, "DataFrame": pd.DataFrame, "Series": pd.Series})

    # Inject scipy if needed
    for tc in test_cases:
        if "scipy" in user_code:
            try:
                import scipy  # noqa: F401
                from scipy import stats
                globs["stats"] = stats
                from scipy import stats as _stats
                import scipy as _scipy
                globs["scipy"] = _scipy
            except ImportError:
                pass
            break

    try:
        exec(compile(user_code, "<submission>", "exec"), globs)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error during execution: {e}"

    lines: list[str] = []
    all_pass = True

    for tc in test_cases:
        fn_name = tc["function"]
        raw_args = tc["args"]
        raw_expected = tc["expected"]

        resolved_args = [_resolve_arg(a) for a in raw_args]
        resolved_expected = _resolve_arg(raw_expected)

        fn = globs.get(fn_name)
        if fn is None:
            return False, f"Function '{fn_name}' not defined in your code."

        try:
            got = _run_with_timeout(lambda: fn(*resolved_args))
            passed = _compare(got, resolved_expected)
        except _TimeoutError as e:
            return False, str(e)
        except Exception as e:
            lines.append(f"  {fn_name}({raw_args}) → Exception: {e}  [FAIL]")
            all_pass = False
            continue

        status = "PASS" if passed else "FAIL"
        # Avoid printing huge DataFrames in the output
        got_repr = repr(got)[:120]
        exp_repr = repr(resolved_expected)[:120]
        lines.append(f"  {fn_name}(...) → got {got_repr}, expected {exp_repr}  [{status}]")
        if not passed:
            all_pass = False

    return all_pass, "\n".join(lines) if lines else "All test cases passed."


def eval_sql(
    user_query: str,
    expected_query: str,
    schema_ddl: str,
    seed_data: str = "",
) -> tuple[bool, str]:
    """
    Run user_query and expected_query against an in-memory SQLite database.

    Compares result sets as frozensets of tuples (order-independent).
    Returns (correct, detail_message).
    """
    def _make_conn() -> sqlite3.Connection:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_ddl + "\n" + seed_data)
        return conn

    def _run(query: str, conn: sqlite3.Connection) -> list[tuple]:
        return conn.execute(query).fetchall()

    try:
        conn_user = _make_conn()
        user_rows = _run(user_query, conn_user)
        conn_user.close()
    except sqlite3.Error as e:
        return False, f"SQL error in your query: {e}"

    try:
        conn_exp = _make_conn()
        expected_rows = _run(expected_query, conn_exp)
        conn_exp.close()
    except sqlite3.Error as e:
        return False, f"Internal error evaluating expected query: {e}"

    user_set = frozenset(tuple(r) for r in user_rows)
    expected_set = frozenset(tuple(r) for r in expected_rows)

    if user_set == expected_set:
        return True, f"Correct! Result set matches ({len(user_rows)} rows)."

    extra = user_set - expected_set
    missing = expected_set - user_set
    parts: list[str] = [
        f"Result set mismatch (got {len(user_rows)} rows, expected {len(expected_rows)} rows)."
    ]
    if missing:
        parts.append(f"  Missing rows (sample): {list(missing)[:3]}")
    if extra:
        parts.append(f"  Unexpected rows (sample): {list(extra)[:3]}")
    return False, "\n".join(parts)
