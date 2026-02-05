try:
    from google import genai
    print("SUCCESS: 'google.genai' imported successfully.")
    import google
    print(f"Google package location: {google.__path__}")
except ImportError as e:
    print(f"ERROR: {e}")
except Exception as e:
    print(f"UNEXPECTED ERROR: {e}")
