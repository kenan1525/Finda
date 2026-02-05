import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("Mevcut Modeller (google-genai):")
try:
    # pager bir generator döner
    for m in client.models.list():
        # m bir Model objesidir.
        # Genellikle .name veya .display_name özellikleri vardır.
        print(f"Model ID: {m.name}")
except Exception as e:
    print(f"Hata: {e}")
