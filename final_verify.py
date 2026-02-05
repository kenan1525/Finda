import os
import django
import dotenv
import json

dotenv.load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finda.settings')
django.setup()

from core.utils import get_all_products

def verify():
    query = "iphone 15"
    print(f"Testing for query: {query}")
    products = get_all_products(query)
    
    findings = []
    for p in products[:5]:
        findings.append({
            "title": p.get("title")[:30],
            "has_image": bool(p.get("image")),
            "is_direct": any(s in p.get("link", "").lower() for s in ["trendyol.com", "hepsiburada.com", "amazon.com.tr", "n11.com"]),
            "domain": p.get("link", "").split("/")[2] if "http" in p.get("link", "") else "N/A"
        })
    
    print(json.dumps(findings, indent=2))

if __name__ == "__main__":
    verify()
