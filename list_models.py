import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key yok!")
else:
    genai.configure(api_key=api_key)
    print("Mevcut Modeller (Filtresiz):")
    try:
        for m in genai.list_models():
            print(f"Ad: {m.name}")
            print(f"Desteklenen Metodlar: {m.supported_generation_methods}")
            print("-" * 20)
    except Exception as e:
        print(f"Hata: {e}")
