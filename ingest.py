import argparse
import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Dict, Any, Tuple

DB_FILE = "esm_operator.db"
SUPPORTED_TABLES = {
    "Aircraft",
    "Facility",
    "GroundUnit",
    "Submarine",
    "Ship",
    "Satellite",
    "Weapon",
    "Platform",
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest data into the ESM database")
    sub = parser.add_subparsers(dest="command", required=True)

    csv_p = sub.add_parser("csv", help="Load a CSV file")
    csv_p.add_argument("table", choices=SUPPORTED_TABLES)
    csv_p.add_argument("path", type=Path)

    json_p = sub.add_parser("json", help="Load a JSON array file")
    json_p.add_argument("table", choices=SUPPORTED_TABLES)
    json_p.add_argument("path", type=Path)

    return parser.parse_args()


def load_csv(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield row

def load_json(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("JSON must be an array of objects")
    for row in data:
        if isinstance(row, dict):
            yield row
        else:
            raise ValueError("JSON array must contain objects")

def get_schema(conn: sqlite3.Connection, table: str) -> Tuple[list, Dict[str, str]]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    columns = []
    types: Dict[str, str] = {}
    for _, name, col_type, *_ in cur.fetchall():
        columns.append(name)
        types[name] = col_type.upper()
    return columns, types

def coerce(value: Any, col_type: str) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
    if value == "":
        return None
    try:
        if "INT" in col_type:
            return int(value)
        if "REAL" in col_type or "FLOA" in col_type or "DOUB" in col_type:
            return float(value)
    except ValueError:
        raise ValueError("non-numeric data")
    return value

def ingest_rows(conn: sqlite3.Connection, table: str, rows: Iterable[Dict[str, Any]]) -> Tuple[int, int, int, list]:
    columns, types = get_schema(conn, table)
    writable = [c for c in columns if c not in {"id", "created_at", "updated_at"}]
    if table == "Platform" and "PlatformName" in columns:
        key_cols = ["PlatformName"]
    elif "Name" in columns:
        key_cols = ["Name"]
    else:
        key_cols = writable

    inserted = updated = skipped = 0
    errors = []

    for idx, row in enumerate(rows, start=1):
        unknown = set(row.keys()) - set(writable)
        for col in unknown:
            print(f"Warning: ignoring unknown column '{col}'")

        data: Dict[str, Any] = {}
        row_errors = []
        for col in writable:
            val = row.get(col)
            try:
                data[col] = coerce(val, types[col])
            except ValueError:
                row_errors.append(f"{col} expects numeric")
        if any(data.get(k) is None for k in key_cols):
            row_errors.append("missing required key columns")
        if row_errors:
            skipped += 1
            errors.append((idx, "; ".join(row_errors)))
            continue
        cur = conn.cursor()
        where = " AND ".join([f"{k}=?" for k in key_cols])
        existing = cur.execute(
            f"SELECT id, created_at FROM {table} WHERE {where}",
            [data[k] for k in key_cols],
        ).fetchone()
        now = datetime.now(timezone.utc).isoformat()
        if existing:
            row_id, created_at = existing
        else:
            row_id = None
            created_at = now
        cols = ["id"] + writable + ["created_at", "updated_at"]
        values = [row_id] + [data[c] for c in writable] + [created_at, now]
        placeholders = ",".join(["?"] * len(cols))
        cur.execute(
            f"INSERT OR REPLACE INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
            values,
        )
        if existing:
            updated += 1
        else:
            inserted += 1
    conn.commit()
    return inserted, updated, skipped, errors

def main() -> None:
    args = parse_args()
    loader = load_csv if args.command == "csv" else load_json
    rows = loader(args.path)
    with sqlite3.connect(DB_FILE) as conn:
        inserted, updated, skipped, errors = ingest_rows(conn, args.table, rows)
    print(f"Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}")
    for idx, msg in errors:
        print(f"Row {idx} skipped: {msg}")

if __name__ == "__main__":
    main()
