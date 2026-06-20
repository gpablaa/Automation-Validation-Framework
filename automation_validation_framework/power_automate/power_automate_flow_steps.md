# Power Automate Flow Summary

## Flow Name

Automation Validation Scheduler

## Purpose

This Power Automate flow was created to support the Automation Validation Framework by triggering notifications when validation exceptions are identified in the workflow data. The flow reads the Exception Log generated from the Python validation framework and sends an alert for flagged issues that require follow-up.

## Workflow Overview

The flow follows this process:

1. **Recurrence Trigger**
   The flow runs on a scheduled basis to check for new or existing validation exceptions.

2. **List Rows Present in a Table**
   The flow connects to the Excel workbook `Automation_Validation_Framework.xlsx` stored in OneDrive and reads rows from `ExceptionLogTable`.

3. **Apply to Each**
   Each row in the Exception Log is processed individually so that every exception can be reviewed and handled separately.

4. **Condition Check**
   The flow checks whether the exception has already been marked as notified using the `Notification Sent` field. This logic helps prevent duplicate notifications for the same exception.

5. **Send Mobile Notification**
   For exceptions that have not already been notified, the flow sends a mobile notification containing key exception details such as workflow stage, issue code, severity, action needed, and stakeholder reference.

## Notification Message Fields

The notification includes the following fields from the Exception Log:

* Workflow Stage
* Issue Code
* Severity
* Action Needed
* Stakeholder Email

## Example Notification

Validation exception logged.

Workflow Stage: In Progress
Issue Code: SLA_BREACH
Severity: High
Action Needed: Escalate overdue request
Stakeholder Email: [stakeholder6@example.com](mailto:stakeholder6@example.com)

Please review this item in the Exception Log.

## Tools Used

* Microsoft Power Automate
* Excel Online
* OneDrive
* Power Automate Mobile Notifications
* Python-generated validation outputs

## Testing Notes

The flow was tested using Power Automate mobile notifications due to account-level email connector authorization limitations. The notification logic successfully demonstrated that exception records from the Excel-based Exception Log could trigger automated alerts.

In a production environment, this same logic could be routed to Outlook email, Microsoft Teams, or stakeholder distribution lists.

## Business Value

This flow reduces manual follow-up effort by automatically notifying users when validation exceptions are detected. Instead of manually reviewing every request row, stakeholders can be alerted when specific issues appear, such as:

* SLA breaches
* Missing owners
* Processing delays
* Priority mismatches
* Workflow bottlenecks
* Status-stage mismatches

## Production Enhancement

For a real business environment, the Excel workbook could be replaced with a SharePoint List or Dataverse table. This would make row updates, notification tracking, and duplicate prevention more reliable by using built-in item IDs and stronger workflow tracking.
