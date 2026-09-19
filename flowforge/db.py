from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DEFAULT_DB = Path("data/flowforge.db")


def connect(path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            source TEXT NOT NULL,
            subject TEXT NOT NULL,
            category TEXT NOT NULL,
            priority_score INTEGER NOT NULL,
            priority_label TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            suggested_owner TEXT NOT NULL,
            suggested_action TEXT NOT NULL,
            text TEXT NOT NULL,
            metadata_json TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def insert_result(result: dict, path: str | Path = DEFAULT_DB) -> int:
    metadata = {
        "emails": result.get("emails", []),
        "phones": result.get("phones", []),
        "monetary_values": result.get("monetary_values", []),
        "reference_ids": result.get("reference_ids", []),
    }
    with connect(path) as conn:
        cur = conn.execute(
            """
            INSERT INTO intake (
                created_at, source, subject, category, priority_score,
                priority_label, sentiment, suggested_owner,
                suggested_action, text, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result["created_at"], result["source"], result["subject"], result["category"],
                result["priority_score"], result["priority_label"], result["sentiment"],
                result["suggested_owner"], result["suggested_action"], result["text"],
                json.dumps(metadata),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_results(path: str | Path = DEFAULT_DB, limit: int = 200) -> list[dict]:
    with connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM intake ORDER BY priority_score DESC, id DESC LIMIT ?", (limit,)
        ).fetchall()
    output = []
    for row in rows:
        item = dict(row)
        item.update(json.loads(item.pop("metadata_json")))
        output.append(item)
    return output


def clear(path: str | Path = DEFAULT_DB) -> None:
    with connect(path) as conn:
        conn.execute("DELETE FROM intake")
        conn.commit()
