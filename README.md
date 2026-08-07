# sql-project-reconciliation

## Overview
This project demonstrates a simple SQL-based reconciliation workflow for project funding and labor tracking. The example uses a SQLite database file and a Python automation script to load fictional project data, run reconciliation logic, and export files that can be used in Power BI for visual presentation.

The workflow is intentionally business-focused and mirrors common finance and operations reporting tasks such as identifying missing funding agreements, reconciling budgets to actual labor activity, and summarizing departmental performance.

## Objectives
- Design a relational database for project reconciliation
- Practice SQL fundamentals and reporting logic
- Load CSV data automatically with Python
- Create a reusable SQLite database file
- Export Power BI-ready summaries from the database
- Build a portfolio project that combines SQL, Python, and analytics

## Database schema
The project uses four core tables:
- Projects: stores project details such as owner, department, status, and budget
- Employees: stores employee names and standard labor rates
- Labor: stores hours charged to projects by employee
- Funding Agreements: stores funding agreements linked to projects

## Example business questions
The SQL queries in this project answer questions such as:
- Which projects are missing a funding agreement?
- Which projects have labor activity but no funding agreement?
- What are the total labor costs by employee?
- How do departments compare on budget, funding, and labor spend?

## Repository structure
```text
sql-project-reconciliation/
- README.md
- schema.sql
- queries.sql
- scripts/reconcile_projects.py
- data/projects.csv
- data/employees.csv
- data/labor.csv
- data/funding_agreements.csv
- output/reconciliation_summary.csv
- output/powerbi_dashboard_data.csv
- sql_project_reconciliation.db
```

## How to run
1. Open a terminal in the repository root.
2. Run: python scripts/reconcile_projects.py
3. Review the generated SQLite database file and CSV outputs in the output/ folder.

## SQL concepts demonstrated
- CREATE TABLE
- PRIMARY KEY
- FOREIGN KEY
- SELECT
- WHERE
- ORDER BY
- GROUP BY
- INNER JOIN
- LEFT JOIN
- Aggregate functions

## Technologies
- SQL
- SQLite
- Python
- CSV data loading
- Power BI-ready exports

## Author
**Johnny Linares**

Finance professional expanding into SQL, Python, Power BI, and automation to build scalable reporting solutions.
