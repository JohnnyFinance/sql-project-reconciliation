from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "sql_project_reconciliation.db"
OUTPUT_DIR = ROOT / "output"


def export_query_to_csv(conn: sqlite3.Connection, query: str, output_path: Path) -> None:
    cursor = conn.execute(query)
    columns = [description[0] for description in cursor.description]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(cursor.fetchall())


def export_analysis_outputs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

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
