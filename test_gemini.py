import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_connection():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file")
        return False
    
    try:
        # Configure and test the API
        genai.configure(api_key=api_key)
        
        # List available models to verify connection
        print("Testing Gemini API connection...")
        models = genai.list_models()
        
        # Check if required models are available
        required_models = ['gemini-pro', 'gemini-pro-vision']
        available_models = [m.name.split('/')[-1] for m in models if 'models/' in m.name]
        
        print("\nAvailable models:")
        for model in available_models:
            print(f"- {model}")
            
        # Test model response
        print("\nTesting text generation...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, can you hear me?")
        
        print("\nAPI Response:")
        print(response.text)
        
        return True
        
    except Exception as e:
        print(f"\nError testing Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Gemini API Test Script")
    print("=====================")
    success = test_gemini_connection()
    if success:
        print("\n✅ Gemini API connection successful!")
    else:
        print("\n❌ Failed to connect to Gemini API. Please check your API key and internet connection.")
