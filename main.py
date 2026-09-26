import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database
from exam_data import EXAM_DATA
from tricks_data import IELTS_TRICKS
from services import ai_service

app = FastAPI(
    title="IELTS - Band 7.5+ Master Prep Suite",
    description="Intelligent Cambridge IELTS & Cyber Forensics Training Suite with Dynamic AI Exam Generation & Personal Guidance",
    version="3.0.0"
)

# Startup sync for database question bank
@app.on_event("startup")
async def startup_event():
    try:
        database.sync_all_exam_questions(EXAM_DATA)
    except Exception as e:
        print(f"Initial questions sync notice: {e}")

# Enable CORS for mobile browsers and remote hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates configuration
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "audio").mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Request Models
class LoginRequest(BaseModel):
    email: str
    name: Optional[str] = None

class WritingRequest(BaseModel):
    essay_text: str
    task_type: str = "Task 2"
    mode: str = "cyber"
    prompt_context: str = ""
    user_email: str = "paem2.donem@gmail.com"

class ReadingSubmission(BaseModel):
    mode: str = "cyber"
    passage_id: str = "passage_1"
    answers: Dict[str, str]
    user_email: str = "paem2.donem@gmail.com"
    custom_passage: Optional[Dict[str, Any]] = None

class ListeningSubmission(BaseModel):
    mode: str = "cyber"
    section_id: str = "section_1"
    answers: Dict[str, str]
    user_email: str = "paem2.donem@gmail.com"

class MentorRequest(BaseModel):
    mode: str = "cyber"
    user_email: str = "paem2.donem@gmail.com"

class GenerateExamRequest(BaseModel):
    module: str = "reading" # "reading" or "writing"
    mode: str = "cyber"
    task_type: Optional[str] = "Task 2"


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Index template not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

# Auth & User Profile
@app.post("/api/auth/login")
async def login_user(req: LoginRequest):
    if not req.email or "@" not in req.email:
        raise HTTPException(status_code=400, detail="Geçerli bir e-posta adresi girin.")
    user = database.get_or_create_user(email=req.email, name=req.name)
    stats = database.get_user_analytics(req.email)
    return {"success": True, "user": user, "stats": stats}

@app.get("/api/user/analytics")
async def user_analytics(email: str = "paem2.donem@gmail.com"):
    return database.get_user_analytics(email)

@app.get("/api/user/mistakes")
async def user_mistakes(email: str = "paem2.donem@gmail.com"):
    mistakes = database.get_user_mistakes(email)
    return {"mistakes": mistakes}

# All Questions Table for Candidate's Account & Bank
@app.get("/api/questions")
async def get_questions_endpoint(module: Optional[str] = None, mode: Optional[str] = None, search: Optional[str] = None):
    items = database.get_all_questions_list(module=module, mode=mode, search=search)
    return {"total": len(items), "questions": items}

# Tricks and Masterclass Library
@app.get("/api/tricks")
async def get_tricks():
    return IELTS_TRICKS

# Dynamic AI Exam Generation
@app.post("/api/exam/generate")
async def generate_exam(req: GenerateExamRequest):
    try:
        if req.module == "reading":
            new_test = ai_service.generate_dynamic_reading_test(mode=req.mode)
            q_id = f"ai_reading_{uuid.uuid4().hex[:8]}"
            database.save_generated_question(
                q_id=q_id,
                mode=req.mode,
                module="reading",
                title=new_test["title"],
                payload=new_test
            )
            # Soru bankasına da kaydet
            try:
                import sqlite3, json, datetime
                conn = sqlite3.connect(database.DB_FILE)
                c = conn.cursor()
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for q in new_test.get("questions", []):
                    c.execute('''
                        INSERT OR REPLACE INTO questions 
                        (id, mode, module, source, passage_or_script, prompt, q_type, options_json, answer, accepted_json, explanation, trick_tip, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"{q_id}_{q.get('id', 'q')}",
                        req.mode,
                        "Reading",
                        f"AI Sınavı - {new_test.get('title', 'Okuma')}",
                        new_test.get("text", ""),
                        q.get("prompt", ""),
                        "TFNG",
                        json.dumps(q.get("options", ["TRUE", "FALSE", "NOT GIVEN"])),
                        q.get("answer", ""),
                        json.dumps([q.get("answer", "")]),
                        q.get("explanation", ""),
                        q.get("trick_tip", ""),
                        now_str
                    ))
                conn.commit()
                conn.close()
            except Exception:
                pass
            return {"success": True, "test_id": q_id, "data": new_test}
        elif req.module == "writing":
            new_prompt = ai_service.generate_dynamic_writing_prompt(task_type=req.task_type or "Task 2", mode=req.mode)
            q_id = f"ai_writing_{uuid.uuid4().hex[:8]}"
            database.save_generated_question(
                q_id=q_id,
                mode=req.mode,
                module="writing",
                title=new_prompt["title"],
                payload=new_prompt
            )
            # Soru bankasına kaydet
            try:
                import sqlite3, json, datetime
                conn = sqlite3.connect(database.DB_FILE)
                c = conn.cursor()
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute('''
                    INSERT OR REPLACE INTO questions 
                    (id, mode, module, source, passage_or_script, prompt, q_type, options_json, answer, accepted_json, explanation, trick_tip, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    q_id,
                    req.mode,
                    "Writing",
                    f"AI Görevi - {new_prompt.get('title', req.task_type)}",
                    f"Min kelime: {new_prompt.get('min_words', 250)} | Anahtar kelimeler: {', '.join(new_prompt.get('key_vocabulary_tips', []))}",
                    new_prompt.get("prompt", ""),
                    req.task_type or "Task 2",
                    json.dumps([]),
                    "Model Band 8.5 Response",
                    json.dumps([]),
                    "Yapay zeka tarafından üretilen özgün kompozisyon konusu.",
                    "Zaman yönetimi: Task 2 için 40 dakika ayırın, en az 250 kelime yazın.",
                    now_str
                ))
                conn.commit()
                conn.close()
            except Exception:
                pass
            return {"success": True, "test_id": q_id, "data": new_prompt}
        else:
            raise HTTPException(status_code=400, detail="Module not supported for generation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sınav üretilemedi: {str(e)}")

# Standard Exam Data
@app.get("/api/exam-data/{mode}")
async def get_exam_content(mode: str):
    if mode not in EXAM_DATA:
        mode = "cyber"
    return EXAM_DATA[mode]

# Evaluation Endpoints
@app.post("/api/evaluate/writing")
async def evaluate_writing_endpoint(req: WritingRequest):
    result = ai_service.evaluate_writing_submission(
        essay_text=req.essay_text,
        task_type=req.task_type,
        mode=req.mode,
        prompt_context=req.prompt_context
    )
    if result.get("success"):
        score = result["score"]
        database.save_score_record(
            module="Writing",
            task_type=req.task_type,
            score=score,
            feedback=result["feedback"],
            mode=req.mode,
            raw_score=f"{result['word_count']} kelime",
            user_email=req.user_email
        )
    return result

@app.post("/api/evaluate/speaking")
async def evaluate_speaking_endpoint(
    audio: UploadFile = File(...),
    part: str = Form("Part 2"),
    mode: str = Form("cyber"),
    prompt_context: str = Form(""),
    user_email: str = Form("guest@forensync.academy")
):
    suffix = Path(audio.filename or "recording.webm").suffix or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_path = tmp_file.name
        shutil.copyfileobj(audio.file, tmp_file)

    try:
        result = ai_service.evaluate_speaking_submission(
            audio_file_path=tmp_path,
            part=part,
            mode=mode,
            prompt_context=prompt_context
        )
        if result.get("success"):
            score = result["score"]
            database.save_score_record(
                module="Speaking",
                task_type=part,
                score=score,
                feedback=result["feedback"],
                mode=mode,
                raw_score=f"Band {score}",
                user_email=user_email
            )
        return result
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

@app.post("/api/grade/reading")
async def grade_reading_endpoint(sub: ReadingSubmission):
    if sub.custom_passage and "questions" in sub.custom_passage:
        questions = sub.custom_passage["questions"]
    else:
        mode_data = EXAM_DATA.get(sub.mode, EXAM_DATA["cyber"])
        passage = mode_data["reading"].get(sub.passage_id, mode_data["reading"]["passage_1"])
        questions = passage["questions"]

    correct_count = 0
    total_q = len(questions)
    breakdown = []

    for q in questions:
        q_id = q["id"]
        user_ans = (sub.answers.get(q_id) or "").strip().upper()
        correct_ans = q["answer"].strip().upper()
        is_correct = (user_ans == correct_ans)
        if is_correct:
            correct_count += 1
        else:
            # Otomatik Yanlış Defterine Kaydet!
            database.record_mistake(
                user_email=sub.user_email,
                module="Reading",
                prompt=q["prompt"],
                user_ans=user_ans or "Boş",
                correct_ans=correct_ans,
                explanation=q.get("explanation", ""),
                trick=q.get("trick_tip", "Soru kökündeki anahtar kelimeler ve metindeki eşanlamlılar (paraphrasing) tekrar incelenmeli.")
            )

        breakdown.append({
            "id": q_id,
            "prompt": q["prompt"],
            "user_answer": user_ans or "Boş",
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
            "trick_tip": q.get("trick_tip", "")
        })

    scale = {4: 8.5, 3: 7.0, 2: 6.0, 1: 5.0, 0: 4.0}
    band_score = scale.get(correct_count, 6.0)

    feedback_text = f"Reading Doğru: {correct_count}/{total_q}. Tahmini Band Skoru: {band_score}"
    database.save_score_record(
        module="Reading",
        task_type="Academic Reading",
        score=band_score,
        feedback=feedback_text,
        mode=sub.mode,
        raw_score=f"{correct_count}/{total_q}",
        user_email=sub.user_email
    )

    return {
        "success": True,
        "correct_count": correct_count,
        "total": total_q,
        "band_score": band_score,
        "breakdown": breakdown
    }

@app.post("/api/grade/listening")
async def grade_listening_endpoint(sub: ListeningSubmission):
    mode_data = EXAM_DATA.get(sub.mode, EXAM_DATA["cyber"])
    section = mode_data["listening"].get(sub.section_id, mode_data["listening"]["section_1"])
    questions = section["questions"]

    correct_count = 0
    total_q = len(questions)
    breakdown = []

    for q in questions:
        q_id = q["id"]
        user_ans = (sub.answers.get(q_id) or "").strip()
        accepted_list = [a.lower().strip() for a in q.get("accepted", [q.get("answer", "")])]
        is_correct = (user_ans.lower() in accepted_list) if user_ans else False
        
        if is_correct:
            correct_count += 1
        else:
            database.record_mistake(
                user_email=sub.user_email,
                module="Listening",
                prompt=q["prompt"],
                user_ans=user_ans or "Boş",
                correct_ans=q.get("answer", ""),
                explanation=q.get("explanation", "Ses kaydındaki çeldirici veya düzeltme ifadesine dikkat ediniz."),
                trick="Listening çeldiricisi: Konuşmacının son anda söylediği düzeltme cümlesine odaklanın."
            )

        breakdown.append({
            "id": q_id,
            "prompt": q["prompt"],
            "user_answer": user_ans or "Boş",
            "correct_answer": q.get("answer", ""),
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    scale = {4: 8.5, 3: 7.0, 2: 6.0, 1: 5.0, 0: 4.0}
    band_score = scale.get(correct_count, 6.0)

    feedback_text = f"Listening Doğru: {correct_count}/{total_q}. Tahmini Band Skoru: {band_score}"
    database.save_score_record(
        module="Listening",
        task_type="Listening Section",
        score=band_score,
        feedback=feedback_text,
        mode=sub.mode,
        raw_score=f"{correct_count}/{total_q}",
        user_email=sub.user_email
    )

    return {
        "success": True,
        "correct_count": correct_count,
        "total": total_q,
        "band_score": band_score,
        "breakdown": breakdown
    }

@app.get("/api/audio/listening/{mode}/{section_id}")
async def get_listening_audio(mode: str, section_id: str):
    mode_data = EXAM_DATA.get(mode, EXAM_DATA["cyber"])
    section = mode_data["listening"].get(section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Listening section not found")

    cache_id = f"{mode}_{section_id}"
    audio_url = ai_service.get_or_generate_tts_audio(cache_id, section["audio_script"])
    if audio_url:
        return {"audio_url": audio_url, "has_audio": True}
    return {"audio_url": None, "has_audio": False, "script": section["audio_script"]}

@app.post("/api/mentor")
async def get_mentor_plan(req: MentorRequest):
    scores = database.get_user_analytics(req.user_email)["history"]
    mistakes = database.get_user_mistakes(req.user_email)
    user_name = req.user_email.split('@')[0].capitalize()
    
    report = ai_service.generate_personalized_guidance(
        user_name=user_name,
        performance_history=scores,
        mistakes=mistakes,
        mode=req.mode
    )
    return {"report": report}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
