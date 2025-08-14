# utils/gemini_answer.py
import os
import certifi

# This line tells the 'requests' library (used by SerpApi) where to find trusted certificates.
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

# --- Search Functions ---

def search_for_gif_on_giphy(query: str):
    """
    Searches for a GIF on Giphy's API and returns the URL.
    """
    try:
        giphy_api_key = os.getenv("GIPHY_API_KEY")
        if not giphy_api_key:
            return None, "GIF search is not configured."

        params = {
            "api_key": giphy_api_key,
            "q": query,
            "limit": 1,
            "rating": "pg-13",
            "lang": "en"
        }
        
        response = requests.get("https://api.giphy.com/v1/gifs/search", params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("data"):
            gif_data = data["data"][0]
            gif_url = gif_data["images"]["original"]["url"]
            attribution = f"GIF result for '{query}' from Giphy."
            return gif_url, attribution
        else:
            return None, f"I couldn't find a Giphy GIF for '{query}'."

    except Exception as e:
        print(f"Giphy API Error: {e}")
        return None, "Sorry, I couldn't connect to the GIF service."


def search_for_image_on_google(query):
    """Searches for a specific image on Google using SerpApi."""
    try:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not serpapi_key: return None, "Specific image search is not configured."
        params = { "q": query, "engine": "google_images", "ijn": "0", "api_key": serpapi_key }
        search = GoogleSearch(params)
        results = search.get_dict()
        if results.get("images_results"):
            return results["images_results"][0].get("original"), f"Image of '{query}' from Google."
        return None, f"I couldn't find a Google Image for '{query}'."
    except Exception as e:
        print(f"SerpApi Error: {e}")
        return None, "Error connecting to specific image search."

def search_for_image_on_pexels(query):
    """Searches for a generic photo on Pexels."""
    try:
        pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not pexels_api_key: return None, "Generic image search is not configured."
        headers = {"Authorization": pexels_api_key}
        params = {"query": query, "per_page": 1}
        response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("photos"):
            photo = data["photos"][0]
            return photo['src']['large'], f"Photo by {photo['photographer']} on Pexels."
        return None, f"I couldn't find a stock photo for '{query}'."
    except Exception as e:
        print(f"Pexels API Error: {e}")
        return None, "Error connecting to the photo service."

def search_for_video_on_youtube(query: str):
    """
    Searches for an embeddable YouTube video with a 3-pass priority system.
    """
    try:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not serpapi_key:
            return None, "YouTube search is not configured."

        OFFICIAL_CHANNELS = [
            "t-series", "sonymusic", "yrf", "saregama", "shemaroo",
            "tips official", "zee music", "eros now", "universal music"
        ]

        params = { "q": query, "engine": "google_videos", "api_key": serpapi_key }
        search = GoogleSearch(params)
        results = search.get_dict()

        if results.get("video_results"):
            videos = results["video_results"]

            # Pass 1: Official Channels
            for video in videos:
                channel_name = video.get("channel", "").lower()
                if any(official in channel_name for official in OFFICIAL_CHANNELS):
                    return video.get("link"), f"Video: '{video.get('title')}' on YouTube."

            # Pass 2: Filter Playlists
            for video in videos:
                title = video.get("title", "").lower()
                length = video.get("length", "")
                if any(kw in title for kw in ["playlist", "jukebox", "compilation", "hits"]): continue
                if length.count(':') == 2: continue
                return video.get("link"), f"Video: '{video.get('title')}' on YouTube."

            # Pass 3: Fallback
            return videos[0].get("link"), f"Video: '{videos[0].get('title')}' on YouTube."

        return None, f"I couldn't find any YouTube video for '{query}'."

    except Exception as e:
        print(f"SerpApi YouTube Error: {e}")
        return None, "Error connecting to YouTube search."


def search_for_video_on_pexels(query):
    """Searches for a generic video on Pexels."""
    try:
        pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not pexels_api_key: return None, "Generic video search is not configured."
        headers = {"Authorization": pexels_api_key}
        params = {"query": query, "per_page": 1}
        response = requests.get("https://api.pexels.com/v1/videos/search", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("videos"):
            video = data["videos"][0]
            mp4_files = [f for f in video['video_files'] if 'video/mp4' in f.get('file_type', '')]
            if mp4_files:
                mp4_files.sort(key=lambda x: x.get('width', 0), reverse=True)
                return mp4_files[0]['link'], f"Video by {video['user']['name']} on Pexels."
        return None, f"I couldn't find a stock video for '{query}'."
    except Exception as e:
        print(f"Pexels Video API Error: {e}")
        return None, "Error connecting to the video service."

# --- The Main AI Brain ---
def get_gemini_answer(text_input):
    """Analyzes user's prompt to decide intent and entity type."""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # --- THE FIX IS HERE ---
        # The 'request_options' parameter was causing a crash because it's not supported
        # in this library's constructor. We have removed it. The library will now
        # use its own reasonable default timeout.
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        
        prompt = f"""
        Analyze the user's request. Respond with ONLY a valid JSON object.

        The JSON must have an "intent" key.
        The "intent" can be: "answer_text", "find_image", "find_pexels_video", "find_youtube_video", or "find_gif".

        - "find_gif": For any request that includes the word "gif" or "giphy". This has high priority.

        Finally, include a "content" key with the search keywords or the full text answer.

        Examples:
        User Request: "who was albert einstein" -> {{"intent": "answer_text", "content": "Albert Einstein was a German-born theoretical physicist..."}}
        User Request: "shreya ghoshal saiyara song video" -> {{"intent": "find_youtube_video", "content": "Shreya Ghoshal Saiyara song"}}
        User Request: "find a gif of a cat typing" -> {{"intent": "find_gif", "content": "cat typing"}}
        User Request: "can you generate a giphy of harry potter magic" -> {{"intent": "find_gif", "content": "harry potter magic"}}

        User's Request: "{text_input}"
        """
        
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_response)

    except Exception as e:
        # This will now catch any real errors without being triggered by our faulty code.
        print(f"Error in Gemini intent analysis: {e}")
        return {"intent": "answer_text", "content": "I'm sorry, I had a problem connecting to the AI. Please try again."}