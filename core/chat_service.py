import os
import json
import re
import requests
from google import genai
from django.conf import settings

# =========================
# CONFIG
# =========================

GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")).strip()
OPENROUTER_API_KEY = getattr(settings, "OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", "")).strip()
GROQ_API_KEY = getattr(settings, "GROQ_API_KEY", os.getenv("GROK_API_KEY", "")).strip()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://finda.ai",
    "X-Title": "Finda AI",
    "Content-Type": "application/json"
}

GROQ_HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def analyze_user_message(user_message, conversation_history=None):
    """Analyze user message with multi-LLM fallback (Gemini -> Groq -> OpenRouter -> Keyword Fallback)"""
    
    context = ""
    if conversation_history:
        context = "\n".join([
            f"{'Kullanıcı' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
            for msg in conversation_history[-3:]
        ])
    
    prompt = f"""Sen Finda AI, bir alışveriş asistanısın. Kullanıcıyla doğal sohbet edebilir ve alışveriş ihtiyaçlarını anlayabilirsin.

Önceki konuşma:
{context if context else "Yok"}

Kullanıcının son mesajı: "{user_message}"

Görevin:
1. Kullanıcının niyetini belirle: ALISVERIS veya SOHBET
2. Eğer alışveriş niyeti varsa, aranacak ürünü İNGİLİZCE olarak çıkar. Eğer kullanıcı spesifik bir model (örn: "Adidas Nizza", "iPhone 15 Pro") belirttiyse, arama sorgusunu (query) OLABİLDİĞİNCE SPESİFİK tut (generalize etme).
3. Kullanıcıya Türkçe uygun bir yanıt oluştur

Yanıtını MUTLAKA şu JSON formatında ver:
{{
    "intent": "ALISVERIS" veya "SOHBET",
    "query": "İNGİLİZCE veya SPESİFİK MODEL adı",
    "response": "kullanıcıya verilecek TÜRKÇE yanıt"
}}"""

    # 1️⃣ Gemini (Primary)
    if GEMINI_API_KEY:
        result = ask_gemini(prompt)
        if result: return format_ai_result(result)

    # 2️⃣ Groq (High-Speed Fallback)
    if GROQ_API_KEY:
        result = ask_groq(prompt, "llama-3.3-70b-versatile")
        if result: return format_ai_result(result)

    # 3️⃣ OpenRouter (Breadth Fallback)
    if OPENROUTER_API_KEY:
        fallback_models = [
            "meta-llama/llama-3.1-8b-instruct:free",
            "mistralai/mistral-7b-instruct:free"
        ]
        for model in fallback_models:
            result = ask_openrouter(prompt, model)
            if result: return format_ai_result(result)

    # 4️⃣ Keyword Fallback
    return self_fallback(user_message)

# =========================
# AI ADAPTERS
# =========================

def ask_gemini(prompt):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        for model_name in ["gemini-1.5-flash", "gemini-1.5-pro"]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return extract_json(response.text)
            except Exception as e:
                if "429" in str(e): break
    except: pass
    return None

def ask_groq(prompt, model_name):
    try:
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        res = requests.post(GROQ_URL, headers=GROQ_HEADERS, json=data, timeout=10)
        if res.status_code == 200:
            content = res.json()["choices"][0]["message"]["content"]
            return extract_json(content)
    except Exception as e:
        print(f"DEBUG: Chat Groq failed: {str(e)}")
    return None

def ask_openrouter(prompt, model_name):
    try:
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        res = requests.post(OPENROUTER_URL, headers=OPENROUTER_HEADERS, json=data, timeout=15)
        if res.status_code == 200:
            content = res.json()["choices"][0]["message"]["content"]
            return extract_json(content)
    except: pass
    return None

def format_ai_result(result_json):
    intent = str(result_json.get('intent', 'SOHBET')).upper()
    return {
        'intent': 'shopping' if 'ALISVERIS' in intent else 'chat',
        'query': result_json.get('query', ''),
        'response': result_json.get('response', 'Size nasıl yardımcı olabilirim?'),
        'error': None
    }

def extract_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match: return json.loads(match.group())
    except: pass
    return None

def self_fallback(user_message):
    message_lower = user_message.strip().lower()
    words = message_lower.split()
    chat_keywords = ['merhaba', 'selam', 'nasılsın', 'kimsin', 'teşekkür', 'sağol', 'hey', 'hi', 'hello']
    
    if any(k == message_lower for k in chat_keywords):
        return {
            'intent': 'chat',
            'query': '',
            'response': 'Merhaba! Şu an yoğunluk nedeniyle kısıtlı moddayım ama ürün aramanıza yardımcı olabilirim. Ne aramıştınız?',
            'error': None
        }

    products_db = {
        'laptop': ['laptop', 'dizüstü', 'macbook', 'bilgisayar', 'pc'],
        'phone': ['phone', 'telefon', 'iphone', 'samsung', 'mobile', 'cep'],
        'headphones': ['kulaklık', 'headphone', 'airpods'],
        'shoes': ['ayakkabı', 'sneaker', 'bot'],
        'woman': ['kadın', 'woman', 'bayan']
    }
    
    detected_query = ""
    for api_name, keywords in products_db.items():
        if any(k in message_lower for k in keywords):
            detected_query = api_name
            break
            
    if not detected_query and len(words) <= 3:
        detected_query = message_lower

    if detected_query:
        return {
            'intent': 'shopping',
            'query': detected_query,
            'response': f'"{user_message}" için ürünleri buluyorum (Kısıtlı Mod aktif)...',
            'error': None
        }
    
    return {
        'intent': 'chat',
        'query': '',
        'response': 'Şu an kısıtlı moddayım. Lütfen aramak istediğiniz ürünü yazın.',
        'error': None
    }
