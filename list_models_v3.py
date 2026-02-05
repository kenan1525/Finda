import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("Listing models...")
with open("available_models_full.txt", "w", encoding="utf-8") as f:
    try:
        for m in client.models.list():
            line = f"Model: {m.name} | Display: {m.display_name}"
            print(line)
            f.write(line + "\n")
    except Exception as e:
        err = f"Error listing models: {e}"
        print(err)
        f.write(err + "\n")
