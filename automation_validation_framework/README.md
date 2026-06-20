# Automation Validation Framework

Portfolio project: **Automation Validation Framework | Python, Power Automate, Excel, Power BI, GitHub Copilot**

This project simulates a request-intake and validation workflow for an engineering/business operations environment. It includes a Python pipeline, generated sample data, validation outputs, an Excel tracker workbook, and setup guides for Power Automate and Power BI.

## What this project demonstrates

- Python data generation and validation logic
- Automated checks for missing fields, SLA breaches, priority mismatches, duplicate requests, processing delays, and bottleneck stages
- Excel request intake/tracking with dashboard-ready output tabs
- Power Automate alert-routing concept for failed validations and critical requests
- Power BI dashboard design for request status, processing time, validation failures, bottlenecks, and estimated efficiency gains
- AI-assisted coding workflow using ChatGPT and GitHub Copilot for prototyping, debugging, documentation, and iteration


## How to run

From the project folder:

```bash
python3 scripts/run_pipeline.py
```

This regenerates the raw request data and validation outputs in the `data/` folder.

