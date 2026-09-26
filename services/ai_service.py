import os
import re
import json
import datetime
from pathlib import Path
from google import genai
from typing import Optional, Tuple, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

PRIMARY_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]
TTS_MODEL = "gemini-3.8-flash-tts"

AUDIO_CACHE_DIR = Path("static/audio")
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def generate_text_with_fallback(contents: Any) -> str:
    """Invokes Gemini models with fallback across 3.5-flash and 3.8-flash."""
    last_err = None
    for model_name in PRIMARY_MODELS:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            return res.text
        except Exception as e:
            last_err = e
            continue
    raise last_err or RuntimeError("No response from AI models.")

def extract_band_score(text: str, default: float = 6.5) -> float:
    """Extracts band score from examiner evaluation text."""
    match = re.search(r'(?:Tahmini\s*)?(?:Band\s*(?:Skoru|Score)?[:\s\*\-]*)([4-9](?:\.[05])?)', text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    match2 = re.search(r'\b([4-9]\.[05])\b', text)
    if match2:
        try:
            return float(match2.group(1))
        except ValueError:
            pass
    return default

def evaluate_writing_submission(essay_text: str, task_type: str = "Task 2", mode: str = "cyber", prompt_context: str = "") -> Dict[str, Any]:
    words = essay_text.strip().split()
    word_count = len(words)
    min_required = 150 if "Task 1" in task_type else 250

    if word_count < 25:
        return {
            "success": False,
            "error": f"Lütfen en az 25 kelimelik bir metin girin. (Bu görev için asgari hedef: {min_required} kelime)."
        }

    is_cyber = (mode == "cyber")
    domain_instructions = """
Adayın Uzmanlık Alanı: Adli Bilişim (Forensic Computing), Siber Suçlar ve Jean Monnet Burs Programı.
Adayın alana özgü teknik ve hukuki terminolojiyi (örn: chain of custody, cryptographic hash, volatile memory, judicial admissibility, MLAT, data sovereignty, triage) kullanım derinliğini de Lexical Resource kriterinde açıkça değerlendir.
""" if is_cyber else """
Adayın Sınav Türü: Cambridge IELTS Academic.
Genel akademik dil çeşitliliği, akademik bağlaçlar, nesnel ton ve formal yapıları titizlikle değerlendir.
"""

    prompt = f"""
Sen resmi Cambridge IELTS Baş Examiner'ı ve Jean Monnet Seçim Komitesi Değerlendiricisisin.
Aşağıdaki {task_type} metnini resmi IELTS değerlendirme kriterlerine göre incele.

{domain_instructions}

Soru / Görev Bağlamı:
{prompt_context}

Adayın Yazdığı Kelime Sayısı: {word_count} kelime. (Asgari Kural: {min_required} kelime).

Değerlendirme Formatı (Markdown olarak yanıt ver):
### 🎯 Genel Sonuç
- **Tahmini Band Skoru:** [Örn: 6.5 veya 7.0]
- **Kelime Sayısı Durumu:** [{word_count} / {min_required} kelime - Eksik/Yeterli durumu]

### 📊 4 Temel Kriter Analizi
1. **Task Response / Task Achievement:** 
2. **Coherence & Cohesion (Tutarlılık ve Bağlantı):** 
3. **Lexical Resource (Kelime Çeşitliliği & Terminoloji):** 
4. **Grammatical Range & Accuracy (Gramer Zenginliği ve Hatasızlık):** 

### 💡 7.5+ Band Hedefi İçin 3 Spesifik Tavsiye
1. ...
2. ...
3. ...

Öğrencinin Yazdığı Metin:
\"\"\"
{essay_text}
\"\"\"
"""
    try:
        feedback = generate_text_with_fallback(prompt)
        score = extract_band_score(feedback, default=6.5)
        return {
            "success": True,
            "score": score,
            "word_count": word_count,
            "min_required": min_required,
            "feedback": feedback
        }
    except Exception as e:
        return {"success": False, "error": f"Yapay zeka analiz hatası: {str(e)}"}

def evaluate_speaking_submission(audio_file_path: str, part: str = "Part 2", mode: str = "cyber", prompt_context: str = "") -> Dict[str, Any]:
    if not os.path.exists(audio_file_path):
        return {"success": False, "error": "Ses dosyası bulunamadı."}

    uploaded_file = None
    try:
        uploaded_file = client.files.upload(file=audio_file_path)

        is_cyber = (mode == "cyber")
        domain_note = "Aday Adli Bilişim & Siber Güvenlik / Jean Monnet adayıdır. Alan terimlerinin doğru telaffuzuna ve kullanımına dikkat et." if is_cyber else "Cambridge Academic standartlarında konuşma yeterliliğini değerlendir."

        prompt = f"""
Sen deneyimli bir Cambridge IELTS Speaking Examiner'ısın.
Adayın {part} ses kaydını dinle ve analiz et.
{domain_note}

Bağlam / Soru:
{prompt_context}

Format:
### 📝 Konuşma Deşifresi (Spoken English Transcript)
[Adayın konuşmasını kelimesi kelimesine İngilizce olarak yaz]

### 🎯 Genel Değerlendirme
- **Tahmini Speaking Band Skoru:** [Örn: 6.5 veya 7.0]

### 🔍 4 Kriter Analizi
1. **Fluency & Coherence (Akıcılık ve Doğallık):** Duraksamalar, bağlaçlar, ritim.
2. **Lexical Resource (Kelime Çeşitliliği):**
3. **Grammatical Range & Accuracy:**
4. **Pronunciation (Telaffuz ve Tonlama):** Anlaşılabilirlik, fonetik hatalar.

### 🚀 Gelişim İçin Tavsiyeler
- ...
"""
        feedback = generate_text_with_fallback([uploaded_file, prompt])
        score = extract_band_score(feedback, default=6.0)
        return {
            "success": True,
            "score": score,
            "feedback": feedback
        }
    except Exception as e:
        return {"success": False, "error": f"Ses analizi hatası: {str(e)}"}
    finally:
        if uploaded_file is not None:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass

def get_or_generate_tts_audio(section_id: str, script_text: str) -> Optional[str]:
    """Generates audio for listening sections via Gemini TTS and saves it in static/audio."""
    clean_id = re.sub(r'[^a-zA-Z0-9_]', '', section_id)
    dest_path = AUDIO_CACHE_DIR / f"{clean_id}.wav"

    if dest_path.exists() and dest_path.stat().st_size > 1000:
        return f"/static/audio/{clean_id}.wav"

    try:
        tts_prompt = f"Please read the following English listening exam audio script clearly at an authentic natural speaking pace for an international Cambridge IELTS test:\n\n{script_text.strip()}"
        res = client.models.generate_content(
            model=TTS_MODEL,
            contents=tts_prompt
        )

        for candidate in res.candidates:
            for part in candidate.content.parts:
                data = getattr(part.inline_data, "data", None)
                if data:
                    with open(dest_path, "wb") as f:
                        f.write(data)
                    return f"/static/audio/{clean_id}.wav"
    except Exception as e:
        print(f"TTS generation error for {section_id}: {e}")
        return None
    return None

# ==========================================
# DYNAMIC AI EXAM GENERATOR (Sonsuz Soru Havuzu)
# ==========================================
def generate_dynamic_reading_test(mode: str = "cyber") -> Dict[str, Any]:
    """Generates a brand new Cambridge Reading passage + 4 questions in JSON."""
    is_cyber = (mode == "cyber")
    topic_hint = "Digital Forensics, Ransomware Investigation, Memory Analysis, or Cloud Evidence Admissibility" if is_cyber else "Renewable Energy, Cognitive Psychology, Ocean Exploration, or Urban Sustainability"

    prompt = f"""
You are a senior Cambridge IELTS Academic Question Writer.
Generate a BRAND-NEW, HIGH-LEVEL Reading Test (Target Band: 7.5 - 8.5 / C1-C2).
Topic Focus: {topic_hint}.

Strict Requirements:
1. Passage length: 300-380 words, dense academic prose with sophisticated vocabulary.
2. 4 True/False/Not Given questions testing subtle distinctions, paraphrasing, and qualifiers.
3. CRITICAL: ANSWER RANDOMIZATION & UNPREDICTABILITY:
   - Do NOT arrange the answers in a predictable sequence (e.g. NEVER do TRUE, FALSE, NOT GIVEN in order, and NEVER put NOT GIVEN always at the end).
   - Randomize the order of answers across the 4 questions (for example: NOT GIVEN, TRUE, FALSE, TRUE or FALSE, NOT GIVEN, TRUE, FALSE or TRUE, NOT GIVEN, FALSE, FALSE).
   - Ensure a balanced mix of TRUE, FALSE, and NOT GIVEN across the 4 questions.
4. For each question, provide:
   - 'prompt': The question statement.
   - 'options': ['TRUE', 'FALSE', 'NOT GIVEN']
   - 'answer': 'TRUE', 'FALSE', or 'NOT GIVEN' (following the randomized distribution)
   - 'explanation': Clear explanation in Turkish explaining WHY it is the answer.
   - 'trick_tip': A Cambridge tip or trap warning (in Turkish).

Return ONLY valid JSON with this exact structure:
{{
  "title": "Passage Title",
  "text": "Full passage text...",
  "questions": [
    {{
      "id": "q1",
      "prompt": "Statement...",
      "options": ["TRUE", "FALSE", "NOT GIVEN"],
      "answer": "NOT GIVEN",
      "explanation": "Açıklama...",
      "trick_tip": "Taktik..."
    }},
    {{
      "id": "q2",
      "prompt": "Statement...",
      "options": ["TRUE", "FALSE", "NOT GIVEN"],
      "answer": "TRUE",
      "explanation": "Açıklama...",
      "trick_tip": "Taktik..."
    }},
    {{
      "id": "q3",
      "prompt": "Statement...",
      "options": ["TRUE", "FALSE", "NOT GIVEN"],
      "answer": "FALSE",
      "explanation": "Açıklama...",
      "trick_tip": "Taktik..."
    }},
    {{
      "id": "q4",
      "prompt": "Statement...",
      "options": ["TRUE", "FALSE", "NOT GIVEN"],
      "answer": "TRUE",
      "explanation": "Açıklama...",
      "trick_tip": "Taktik..."
    }}
  ]
}}
"""
    raw_text = generate_text_with_fallback(prompt)
    clean_json = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
    clean_json = re.sub(r'```$', '', clean_json.strip(), flags=re.MULTILINE)
    return json.loads(clean_json)

def generate_dynamic_writing_prompt(task_type: str = "Task 2", mode: str = "cyber") -> Dict[str, Any]:
    """Generates a brand new Writing prompt for Task 1 or Task 2."""
    is_cyber = (mode == "cyber")
    topic_hint = "Cyber sovereignty, AI surveillance admissibility, encryption vs national security" if is_cyber else "Workplace automation, university curriculum, environmental taxation"
    
    prompt = f"""
You are a Cambridge IELTS Chief Writing Examiner.
Generate a NEW, rigorous IELTS {task_type} prompt.
Domain: {'Forensic Computing / Jean Monnet' if is_cyber else 'Cambridge Academic'}.
Theme: {topic_hint}.

Return ONLY valid JSON:
{{
  "title": "{task_type} (Prompt Title)",
  "prompt": "Official IELTS prompt statement...",
  "min_words": {150 if 'Task 1' in task_type else 250},
  "key_vocabulary_tips": ["word1", "word2", "word3"]
}}
"""
    raw_text = generate_text_with_fallback(prompt)
    clean_json = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
    clean_json = re.sub(r'```$', '', clean_json.strip(), flags=re.MULTILINE)
    return json.loads(clean_json)

def generate_dynamic_listening_test(mode: str = "cyber") -> Dict[str, Any]:
    """Generates a brand new Cambridge Listening section with audio script + 4 questions in JSON."""
    is_cyber = (mode == "cyber")
    topic_hint = "Ransomware negotiation, forensic incident response triage, or cryptographic token handling" if is_cyber else "University library registration, community sports facility booking, or public transport inquiry"

    prompt = f"""
You are a Cambridge IELTS Senior Listening Examination Designer.
Generate a BRAND-NEW, HIGH-QUALITY IELTS Listening Section (Section 1 dialogue or Section 2 presentation).
Target Band: 7.5 - 8.5.
Theme: {topic_hint}.

Strict Requirements:
1. 'audio_script': Authentic English dialogue or talk between 2 people (or speaker delivering guidance), 180-260 words. Include clear factual information (names, numbers, dates, locations, prices, technical codes) and authentic Cambridge distractors (e.g. self-correction).
2. 'intro': 1-2 sentence context introduction.
3. 4 fill-in-the-blank questions (or note completion) matching specific information in the dialogue.
4. For each question:
   - 'id': 'lq1', 'lq2', etc.
   - 'prompt': The sentence with a blank '______'
   - 'type': 'fill'
   - 'answer': 1-2 words or numbers that fit in the blank
   - 'accepted': list of accepted casing/spelling variations
   - 'explanation': Clear explanation in Turkish detailing where in the audio this answer occurs
   - 'trick_tip': Cambridge listening distractor trap tip in Turkish

Return ONLY valid JSON:
{{
  "title": "Section 1: ...",
  "intro": "You will hear...",
  "audio_script": "Officer: ...\\nCaller: ...",
  "questions": [
    {{
      "id": "lq1",
      "type": "fill",
      "prompt": "1. Reference ID: ______",
      "answer": "...",
      "accepted": ["..."],
      "explanation": "...",
      "trick_tip": "..."
    }}
  ]
}}
"""
    raw_text = generate_text_with_fallback(prompt)
    clean_json = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
    clean_json = re.sub(r'```$', '', clean_json.strip(), flags=re.MULTILINE)
    return json.loads(clean_json)

def generate_dynamic_speaking_test(mode: str = "cyber") -> Dict[str, Any]:
    """Generates a brand new Speaking test with Part 1, Part 2 Cue Card, and Part 3."""
    is_cyber = (mode == "cyber")
    topic_hint = "Cyber defense operations, AI forensics, cryptographic privacy" if is_cyber else "Urban development, technological changes, international cultural exchange"

    prompt = f"""
You are a Cambridge IELTS Chief Speaking Examiner.
Generate a BRAND-NEW, COMPLETE IELTS Speaking Exam.
Domain: {'Forensic Computing / Jean Monnet' if is_cyber else 'Cambridge Academic'}.
Theme: {topic_hint}.

Return ONLY valid JSON:
{{
  "title": "IELTS Speaking Examination - {topic_hint}",
  "part_1": {{
    "title": "Part 1: Introduction & Specialization",
    "questions": [
      "Can you describe your background in this field?",
      "What is the most significant technological challenge you face daily?",
      "How do you foresee your specialization evolving over the next decade?"
    ]
  }},
  "part_2": {{
    "title": "Part 2: Cue Card (Long Turn)",
    "cue_card": "Describe a significant challenge or breakthrough in your domain.\\n\\nYou should say:\\n• What the nature of the situation was\\n• What methodologies or tools were used to address it\\n• What complications or obstacles occurred\\nAnd explain what profound insight you derived from this experience.",
    "prep_time": 60,
    "speak_time": 120
  }},
  "part_3": {{
    "title": "Part 3: In-Depth Analytical Discussion",
    "questions": [
      "How does international regulatory disparity impact cross-border investigations and policy?",
      "To what extent will automated artificial intelligence render traditional human expertise obsolete?",
      "What ethical balances must modern societies strike between public security and individual privacy rights?"
    ]
  }},
  "examiner_tips": [
    "Use varied cohesive devices and idiomatic phrases.",
    "Avoid simple monolithic statements; structure your answers using thesis-antithesis."
  ]
}}
"""
    raw_text = generate_text_with_fallback(prompt)
    clean_json = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
    clean_json = re.sub(r'```$', '', clean_json.strip(), flags=re.MULTILINE)
    return json.loads(clean_json)

def generate_personalized_guidance(user_name: str, performance_history: list, mistakes: list, mode: str = "cyber") -> str:
    """Analyzes a specific candidate's mistakes log and generates personalized remedial training."""
    is_cyber = (mode == "cyber")
    
    prompt = f"""
Sen {user_name} adlı adayın kişisel Cambridge IELTS ve Jean Monnet Baş Danışmanısın.
Adayın sınav performans geçmişi:
{performance_history}

Adayın 'Yanlış Defteri'ndeki son hataları:
{mistakes[:8]}

Lütfen adaya doğrudan hitap ederek Türkçe, son derece motive edici, analitik ve stratejik bir kılavuz hazırla:
1. 🎯 **Hata Teşhisi ve Tuzak Analizi:** Adayın en çok puan kaybettiği soru tipi veya yanılgı kalıbı nedir? (Örn: NOT GIVEN ile FALSE farkı, kelime sayısı yetersizliği, bağlaç eksikliği).
2. 💡 **Bu Hataları Çözen 2 Altın Taktik (Cheat Codes):** Bir sonraki denemede derhal uygulayacağı sınav ipuçları.
3. 🛡️ **{"Jean Monnet / Siber Terminoloji Reçetesi" if is_cyber else "C1-C2 Akademik Sözlük Hedefi"}:** Mutlaka hafızaya atması gereken 3 ileri seviye kelime ve örnek kullanım.
4. ⏱️ **Bugüne Özel 35 Dakikalık Hızlı Telafi Planı:**
"""
    try:
        return generate_text_with_fallback(prompt)
    except Exception as e:
        return f"Mentor analiz motoru şu an meşgul: {str(e)}"
