import sqlite3
import datetime
import json
import pandas as pd
from typing import List, Dict, Any, Optional

DB_FILE = "tracker.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Scores Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT DEFAULT 'guest@forensync.academy',
            date TEXT,
            mode TEXT DEFAULT 'cyber',
            module TEXT,
            task_type TEXT,
            score REAL,
            raw_score TEXT,
            feedback TEXT
        )
    ''')

    # Schema migration for existing scores table
    cursor.execute("PRAGMA table_info(scores)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if "user_email" not in existing_cols:
        cursor.execute("ALTER TABLE scores ADD COLUMN user_email TEXT DEFAULT 'guest@forensync.academy'")
    if "mode" not in existing_cols:
        cursor.execute("ALTER TABLE scores ADD COLUMN mode TEXT DEFAULT 'cyber'")
    if "raw_score" not in existing_cols:
        cursor.execute("ALTER TABLE scores ADD COLUMN raw_score TEXT DEFAULT ''")

    # 2. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            target_band REAL DEFAULT 7.5,
            created_at TEXT,
            last_active TEXT
        )
    ''')

    # 3. User Mistakes (Yanlış Defteri / Error Notebook)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_mistakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            module TEXT,
            question_prompt TEXT,
            user_answer TEXT,
            correct_answer TEXT,
            explanation TEXT,
            trick_tip TEXT,
            date TEXT,
            resolved INTEGER DEFAULT 0
        )
    ''')

    # 4. Dynamic AI Question Bank
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_bank (
            id TEXT PRIMARY KEY,
            mode TEXT,
            module TEXT,
            title TEXT,
            payload_json TEXT,
            created_at TEXT
        )
    ''')

    conn.commit()
    conn.close()

# User Management
def get_or_create_user(email: str, name: Optional[str] = None) -> Dict[str, Any]:
    email = email.strip().lower()
    if not name:
        name = email.split('@')[0].capitalize()
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user:
        cursor.execute("UPDATE users SET last_active = ? WHERE email = ?", (now_str, email))
        user_dict = dict(user)
    else:
        cursor.execute(
            "INSERT INTO users (email, name, target_band, created_at, last_active) VALUES (?, ?, 7.5, ?, ?)",
            (email, name, now_str, now_str)
        )
        user_dict = {
            "email": email,
            "name": name,
            "target_band": 7.5,
            "created_at": now_str,
            "last_active": now_str
        }

    conn.commit()
    conn.close()
    return user_dict

# Score Records
def save_score_record(module: str, task_type: str, score: float, feedback: str, mode: str = "cyber", raw_score: str = "", user_email: str = "guest@forensync.academy") -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO scores (user_email, date, mode, module, task_type, score, raw_score, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_email.lower(), date_str, mode, module, task_type, float(score), raw_score, feedback)
    )
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id

# Mistake Notebook (Yanlış Defteri)
def record_mistake(user_email: str, module: str, prompt: str, user_ans: str, correct_ans: str, explanation: str, trick: str = ""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO user_mistakes (user_email, module, question_prompt, user_answer, correct_answer, explanation, trick_tip, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_email.lower(), module, prompt, user_ans, correct_ans, explanation, trick, date_str)
    )
    conn.commit()
    conn.close()

def get_user_mistakes(user_email: str, unresolved_only: bool = True) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM user_mistakes WHERE user_email = ?"
    if unresolved_only:
        query += " AND resolved = 0"
    query += " ORDER BY id DESC LIMIT 50"
    
    cursor.execute(query, (user_email.lower(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Analytics Summary per User
def get_user_analytics(user_email: str) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM scores WHERE LOWER(user_email) = ? ORDER BY id ASC", conn, params=(user_email.lower(),))
    except Exception:
        df = pd.DataFrame()

    mistakes_count = 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_mistakes WHERE LOWER(user_email) = ? AND resolved = 0", (user_email.lower(),))
        mistakes_count = cursor.fetchone()[0]
    except Exception:
        pass

    conn.close()

    if df.empty:
        return {
            "total_tests": 0,
            "overall_average": 0.0,
            "module_averages": {"Listening": 0.0, "Reading": 0.0, "Writing": 0.0, "Speaking": 0.0},
            "mistakes_count": mistakes_count,
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
        "mistakes_count": mistakes_count,
        "history": history
    }

# Question Bank
def save_generated_question(q_id: str, mode: str, module: str, title: str, payload: dict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT OR REPLACE INTO question_bank (id, mode, module, title, payload_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (q_id, mode, module, title, json.dumps(payload), now_str)
    )
    conn.commit()
    conn.close()

def get_generated_questions(module: str, mode: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, mode, module, title, payload_json, created_at FROM question_bank WHERE module = ? AND mode = ? ORDER BY created_at DESC",
        (module, mode)
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        item = dict(r)
        item["payload"] = json.loads(item["payload_json"])
        results.append(item)
    return results

init_db()
