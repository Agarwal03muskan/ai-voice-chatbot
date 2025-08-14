# check_models.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()

try:
    print("Connecting to Google AI...")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("\nFetching available models...\n")
    
    # List all models and print their names
    for model in genai.list_models():
        # We only care about models that support the 'generateContent' method
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")

    print("\nScript finished.")

except Exception as e:
    print(f"\nAn error occurred: {e}")