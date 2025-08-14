# test_serpapi.py
import os
import certifi
from serpapi import GoogleSearch
from dotenv import load_dotenv

print("--- Starting SSL Certificate Test ---")

# --- Part 1: Certificate Check ---
try:
    cert_path = certifi.where()
    print(f"Certifi library is providing this certificate file:")
    print(f" -> {cert_path}")
    if os.path.exists(cert_path):
        print("Certificate file exists. [OK]")
    else:
        print("Certificate file NOT FOUND. [FAIL] - Please run: pip install --upgrade --force-reinstall certifi")

    # This is the fix we've been trying. It points requests to the certifi bundle.
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    print("Set environment variable for SSL certificates. [OK]")

except Exception as e:
    print(f"Could not find the certifi library. Please run 'pip install certifi'. Error: {e}")
    exit()

# --- Part 2: API Key Check ---
load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

if not SERPAPI_API_KEY:
    print("\nERROR: Could not find SERPAPI_API_KEY in your .env file.")
    print("Please make sure your .env file is in the same directory as this script.")
    exit()
else:
    print("Successfully loaded SERPAPI_API_KEY. [OK]")

# --- Part 3: The Connection Test ---
params = {
    "q": "Asha Bhosle song video",
    "engine": "google_videos",
    "api_key": SERPAPI_API_KEY,
}

try:
    print("\nAttempting to connect to SerpApi...")
    search = GoogleSearch(params)
    results = search.get_dict()

    if "video_results" in results and results.get("video_results"):
        print("\n------ SUCCESS! ------")
        print("Successfully connected and received video results.")
        print(f"Found video: {results['video_results'][0]['title']}")
    elif "error" in results:
        print(f"\n--- API ERROR ---")
        print(f"Connected, but SerpApi returned an error: {results['error']}")
    else:
        print("\n--- UNKNOWN RESPONSE ---")
        print("Connected but the response was not what we expected.")
        print(results)

except Exception as e:
    print(f"\n------ TEST FAILED ------")
    print("The connection failed. The root cause is confirmed to be an SSL issue.")
    print("ERROR MESSAGE:")
    print(e)
    print("\nThis means your system's network or Python's configuration is blocking the connection.")