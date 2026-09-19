from __future__ import annotations

import csv
from pathlib import Path

from flowforge import analyze_intake, insert_result
from flowforge.db import clear


def main() -> None:
    clear()
    path = Path("sample_data/demo_requests.csv")
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            result = analyze_intake(row["source"], row["subject"], row["text"])
            insert_result(result.to_dict())
    print("Demo data loaded into data/flowforge.db")


if __name__ == "__main__":
    main()
