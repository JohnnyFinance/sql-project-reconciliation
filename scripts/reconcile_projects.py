from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "sql_project_reconciliation.db"
SCHEMA_PATH = ROOT / "schema.sql"
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def insert_projects(conn: sqlite3.Connection, rows: list[dict[str, str]]) -> None:
    conn.executemany(
        """
        INSERT INTO projects (
            project_id, project_name, owner, department, status, budget, start_date, end_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["project_id"],
                row["project_name"],
                row["owner"],
                row["department"],
                row["status"],
                float(row["budget"]),
                row["start_date"],
                row["end_date"],
            )
            for row in rows
        ],
    )


def insert_employees(conn: sqlite3.Connection, rows: list[dict[str, str]]) -> None:
    conn.executemany(
        """
        INSERT INTO employees (employee_id, employee_name, department, hourly_rate)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                row["employee_id"],
                row["employee_name"],
                row["department"],
                float(row["hourly_rate"]),
            )
            for row in rows
        ],
    )


def insert_labor(conn: sqlite3.Connection, rows: list[dict[str, str]]) -> None:
    conn.executemany(
        """
        INSERT INTO labor (project_id, employee_id, work_date, hours, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                row["project_id"],
                row["employee_id"],
                row["work_date"],
                float(row["hours"]),
                row["notes"],
            )
            for row in rows
        ],
    )


def insert_funding(conn: sqlite3.Connection, rows: list[dict[str, str]]) -> None:
    conn.executemany(
        """
        INSERT INTO funding_agreements (
            agreement_id, project_id, agreement_type, amount, start_date, end_date
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["agreement_id"],
                row["project_id"],
                row["agreement_type"],
                float(row["amount"]),
                row["start_date"],
                row["end_date"],
            )
            for row in rows
        ],
    )


def export_csv(query: str, output_path: Path, conn: sqlite3.Connection) -> None:
    cursor = conn.execute(query)
    columns = [description[0] for description in cursor.description]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(cursor.fetchall())


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    insert_projects(conn, load_csv_rows(DATA_DIR / "projects.csv"))
    insert_employees(conn, load_csv_rows(DATA_DIR / "employees.csv"))
    insert_labor(conn, load_csv_rows(DATA_DIR / "labor.csv"))
    insert_funding(conn, load_csv_rows(DATA_DIR / "funding_agreements.csv"))
    conn.commit()

    project_summary_query = """
    WITH labor_summary AS (
        SELECT
            l.project_id,
            ROUND(SUM(l.hours), 2) AS labor_hours,
            ROUND(SUM(l.hours * e.hourly_rate), 2) AS labor_cost
        FROM labor AS l
        LEFT JOIN employees AS e
            ON l.employee_id = e.employee_id
        GROUP BY l.project_id
    ),
    funding_summary AS (
        SELECT
            project_id,
            ROUND(SUM(amount), 2) AS funding_amount
        FROM funding_agreements
        GROUP BY project_id
    )
    SELECT
        p.project_id,
        p.project_name,
        p.department,
        p.status,
        ROUND(p.budget, 2) AS budget,
        COALESCE(fs.funding_amount, 0) AS funding_amount,
        COALESCE(ls.labor_hours, 0) AS labor_hours,
        COALESCE(ls.labor_cost, 0) AS labor_cost,
        ROUND(COALESCE(fs.funding_amount, 0) - p.budget, 2) AS funding_gap,
        CASE
            WHEN fs.funding_amount IS NULL THEN 'Missing funding'
            ELSE 'Funding present'
        END AS funding_status
    FROM projects AS p
    LEFT JOIN labor_summary AS ls
        ON p.project_id = ls.project_id
    LEFT JOIN funding_summary AS fs
        ON p.project_id = fs.project_id
    ORDER BY p.project_id
    """

    powerbi_query = """
    WITH project_rollup AS (
        SELECT
            p.project_id,
            p.project_name,
            p.department,
            ROUND(p.budget, 2) AS budget,
            COALESCE(fs.funding_amount, 0) AS funding_amount,
            COALESCE(ls.labor_hours, 0) AS labor_hours,
            COALESCE(ls.labor_cost, 0) AS labor_cost
        FROM projects AS p
        LEFT JOIN (
            SELECT
                l.project_id,
                ROUND(SUM(l.hours), 2) AS labor_hours,
                ROUND(SUM(l.hours * e.hourly_rate), 2) AS labor_cost
            FROM labor AS l
            LEFT JOIN employees AS e
                ON l.employee_id = e.employee_id
            GROUP BY l.project_id
        ) AS ls
            ON p.project_id = ls.project_id
        LEFT JOIN (
            SELECT
                project_id,
                ROUND(SUM(amount), 2) AS funding_amount
            FROM funding_agreements
            GROUP BY project_id
        ) AS fs
            ON p.project_id = fs.project_id
    )
    SELECT
        department,
        COUNT(*) AS project_count,
        ROUND(SUM(budget), 2) AS total_budget,
        ROUND(SUM(funding_amount), 2) AS total_funding,
        ROUND(SUM(labor_cost), 2) AS total_labor_cost,
        SUM(CASE WHEN funding_amount = 0 THEN 1 ELSE 0 END) AS projects_missing_funding
    FROM project_rollup
    GROUP BY department
    ORDER BY department
    """

    export_csv(project_summary_query, OUTPUT_DIR / "reconciliation_summary.csv", conn)
    export_csv(powerbi_query, OUTPUT_DIR / "powerbi_dashboard_data.csv", conn)
    conn.close()

    print(f"Database created at {DB_PATH}")
    print(f"Outputs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
