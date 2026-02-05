import os
import requests
import json
import dotenv

dotenv.load_dotenv()
api_key = os.getenv("SERP_API_KEY")

params = {
    "engine": "google",
    "q": "iphone 15",
    "api_key": api_key,
    "gl": "tr",
    "hl": "tr"
}

try:
    response = requests.get("https://serpapi.com/search", params=params, timeout=10)
    data = response.json()
    
    inline = data.get("inline_shopping_results", [])
    shopping = data.get("shopping_results", [])
    organic = data.get("organic_results", [])
    
    print("--- Inline Shopping Results (Ads) ---")
    for p in inline[:2]:
        print(f"Title: {p.get('title')}")
        print(f"Thumbnail: {p.get('thumbnail')}")
        print(f"Image: {p.get('image')}")
        print(f"Keys: {list(p.keys())}")
        print("-" * 20)

    print("\n--- Shopping Results (Embedded) ---")
    for p in shopping[:2]:
        print(f"Title: {p.get('title')}")
        print(f"Thumbnail: {p.get('thumbnail')}")
        print(f"Image: {p.get('image')}")
        print(f"Keys: {list(p.keys())}")
        print("-" * 20)
        
    print("\n--- Organic Results ---")
    for p in organic[:2]:
        print(f"Title: {p.get('title')}")
        print(f"Thumbnail: {p.get('thumbnail')}")
        print(f"Rich Snippet: {p.get('rich_snippet', {}).get('top', {}).get('detected_extensions', {}).get('image')}")
        print(f"Keys: {list(p.keys())}")
        print("-" * 20)

except Exception as e:
    print(f"Error: {e}")
