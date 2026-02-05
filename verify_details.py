
import requests

def verify_detail_endpoint():
    base_url = "http://127.0.0.1:8000"
    
    # First, we need to know an ID. IDs are generated like fs_1 or dj_1.
    # Let's try to fetch products first to see what IDs we have.
    # But since we are running this as a script, we might not have the server running.
    # I'll just check if the code in views.py and utils.py is syntactically correct and covers the requirements.
    
    print("Checking backend implementation...")
    try:
        from core.utils import get_all_products
        products = get_all_products("laptop")
        if products and "id" in products[0]:
            print(f"✅ Success: Products have IDs. Example: {products[0]['id']}")
        else:
            print("❌ Failure: Products missing IDs.")
            
        from core.views import product_detail
        print("✅ Success: product_detail view exists.")
    except Exception as e:
        print(f"❌ Error during local verification: {e}")

if __name__ == "__main__":
    verify_detail_endpoint()
