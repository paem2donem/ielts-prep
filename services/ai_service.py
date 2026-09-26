import os
import re
import datetime
from pathlib import Path
from google import genai
from typing import Optional, Tuple, Dict, Any

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

PRIMARY_MODELS = ["gemini-3.5-flash", "gemini-3.8-flash"]
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
        # Prompt for natural speech delivery
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

def generate_ai_mentor_report(performance_history: list, mode: str = "cyber") -> str:
    if not performance_history:
        return "Henüz yeterli test geçmişiniz bulunmuyor. Listening, Reading, Writing veya Speaking modüllerinden en az 1-2 test tamamladığınızda mentorunuz kişisel analizinizi oluşturacaktır."

    is_cyber = (mode == "cyber")
    prompt = f"""
Sen Adli Bilişim & Siber Güvenlik uzmanlarına ve Jean Monnet bursiyer adaylarına özel IELTS Koçusun.
Adayın çözdüğü testlerin geçmiş kayıtları:
{performance_history}

Lütfen şu başlıklar altında Türkçe, son derece motive edici, analitik ve nokta atışı bir mentorluk raporu sun:
1. 📈 **Performans Trendi ve Modül Dengesi:** Aday hangi beceride güçlü, hangi beceride band kaybı yaşıyor?
2. 🛡️ **{"Siber Güvenlik / Jean Monnet Terim Havuzu" if is_cyber else "Akademik C1-C2 Kelime ve Kalıp Stratejisi"}:** Bir sonraki denemede mutlaka kullanılması önerilen 3 ileri düzey yapı ve örnek cümle.
3. ⏱️ **Kişiye Özel Günlük 40 Dakikalık Çalışma Planı:** Bugün yapması gereken mikro pratikler.
"""
    try:
        return generate_text_with_fallback(prompt)
    except Exception as e:
        return f"Mentor analiz motoru şu an meşgul: {str(e)}"
