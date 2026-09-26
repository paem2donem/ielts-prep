import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database
from exam_data import EXAM_DATA
from services import ai_service

app = FastAPI(
    title="ForenSync Academy - IELTS & Cyber Prep Platform",
    description="Oracle Cloud Ready, Mobile-First IELTS Academic & Cyber Forensics Training Suite",
    version="2.0.0"
)

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
class WritingRequest(BaseModel):
    essay_text: str
    task_type: str = "Task 2"
    mode: str = "cyber"
    prompt_context: str = ""

class ReadingSubmission(BaseModel):
    mode: str = "cyber"
    passage_id: str = "passage_1"
    answers: Dict[str, str]

class ListeningSubmission(BaseModel):
    mode: str = "cyber"
    section_id: str = "section_1"
    answers: Dict[str, str]

class MentorRequest(BaseModel):
    mode: str = "cyber"


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Index template not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/exam-data/{mode}")
async def get_exam_content(mode: str):
    if mode not in EXAM_DATA:
        mode = "cyber"
    return EXAM_DATA[mode]


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
            raw_score=f"{result['word_count']} kelime"
        )
    return result


@app.post("/api/evaluate/speaking")
async def evaluate_speaking_endpoint(
    audio: UploadFile = File(...),
    part: str = Form("Part 2"),
    mode: str = Form("cyber"),
    prompt_context: str = Form("")
):
    # Save uploaded audio to a temp file
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
                raw_score=f"Band {score}"
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

        breakdown.append({
            "id": q_id,
            "prompt": q["prompt"],
            "user_answer": user_ans or "Boş",
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    # Band score conversion
    # 4 questions scale: 4 -> 8.5, 3 -> 7.0, 2 -> 6.0, 1 -> 5.0, 0 -> 4.0
    scale = {4: 8.5, 3: 7.0, 2: 6.0, 1: 5.0, 0: 4.0}
    band_score = scale.get(correct_count, 6.0)

    feedback_text = f"Reading Doğru: {correct_count}/{total_q}. Tahmini Band Skoru: {band_score}"
    database.save_score_record(
        module="Reading",
        task_type="Academic Reading",
        score=band_score,
        feedback=feedback_text,
        mode=sub.mode,
        raw_score=f"{correct_count}/{total_q}"
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
        raw_score=f"{correct_count}/{total_q}"
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


@app.get("/api/analytics")
async def get_analytics():
    return database.get_analytics_summary()


@app.post("/api/mentor")
async def get_mentor_plan(req: MentorRequest):
    scores = database.get_all_scores(limit=15)
    history_summary = []
    for s in scores:
        history_summary.append(f"Tarih: {s['date']}, Modül: {s['module']}, Skor: {s['score']}, Görev: {s['task_type']}")
    
    report = ai_service.generate_ai_mentor_report(history_summary, mode=req.mode)
    return {"report": report}


if __name__ == "__main__":
    import uvicorn
    # Oracle Cloud ve yerel kullanım için 0.0.0.0 üzerinden 8000 portunda başlatılır
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
