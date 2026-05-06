"""Tests for evaluators.py — eval_code and eval_sql."""
from __future__ import annotations

import pytest

from ds_trainer.evaluators import SAFE_BUILTINS, eval_code, eval_sql


# ── eval_code ──────────────────────────────────────────────────────────────

class TestEvalCode:
    def test_correct_simple_function(self):
        code = "def add(a, b):\n    return a + b"
        passed, msg = eval_code(code, [{"function": "add", "args": [2, 3], "expected": 5}])
        assert passed
        assert "PASS" in msg

    def test_wrong_answer(self):
        code = "def add(a, b):\n    return a - b"
        passed, msg = eval_code(code, [{"function": "add", "args": [2, 3], "expected": 5}])
        assert not passed
        assert "FAIL" in msg

    def test_syntax_error(self):
        code = "def add(a b):\n    return a + b"
        passed, msg = eval_code(code, [{"function": "add", "args": [1, 2], "expected": 3}])
        assert not passed
        assert "Syntax error" in msg

    def test_undefined_function(self):
        code = "x = 1"
        passed, msg = eval_code(code, [{"function": "add", "args": [1, 2], "expected": 3}])
        assert not passed
        assert "not defined" in msg

    def test_exception_in_function(self):
        code = "def bad(x):\n    raise ValueError('boom')"
        passed, msg = eval_code(code, [{"function": "bad", "args": [1], "expected": 1}])
        assert not passed

    def test_float_tolerance(self):
        code = "def mean(nums):\n    return sum(nums) / len(nums)"
        passed, _ = eval_code(
            code,
            [{"function": "mean", "args": [[1.0, 2.0, 3.0]], "expected": 2.0}],
        )
        assert passed

    def test_no_open_builtin(self):
        code = "def attack():\n    return open('/etc/passwd').read()"
        passed, _ = eval_code(code, [{"function": "attack", "args": [], "expected": ""}])
        assert not passed

    def test_pandas_df_marker(self):
        import pandas as pd
        code = "def row_count(df):\n    return len(df)"
        marker = {"__pandas_df__": True, "data": {"a": [1, 2, 3]}}
        passed, _ = eval_code(
            code,
            [{"function": "row_count", "args": [marker], "expected": 3}],
            inject_pandas=True,
        )
        assert passed

    def test_pandas_series_marker(self):
        code = "def total(s):\n    return int(s.sum())"
        marker = {"__pandas_series__": True, "values": [10, 20, 30]}
        passed, _ = eval_code(
            code,
            [{"function": "total", "args": [marker], "expected": 60}],
            inject_pandas=True,
        )
        assert passed

    def test_multiple_test_cases_all_pass(self):
        code = "def double(n):\n    return n * 2"
        tcs = [
            {"function": "double", "args": [1], "expected": 2},
            {"function": "double", "args": [5], "expected": 10},
            {"function": "double", "args": [0], "expected": 0},
        ]
        passed, _ = eval_code(code, tcs)
        assert passed

    def test_multiple_test_cases_partial_fail(self):
        code = "def double(n):\n    return n * 2 if n > 0 else 99"
        tcs = [
            {"function": "double", "args": [1], "expected": 2},
            {"function": "double", "args": [0], "expected": 0},
        ]
        passed, msg = eval_code(code, tcs)
        assert not passed
        assert "FAIL" in msg


class TestSafeBuiltins:
    def test_open_not_available(self):
        assert "open" not in SAFE_BUILTINS

    def test_unsafe_import_blocked(self):
        code = "import subprocess\ndef attack():\n    return subprocess.run(['ls'])"
        passed, msg = eval_code(code, [{"function": "attack", "args": [], "expected": ""}])
        assert not passed

    def test_safe_import_allowed(self):
        code = "from collections import defaultdict\ndef f():\n    d = defaultdict(list)\n    d['a'].append(1)\n    return len(d)"
        passed, _ = eval_code(code, [{"function": "f", "args": [], "expected": 1}])
        assert passed

    def test_len_available(self):
        assert "len" in SAFE_BUILTINS


# ── eval_sql ───────────────────────────────────────────────────────────────

_SCHEMA = "CREATE TABLE t (id INTEGER, val TEXT);"
_SEED = "INSERT INTO t VALUES (1, 'a'), (2, 'b'), (3, 'c');"


class TestEvalSql:
    def test_correct_query(self):
        passed, msg = eval_sql(
            "SELECT id, val FROM t;",
            "SELECT id, val FROM t;",
            _SCHEMA,
            _SEED,
        )
        assert passed
        assert "3 rows" in msg

    def test_wrong_rows(self):
        passed, msg = eval_sql(
            "SELECT id, val FROM t WHERE id = 1;",
            "SELECT id, val FROM t;",
            _SCHEMA,
            _SEED,
        )
        assert not passed
        assert "mismatch" in msg

    def test_order_independent(self):
        passed, _ = eval_sql(
            "SELECT id, val FROM t ORDER BY id DESC;",
            "SELECT id, val FROM t ORDER BY id ASC;",
            _SCHEMA,
            _SEED,
        )
        assert passed

    def test_invalid_user_sql(self):
        passed, msg = eval_sql(
            "SELEXT * FROM t;",
            "SELECT id, val FROM t;",
            _SCHEMA,
            _SEED,
        )
        assert not passed
        assert "SQL error" in msg

    def test_aggregation(self):
        schema = "CREATE TABLE sales (product TEXT, amount INTEGER);"
        seed = "INSERT INTO sales VALUES ('a', 10), ('a', 20), ('b', 5);"
        passed, _ = eval_sql(
            "SELECT product, SUM(amount) FROM sales GROUP BY product;",
            "SELECT product, SUM(amount) FROM sales GROUP BY product;",
            schema,
            seed,
        )
        assert passed
