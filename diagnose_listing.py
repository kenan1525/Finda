import os
import django
import dotenv
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finda.settings')
django.setup()

from core.utils import get_all_products
from core.chat_service import analyze_user_message
from core.ai_service import ask_gemini as ask_gemini_service

def test_listing():
    query = "iphone 15"
    print(f"Testing product listing for: {query}")
    products = get_all_products(query)
    print(f"Found {len(products)} products.")
    for p in products[:2]:
        print(f" - {p.get('title')} ({p.get('site')})")

def test_ai():
    print("\nTesting AI Intent Detection...")
    hist = []
    res = analyze_user_message("iphone 15 almak istiyorum", hist)
    print(f"Result: {res}")

def test_models():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    print("\nListing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    test_listing()
    test_ai()
    test_models()
