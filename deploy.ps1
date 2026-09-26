# ==========================================
# ForenSync Academy - Oracle Cloud Deployment Script
# Tek tıkla Oracle Cloud sunucusunu günceller
# ==========================================
Write-Host "🚀 Oracle Cloud sunucusuna bağlanılıyor ve güncellemeler çekiliyor..." -ForegroundColor Cyan

$keyPath = "$env:USERPROFILE\Downloads\ssh-key-2026-09-26.key"
$serverIp = "158.180.55.223"

if (-not (Test-Path $keyPath)) {
    Write-Host "❌ SSH anahtarı bulunamadı: $keyPath" -ForegroundColor Red
    exit 1
}

ssh -i $keyPath ubuntu@$serverIp "cd /home/ubuntu/ielts && git pull && sudo docker compose up -d --build && sudo docker ps"

Write-Host "✅ Güncelleme tamamlandı! Uygulamanız canlı: http://$serverIp:8000" -ForegroundColor Green
