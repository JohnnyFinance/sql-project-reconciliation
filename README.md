# sql-project-reconciliation
## Overview
This project simulates a project reconciliation process similar to those used by financial analysts supporting clinical operations.

The database tracks projects, employees, labor hours, and funding agreements. Using SQL, the project identifies missing records, validates data between systems, and produces reports that support financial planning and project management. 

Although the data is fictional, the workflow is inspired by the types of reconciliation and financial reporting commonly performed by financial analysts in healthcare organizations.
## Objectives
- Design a relational database from scratch
- Practice SQL fundamentals
- Perform data validation and reconciliation 
- Generate labor cost reports
- Identify missing project information
- Build a portfolio project demonstrating business-focused SQL skills
---
## Database schema
The project contains four primary tables
### Projects
Stores project information including owner, status, department, and budget
### Employees
Stores employee information and standard labor rates.
### Labor
Stores hours worked by employee and project.
### Funding Agreements
Tracks funding agreements associated with projects.

---
## Example Business Questions
This project answers questions such as:
- Which projects are currently active?
- Which projects are missing a Funding Agreement?
- What are the total labor costs by employee?
- How many projects exist within each department?
- Which projects have the highest budgets?
- How many hours have employees charged to each project?
---
## SQL Concepts Demonstrated
- CREATE TABLE
- PRIMARY KEY
- FOREIGN KEY
- SELECT
- WHERE
- ORDER BY
- GROUP BY
- HAVING
- INNER JOIN
- LEFT JOIN
- Aggregate Functions
- Views (Future Enhancement)
---
## Repository Structure

```text
sql-project-reconciliation/
- README.md
- schema.sql
- queries.sql
- screenshots/
```

---
## Future Enhancements
- Import CSV files automatically using Python
- Load data into SQLite
- Create SQL Views
- Build stored procedures
- Connect the database to PowerBI
- Automate monthly reconiliation reports
---
## Technologies
- SQL
- SQLite
- Git
- GitHub
- Visual Studio Code
---
## Author
**Johnny Linares**

Finance Professional expanding into SQL, Python, PowerBI, and automation to build scalable financial reporting solutions.