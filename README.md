# 🛡️ ForenSync Academy: IELTS & Cyber Prep Suite

**Oracle Cloud (OCI) Uyumlu, Mobil Öncelikli, Çift Modlu Tam IELTS Sınav ve Hazırlık Platformu**

ForenSync Academy, **Adli Bilişim (Digital Forensics)** ve **Siber Güvenlik** profesyonellerine Jean Monnet Bursu ve Cambridge IELTS 7.5+ seviyesine yönelik hazırlanmış, aynı zamanda standart **Cambridge IELTS Academic** formatını da destekleyen yeni nesil bir yapay zeka çalışma istasyonudur.

---

## 🌟 Öne Çıkan Özellikler

### 1. 📱 Mobil Öncelikli (Mobile-First) Web Deneyimi
- **Alt Navigasyon Çubuğu (Bottom Navigation):** Telefon ve tabletlerde tek elle kolay erişim.
- **Duyarlı Okuma Alanı (Responsive Split Reading):** Mobilde "Metin" ve "Sorular" sekmeleri arasında tek dokunuşla kayma, masaüstünde çift sütunlu ferah çalışma düzeni.
- **Süre ve Kelime Sayaçları:** IELTS Task 1 (150 kelime) ve Task 2 (250 kelime) hedeflerine ulaşıldığında otomatik renk değiştiren canlı sayaç.

### 2. 🔀 Çift Mod (Dual Mode) Desteği
- **Cyber Mode (Adli Bilişim & Jean Monnet):** Europol EC3 standartlarında siber suçlar, ISO/IEC 27037 standartları, adli bellek analizi (volatile RAM), delil zinciri (chain of custody) ve MLAT odaklı sorular.
- **Academic Mode (Cambridge Standart):** Yenilenebilir enerji, bilimsel araştırmalar, çevre ve eğitim temalı resmi Cambridge IELTS soru setleri.

### 3. 🎯 4 Tam Sınav Modülü
- 🎧 **Listening (Dinleme):** Gemini Audio TTS motoruyla seslendirilmiş, form doldurma ve çoktan seçmeli sorulardan oluşan 4 bölümlük sınav.
- 📖 **Reading (Okuma):** Cambridge Academic formatında True / False / Not Given ve çoktan seçmeli sorular, anında puanlama ve soru gerekçeleri.
- ✍️ **Writing (Yazma):** Task 1 (Akademik Rapor) ve Task 2 (Kompozisyon), Cambridge & Jean Monnet kriterlerine göre çok boyutlu yapay zeka incelemesi.
- 🎙️ **Speaking (Konuşma):** Part 1, Part 2 (Cue Card - 1 dk hazırlık + 2 dk konuşma) ve Part 3; tarayıcıdan doğrudan ses kaydı ve Gemini çok modlu yapay zeka ile telaffuz, akıcılık ve kelime analizi.
- 🧠 **AI Mentor & İlerleme Takibi:** Tüm modüllerin puan geçmişini SQLite üzerinde saklar, Canvas tabanlı radar/çubuk grafiğinde görselleştirir ve adaya özel günlük 40 dakikalık mikro çalışma planı üretir.

---

## 🚀 Yerel Olarak Çalıştırma

```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python main.py
```
Tarayıcınızdan `http://localhost:8000` adresini açın.

---

## ☁️ Oracle Cloud (OCI) Üzerinde Dağıtım

Proje, Oracle Cloud Always Free (Ömür Boyu Ücretsiz) Sanal Sunucusu üzerinde 7/24 çalışacak şekilde Dockerize edilmiştir.

Detaylı kurulum, VCN güvenlik listesi ayarları ve mobil cihazlarda mikrofon kaydı için zorunlu olan ücretsiz SSL (Let's Encrypt) yapılandırması için:
👉 **[DEPLOY_OCI.md](DEPLOY_OCI.md)** rehberini inceleyebilirsiniz.

```bash
# Sunucuda tek komutla başlatma:
docker compose up -d --build
```
