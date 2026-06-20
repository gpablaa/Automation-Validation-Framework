"""
Generate simulated engineering workflow request data 

"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

REQUEST_TYPES = [
    "Data Update",
    "Report Request",
    "Product Change",
    "Validation Check",
    "Access Request",
    "Bug Triage",
    "Process Improvement",
]
DEPARTMENTS = ["Engineering", "Product", "Operations", "Finance", "QA", "Business Enablement"]
OWNERS = ["Analyst A", "Engineer B", "Program Manager C", "QA Lead D", "Operations E", ""]
REQUESTERS = ["Team Alpha", "Team Beta", "Team Gamma", "Team Delta", "Team Omega"]
PRIORITIES = ["Low", "Medium", "High", "Critical", "Urgent", ""]
STATUSES = ["Submitted", "In Progress", "Blocked", "In Review", "Completed", "Failed", "Cancelled", "Done", ""]
WORKFLOW_STAGES = ["Intake", "Validation", "Assignment", "In Progress", "Review", "Completion", "Blocked"]
FAILURE_REASONS = ["Missing Input", "SLA Breach", "Priority Mismatch", "Owner Missing", "Failed Check", "Duplicate", ""]

SLA_DAYS = {
    "Critical": 2,
    "High": 5,
    "Medium": 10,
    "Low": 15,
}


def choose_weighted(values: list[str], weights: list[int]) -> str:
    return random.choices(values, weights=weights, k=1)[0]


def generate_requests(n: int = 525, seed: int = 42) -> list[dict[str, object]]:
    random.seed(seed)
    start = date(2026, 3, 1)
    rows: list[dict[str, object]] = []

    for i in range(1, n + 1):
        request_id = f"REQ-{i:04d}"
        # Intentionally create a few duplicate IDs for validation testing.
        if i in {101, 214, 389}:
            request_id = f"REQ-{i - 1:04d}"

        request_date = start + timedelta(days=random.randint(0, 30))
        priority = choose_weighted(PRIORITIES, [22, 35, 25, 12, 3, 3])
        status = choose_weighted(STATUSES, [14, 24, 10, 15, 25, 7, 2, 2, 1])
        request_type = choose_weighted(REQUEST_TYPES + [""], [16, 17, 16, 18, 8, 12, 10, 3])
        owner = choose_weighted(OWNERS, [23, 23, 20, 14, 12, 8])
        department = random.choice(DEPARTMENTS)
        stage = choose_weighted(WORKFLOW_STAGES, [16, 18, 12, 25, 18, 8, 3])

        base_sla = SLA_DAYS.get(priority, random.choice([5, 10, 15]))
        due_date = request_date + timedelta(days=base_sla + random.choice([-1, 0, 0, 1, 2, 5, 10]))
        # Intentionally blank some due dates.
        due_date_value = "" if random.random() < 0.06 else due_date.isoformat()

        completion_date_value = ""
        if status in {"Completed", "Failed", "Done", "Cancelled"}:
            completion_offset = random.randint(1, base_sla + random.choice([0, 2, 4, 8, 15]))
            completion_date = request_date + timedelta(days=completion_offset)
            completion_date_value = completion_date.isoformat()
            # Intentionally blank a few completed dates.
            if random.random() < 0.05:
                completion_date_value = ""

        failure_reason = ""
        if status in {"Failed", "Blocked"}:
            failure_reason = choose_weighted(FAILURE_REASONS, [20, 20, 12, 10, 18, 7, 13])

        manual_review = random.choice([15, 18, 20, 22, 25, 30])
        automated_review = max(4, int(manual_review * random.uniform(0.55, 0.72)))
        complexity = random.choice(["Low", "Medium", "High"])
        business_impact = random.choice(["Low", "Medium", "High"])
        automation_candidate = "Yes" if complexity != "High" and request_type in {"Data Update", "Report Request", "Validation Check", "Process Improvement"} else "No"

        rows.append(
            {
                "Request ID": request_id,
                "Request Date": request_date.isoformat(),
                "Request Type": request_type,
                "Department": department,
                "Requester": random.choice(REQUESTERS),
                "Owner": owner,
                "Priority": priority,
                "Status": status,
                "Workflow Stage": stage,
                "Due Date": due_date_value,
                "Completion Date": completion_date_value,
                "Failure Reason": failure_reason,
                "Estimated Manual Review Min": manual_review,
                "Estimated Automated Review Min": automated_review,
                "Automation Candidate": automation_candidate,
                "Business Impact": business_impact,
                "Complexity": complexity,
                "Stakeholder Email": f"stakeholder{random.randint(1,8)}@example.com",
                "Description": f"Simulated {request_type or 'workflow'} request for {department} team",
            }
        )

    return rows


def write_csv(rows: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=525)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/raw_requests.csv"))
    args = parser.parse_args()

    rows = generate_requests(n=args.rows, seed=args.seed)
    write_csv(rows, args.output)
    print(f"Generated {len(rows)} rows at {args.output}")


if __name__ == "__main__":
    main()
