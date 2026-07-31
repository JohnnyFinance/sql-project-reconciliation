PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    owner TEXT NOT NULL,
    department TEXT NOT NULL,
    status TEXT NOT NULL,
    budget REAL NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    employee_name TEXT NOT NULL,
    department TEXT NOT NULL,
    hourly_rate REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS labor (
    labor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    work_date TEXT NOT NULL,
    hours REAL NOT NULL,
    notes TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS funding_agreements (
    agreement_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL UNIQUE,
    agreement_type TEXT NOT NULL,
    amount REAL NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE INDEX IF NOT EXISTS idx_labor_project ON labor(project_id);
CREATE INDEX IF NOT EXISTS idx_labor_employee ON labor(employee_id);
CREATE INDEX IF NOT EXISTS idx_funding_project ON funding_agreements(project_id);
