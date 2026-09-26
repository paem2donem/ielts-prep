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

    # 5. Global Questions Table (Herkes için soru bankası)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            mode TEXT,
            module TEXT,
            source TEXT,
            passage_or_script TEXT,
            prompt TEXT,
            q_type TEXT,
            options_json TEXT,
            answer TEXT,
            accepted_json TEXT,
            explanation TEXT,
            trick_tip TEXT,
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

def sync_all_exam_questions(exam_data: Dict[str, Any]):
    """Syncs questions from exam_data.py into the questions SQLite table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for mode_key, mode_val in exam_data.items():
        mode_title = mode_val.get("title", mode_key)

        # 1. Reading
        reading_dict = mode_val.get("reading", {})
        for p_key, passage in reading_dict.items():
            source = passage.get("title", p_key)
            text = passage.get("text", "")
            for q in passage.get("questions", []):
                q_id = q.get("id", f"{mode_key}_{p_key}_{q.get('prompt', '')[:10]}")
                cursor.execute('''
                    INSERT OR REPLACE INTO questions 
                    (id, mode, module, source, passage_or_script, prompt, q_type, options_json, answer, accepted_json, explanation, trick_tip, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    q_id,
                    mode_key,
                    "Reading",
                    source,
                    text,
                    q.get("prompt", ""),
                    q.get("type", "tfng").upper(),
                    json.dumps(q.get("options", ["TRUE", "FALSE", "NOT GIVEN"])),
                    q.get("answer", ""),
                    json.dumps([q.get("answer", "")]),
                    q.get("explanation", ""),
                    q.get("trick_tip", "Soru kökündeki aşırı niteleyicilere (always, completely, only) dikkat edin."),
                    now_str
                ))

        # 2. Listening
        listening_dict = mode_val.get("listening", {})
        for s_key, section in listening_dict.items():
            source = section.get("title", s_key)
            script = section.get("audio_script", "")
            for q in section.get("questions", []):
                q_id = q.get("id", f"{mode_key}_{s_key}_{q.get('prompt', '')[:10]}")
                cursor.execute('''
                    INSERT OR REPLACE INTO questions 
                    (id, mode, module, source, passage_or_script, prompt, q_type, options_json, answer, accepted_json, explanation, trick_tip, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    q_id,
                    mode_key,
                    "Listening",
                    source,
                    script,
                    q.get("prompt", ""),
                    q.get("type", "fill").upper(),
                    json.dumps(q.get("options", [])),
                    q.get("answer", ""),
                    json.dumps(q.get("accepted", [q.get("answer", "")])),
                    q.get("explanation", "Ses kaydındaki çeldirici veya son dakika düzeltmelerine dikkat ediniz."),
                    q.get("trick_tip", "Listening çeldiricisi: Konuşmacının fikrini değiştirdiği veya düzelttiği cümlelere odaklanın."),
                    now_str
                ))

        # 3. Writing
        writing_dict = mode_val.get("writing", {})
        for w_key, task in writing_dict.items():
            q_id = f"{mode_key}_{w_key}"
            source = f"{mode_title} - {task.get('title', w_key)}"
            is_task1 = ("task_1" in w_key)
            cursor.execute('''
                INSERT OR REPLACE INTO questions 
                (id, mode, module, source, passage_or_script, prompt, q_type, options_json, answer, accepted_json, explanation, trick_tip, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                q_id,
                mode_key,
                "Writing",
                source,
                task.get("data_context", task.get("prompt", "")),
                task.get("prompt", ""),
                "Task 1 (Report - 150w)" if is_task1 else "Task 2 (Essay - 250w)",
                json.dumps([]),
                "Model Band 8.5 Academic Response" if not is_task1 else "Accurate Data Comparison & Trend Summary",
                json.dumps([]),
                "IELTS Writing 4 Kriter: Task Achievement/Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy.",
                "Paragrafları PEEL formatında kurgulayın: Point, Evidence, Explanation, Link.",
                now_str
            ))

        # 4. Speaking
        speaking_dict = mode_val.get("speaking", {})
        if "part_1" in speaking_dict:
            p1 = speaking_dict["part_1"]
            for idx, q_text in enumerate(p1.get("questions", [])):
                q_id = f"{mode_key}_spk_p1_{idx+1}"
                cursor.execute('''
                    INSERT OR REPLACE INTO questions 
                    (id, mode, module, source, passage_or_script, prompt, q_type, options_json, answer, accepted_json, explanation, trick_tip, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    q_id,
                    mode_key,
                    "Speaking",
                    f"{mode_title} - Part 1",
                    "Giriş ve Genel Konuşma Bölümü (4-5 dakika)",
                    q_text,
                    "Part 1 (Short Answer)",
                    json.dumps([]),
                    "Akıcı, doğal ve 2-3 cümlelik net açıklama",
                    json.dumps([]),
                    "Sorulara direkt cevap verin, ardından nedenini veya kısa bir örneği ekleyin.",
                    "Bağlaç kullanımı (actually, well, generally speaking) akıcılık puanını yükseltir.",
                    now_str
                ))

        if "part_2" in speaking_dict:
            p2 = speaking_dict["part_2"]
            q_id = f"{mode_key}_spk_p2"
            cursor.execute('''
                INSERT OR REPLACE INTO questions 
                (id, mode, module, source, passage_or_script, prompt, q_type, options_json, answer, accepted_json, explanation, trick_tip, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                q_id,
                mode_key,
                "Speaking",
                f"{mode_title} - Part 2 Cue Card",
                "1 dakika hazırlık süresi, 2 dakika kesintisiz bireysel konuşma.",
                p2.get("cue_card", ""),
                "Part 2 (Cue Card)",
                json.dumps([]),
                "Kesintisiz 2 dakikalık C1-C2 seviyesinde yapılandırılmış monolog",
                json.dumps([]),
                "Karttaki 4 maddenin tamamına değinilmeli, geçmiş zaman ve hikayeleştirme teknikleri kullanılmalıdır.",
                "Hazırlık süresinde tam cümleler değil, yalnızca anahtar kelimeler ve idiyomlar not alınmalıdır.",
                now_str
            ))

        if "part_3" in speaking_dict:
            p3 = speaking_dict["part_3"]
            for idx, q_text in enumerate(p3.get("questions", [])):
                q_id = f"{mode_key}_spk_p3_{idx+1}"
                cursor.execute('''
                    INSERT OR REPLACE INTO questions 
                    (id, mode, module, source, passage_or_script, prompt, q_type, options_json, answer, accepted_json, explanation, trick_tip, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    q_id,
                    mode_key,
                    "Speaking",
                    f"{mode_title} - Part 3 Discussion",
                    "Derinlemesine ve Soyut Tartışma Bölümü (4-5 dakika)",
                    q_text,
                    "Part 3 (Analytical Discussion)",
                    json.dumps([]),
                    "Analitik argüman, varsayımsal gramer yapıları (would, might, should)",
                    json.dumps([]),
                    "Kişisel örnekler yerine küresel, toplumsal ve akademik bir bakış açısı sunulmalıdır.",
                    "Zıt görüşleri ele alıp çürüten cümle kalıpları (While some argue..., it is indisputable that...) kullanılmalıdır.",
                    now_str
                ))

    conn.commit()
    conn.close()

def get_all_questions_list(module: Optional[str] = None, mode: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns all questions with flexible filtering and search for the candidate's question bank."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM questions WHERE 1=1"
    params = []

    if module and module != "all":
        query += " AND module = ?"
        params.append(module)

    if mode and mode != "all":
        query += " AND mode = ?"
        params.append(mode)

    if search:
        query += " AND (prompt LIKE ? OR source LIKE ? OR answer LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    query += " ORDER BY module ASC, source ASC, id ASC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        try:
            d["options"] = json.loads(d.get("options_json") or "[]")
        except:
            d["options"] = []
        try:
            d["accepted"] = json.loads(d.get("accepted_json") or "[]")
        except:
            d["accepted"] = []
        results.append(d)

    return results

init_db()
