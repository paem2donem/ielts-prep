"""
IELTS Masterclass & Cambridge Tactics Library
Comprehensive exam tricks, examiner traps, and high-yield scoring strategies
tailored for Academic 7.5+ and Jean Monnet / Cyber Forensics candidates.
"""

IELTS_TRICKS = {
    "reading": {
        "title": "📖 Reading: Cambridge Masterclass & Altın Taktikler",
        "description": "True/False/Not Given tuzakları, zaman yönetimi ve eşanlamlı kelime (paraphrasing) şifreleri.",
        "sections": [
            {
                "topic": "True / False / Not Given (T/F/NG) Çözüm Stratejisi",
                "badge": "En Kritik Taktik",
                "rules": [
                    "<strong>TRUE:</strong> Metindeki bilgiyle soru BİREBİR ve EKSİKSİZ örtüşür. Sadece eşanlamlı kelimeler (synonyms) kullanılmıştır.",
                    "<strong>FALSE:</strong> Soru metindeki bilgiyle DOĞRUDAN ÇELİŞİR (Opposite / Contradiction). Birinin doğru olması diğerini imkansız kılar.",
                    "<strong>NOT GIVEN:</strong> Soru mantıklı gelebilir veya genel kültürünüze göre doğru olabilir; ancak METİNDE bu yargıyı doğrulayan veya çürüten bir kanıt YOKTUR.",
                    "<strong>Uç Kelimeler (Extreme Qualifiers) Tuzağı:</strong> Soruda <em>all, only, always, never, completely, impossible</em> gibi keskin kelimeler varsa, metinde ise <em>often, usually, some, might</em> gibi esnek kelimeler geçiyorsa cevap %90 <strong>FALSE</strong> veya <strong>NOT GIVEN</strong>'dır.",
                    "<strong>Kendi Bilginizi Unutun:</strong> Paragrafta 'Ay peynirden yapılmıştır' yazıyorsa, soru için doğru kabul edin. Asla genel kültürünüzle cevap vermeyin."
                ],
                "example": {
                    "passage": "Live forensics requires interaction with running memory, which inevitably alters system timestamps.",
                    "question": "Live forensic acquisition leaves the computer timestamps completely unchanged.",
                    "answer": "FALSE (Metinde 'inevitably alters' denmektedir, 'completely unchanged' ifadesiyle taban tabana zıttır)."
                }
            },
            {
                "topic": "60 Dakikalık Zaman Yönetimi & Tarama (Skim & Scan)",
                "badge": "Zaman Tuzağı",
                "rules": [
                    "Asla önce 900 kelimelik metni baştan sona roman gibi okumayın! Önce soruları okuyup 'Anahtar Kelimeleri' (Keywords) çizin.",
                    "<strong>Soru Sırası Kuralı:</strong> T/F/NG, Gap Fill ve Multiple Choice soruları metinde KRONOLOJİK (sırasıyla) ilerler. 1. sorunun cevabı 2. sorunun yukarısındadır.",
                    "<strong>Matching Headings İstisnası:</strong> Başlık eşleştirme soruları sırayla gitmez; tüm paragrafın ana fikrini (Topic Sentence) ister. Genellikle ilk 2 ve son 1 cümleye odaklanın."
                ]
            }
        ]
    },
    "listening": {
        "title": "🎧 Listening: Çeldirici (Distractor) Avlama & Not Alma",
        "description": "IELTS Listening'de en çok puan kaybettiren son dakika düzeltmeleri ve harf/sayı kodlamaları.",
        "sections": [
            {
                "topic": "Çeldirici (Distractor) Tuzağını Yakalama",
                "badge": "IELTS 7.5+ Sırrı",
                "rules": [
                    "<strong>'Oh, wait...' Tuzağı:</strong> Konuşmacı önce bir bilgi verir (örn: 'It's at 4 PM'), ancak 2 saniye sonra düzeltir: 'Oh, sorry, actually the room is booked, let's meet at 5:30 PM'. İlk duyduğunuzu hemen yazıp bırakmayın, cümleyi sonuna kadar dinleyin!",
                    "<strong>Tekil / Çoğul (S takısı) Hassasiyeti:</strong> Cevap 'computers' iken 'computer' yazarsanız soru sıfır puan alır. Önündeki 'a/an' artikeline dikkat edin.",
                    "<strong>Alfabe ve Rakam Kodlamaları:</strong> İngiliz aksanında 'A' ile 'I', 'E' ile 'I', 'J' ile 'G' karışabilir. 'Double' kelimesine dikkat edin ('double six' = 66)."
                ]
            }
        ]
    },
    "writing": {
        "title": "✍️ Writing: 7.5+ Band Essay Mimarisi & Jean Monnet Şablonu",
        "description": "Examiner'ın aradığı Task Response, Coherence ve ileri düzey argümantasyon yapısı.",
        "sections": [
            {
                "topic": "Task 2: 4 Paragraflı Çelik Şablon (PEEL Metodu)",
                "badge": "7.5+ Mimarisi",
                "rules": [
                    "<strong>Paragraf 1 (Giriş - 45 Kelime):</strong> 1. Cümle: Soruyu paraphrase edin (kendi kelimelerinizle yeniden yazın). 2. Cümle: Net tezinizi (Thesis Statement) belirtin.",
                    "<strong>Paragraf 2 (Gelişme 1 - 90 Kelime):</strong> Karşıt görüşü veya 1. argümanı tartışın. (Point -> Explanation -> Evidence/Örnek -> Link back).",
                    "<strong>Paragraf 3 (Gelişme 2 - 90 Kelime):</strong> Kendi savunduğunuz güçlü görüşü siber/adli bilişim kanıtlarıyla destekleyin.",
                    "<strong>Paragraf 4 (Sonuç - 35 Kelime):</strong> Asla yeni bir fikir eklemeyin! Girişteki tezinizi farklı kelimelerle özetleyin.",
                    "<strong>Asgari Kelime Limiti:</strong> 249 kelime yazarsanız doğrudan Task Response kriterinden 5.0'a düşürülürsünüz. İdeal hedef: 265 - 290 kelimedir."
                ]
            },
            {
                "topic": "Jean Monnet & Europol İçin Altın Kelime Dağarcığı (C1-C2)",
                "badge": "Terminoloji",
                "rules": [
                    "<em>'Chain of custody'</em> (Delil zinciri bütünlüğü)",
                    "<em>'Cryptographic checksum / SHA-256 verification'</em> (Veri manipülasyonu olmadığını kanıtlama)",
                    "<em>'Volatile memory triage'</em> (Canlı sistem bellek analizi)",
                    "<em>'Judicially inadmissible'</em> (Hukuken geçersiz delil)",
                    "<em>'Mutual Legal Assistance Treaties (MLATs)'</em> (Sınır ötesi siber soruşturma anlaşmaları)",
                    "<em>'Territorial sovereignty vs Cloud computing'</em> (Veri egemenliği çatışması)"
                ]
            }
        ]
    },
    "speaking": {
        "title": "🎙️ Speaking: Akıcılık, Telaffuz ve Cue Card Hileleri",
        "description": "Duraksamaları yok eden profesyonel bağlaçlar ve 2 dakikalık kesintisiz konuşma tekniği.",
        "sections": [
            {
                "topic": "Part 2 Cue Card: 1 Dakikalık Hazırlıkta Ne Yapmalı?",
                "badge": "2 Dakika Kuralı",
                "rules": [
                    "1 dakikalık sürede tam cümle yazmaya ÇALIŞMAYIN! Zaman yetmez.",
                    "Kağıda sadece 4-5 adet anahtar kelime ve C1 seviyesinde idiom/bağlaç yazın (Örn: <em>double-edged sword, paramount, watershed moment</em>).",
                    "Hikayenizi geçmiş -> şimdi -> gelecek ekseninde kurun. Bu, tüm zaman kiplerini (tenses) kullanarak Grammatical Range'den tam puan almanızı sağlar."
                ]
            },
            {
                "topic": "Sessizliği Engelleyen Profesyonel 'Filler' Kalıpları",
                "badge": "Akıcılık Sırrı",
                "rules": [
                    "Asla 'eeee', 'ıııı' diye duraksamayın! Düşünürken şu akademik kalıpları kullanın:",
                    "<em>'That is a multifaceted question, but looking at it from an institutional standpoint...'</em>",
                    "<em>'I haven't considered that specific angle before, however, it seems to me that...'</em>",
                    "<em>'To put it into perspective, one must consider...'</em>"
                ]
            }
        ]
    }
}
