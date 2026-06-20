# Validation Rules

The Python framework applies the following validation checks.

| Rule | Issue Code | What it flags | Example action |
|---|---|---|---|
| Missing request ID | MISSING_REQUEST_ID | Request has no unique ID | Add unique ID |
| Duplicate request ID | DUPLICATE_REQUEST_ID | Same ID appears more than once | Investigate duplicate |
| Missing request type | MISSING_REQUEST_TYPE | Blank request category | Update category |
| Missing owner | MISSING_OWNER | No assigned owner | Assign owner |
| Missing due date | MISSING_DUE_DATE | Due date is blank or invalid | Add deadline |
| Invalid priority | INVALID_PRIORITY | Priority outside approved values | Select Low, Medium, High, or Critical |
| Invalid status | INVALID_STATUS | Status outside approved values | Select approved status |
| Priority mismatch | PRIORITY_MISMATCH | Critical request has due date outside 2-day SLA | Review priority or due date |
| SLA breach | SLA_BREACH | Request completed late or currently past due | Escalate overdue request |
| Processing delay | PROCESSING_DELAY | Open request exceeds expected processing time | Review blockers |
| Failed without reason | FAILED_WITHOUT_REASON | Failed request has no reason | Add failure reason |
| Completed without date | COMPLETED_WITHOUT_DATE | Completed request has no completion date | Add completion date |
| Status/stage mismatch | STATUS_STAGE_MISMATCH | Completed request is not in expected workflow stage | Align status and stage |
| Bottleneck stage | BOTTLENECK_STAGE | Request appears stuck in review/blocked stage | Unblock owner or escalate |

## Severity logic

High severity includes SLA breaches, duplicate IDs, priority mismatches, failed requests without a reason, and bottleneck stages.

Medium severity includes missing owners, missing due dates, processing delays, completed-without-date issues, and status/stage mismatches.

Low severity includes remaining issues that should be corrected but are less urgent.

## Estimated efficiency logic

Manual review reduction is calculated as:

```
Estimated Reduction = (Manual Review Minutes - Automated Review Minutes) / Manual Review Minutes
```

The generated dataset creates manual and automated review time assumptions per request so the improvement can be summarized across 500+ simulated requests.
