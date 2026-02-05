import os
import requests
import json
import dotenv

dotenv.load_dotenv()
api_key = os.getenv("SERP_API_KEY", "").strip()

def search(query, engine="google", tbm="shop"):
    print(f"\n--- Testing Engine: {engine} | TBM: {tbm} ---")
    params = {
        "engine": engine,
        "q": query,
        "api_key": api_key,
        "gl": "tr",
        "hl": "tr",
        "no_cache": "true"
    }
    if tbm:
        params["tbm"] = tbm
        
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        data = response.json()
        
        # Check all possible result containers
        containers = ["shopping_results", "inline_shopping_results", "ads", "organic_results"]
        for container in containers:
            items = data.get(container, [])
            if not items: continue
            
            print(f"Found {len(items)} in {container}")
            for i, item in enumerate(items[:3]):
                print(f"  [{container} {i}] Title: {item.get('title')}")
                print(f"  [{container} {i}] Source: {item.get('source')}")
                print(f"  [{container} {i}] Link: {item.get('link')}")
                print(f"  [{container} {i}] Product Link: {item.get('product_link')}")
                # Check for nested links (e.g. in offers)
                offers = item.get("offers", [])
                if offers:
                    print(f"  [{container} {i}] Offers: {len(offers)}")
                    for j, offer in enumerate(offers[:2]):
                        print(f"    - Offer {j} Link: {offer.get('link')}")
                
                # Check if 'trendyol' or 'hepsi' or 'amazon' is in any string value
                item_str = json.dumps(item).lower()
                for store in ["trendyol", "hepsiburada", "amazon"]:
                    if store in item_str:
                        print(f"  [!!!] Found '{store}' in raw item data.")

        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

query = "iphone 15"
# Try standard shopping search
data1 = search(query, engine="google", tbm="shop")
# Try google_shopping engine
data2 = search(query, engine="google_shopping", tbm=None)
# Try regular search (ads often have direct links)
data3 = search(query, engine="google", tbm=None)

# Save one for deep manual inspection if needed
if data1:
    with open("raw_serp_deep_analysis.json", "w", encoding="utf-8") as f:
        json.dump(data1, f, indent=4, ensure_ascii=False)
