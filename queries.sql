-- Reconcile projects that do not yet have a funding agreement.
SELECT
    p.project_id,
    p.project_name,
    p.department,
    p.status,
    p.budget
FROM projects AS p
LEFT JOIN funding_agreements AS fa
    ON p.project_id = fa.project_id
WHERE fa.project_id IS NULL
ORDER BY p.project_id;

-- Identify projects that have labor activity but no funding agreement.
SELECT
    p.project_id,
    p.project_name,
    COUNT(l.labor_id) AS labor_entries,
    ROUND(SUM(l.hours), 2) AS labor_hours
FROM projects AS p
JOIN labor AS l
    ON p.project_id = l.project_id
LEFT JOIN funding_agreements AS fa
    ON p.project_id = fa.project_id
WHERE fa.project_id IS NULL
GROUP BY p.project_id, p.project_name
ORDER BY p.project_id;

-- Calculate labor cost by employee.
SELECT
    e.employee_id,
    e.employee_name,
    ROUND(SUM(l.hours * e.hourly_rate), 2) AS labor_cost
FROM labor AS l
JOIN employees AS e
    ON l.employee_id = e.employee_id
GROUP BY e.employee_id, e.employee_name
ORDER BY labor_cost DESC;

-- Summarize budgets, funding, and labor by department.
WITH labor_by_project AS (
    SELECT
        l.project_id,
        SUM(l.hours * e.hourly_rate) AS labor_cost
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
ORDER BY p.department;
