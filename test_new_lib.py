from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"API Key: {api_key[:5]}..." if api_key else "API Key YOK")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="Merhaba dünya"
    )
    print("Sonuç:", response.text)
except Exception as e:
    print("Hata:", e)
