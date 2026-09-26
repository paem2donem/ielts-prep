import os
import re
import datetime
import sqlite3
import pandas as pd
import gradio as gr
from google import genai

# ==========================================
# 1. AYARLAR VE API ENTEGRASYONU
# ==========================================
# API anahtarı: Çevre değişkeni tanımlıysa oradan alınır, yoksa varsayılan anahtar kullanılır.
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# Birincil ve yedek model listesi (503 yoğunluk durumunda otomatik geçiş için)
PRIMARY_MODELS = ["gemini-3.5-flash", "gemini-3.8-flash"]

def generate_content_with_fallback(contents):
    """
    Geçici 503 (High Demand) ya da model kota hatalarında otomatik olarak
    yedek modele geçiş yaparak kesintisiz çalışma sağlar.
    """
    last_error = None
    for model_name in PRIMARY_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            last_error = e
            continue
    raise last_error

# ==========================================
# 2. VERİTABANI (SQLite) KURULUMU
# ==========================================
DB_FILE = "tracker.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            module TEXT,
            task_type TEXT,
            score REAL,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_score(module, task_type, score, feedback):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO scores (date, module, task_type, score, feedback) VALUES (?, ?, ?, ?, ?)",
        (date_str, module, task_type, float(score), feedback)
    )
    conn.commit()
    conn.close()

def get_performance_data():
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT id, date, module, task_type, score, feedback FROM scores ORDER BY id DESC", conn)
    except Exception:
        df = pd.DataFrame(columns=["id", "date", "module", "task_type", "score", "feedback"])
    conn.close()
    return df

def extract_band_score(text, default=6.5):
    """Yapay zeka çıktısındaki gerçek Band Skorunu yakalar (Örn: Band 7.0, Skor: 6.5 vb.)"""
    match = re.search(r'(?:Tahmini\s*)?(?:Band\s*(?:Skoru|Score)?[:\s\*\-]*)([4-9](?:\.[05])?)', text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    # Alternatif eşleşme: Sadece 4.0 - 9.0 formatında puan arama
    match2 = re.search(r'\b([4-9]\.[05])\b', text)
    if match2:
        try:
            return float(match2.group(1))
        except ValueError:
            pass
    return default

init_db()

# ==========================================
# 3. READING MATERYALİ VE TESTİ (Cyber Forensics)
# ==========================================
READING_PASSAGE = """
### Reading Passage: Digital Forensics and the Chain of Custody in Modern Law Enforcement

The integration of cloud computing and decentralized networks has fundamentally transformed the landscape of digital forensic investigation. In conventional digital forensics, investigators adhered strictly to ISO/IEC 27037 standards, which prescribe procedures for identifying, collecting, acquiring, and preserving digital evidence from physical storage media such as hard drives and USB peripherals. A primary cornerstone of this regime is the 'Chain of Custody' (CoC)—a meticulous chronological documentation tracking the custody, transfer, and disposition of physical and electronic evidence.

However, volatile memory (RAM) and cloud-hosted enterprise workloads introduce substantial volatility. When malicious actors orchestrate advanced persistent threats (APTs) or ransomware attacks, vital artifacts may reside solely within unallocated memory space or transient virtual machines. Powering down a seized machine to preserve physical storage inadvertently purges ephemeral evidence, making live forensics an indispensable prerequisite despite inherent risks of altering device state.

Furthermore, international cross-border data sovereignty creates complex evidentiary obstacles. Under legal frameworks like the European Union's GDPR and the US CLOUD Act, cross-jurisdictional evidence acquisition necessitates bilateral mutual legal assistance treaties (MLATs). Courts increasingly scrutinize whether cryptographic integrity was sustained via cryptographic hash functions (such as SHA-256) throughout data transit. Without incontrovertible proof that automated surveillance and forensic acquisition algorithms adhere to strict legal admissibility doctrines, evidence runs the immediate risk of judicial exclusion.
"""

READING_QUESTIONS = [
    {
        "id": "q1",
        "question": "1. ISO/IEC 27037 standards deal exclusively with volatile memory (RAM) analysis.",
        "options": ["TRUE", "FALSE", "NOT GIVEN"],
        "answer": "FALSE",
        "explanation": "Metinde bu standardın geleneksel olarak sabit diskler ('physical storage media') için olduğu, uçucu bellek (RAM) için olmadığı vurgulanmaktadır."
    },
    {
        "id": "q2",
        "question": "2. Turning off a compromised computer system can permanently destroy crucial forensic evidence.",
        "options": ["TRUE", "FALSE", "NOT GIVEN"],
        "answer": "TRUE",
        "explanation": "'Powering down a seized machine... inadvertently purges ephemeral evidence' ifadesi bunu açıkça belirtmektedir."
    },
    {
        "id": "q3",
        "question": "3. The CLOUD Act was drafted with direct consultation from Europol cyber intelligence teams.",
        "options": ["TRUE", "FALSE", "NOT GIVEN"],
        "answer": "NOT GIVEN",
        "explanation": "Metinde CLOUD Act ve GDPR geçmekte ancak Europol ile istişare edildiğine dair hiçbir bilgi yer almamaktadır."
    },
    {
        "id": "q4",
        "question": "4. Cryptographic hashing functions like SHA-256 are utilized to verify that evidence remained unaltered during transit.",
        "options": ["TRUE", "FALSE", "NOT GIVEN"],
        "answer": "TRUE",
        "explanation": "'cryptographic integrity was sustained via cryptographic hash functions (such as SHA-256)' ifadesi bu yargıyı doğrulamaktadır."
    }
]

# ==========================================
# 4. DEĞERLENDİRME FONKSİYONLARI
# ==========================================
def evaluate_writing(essay_text):
    if not essay_text or len(essay_text.strip().split()) < 30:
        return "⚠️ Lütfen en az 30 kelimelik bir metin girin. (IELTS Task 2 için ideal hedef en az 250 kelimedir)."
    
    word_count = len(essay_text.strip().split())
    
    prompt = f"""
Sen Jean Monnet bursu ve Europol standartlarına hakim, zorlu bir Cambridge IELTS Baş Examiner'ısın.
Aşağıdaki Task 2 kompozisyonunu IELTS 7.0+ kriterlerine göre değerlendir.

Adayın Uzmanlık Alanı: Adli Bilişim (Digital Forensics) ve Siber Suçlar.
Adayın alan terminolojisini (örneğin: chain of custody, cryptographic hash, volatile memory, digital evidence, judicial admissibility, MLAT, data sovereignty) ne kadar doğru ve yerinde kullandığını özellikle analiz et.

Kelime Sayısı: {word_count} kelime. (Task 2 kuralı: En az 250 kelime).

Değerlendirme Çıktı Formatı:
### 🎯 Genel Sonuç
- **Tahmini Band Skoru:** [Örn: 6.5]
- **Kelime Sayısı Analizi:** [{word_count} kelime - Yeterlilik durumu]

### 📊 Kriter Bazlı Analiz
1. **Task Response (Göreve Uygunluk):** 
2. **Coherence & Cohesion (Tutarlılık ve Bağlantı):** 
3. **Lexical Resource (Kelime Çeşitliliği & Siber Terminoloji):** 
4. **Grammatical Range & Accuracy (Gramer Yelpazesi ve Doğruluk):** 

### 💡 Jean Monnet / IELTS 7.5+ Hedefi İçin 3 Kritik Tavsiye
1. ...
2. ...
3. ...

Öğrencinin Metni:
\"\"\"
{essay_text}
\"\"\"
"""
    try:
        feedback = generate_content_with_fallback(prompt)
        score = extract_band_score(feedback, default=6.5)
        save_score("Writing", "Task 2", score, feedback)
        return feedback
    except Exception as e:
        return f"❌ API Hatası: {str(e)}"


def evaluate_speaking(audio_path):
    if not audio_path or not os.path.exists(audio_path):
        return "⚠️ Lütfen mikrofonunuzla bir ses kaydı yapın veya ses dosyası yükleyin."
    
    uploaded_file = None
    try:
        # Ses dosyasını doğrudan Google GenAI'ye yüklüyoruz (Whisper kurulumu veya ffmpeg gerektirmez)
        uploaded_file = client.files.upload(file=audio_path)
        
        prompt = """
Sen Europol ve Jean Monnet standartlarında uzman bir IELTS Speaking Examiner'ısın.
Kullanıcının kaydettiği sesi dinle ve aşağıdaki detaylı analizi yap:

1. 📝 **Deşifre (Spoken Transcript):** Konuşmacının söylediklerini İngilizce olarak tam ve doğru şekilde yazıya dök.
2. 🎯 **Tahmini Band Skoru:** [Örn: 6.5 veya 7.0]
3. 🔍 **4 Temel Kriter Analizi:**
   - **Fluency & Coherence (Akıcılık ve Tutarlılık):** Duraksamalar, bağlaç kullanımı, fikir akışı.
   - **Lexical Resource (Kelime Dağarcığı):** Siber güvenlik / adli bilişim terimlerinin (chain of custody, digital evidence vb.) telaffuzu ve kullanımı.
   - **Grammatical Range & Accuracy (Gramer Zenginliği ve Hatasızlık):** Zaman uyumları, karmaşık cümle yapıları.
   - **Pronunciation (Telaffuz):** Vurgu, tonlama ve anlaşılırlık.
4. 🚀 **7.5+ Seviyesine Ulaşmak İçin Tavsiyeler:**
"""
        feedback = generate_content_with_fallback([uploaded_file, prompt])
        score = extract_band_score(feedback, default=6.0)
        save_score("Speaking", "Part 3", score, feedback)
        return feedback
    except Exception as e:
        return f"❌ Ses Analizi Hatası: {str(e)}"
    finally:
        if uploaded_file is not None:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass


def grade_reading(ans1, ans2, ans3, ans4):
    user_answers = [ans1, ans2, ans3, ans4]
    correct_count = 0
    details = []
    
    for i, q in enumerate(READING_QUESTIONS):
        user_ans = user_answers[i]
        is_correct = (user_ans == q["answer"])
        if is_correct:
            correct_count += 1
            status = "✅ DOĞRU"
        else:
            status = f"❌ YANLIŞ (Doğru Cevap: {q['answer']})"
        
        details.append(f"- **Soru {i+1}:** {status}\n  *Açıklama:* {q['explanation']}\n")
    
    # 4 soruluk mini testte tahmini band skoru haritası
    score_map = {4: 8.5, 3: 7.0, 2: 6.0, 1: 5.0, 0: 4.0}
    band_score = score_map.get(correct_count, 6.0)
    
    feedback_text = f"""
### 📊 Reading Test Sonucu
- **Doğru Sayısı:** {correct_count} / 4
- **Tahmini Band Skoru:** {band_score}

#### Soru Çözümleri:
{"".join(details)}
"""
    save_score("Reading", "Academic T/F/NG", band_score, feedback_text)
    return feedback_text


def mentor_update():
    df = get_performance_data()
    if df.empty:
        summary_md = "### 📈 Henüz sınav kaydı bulunmuyor.\nWriting, Speaking veya Reading sekmelerinden en az bir test çözün."
        return summary_md, df
    
    avg_score = df["score"].mean()
    total_tests = len(df)
    last_score = df.iloc[0]["score"]
    
    summary_stats = f"""
### 📊 Genel Performans Özeti
- **Toplam Çözülen Test:** {total_tests}
- **Ortalama Band Skoru:** {avg_score:.2f}
- **Son Test Skoru:** {last_score:.1f}
---
"""
    
    prompt = f"""
Sen Adli Bilişim (Digital Forensics) ve Siber Güvenlik alanında uzmanlaşan adaylara Jean Monnet Bursu ve IELTS 7.5+ hazırlığı yaptıran elit bir Mentorsun.
Adayın sınav performans verileri aşağıdadır:

{df.head(10)[["date", "module", "task_type", "score"]].to_string()}

Lütfen şu başlıklar altında Türkçe, nokta atışı ve motive edici bir rapor hazırla:
1. 🔍 **Güçlü ve Gelişime Açık Alanlar:** Hangi modülde ilerleme var, nerede takılma yaşanıyor?
2. 🛡️ **Siber Suçlar & Adli Bilişim Terminoloji Stratejisi:** Cevaplara entegre edilmesi gereken 3 ileri düzey terim ve örnek kullanım.
3. 🎯 **Bugüne Özel 45 Dakikalık Mikro Çalışma Planı:** Zamanı verimli kullandıran pratik adımlar.
"""
    try:
        feedback = generate_content_with_fallback(prompt)
        full_feedback = summary_stats + feedback
        return full_feedback, df
    except Exception as e:
        return f"{summary_stats}\n❌ Mentor analizi üretilemedi: {str(e)}", df


# ==========================================
# 5. GRADIO ARAYÜZÜ (UI)
# ==========================================
custom_css = """
.gradio-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
}
"""

with gr.Blocks(title="ForenSync Academy - IELTS & Cyber Prep") as app:
    gr.Markdown("# 🛡️ ForenSync Academy: IELTS & Cyber Prep")
    gr.Markdown(
        "**Adli Bilişim & Siber Güvenlik** uzmanlarına özel, yapay zeka destekli **Jean Monnet & IELTS 7.5+** çalışma istasyonu."
    )
    
    with gr.Tabs():
        # --- TAB 1: WRITING ---
        with gr.TabItem("✍️ Writing (Task 2)"):
            gr.Markdown("### Soru (Task 2 Essay):")
            gr.Markdown(
                "> *\"The rapid proliferation of automated surveillance tools and AI-driven evidence acquisition has ignited intense legal debate regarding the admissibility of digital evidence in criminal proceedings. Discuss the advantages and potential threats to civil liberties, and give your own reasoned opinion.\"*"
            )
            with gr.Row():
                with gr.Column(scale=1):
                    writing_input = gr.Textbox(
                        lines=14,
                        placeholder="Kompozisyonunuzu buraya yazın (IELTS standardı: En az 250 kelime)...\nÖrn: In the contemporary era of cyber jurisprudence...",
                        label="Essay Metniniz"
                    )
                    writing_btn = gr.Button("🚀 Kompozisyonu Değerlendir", variant="primary")
                with gr.Column(scale=1):
                    writing_output = gr.Markdown(label="IELTS Examiner Geri Bildirimi")
            
            writing_btn.click(fn=evaluate_writing, inputs=writing_input, outputs=writing_output)

        # --- TAB 2: SPEAKING ---
        with gr.TabItem("🎙️ Speaking (Part 3)"):
            gr.Markdown("### Soru (Speaking Part 3):")
            gr.Markdown(
                "> *\"How do cloud computing architectures and cross-border digital jurisdictions complicate the collection and validation of forensic evidence for international law enforcement agencies?\"*"
            )
            with gr.Row():
                with gr.Column(scale=1):
                    speaking_input = gr.Audio(
                        sources=["microphone", "upload"],
                        type="filepath",
                        label="Cevabınızı Ses Kaydedin veya Ses Dosyası Yükleyin"
                    )
                    speaking_btn = gr.Button("🎧 Ses Kaydını Dinle & Değerlendir", variant="primary")
                with gr.Column(scale=1):
                    speaking_output = gr.Markdown(label="Transkript ve Band Skoru Analizi")
                    
            speaking_btn.click(fn=evaluate_speaking, inputs=speaking_input, outputs=speaking_output)

        # --- TAB 3: READING ---
        with gr.TabItem("📖 Reading (T/F/NG)"):
            gr.Markdown("### Cambridge Academic Reading: Digital Forensics")
            gr.Markdown(READING_PASSAGE)
            gr.Markdown("---")
            gr.Markdown("#### Sorular (True / False / Not Given)")
            
            q1_radio = gr.Radio(
                label=READING_QUESTIONS[0]["question"],
                choices=READING_QUESTIONS[0]["options"],
                value=None
            )
            q2_radio = gr.Radio(
                label=READING_QUESTIONS[1]["question"],
                choices=READING_QUESTIONS[1]["options"],
                value=None
            )
            q3_radio = gr.Radio(
                label=READING_QUESTIONS[2]["question"],
                choices=READING_QUESTIONS[2]["options"],
                value=None
            )
            q4_radio = gr.Radio(
                label=READING_QUESTIONS[3]["question"],
                choices=READING_QUESTIONS[3]["options"],
                value=None
            )
            
            reading_btn = gr.Button("📝 Reading Testini Puanla", variant="primary")
            reading_output = gr.Markdown()
            
            reading_btn.click(
                fn=grade_reading,
                inputs=[q1_radio, q2_radio, q3_radio, q4_radio],
                outputs=reading_output
            )

        # --- TAB 4: MENTOR & ANALYTICS ---
        with gr.TabItem("🧠 AI Mentor & Gelişim Takibi"):
            gr.Markdown("### Kişiselleştirilmiş Gelişim Analizi")
            gr.Markdown("Sınav geçmişinize göre zayıf halkalarınızı tespit eden ve Jean Monnet bursuna yönelik strateji sunan AI Mentor.")
            mentor_btn = gr.Button("🔄 Verilerimi Analiz Et ve Çalışma Planı Oluştur", variant="primary")
            mentor_plan = gr.Markdown(label="Günün Mentor Raporu")
            mentor_data = gr.Dataframe(label="Geçmiş Test Kayıtları")
            
            mentor_btn.click(fn=mentor_update, inputs=None, outputs=[mentor_plan, mentor_data])

if __name__ == "__main__":
    # Gradio 6.x uyumlu tema ve CSS yapılandırması
    app.launch(
        theme=gr.themes.Soft(primary_hue="blue"),
        css=custom_css
    )
