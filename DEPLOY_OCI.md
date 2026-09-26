# ☁️ Oracle Cloud Infrastructure (OCI) Kurulum ve Dağıtım Rehberi

Bu rehber, **ForenSync Academy: IELTS & Cyber Prep** platformunu **Oracle Cloud Infrastructure (OCI) Always Free (Ömür Boyu Ücretsiz)** sanal sunucusu üzerinde 7/24 kesintisiz ve mobil cihazlarla uyumlu (HTTPS / Mikrofon desteğiyle) yayına almanız için hazırlanmıştır.

---

## ⚠️ Kritik Bilgi: Mobil Cihazlarda Mikrofon ve HTTPS Zorunluluğu
> [!IMPORTANT]
> iOS Safari ve Android Chrome gibi tüm modern mobil tarayıcılar, güvenlik nedeniyle **Speaking (Mikrofon)** kaydı için **HTTPS (SSL)** bağlantısını zorunlu tutar. Sadece `http://` üzerinden bağlanıldığında mobil tarayıcı mikrofona erişim izni vermez. Bu nedenle sunucuya ücretsiz bir domain (veya alt alan adı) ve Let's Encrypt SSL sertifikası tanımlanmalıdır.

---

## Adım 1: Oracle Cloud Üzerinde Ücretsiz Sunucu (Compute VM) Açma

1. [Oracle Cloud Console](https://cloud.oracle.com)'a giriş yapın.
2. **Compute** -> **Instances** -> **Create Instance** seçeneğine tıklayın.
3. **Image & Shape:**
   - **Image:** `Ubuntu 22.04 LTS` veya `Oracle Linux 8/9`
   - **Shape:** `Ampere (Arm)` (4 OCPU, 24 GB RAM - Always Free) veya standart `VM.Standard.E2.1.Micro` (AMD 1 OCPU - Always Free)
4. **Networking:** Yeni bir VCN veya mevcut VCN seçin ve **Assign a public IPv4 address** seçeneğini işaretleyin.
5. **Add SSH Keys:** Kendi SSH anahtarınızı (`.pub`) yükleyin veya "Generate a key pair for me" seçeneğiyle özel anahtarı bilgisayarınıza indirin.
6. **Create** butonuna basarak sunucunuzu başlatın ve atanan **Public IP** adresini not edin.

---

## Adım 2: OCI Güvenlik Listesinde (VCN Ingress Rules) Portları Açma

Oracle Cloud sanal ağında internet trafiğine izin vermek için:

1. Instance detay sayfasında bağlı olduğunuz **Subnet** linkine tıklayın.
2. **Security Lists** altında **Default Security List**'i açın.
3. **Add Ingress Rules** butonuna tıklayın:
   - **Source CIDR:** `0.0.0.0/0`
   - **IP Protocol:** `TCP`
   - **Destination Port Range:** `80, 443, 8000`
   - **Description:** `IELTS Web HTTP, HTTPS and App Ports`
4. **Add Ingress Rules** diyerek kaydedin.

---

## Adım 3: Sunucuya Bağlanma ve İşletim Sistemi Güvenlik Duvarını Ayarlama

SSH ile sunucunuza bağlanın:
```bash
ssh -i /path/to/your_private_key ubuntu@SUNUCU_PUBLIC_IP
```

### Ubuntu Kullanıyorsanız (Önerilen):
```bash
# Sistem güncellemeleri
sudo apt update && sudo apt upgrade -y

# Güvenlik duvarı (ufw) portlarını açın
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

### Oracle Linux Kullanıyorsanız:
```bash
sudo firewall-cmd --permanent --zone=public --add-port=80/tcp
sudo firewall-cmd --permanent --zone=public --add-port=443/tcp
sudo firewall-cmd --permanent --zone=public --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## Adım 4: Docker & Docker Compose Kurulumu

Sunucuda Docker yüklü değilse:
```bash
# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Mevcut kullanıcıya docker yetkisi verme
sudo usermod -aG docker $USER

# Yeni oturum açın veya şu komutu verin:
newgrp docker
```

---

## Adım 5: Projeyi Sunucuya Yükleme ve Başlatma

1. Proje dosyalarını sunucuda `/opt/ielts` dizinine kopyalayın veya Git ile çekin:
   ```bash
   sudo mkdir -p /opt/ielts
   sudo chown -R $USER:$USER /opt/ielts
   cd /opt/ielts
   ```

2. `.env` dosyasını oluşturun ve Gemini API anahtarınızı girin:
   ```bash
   nano .env
   ```
   İçeriğine ekleyin:
   ```env
   GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
   ```

3. Uygulamayı Docker ile başlatın:
   ```bash
   docker compose up -d --build
   ```

4. Konteyner durumunu kontrol edin:
   ```bash
   docker compose ps
   docker compose logs -f
   ```

Uygulamanız şu anda `http://SUNUCU_PUBLIC_IP:8000` adresinde çalışmaktadır!

---

## Adım 6: Ücretsiz SSL (HTTPS) ve Domain Kurulumu (Mobil Mikrofon İçin Zorunlu)

1. Bir alan adı (domain) veya ücretsiz alt alan adı (örneğin DuckDNS / Cloudflare) alarak `A kaydı` olarak sunucunuzun **Public IP** adresini yönlendirin. (Örn: `ielts.siteniz.com`).

2. Sunucuda Nginx ve Certbot kurun:
   ```bash
   sudo apt install -y nginx certbot python3-certbot-nginx
   ```

3. Nginx konfigürasyonunu `/etc/nginx/sites-available/ielts` dosyasına kaydedin:
   ```nginx
   server {
       server_name ielts.siteniz.com;

       client_max_body_size 50M;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

4. Siteyi aktif edin:
   ```bash
   sudo ln -s /etc/nginx/sites-available/ielts /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. Let's Encrypt ile tek komutla ücretsiz SSL sertifikasını kurun:
   ```bash
   sudo certbot --nginx -d ielts.siteniz.com
   ```

Artık cep telefonunuzdan `https://ielts.siteniz.com` adresine girdiğinizde:
- Doğrudan tam ekran uygulama deneyimi açılır.
- Speaking modülünde tarayıcı mikrofon iznini sorunsuz onaylar.
- Listening modülünde Gemini sesleri takılmadan çalar.
- Tüm test verileriniz OCI sanal sunucusundaki SQLite diskinde güvenle saklanır.
