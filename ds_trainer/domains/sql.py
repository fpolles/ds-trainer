from ds_trainer.models import Difficulty, Domain, ExerciseType, Question

_SCHEMA_ORDERS = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    country     TEXT NOT NULL
);
CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    amount      REAL NOT NULL,
    order_date  TEXT NOT NULL
);
"""

_SEED_ORDERS = """
INSERT INTO customers VALUES (1,'Alice','US'),(2,'Bob','UK'),(3,'Carol','US'),(4,'Dave','CA');
INSERT INTO orders VALUES
 (1,1,120.0,'2024-01-10'),
 (2,1,200.0,'2024-02-15'),
 (3,2,80.0,'2024-01-20'),
 (4,3,300.0,'2024-03-01'),
 (5,3,50.0,'2024-03-15'),
 (6,1,170.0,'2024-04-01');
"""

_SCHEMA_EMPLOYEES = """
CREATE TABLE employees (
    emp_id     INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    dept       TEXT NOT NULL,
    salary     REAL NOT NULL,
    manager_id INTEGER
);
"""

_SEED_EMPLOYEES = """
INSERT INTO employees VALUES
 (1,'Alice','Engineering',95000,NULL),
 (2,'Bob','Engineering',85000,1),
 (3,'Carol','Marketing',70000,NULL),
 (4,'Dave','Engineering',78000,1),
 (5,'Eve','Marketing',65000,3),
 (6,'Frank','Engineering',92000,1);
"""

_SCHEMA_PRODUCTS = """
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    category   TEXT NOT NULL
);
CREATE TABLE sales (
    sale_id    INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL,
    revenue    REAL NOT NULL,
    sale_date  TEXT NOT NULL
);
"""

_SEED_PRODUCTS = """
INSERT INTO products VALUES
 (1,'Widget A','Electronics'),(2,'Widget B','Electronics'),
 (3,'Gadget X','Home'),(4,'Gadget Y','Home'),(5,'Tool Z','Hardware');
INSERT INTO sales VALUES
 (1,1,10,500.0,'2024-01-05'),(2,1,5,250.0,'2024-02-10'),
 (3,2,8,320.0,'2024-01-15'),(4,3,3,90.0,'2024-01-20'),
 (5,4,6,180.0,'2024-02-25'),(6,5,2,60.0,'2024-03-01'),
 (7,1,12,600.0,'2024-03-10'),(8,2,4,160.0,'2024-03-15');
"""

QUESTIONS: list[Question] = [
    # ── Easy ──────────────────────────────────────────────────────────────
    Question(
        id="sql_e_001",
        domain=Domain.SQL,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt="Which SQL clause is used to filter rows AFTER grouping/aggregation?",
        choices=["WHERE", "HAVING", "FILTER", "GROUP BY"],
        answer_index=1,
        explanation=(
            "HAVING filters groups produced by GROUP BY, while WHERE filters individual rows "
            "before aggregation. You cannot use aggregate functions (e.g. SUM, COUNT) in WHERE."
        ),
        hints=["Think about when GROUP BY produces intermediate result sets."],
        tags=["aggregation", "filtering"],
    ),
    Question(
        id="sql_e_002",
        domain=Domain.SQL,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "What type of JOIN returns all rows from the LEFT table and matching rows from "
            "the RIGHT table (NULLs where no match)?"
        ),
        choices=["INNER JOIN", "RIGHT JOIN", "LEFT JOIN", "FULL OUTER JOIN"],
        answer_index=2,
        explanation=(
            "LEFT JOIN (or LEFT OUTER JOIN) keeps every row from the left table. "
            "Columns from the right table are NULL where no matching row exists."
        ),
        hints=["The result includes all rows from one specific side regardless of matches."],
        tags=["joins"],
    ),
    Question(
        id="sql_e_003",
        domain=Domain.SQL,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.SQL_CHALLENGE,
        prompt=(
            "List the total order amount per customer. Return customer name and total_amount, "
            "ordered by total_amount descending."
        ),
        schema_ddl=_SCHEMA_ORDERS,
        seed_data=_SEED_ORDERS,
        expected_query=(
            "SELECT c.name, SUM(o.amount) AS total_amount "
            "FROM customers c JOIN orders o ON c.customer_id = o.customer_id "
            "GROUP BY c.customer_id, c.name "
            "ORDER BY total_amount DESC"
        ),
        explanation=(
            "JOIN customers → orders on customer_id, GROUP BY customer, SUM amounts, "
            "ORDER BY the aggregate DESC."
        ),
        hints=[
            "You need a JOIN and GROUP BY.",
            "SUM(o.amount) gives the total per group.",
        ],
        tags=["joins", "aggregation", "group-by"],
    ),
    Question(
        id="sql_e_004",
        domain=Domain.SQL,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt="Which aggregate function counts only non-NULL values in a column?",
        choices=["COUNT(*)", "COUNT(column)", "SUM(column)", "COALESCE(column)"],
        answer_index=1,
        explanation=(
            "COUNT(column) ignores NULLs — it counts only rows where the column is not NULL. "
            "COUNT(*) counts all rows including those with NULLs."
        ),
        hints=["COUNT(*) and COUNT(col) behave differently around NULLs."],
        tags=["aggregation", "nulls"],
    ),
    # ── Medium ─────────────────────────────────────────────────────────────
    Question(
        id="sql_m_001",
        domain=Domain.SQL,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.SQL_CHALLENGE,
        prompt=(
            "For each customer, find their highest single order amount and rank customers "
            "by that value (highest first). Return: name, max_order, rank. "
            "Use a window function for the rank."
        ),
        schema_ddl=_SCHEMA_ORDERS,
        seed_data=_SEED_ORDERS,
        expected_query=(
            "SELECT c.name, MAX(o.amount) AS max_order, "
            "RANK() OVER (ORDER BY MAX(o.amount) DESC) AS rank "
            "FROM customers c JOIN orders o ON c.customer_id = o.customer_id "
            "GROUP BY c.customer_id, c.name"
        ),
        explanation=(
            "Aggregate with MAX per customer first (GROUP BY), then apply RANK() as a "
            "window function over the aggregated result."
        ),
        hints=[
            "You need GROUP BY to compute MAX per customer, then a window function for rank.",
            "RANK() OVER (ORDER BY ... DESC) assigns 1 to the highest value.",
        ],
        tags=["window-functions", "aggregation", "ranking"],
    ),
    Question(
        id="sql_m_002",
        domain=Domain.SQL,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.SQL_CHALLENGE,
        prompt=(
            "Find customers who have placed MORE than 2 orders. "
            "Return customer name and order_count."
        ),
        schema_ddl=_SCHEMA_ORDERS,
        seed_data=_SEED_ORDERS,
        expected_query=(
            "SELECT c.name, COUNT(o.order_id) AS order_count "
            "FROM customers c JOIN orders o ON c.customer_id = o.customer_id "
            "GROUP BY c.customer_id, c.name "
            "HAVING COUNT(o.order_id) > 2"
        ),
        explanation="Use HAVING to filter groups after COUNT, not WHERE which runs before aggregation.",
        hints=[
            "Filtering on an aggregate requires HAVING, not WHERE.",
        ],
        tags=["having", "aggregation", "joins"],
    ),
    Question(
        id="sql_m_003",
        domain=Domain.SQL,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.SQL_CHALLENGE,
        prompt=(
            "For each department, find the highest-paid employee. "
            "Return dept, name, salary. If there is a tie, return all tied employees."
        ),
        schema_ddl=_SCHEMA_EMPLOYEES,
        seed_data=_SEED_EMPLOYEES,
        expected_query=(
            "SELECT dept, name, salary FROM employees e "
            "WHERE salary = (SELECT MAX(salary) FROM employees e2 WHERE e2.dept = e.dept)"
        ),
        explanation=(
            "A correlated subquery finds the max salary per department. The outer query "
            "returns all employees matching that max (handles ties naturally)."
        ),
        hints=[
            "A correlated subquery can find the max salary in the same department.",
            "Filter WHERE salary = (SELECT MAX(salary) FROM employees WHERE dept = e.dept).",
        ],
        tags=["correlated-subquery", "window-functions"],
    ),
    Question(
        id="sql_m_004",
        domain=Domain.SQL,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "What does ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) compute?"
        ),
        choices=[
            "The salary rank within each department, with gaps for ties",
            "A sequential integer per row within each department, ordered by salary descending",
            "The dense rank of the salary across the entire table",
            "The count of employees in each department",
        ],
        answer_index=1,
        explanation=(
            "ROW_NUMBER() assigns a unique sequential integer per row within each PARTITION. "
            "Unlike RANK() or DENSE_RANK(), it never produces ties — each row gets a distinct number."
        ),
        hints=["ROW_NUMBER never repeats a number within a partition."],
        tags=["window-functions"],
    ),
    Question(
        id="sql_m_005",
        domain=Domain.SQL,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.SQL_CHALLENGE,
        prompt=(
            "Compute a 3-period moving average of revenue over time for product_id=1. "
            "Order by sale_date. Return sale_date and moving_avg rounded to 2 decimal places."
        ),
        schema_ddl=_SCHEMA_PRODUCTS,
        seed_data=_SEED_PRODUCTS,
        expected_query=(
            "SELECT sale_date, "
            "ROUND(AVG(revenue) OVER (ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg "
            "FROM sales WHERE product_id = 1 ORDER BY sale_date"
        ),
        explanation=(
            "ROWS BETWEEN 2 PRECEDING AND CURRENT ROW defines a sliding window of 3 rows "
            "(current + 2 before) for the moving average."
        ),
        hints=[
            "Use AVG(...) OVER (ORDER BY date ROWS BETWEEN ...).",
            "2 PRECEDING AND CURRENT ROW = window of 3 rows.",
        ],
        tags=["window-functions", "moving-average"],
    ),
    # ── Hard ───────────────────────────────────────────────────────────────
    Question(
        id="sql_h_001",
        domain=Domain.SQL,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.SQL_CHALLENGE,
        prompt=(
            "Using a CTE, find the top-2 products by total revenue within EACH category. "
            "Return category, name, total_revenue, and rank_in_category."
        ),
        schema_ddl=_SCHEMA_PRODUCTS,
        seed_data=_SEED_PRODUCTS,
        expected_query=(
            "WITH ranked AS ("
            "  SELECT p.category, p.name, SUM(s.revenue) AS total_revenue, "
            "  DENSE_RANK() OVER (PARTITION BY p.category ORDER BY SUM(s.revenue) DESC) AS rank_in_category "
            "  FROM products p JOIN sales s ON p.product_id = s.product_id "
            "  GROUP BY p.category, p.product_id, p.name"
            ") SELECT category, name, total_revenue, rank_in_category FROM ranked WHERE rank_in_category <= 2"
        ),
        explanation=(
            "Step 1: Aggregate revenue per product per category. "
            "Step 2: Apply DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC). "
            "Step 3: Filter ranks <= 2 in the outer query (CTEs make this clean)."
        ),
        hints=[
            "Use a CTE to compute aggregated revenue first.",
            "DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) gives the rank within each category.",
            "Filter rank_in_category <= 2 in the outer SELECT.",
        ],
        tags=["cte", "window-functions", "top-n-per-group"],
    ),
    Question(
        id="sql_h_002",
        domain=Domain.SQL,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.SQL_CHALLENGE,
        prompt=(
            "Find employees who earn more than the average salary of their own department. "
            "Return name, dept, salary, dept_avg (rounded to 2 decimal places)."
        ),
        schema_ddl=_SCHEMA_EMPLOYEES,
        seed_data=_SEED_EMPLOYEES,
        expected_query=(
            "SELECT e.name, e.dept, e.salary, "
            "ROUND(AVG(e2.salary), 2) AS dept_avg "
            "FROM employees e "
            "JOIN employees e2 ON e.dept = e2.dept "
            "GROUP BY e.emp_id, e.name, e.dept, e.salary "
            "HAVING e.salary > AVG(e2.salary)"
        ),
        explanation=(
            "Self-join on dept to group each employee with all dept members, compute dept average, "
            "then HAVING filters only those earning above that average."
        ),
        hints=[
            "Try a self-join: JOIN employees e2 ON e.dept = e2.dept",
            "HAVING e.salary > AVG(e2.salary) filters after aggregation.",
        ],
        tags=["self-join", "aggregation", "having"],
    ),
    Question(
        id="sql_h_003",
        domain=Domain.SQL,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "What is the difference between RANK() and DENSE_RANK() when there are ties?"
        ),
        choices=[
            "RANK() skips numbers after a tie; DENSE_RANK() does not skip numbers",
            "DENSE_RANK() skips numbers after a tie; RANK() does not skip numbers",
            "They behave identically — both skip numbers after ties",
            "RANK() assigns the same number to ties; DENSE_RANK() assigns distinct numbers",
        ],
        answer_index=0,
        explanation=(
            "Example: salaries [100, 100, 80]. "
            "RANK()       → 1, 1, 3 (skips 2). "
            "DENSE_RANK() → 1, 1, 2 (no gap). "
            "ROW_NUMBER() → 1, 2, 3 (unique)."
        ),
        hints=["Think about what happens to position 2 when two rows tie for position 1."],
        tags=["window-functions", "ranking"],
    ),
]
