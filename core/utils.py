import requests
import random
import re
import os
from urllib.parse import urlparse, parse_qs, quote
from django.conf import settings
import time

CACHE = {}

# -------------------------
# TEXT NORMALIZATION & UTILS
# -------------------------
def normalize_title(title):
    text = title.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_real_link(google_link, title="", source=""):
    """
    Google'ın hapis linklerini kırar. 
    Eğer link temizlenemiyorsa, ilgili mağazanın arama sayfasına yönlendirir.
    """
    if not google_link or google_link == "#":
        return "#"
    
    source_lower = (source or "").lower()
    query_encoded = quote(title or "")

    # 1. Google içermiyorsa zaten direkt linktir
    if "google.com" not in google_link:
        return google_link

    # 2. URL Parametrelerini temizlemeyi dene
    try:
        parsed_url = urlparse(google_link)
        params = parse_qs(parsed_url.query)
        
        # 'adurl' veya 'url' parametreleri varsa çek
        for key in ['adurl', 'url', 'q']:
            if params.get(key):
                clean = params.get(key)[0]
                if clean.startswith("http"):
                    return clean
    except:
        pass

    # 3. ZORLAYICI MANTIK (Fallback): Google bizi bırakmıyorsa biz kendi linkimizi yaparız
    if "trendyol" in source_lower:
        return f"https://www.trendyol.com/sr?q={query_encoded}"
    elif "amazon" in source_lower:
        return f"https://www.amazon.com.tr/s?k={query_encoded}"
    elif "hepsiburada" in source_lower:
        return f"https://www.hepsiburada.com/ara?q={query_encoded}"
    elif "n11" in source_lower:
        return f"https://www.n11.com/arama?q={query_encoded}"
    elif "boyner" in source_lower:
        return f"https://www.boyner.com.tr/arama?q={query_encoded}"

    return google_link

# -------------------------
# SERP API (GÜÇLENDİRİLMİŞ)
# -------------------------
def fetch_serp_products(query):
    results = []
    api_key = getattr(settings, "SERP_API_KEY", os.getenv("SERP_API_KEY", "")).strip()

    if not api_key:
        print("SERP API KEY bulunamadı")
        return results

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "gl": "tr",
        "hl": "tr",
        "direct_link": "true"
    }

    try:
        response = requests.get("https://serpapi.com/search.json", params=params, timeout=10)
        data = response.json()
        shopping_results = data.get("shopping_results", [])

        for i, p in enumerate(shopping_results[:15]):
            p_id = f"serp_{i}_{random.randint(1000,9999)}"
            
            # Ham linki al
            raw_link = p.get("direct_link")
            offers = p.get("offers")
            if not raw_link and offers and isinstance(offers, list) and len(offers) > 0:
                raw_link = offers[0].get("link")
            if not raw_link:
                raw_link = p.get("product_link") or p.get("link") or "#"

            # FİNDA DOKUNUŞU: Linki mağazaya zorla
            product_title = p.get("title", "")
            source_name = p.get("source", "")
            final_link = extract_real_link(raw_link, product_title, source_name)

            # Site Renkleri
            source_lower = source_name.lower()
            site_color = "warning"
            if "trendyol" in source_lower: site_color = "orange"
            elif "hepsiburada" in source_lower: site_color = "hb"
            elif "amazon" in source_lower: site_color = "amazon"
            elif "n11" in source_lower: site_color = "n11"
            elif "boyner" in source_lower: site_color = "boyner"

            results.append({
                "id": p_id,
                "title": product_title,
                "price": p.get("price", "Fiyat yok"),
                "image": p.get("thumbnail") or p.get("image"),
                "brand": source_name,
                "rating": p.get("rating", 0),
                "review_count": p.get("reviews", 0),
                "site": source_name,
                "site_color": site_color,
                "delivery_info": p.get("delivery", "Mağaza Detayı"),
                "positive_ratio": int(p.get("rating", 0) * 20) if p.get("rating") else 0,
                "review_summary": "",
                "description": p.get("snippet", ""),
                "link": final_link
            })
    except Exception as e:
        print("SerpAPI Error:", e)

    return results

# -------------------------
# DEMO APIs (FakeStore + DummyJSON)
# -------------------------
def fetch_demo_products(query):
    results = []
    query_words = query.lower().split()
    try:
        res = requests.get("https://fakestoreapi.com/products", timeout=5)
        for p in res.json():
            title_lower = p["title"].lower()
            if query_words and not all(word in title_lower for word in query_words):
                continue
            results.append({
                "id": f"fs_{p['id']}",
                "title": p["title"],
                "price": f"{p['price']} $",
                "image": p["image"],
                "rating": p.get("rating", {}).get("rate", 0),
                "review_count": p.get("rating", {}).get("count", 0),
                "site": "FakeStore",
                "site_color": "primary",
                "delivery_info": "2-3 gün",
                "positive_ratio": int(p.get("rating", {}).get("rate", 0) * 20),
                "link": "#"
            })
    except: pass
    return results

# -------------------------
# MAIN ENTRY
# -------------------------
# def get_all_products(query):
#     results = []
#     serp_results = fetch_serp_products(query)
#     results.extend(serp_results)
#     if len(results) < 5:
#         results.extend(fetch_demo_products(query))
#     return results




def get_all_products(query):
    now = time.time()

    # cache varsa ve süresi geçmediyse
    if query in CACHE:
        cached_data, cached_time = CACHE[query]
        if now - cached_time < 600:
            print("✅ CACHE'DEN GELDİ:", query)
            return cached_data
        else:
            del CACHE[query]

    print("🌐 API'DEN GELDİ:", query)

    results = []
    serp_results = fetch_serp_products(query)
    results.extend(serp_results)

    if len(results) < 5:
        results.extend(fetch_demo_products(query))

    CACHE[query] = (results, now)
    return results
