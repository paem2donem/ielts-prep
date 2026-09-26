import sqlite3
import datetime
import pandas as pd
from typing import List, Dict, Any, Optional

DB_FILE = "tracker.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mode TEXT DEFAULT 'cyber',
            module TEXT,
            task_type TEXT,
            score REAL,
            raw_score TEXT,
            feedback TEXT
        )
    ''')
    # Check and add missing columns if upgrading from old database
    cursor.execute("PRAGMA table_info(scores)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if "mode" not in existing_cols:
        cursor.execute("ALTER TABLE scores ADD COLUMN mode TEXT DEFAULT 'cyber'")
    if "raw_score" not in existing_cols:
        cursor.execute("ALTER TABLE scores ADD COLUMN raw_score TEXT DEFAULT ''")

    conn.commit()
    conn.close()

def save_score_record(module: str, task_type: str, score: float, feedback: str, mode: str = "cyber", raw_score: str = "") -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO scores (date, mode, module, task_type, score, raw_score, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (date_str, mode, module, task_type, float(score), raw_score, feedback)
    )
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id

def get_all_scores(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scores ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_analytics_summary() -> Dict[str, Any]:
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM scores ORDER BY id ASC", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()

    if df.empty:
        return {
            "total_tests": 0,
            "overall_average": 0.0,
            "module_averages": {
                "Listening": 0.0,
                "Reading": 0.0,
                "Writing": 0.0,
                "Speaking": 0.0
            },
            "history": []
        }

    module_avgs = {}
    for mod in ["Listening", "Reading", "Writing", "Speaking"]:
        subset = df[df["module"].str.lower() == mod.lower()]
        if not subset.empty:
            module_avgs[mod] = round(float(subset["score"].mean()), 2)
        else:
            module_avgs[mod] = 0.0

    overall_avg = round(float(df["score"].mean()), 2)

    history = []
    for _, row in df.tail(15).iterrows():
        history.append({
            "id": int(row["id"]),
            "date": str(row["date"]),
            "module": str(row["module"]),
            "task_type": str(row["task_type"]),
            "score": float(row["score"]),
            "mode": str(row.get("mode", "cyber"))
        })

    return {
        "total_tests": len(df),
        "overall_average": overall_avg,
        "module_averages": module_avgs,
        "history": history
    }

init_db()
