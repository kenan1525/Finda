import os
from pathlib import Path
from dotenv import load_dotenv

# Mevcut dizin
current_dir = Path.cwd()
print(f"Çalışma Dizini: {current_dir}")

# .env dosyası yolu
env_path = current_dir / '.env'
print(f".env dosyası aranıyor: {env_path}")

if env_path.exists():
    print(".env dosyası BULUNDU.")
    # İçeriği ham olarak okuyalım (sadece kontrol için, yazdırmayalım güvenlik için)
    content = env_path.read_text()
    if "GEMINI_API_KEY" in content:
        print("Dosya içinde GEMINI_API_KEY metni VAR.")
    else:
        print("Dosya içinde GEMINI_API_KEY metni YOK.")
else:
    print(".env dosyası BULUNAMADI.")

# Kütüphane ile yüklemeyi deneyelim
loaded = load_dotenv(dotenv_path=env_path)
print(f"load_dotenv sonucu: {loaded}")

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"Başarılı! Anahtar okundu: {api_key[:5]}...{api_key[-5:]}")
else:
    print("BAŞARISIZ! os.getenv ile anahtar okunamadı.")
