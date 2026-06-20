"""
Automation Validation Framework

Reads simulated workflow request data, applies validation rules, flags exceptions,
and exports dashboard-ready CSV outputs for Excel and Power BI.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}
VALID_STATUSES = {"Submitted", "In Progress", "Blocked", "In Review", "Completed", "Failed", "Cancelled"}
SLA_DAYS = {"Critical": 2, "High": 5, "Medium": 10, "Low": 15}
TODAY = date(2026, 4, 5)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def check_row(row: dict[str, str], duplicate_ids: set[str]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    descriptions: list[str] = []

    request_id = row.get("Request ID", "")
    request_type = row.get("Request Type", "")
    owner = row.get("Owner", "")
    priority = row.get("Priority", "")
    status = row.get("Status", "")
    due_date = parse_date(row.get("Due Date"))
    request_date = parse_date(row.get("Request Date"))
    completion_date = parse_date(row.get("Completion Date"))
    failure_reason = row.get("Failure Reason", "")
    stage = row.get("Workflow Stage", "")

    if not request_id:
        issues.append("MISSING_REQUEST_ID")
        descriptions.append("Request ID is missing")

    if request_id in duplicate_ids:
        issues.append("DUPLICATE_REQUEST_ID")
        descriptions.append("Request ID appears more than once")

    if not request_type:
        issues.append("MISSING_REQUEST_TYPE")
        descriptions.append("Request type is missing")

    if not owner:
        issues.append("MISSING_OWNER")
        descriptions.append("Owner is missing")

    if not due_date:
        issues.append("MISSING_DUE_DATE")
        descriptions.append("Due date is missing or invalid")

    if priority not in VALID_PRIORITIES:
        issues.append("INVALID_PRIORITY")
        descriptions.append("Priority is blank or outside the approved values")

    if status not in VALID_STATUSES:
        issues.append("INVALID_STATUS")
        descriptions.append("Status is blank or outside the approved values")

    if priority == "Critical" and due_date and request_date and (due_date - request_date).days > SLA_DAYS["Critical"]:
        issues.append("PRIORITY_MISMATCH")
        descriptions.append("Critical request has a due date outside the 2-day SLA")

    end_date = completion_date or TODAY
    if due_date and status not in {"Cancelled"} and end_date > due_date:
        issues.append("SLA_BREACH")
        descriptions.append("Request is completed late or currently past due")

    if request_date and status not in {"Completed", "Failed", "Cancelled"}:
        open_days = (TODAY - request_date).days
        expected_days = SLA_DAYS.get(priority, 10)
        if open_days > expected_days:
            issues.append("PROCESSING_DELAY")
            descriptions.append("Open request has exceeded expected processing time")

    if status == "Failed" and not failure_reason:
        issues.append("FAILED_WITHOUT_REASON")
        descriptions.append("Failed request has no failure reason")

    if status == "Completed" and not completion_date:
        issues.append("COMPLETED_WITHOUT_DATE")
        descriptions.append("Completed request has no completion date")

    if status == "Completed" and stage not in {"Completion", "Review"}:
        issues.append("STATUS_STAGE_MISMATCH")
        descriptions.append("Completed request is not in an expected workflow stage")

    if stage in {"Blocked", "Review"} and request_date and (TODAY - request_date).days > 7 and status not in {"Completed", "Cancelled"}:
        issues.append("BOTTLENECK_STAGE")
        descriptions.append("Request appears stuck in a bottleneck stage")

    return issues, descriptions


def validation_severity(issue_codes: Iterable[str]) -> str:
    high = {"SLA_BREACH", "PRIORITY_MISMATCH", "DUPLICATE_REQUEST_ID", "FAILED_WITHOUT_REASON", "BOTTLENECK_STAGE"}
    medium = {"MISSING_OWNER", "MISSING_DUE_DATE", "PROCESSING_DELAY", "COMPLETED_WITHOUT_DATE", "STATUS_STAGE_MISMATCH"}
    issues = set(issue_codes)
    if issues & high:
        return "High"
    if issues & medium:
        return "Medium"
    if issues:
        return "Low"
    return "None"


def validate_requests(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    counts = Counter(row.get("Request ID", "") for row in rows)
    duplicate_ids = {request_id for request_id, count in counts.items() if request_id and count > 1}

    validated: list[dict[str, object]] = []
    exceptions: list[dict[str, object]] = []
    rule_counter: Counter[str] = Counter()
    group_metrics = defaultdict(lambda: {"Total Requests": 0, "Failed Requests": 0, "Completed Requests": 0, "Total Processing Days": 0, "Total Time Saved Min": 0})

    for row in rows:
        issues, descriptions = check_row(row, duplicate_ids)
        issue_count = len(issues)
        result = "Fail" if issues else "Pass"
        severity = validation_severity(issues)

        request_date = parse_date(row.get("Request Date"))
        completion_date = parse_date(row.get("Completion Date"))
        end_date = completion_date or TODAY
        processing_days = (end_date - request_date).days if request_date else 0

        try:
            manual_min = int(row.get("Estimated Manual Review Min", "0") or 0)
            automated_min = int(row.get("Estimated Automated Review Min", "0") or 0)
        except ValueError:
            manual_min, automated_min = 0, 0

        time_saved = max(0, manual_min - automated_min)
        efficiency_gain = round(time_saved / manual_min, 4) if manual_min else 0
        bottleneck_flag = "Yes" if "BOTTLENECK_STAGE" in issues else "No"
        sla_breached = "Yes" if "SLA_BREACH" in issues else "No"

        output = dict(row)
        output.update(
            {
                "Validation Result": result,
                "Validation Severity": severity,
                "Issue Count": issue_count,
                "Issue Codes": "; ".join(issues),
                "Issue Description": "; ".join(descriptions),
                "SLA Breached": sla_breached,
                "Bottleneck Flag": bottleneck_flag,
                "Processing Time Days": processing_days,
                "Time Saved Min": time_saved,
                "Efficiency Gain %": efficiency_gain,
            }
        )
        validated.append(output)

        for issue in issues:
            rule_counter[issue] += 1
            exceptions.append(
                {
                    "Request ID": row.get("Request ID", ""),
                    "Department": row.get("Department", ""),
                    "Owner": row.get("Owner", ""),
                    "Priority": row.get("Priority", ""),
                    "Status": row.get("Status", ""),
                    "Workflow Stage": row.get("Workflow Stage", ""),
                    "Issue Code": issue,
                    "Severity": severity,
                    "Action Needed": map_action(issue),
                    "Stakeholder Email": row.get("Stakeholder Email", ""),
                }
            )

        dept = row.get("Department", "Unknown") or "Unknown"
        group_metrics[dept]["Total Requests"] += 1
        group_metrics[dept]["Failed Requests"] += 1 if result == "Fail" else 0
        group_metrics[dept]["Completed Requests"] += 1 if row.get("Status") == "Completed" else 0
        group_metrics[dept]["Total Processing Days"] += processing_days
        group_metrics[dept]["Total Time Saved Min"] += time_saved

    summary_rows: list[dict[str, object]] = []
    total_requests = len(validated)
    passed = sum(1 for row in validated if row["Validation Result"] == "Pass")
    failed = total_requests - passed
    total_manual = sum(int(row.get("Estimated Manual Review Min", 0) or 0) for row in validated)
    total_automated = sum(int(row.get("Estimated Automated Review Min", 0) or 0) for row in validated)
    total_saved = total_manual - total_automated
    summary_rows.extend(
        [
            {"Metric": "Total Requests", "Value": total_requests},
            {"Metric": "Passed Requests", "Value": passed},
            {"Metric": "Failed Requests", "Value": failed},
            {"Metric": "Pass Rate", "Value": round(passed / total_requests, 4)},
            {"Metric": "Failure Rate", "Value": round(failed / total_requests, 4)},
            {"Metric": "Estimated Manual Review Min", "Value": total_manual},
            {"Metric": "Estimated Automated Review Min", "Value": total_automated},
            {"Metric": "Estimated Time Saved Min", "Value": total_saved},
            {"Metric": "Estimated Manual Review Reduction", "Value": round(total_saved / total_manual, 4)},
        ]
    )

    rule_summary = [{"Issue Code": code, "Count": count} for code, count in sorted(rule_counter.items(), key=lambda x: x[1], reverse=True)]

    department_summary: list[dict[str, object]] = []
    for dept, values in sorted(group_metrics.items()):
        total = values["Total Requests"]
        department_summary.append(
            {
                "Department": dept,
                "Total Requests": total,
                "Failed Requests": values["Failed Requests"],
                "Completed Requests": values["Completed Requests"],
                "Failure Rate": round(values["Failed Requests"] / total, 4) if total else 0,
                "Avg Processing Days": round(values["Total Processing Days"] / total, 2) if total else 0,
                "Total Time Saved Min": values["Total Time Saved Min"],
            }
        )

    return validated, exceptions, summary_rows, rule_summary, department_summary


def map_action(issue: str) -> str:
    actions = {
        "MISSING_REQUEST_ID": "Add a unique request ID",
        "DUPLICATE_REQUEST_ID": "Investigate duplicate request and merge or reassign ID",
        "MISSING_REQUEST_TYPE": "Update the request category",
        "MISSING_OWNER": "Assign an owner",
        "MISSING_DUE_DATE": "Add or correct the due date",
        "INVALID_PRIORITY": "Select an approved priority value",
        "INVALID_STATUS": "Select an approved status value",
        "PRIORITY_MISMATCH": "Review urgency and adjust due date or priority",
        "SLA_BREACH": "Escalate overdue request",
        "PROCESSING_DELAY": "Review blockers and next action",
        "FAILED_WITHOUT_REASON": "Add failure reason for audit trail",
        "COMPLETED_WITHOUT_DATE": "Add completion date",
        "STATUS_STAGE_MISMATCH": "Align request status with workflow stage",
        "BOTTLENECK_STAGE": "Review stuck workflow stage and unblock owner",
    }
    return actions.get(issue, "Review request")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw_requests.csv"))
    parser.add_argument("--validated-output", type=Path, default=Path("data/validated_requests.csv"))
    parser.add_argument("--exception-output", type=Path, default=Path("data/exception_log.csv"))
    parser.add_argument("--summary-output", type=Path, default=Path("data/validation_summary.csv"))
    parser.add_argument("--rule-output", type=Path, default=Path("data/rule_summary.csv"))
    parser.add_argument("--department-output", type=Path, default=Path("data/department_summary.csv"))
    args = parser.parse_args()

    rows = read_csv(args.input)
    validated, exceptions, summary, rules, departments = validate_requests(rows)
    write_csv(validated, args.validated_output)
    write_csv(exceptions, args.exception_output)
    write_csv(summary, args.summary_output)
    write_csv(rules, args.rule_output)
    write_csv(departments, args.department_output)
    print(f"Validated {len(validated)} requests")
    print(f"Exceptions flagged: {len(exceptions)}")
    print(f"Summary exported to {args.summary_output}")


if __name__ == "__main__":
    main()
