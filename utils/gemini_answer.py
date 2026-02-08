# utils/gemini_answer.py
import os
import certifi
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

# --- MODIFIED: This function is now conversational and the error is fixed ---
def generate_conversational_answer(query: str, history: list):
    """
    Generates a conversational text answer using the Gemini API, aware of chat history.
    """
    try:
        # --- THIS IS THE FIX ---
        # The incorrect check 'if not genai._config.get('api_key')' has been removed.
        # We now directly configure the API key. This is safe and idempotent.
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        model = genai.GenerativeModel('models/gemini-robotics-er-1.5-preview')
        
        # Start a chat session with the provided history
        chat = model.start_chat(history=history)
        response = chat.send_message(query)
        
        return response.text
    except Exception as e:
        print(f"Error during conversational text generation: {e}")
        return "I'm sorry, I encountered an error while trying to formulate a response."

# --- MODIFIED: This function now uses the conversational one as a fallback ---
def google_search_for_answer(query: str, history: list):
    """
    Performs a direct Google search for factual questions. If no direct answer is found,
    it falls back to the conversational model.
    """
    try:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not serpapi_key:
            return "I'm sorry, my search feature is not configured."

        params = {"q": query, "api_key": serpapi_key, "engine": "google"}
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        elif "answer_box" in results and "snippet" in results["answer_box"]:
            return results["answer_box"]["snippet"]
        elif "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        elif "organic_results" in results and results["organic_results"][0].get("snippet"):
            return results["organic_results"][0]["snippet"]
        else:
            # Fallback to the conversational model if no direct search result is found
            return generate_conversational_answer(query, history)
            
    except Exception as e:
        print(f"SerpApi factual search error: {e}")
        return generate_conversational_answer(query, history)

# --- All other functions (get_meme_suggestion, search_for_gif, etc.) remain unchanged ---
def get_meme_suggestion(image_bytes):
    """
    Uses Gemini Vision to generate meme text for a given image.
    """
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes
        }

        prompt = """
        You are a witty meme expert. Look at this image and generate a short, funny meme caption for it.
        Respond with ONLY a valid JSON object with a "top_text" key and a "bottom_text" key.
        Keep the text concise and punchy. The text should be in all caps.
        
        Example response:
        {"top_text": "WHEN YOU SEE THE WAITER", "bottom_text": "COMING WITH YOUR FOOD"}
        """
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content([prompt, image_part])
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        suggestion = json.loads(cleaned_response)
        return True, suggestion

    except Exception as e:
        print(f"Error in Gemini meme suggestion: {e}")
        return False, {"top_text": "AI couldn't think", "bottom_text": "of a joke"}
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


# The Main AI Brain
def get_gemini_answer(text_input):
    """
    Analyzes user's prompt to decide intent and entity type.
    This function ONLY detects intent; it does not generate answers.
    """
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        model = genai.GenerativeModel('models/gemini-robotics-er-1.5-preview')
        
        prompt = f"""
        Analyze the user's request. Respond with ONLY a valid JSON object.

        The JSON must have an "intent" key.
        The "intent" can be one of: "fact_check", "answer_text", "find_image", "find_pexels_video", "find_youtube_video", or "find_gif".

        - "fact_check": Use for questions seeking a specific, verifiable fact (e.g., dates, definitions, math, stats).
        - "find_gif": Use for any request that includes "gif" or "giphy".
        - "find_youtube_video": Use for requests explicitly asking for a "video" of a song, person, or specific event.
        - "find_pexels_video": Use for generic video requests like "show me a video of the ocean".
        - "find_image": Use for requests explicitly asking for an "image", "picture", or "photo".
        - "answer_text": Use for all other general questions, conversations, or creative tasks (like writing a poem).

        Finally, include a "content" key with the simplified search keywords. For "fact_check" and "answer_text", this should be the user's original, unmodified question.

        Examples:
        User Request: "when was diwali celebrated in 2024" -> {{"intent": "fact_check", "content": "when was diwali celebrated in 2024"}}
        User Request: "what is the capital of France" -> {{"intent": "fact_check", "content": "what is the capital of France"}}
        User Request: "write a short story about a dragon" -> {{"intent": "answer_text", "content": "write a short story about a dragon"}}
        User Request: "shreya ghoshal saiyara song video" -> {{"intent": "find_youtube_video", "content": "Shreya Ghoshal Saiyara song"}}
        User Request: "find a gif of a cat typing" -> {{"intent": "find_gif", "content": "cat typing"}}
        User Request: "show me a picture of the Eiffel Tower" -> {{"intent": "find_image", "content": "Eiffel Tower"}}

        User's Request: "{text_input}"
        """
        
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_response)

    except Exception as e:
        print(f"Error in Gemini intent analysis: {e}")
        return {"intent": "answer_text", "content": "I'm sorry, I had a problem understanding your request. Could you try rephrasing?"}