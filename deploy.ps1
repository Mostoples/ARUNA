# ARUNA — deploy otomatis ke Firebase (Hosting + Rules RTDB & Firestore)
# Cara pakai: jalankan  .\deploy.ps1  dari folder proyek
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Pakai service account (bukan akun "firebase login" yang mungkin berbeda).
# XDG_CONFIG_HOME dialihkan agar CLI mengabaikan sesi login lokal.
$env:GOOGLE_APPLICATION_CREDENTIALS = Join-Path $root "secrets\service-account.json"
$env:XDG_CONFIG_HOME = Join-Path $env:TEMP "aruna-fbconfig"
New-Item -ItemType Directory -Force $env:XDG_CONFIG_HOME | Out-Null

Set-Location $root
firebase deploy --only "hosting,database" --project aruna-id --non-interactive

# Rules Firestore butuh role "Firebase Rules Admin" pada service account.
# Jika belum diberikan (403), langkah ini dilewati tanpa menggagalkan deploy.
firebase deploy --only "firestore:rules" --project aruna-id --non-interactive
if ($LASTEXITCODE -ne 0) {
  Write-Host ""
  Write-Host "PERINGATAN: rules Firestore belum ter-deploy (izin kurang)." -ForegroundColor Yellow
  Write-Host "Beri role 'Firebase Rules Admin' ke firebase-adminsdk-fbsvc@aruna-id.iam.gserviceaccount.com" -ForegroundColor Yellow
  Write-Host "di https://console.cloud.google.com/iam-admin/iam?project=aruna-id lalu jalankan ulang," -ForegroundColor Yellow
  Write-Host "atau salin isi firestore.rules manual ke Firebase Console > Firestore > Rules." -ForegroundColor Yellow
  exit 0
}
