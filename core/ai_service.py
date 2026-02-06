import os
import time
import json
import re
import hashlib
import requests
from google import genai

from django.conf import settings
from django.core.cache import cache

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

# Cache (in-memory + Django cache)
MEMORY_CACHE = {}


# =========================
# CACHE HELPERS
# =========================

def get_cache_key(products):
    """Ürün listesi hash'i ile cache key oluştur"""
    products_str = json.dumps(
        [(p.get('title'), p.get('site'), p.get('price')) for p in products],
        sort_keys=True
    )
    return hashlib.md5(products_str.encode()).hexdigest()

def get_cached_analysis(products):
    """Memory cache'ten kontrol et"""
    cache_key = get_cache_key(products)
    
    # 1. Memory cache (hızlı)
    if cache_key in MEMORY_CACHE:
        cached_time, cached_data = MEMORY_CACHE[cache_key]
        if time.time() - cached_time < 3600:  # 1 saat geçerliliği
            print(f"✅ MEMORY CACHE HIT: {cache_key[:8]}")
            return cached_data
    
    # 2. Django cache (daha büyük)
    try:
        django_cache_key = f"ai_analysis_{cache_key}"
        cached_data = cache.get(django_cache_key)
        if cached_data:
            print(f"✅ DJANGO CACHE HIT: {cache_key[:8]}")
            MEMORY_CACHE[cache_key] = (time.time(), cached_data)
            return cached_data
    except:
        pass
    
    return None

def set_cached_analysis(products, data):
    """Cache'le her iki sisteme de"""
    cache_key = get_cache_key(products)
    
    # Memory cache
    MEMORY_CACHE[cache_key] = (time.time(), data)
    
    # Django cache
    try:
        django_cache_key = f"ai_analysis_{cache_key}"
        cache.set(django_cache_key, data, timeout=3600)
    except:
        pass


# =========================
# PRICE & RATING PARSERS
# =========================

def parse_price(price_str):
    if not price_str:
        return None
    cleaned = re.sub(r"[^\d.,]", "", str(price_str))
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except:
        return None

def get_num_rating(p):
    r = p.get("rating", 0)
    if isinstance(r, str):
        mapping = {"five": 5, "four": 4, "three": 3, "two": 2, "one": 1}
        r_lower = r.lower()
        if r_lower in mapping: return mapping[r_lower]
        return parse_price(r) or 0
    return float(r) if r else 0

def get_num_reviews(p):
    rev = p.get("review_count", 0)
    if isinstance(rev, str):
        cleaned = re.sub(r"[^\d]", "", rev)
        return int(cleaned) if cleaned else 0
    return int(rev) if rev else 0


# =========================
# 1️⃣ ÜRÜN ETİKETLEME & SIRALAMA
# =========================

def tag_products(products):
    if not products:
        return products

    try:
        # Değerleri hesapla
        for p in products:
            p["_price_val"] = parse_price(p.get("price")) or 999999
            p["_rating_val"] = get_num_rating(p)
            p["_review_val"] = get_num_reviews(p)
            p["tags"] = []

        cheapest = min(products, key=lambda x: x["_price_val"])
        highest_rating = max(products, key=lambda x: x["_rating_val"])
        most_reviews = max(products, key=lambda x: x["_review_val"])

        for p in products:
            p["_sort_priority"] = 99
            if p == cheapest:
                p["tags"].append("En iyi fiyat")
                p["_sort_priority"] = 1
            elif p == highest_rating:
                p["tags"].append("En yüksek puan")
                p["_sort_priority"] = 2
            elif p == most_reviews:
                p["tags"].append("En çok yorum")
                p["_sort_priority"] = 3

        products.sort(key=lambda x: x["_sort_priority"])

    except Exception as e:
        print(f"DEBUG: Tagging/Sorting error: {str(e)}")
        return products

    return products


def build_products_text(products):
    return "\n".join([
        f"{p.get('title')} | {p.get('site')} | {p.get('price')} TL | "
        f"Puan:{p.get('rating','N/A')} | Yorum:{p.get('review_count',0)} | "
        f"Etiketler: {', '.join(p.get('tags', []))}"
        for p in products
    ])


# =========================
# MAIN FUNCTION
# =========================

def analyze_products(products):
    if not products:
        return {"error": "Ürün bulunamadı."}
    
    products = tag_products(products)

    # Cache kontrol
    cached_result = get_cached_analysis(products)
    if cached_result:
        return {"data": cached_result, "source": "cache"}

    products_text = build_products_text(products[:10])
    prompt = build_prompt(products_text)

    # 1️⃣ Gemini (Primary)
    if GEMINI_API_KEY:
        result = ask_gemini(prompt)
        if result:
            set_cached_analysis(products, result)
            return {"data": result, "source": "gemini"}

    # 2️⃣ Groq (High-Speed Fallback)
    if GROQ_API_KEY:
        result = ask_groq(prompt, "llama-3.3-70b-versatile")
        if result:
            set_cached_analysis(products, result)
            return {"data": result, "source": "groq"}

    # 3️⃣ OpenRouter (Breadth Fallback)
    if OPENROUTER_API_KEY:
        fallback_models = [
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemma-2-9b-it:free",
            "mistralai/mistral-7b-instruct:free"
        ]
        for model in fallback_models:
            result = ask_openrouter(prompt, model)
            if result:
                set_cached_analysis(products, result)
                return {"data": result, "source": "openrouter"}

    return {"error": "AI servisleri yoğunlukta. Lütfen biraz sonra tekrar deneyin."}


def build_prompt(products_text):
    return f"""Sen akıllı bir alışveriş asistanısın. Aşağıdaki ürünleri incele ve kullanıcıya samimi, kısa ve yardımcı bir yorum yap. 
İlla bir karşılaştırma tablosu yapmana gerek yok, sadece genel bir öneri veya dikkat çekici bir noktayı belirtmen yeterli.
Yanıtını MUTLAKA şu JSON formatında ver, başka metin ekleme:
{{
  "commentary": "buraya doğal ve yardımcı yorumunu yaz"
}}

Ürünler:
{products_text}"""


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
                print(f"DEBUG: Gemini {model_name} failed: {str(e)}")
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
        print(f"DEBUG: Groq failed: {str(e)}")
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

def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match: return json.loads(match.group())
    except: pass
    return None
