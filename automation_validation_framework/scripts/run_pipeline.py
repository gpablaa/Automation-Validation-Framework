"""Run the complete data-generation and validation pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print("Running:", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run([sys.executable, "scripts/generate_request_data.py", "--rows", "525", "--output", "data/raw_requests.csv"])
    run([sys.executable, "scripts/validation_framework.py", "--input", "data/raw_requests.csv"])
    print("Pipeline complete. Outputs are in the data folder.")


if __name__ == "__main__":
    main()
