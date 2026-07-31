from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from reconcile_projects import (
    insert_employees,
    insert_funding,
    insert_labor,
    insert_projects,
    load_csv_rows,
)

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "sql_project_reconciliation.db"
SCHEMA_PATH = ROOT / "schema.sql"
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def export_query_to_csv(conn: sqlite3.Connection, query: str, output_path: Path) -> None:
    cursor = conn.execute(query)
    columns = [description[0] for description in cursor.description]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(cursor.fetchall())


def initialize_database(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    insert_projects(conn, load_csv_rows(DATA_DIR / "projects.csv"))
    insert_employees(conn, load_csv_rows(DATA_DIR / "employees.csv"))
    insert_labor(conn, load_csv_rows(DATA_DIR / "labor.csv"))
    insert_funding(conn, load_csv_rows(DATA_DIR / "funding_agreements.csv"))
    conn.commit()


def refresh_tables_from_csv(conn: sqlite3.Connection) -> None:
    """
    Clear existing rows from the tables in a foreign-key-safe order and
    reload the CSV files from data/.

    Deletion order (safe for foreign keys):
      1. labor (references projects, employees)
      2. funding_agreements (references projects)
      3. projects
      4. employees

    Insertion order: projects, employees, funding_agreements, labor
    """
    conn.execute("PRAGMA foreign_keys = ON")
    # Delete rows in foreign-key-safe order
    conn.execute("DELETE FROM labor")
    conn.execute("DELETE FROM funding_agreements")
    conn.execute("DELETE FROM projects")
    conn.execute("DELETE FROM employees")

    # Insert fresh data. Parents first, then children.
    insert_projects(conn, load_csv_rows(DATA_DIR / "projects.csv"))
    insert_employees(conn, load_csv_rows(DATA_DIR / "employees.csv"))
    insert_funding(conn, load_csv_rows(DATA_DIR / "funding_agreements.csv"))
    insert_labor(conn, load_csv_rows(DATA_DIR / "labor.csv"))
    conn.commit()


def database_is_initialized(conn: sqlite3.Connection) -> bool:
    existing_tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    required_tables = {"projects", "employees", "labor", "funding_agreements"}
    if not required_tables.issubset(existing_tables):
        return False

    for table_name in required_tables:
        if conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0] == 0:
            return False

    return True


def export_analysis_outputs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Create schema and load CSVs if DB is missing or not initialized.
    if not DB_PATH.exists() or not database_is_initialized(conn):
        initialize_database(conn)
    else:
        # Refresh tables from CSV files on every run so outputs reflect latest data.
        refresh_tables_from_csv(conn)

    missing_funding_query = """
    SELECT
        p.project_id,
        p.project_name,
        p.department,
        p.status,
        ROUND(p.budget, 2) AS budget
    FROM projects AS p
    LEFT JOIN funding_agreements AS fa
        ON p.project_id = fa.project_id
    WHERE fa.project_id IS NULL
    ORDER BY p.project_id
    """

    employee_labor_query = """
    SELECT
        e.employee_id,
        e.employee_name,
        e.department,
        ROUND(SUM(l.hours * e.hourly_rate), 2) AS labor_cost
    FROM labor AS l
    JOIN employees AS e
        ON l.employee_id = e.employee_id
    GROUP BY e.employee_id, e.employee_name, e.department
    ORDER BY labor_cost DESC
    """

    department_summary_query = """
    WITH labor_by_project AS (
        SELECT
            l.project_id,
            ROUND(SUM(l.hours * e.hourly_rate), 2) AS labor_cost
        FROM labor AS l
        JOIN employees AS e
            ON l.employee_id = e.employee_id
        GROUP BY l.project_id
    )
    SELECT
        p.department,
        COUNT(p.project_id) AS project_count,
        ROUND(SUM(p.budget), 2) AS total_budget,
        ROUND(SUM(COALESCE(fa.amount, 0)), 2) AS total_funding,
        ROUND(SUM(COALESCE(lb.labor_cost, 0)), 2) AS total_labor_cost
    FROM projects AS p
    LEFT JOIN funding_agreements AS fa
        ON p.project_id = fa.project_id
    LEFT JOIN labor_by_project AS lb
        ON p.project_id = lb.project_id
    GROUP BY p.department
    ORDER BY p.department
    """

    export_query_to_csv(conn, missing_funding_query, OUTPUT_DIR / "missing_funding_projects.csv")
    export_query_to_csv(conn, employee_labor_query, OUTPUT_DIR / "employee_labor_costs.csv")
    export_query_to_csv(conn, department_summary_query, OUTPUT_DIR / "department_summary.csv")

    conn.close()
    print("Analysis exports generated in output/")


if __name__ == "__main__":
    export_analysis_outputs()
