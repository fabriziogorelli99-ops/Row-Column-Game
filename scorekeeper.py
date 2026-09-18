# scorekeeper.py
import csv
import os
from datetime import datetime
from typing import Dict, List

# --- File fields and location ----------------------------------------------

HISTORY_FILENAME = "history.csv"
FIELDNAMES = ["date", "match", "a_score", "b_score", "winner", "rounds", "mode"]

def _history_path() -> str:
    """History file path (same directory as main scripts)."""
    return os.path.join(os.path.dirname(__file__), HISTORY_FILENAME)

# --- History file origination ----------------------------------------------

def _ensure_file_exists() -> None:
    """Create CSV with header if missing."""
    path = _history_path()
    if not os.path.exists(path):
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            
# --- History file operations ----------------------------------------------

def append_result(*, match: str, a_score: int, b_score: int, winner: str, rounds: int, mode: str) -> None:
    """
    Append one game result.
    - date: Y-M-D H:M
    - match: e.g. "Alice VS Bob"
    - a_score, b_score: integers
    - winner: "A" | "B" | "Tie"
    - rounds: number of rounds shown by the board UI
    - mode: "H_VS_H" | "H_VS_C" | "C_VS_C"
    """
    _ensure_file_exists()
    path = _history_path()
    row = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "match": match,
        "a_score": str(a_score),
        "b_score": str(b_score),
        "winner": winner,
        "rounds": str(rounds),
        "mode": mode,
    }
    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)

def read_history() -> List[Dict[str, str]]:
    """
    Read all history rows as a list of dicts (may be empty).
    Fields are strings, matching FIELDNAMES.
    """
    path = _history_path()
    if not os.path.exists(path):
        return []
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Only keep expected fields; ignore extra/unknown columns gracefully
        rows: List[Dict[str, str]] = []
        for r in reader:
            rows.append({k: r.get(k, "") for k in FIELDNAMES})
        return rows
