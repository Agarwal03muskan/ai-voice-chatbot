Genivus AI Chatbot

A multi-modal, conversational AI voice chatbot built with Flask and Google Gemini. This interactive assistant can understand context, answer questions, search for media, create sketches from images, and generate memes on demand.
![alt text](https://via.placeholder.com/800x400.png?text=App+Demo+GIF+Goes+Here)

✨ Core Features

Conversational Memory: Remembers the context of the current conversation in a single session, just like modern LLMs.
Voice-to-Text: Uses the browser's SpeechRecognition API for voice input.
Text-to-Speech: Provides spoken audio responses for answers.
Multi-Modal Functionality:
Fact-Checking: Performs real-time Google searches for factual queries.
Image & GIF Search: Fetches images and GIFs from Google Images and Giphy.
YouTube Video Search: Finds and embeds YouTube videos.
AI Sketch Generation: Converts user-uploaded images into artistic sketches using OpenCV.
AI Meme Generation: Creates memes from user-uploaded images with custom or AI-suggested text.
User Authentication: Secure login, registration, and profile management.
Conversation History: Saves and allows users to revisit past conversations.
⚠️ Disclaimer: This project is intended for demonstration and educational purposes only. It is not configured for a production environment. Do not deploy it with the default settings or expose sensitive API keys on a public server.


🛠️ Tech Stack

Backend: Flask, Python
Database: Flask-SQLAlchemy (with SQLite for development)
AI & APIs:
Google Gemini Pro: For intent detection and conversational text generation.
Google Gemini Vision: For AI-powered meme text suggestions.
SerpApi: For real-time Google Search, Image, and Video results.
Giphy API: For GIF search.
gTTS: For text-to-speech conversion.
Frontend: HTML, CSS, JavaScript (no frameworks)
Image Processing: OpenCV, Pillow


⚙️ How It Works (Architecture)

The chatbot's intelligence comes from a multi-step process designed to understand user intent before acting.
Input: The user either types a message or speaks into the microphone. The frontend JavaScript captures this input.
Session Management: The frontend maintains the current conversation log in sessionStorage. This entire log is sent to the backend with every new message.
Intent Detection: The backend's primary endpoint (/process-text) first sends the user's raw text to a Gemini model trained to classify the user's intent (e.g., fact_check, find_image, answer_text).
Tool Use: Based on the detected intent, the backend routes the request to the appropriate tool:
fact_check → Calls SerpApi for a Google search.
find_image → Calls SerpApi for Google Images.
find_gif → Calls the Giphy API.
answer_text → Calls a conversational Gemini model, providing the full session history for context.
Image/Meme routes are handled by separate endpoints (/upload-image, /generate-meme).
Response Generation: The tool returns a result (a text answer, an image URL, etc.). A text summary is generated and converted to an MP3 file using gTTS.
Rendering: The backend sends a JSON object to the frontend containing the text response, an audio URL, and any media URLs (image, GIF, YouTube embed). The JavaScript then dynamically renders these elements in the chat window.



🚀 Local Setup and Installation
Follow these steps to run the project on your local machine.
1. Prerequisites
Git installed.
Python 3.10+ installed.
2. Clone the Repository


git clone https://github.com/YourUsername/chatbot_final.git
cd chatbot_final


3. Set Up a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.



# Create the virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
4. Install Dependencies
Install all the required Python libraries from the requirements.txt file.


pip install -r requirements.txt


5. Set Up Environment Variables
This is the most important step. The application requires API keys to function.
Create a new file in the root directory named .env.
Copy the content of .env.example (if provided) or paste the following into your new .env file:
code
Env
# Flask Secret Key (can be any random string)
SECRET_KEY='a_very_long_and_random_secret_key_for_security'

# Google AI API Key (for Gemini)
# Get it from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY='YOUR_GOOGLE_API_KEY'

# SerpApi API Key (for Google Search, Images, Videos)
# Get it from: https://serpapi.com/
SERPAPI_API_KEY='YOUR_SERPAPI_KEY'

# Giphy API Key (for GIFs)
# Get it from: https://developers.giphy.com/
GIPHY_API_KEY='YOUR_GIPHY_API_KEY'
Replace the placeholder values ('YOUR_...') with your actual API keys.



6. Run the Application
The application will automatically create the site.db database file on the first run.


flask run --port=5001

You can now access the chatbot in your web browser at: http://127.0.0.1:5001
You will need to register a new user to start chatting.