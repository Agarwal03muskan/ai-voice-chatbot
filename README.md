# Genivus AI Chatbot

A multi-modal, conversational AI voice chatbot built with Flask and Google Gemini. This interactive assistant can understand context, answer questions, search for media, create sketches from images, and generate memes on demand.

[![Genivus Chat Demo](./assets/Screenshot%202025-08-17%20221105.png)](./assets/Screenshot%202025-08-17%20221105.png)

## ✨ Core Features

*   **Conversational Memory:** Remembers the context of the current conversation in a single session.
*   **Voice-to-Text:** Uses the browser's SpeechRecognition API for voice input.
*   **Text-to-Speech:** Provides spoken audio responses for answers.
*   **Multi-Modal Functionality:**
    *   **Fact-Checking:** Performs real-time Google searches for factual queries.
    *   **Image & GIF Search:** Fetches images and GIFs from Google Images and Giphy.
    *   **YouTube Video Search:** Finds and embeds YouTube videos.
    *   **AI Sketch Generation:** Converts user-uploaded images into artistic sketches using OpenCV.
    *   **AI Meme Generation:** Creates memes from user-uploaded images with custom or AI-suggested text.
*   **User Authentication:** Secure login, registration, and profile management.
*   **Conversation History:** Saves and allows users to revisit and delete past conversations.

---

## 📸 Screenshots (Clickable)

| Welcome Page | Login Page |
| :---: | :---: |
| [![Welcome Page](./assets/Screenshot%202025-08-17%20221638.png)](./assets/Screenshot%202025-08-17%20221638.png) | [![Login Page](./assets/Screenshot%202025-08-17%20223044.png)](./assets/Screenshot%202025-08-17%20223044.png) |

| User Profile | Edit Profile |
| :---: | :---: |
| [![User Profile](./assets/Screenshot%202025-08-17%20221439.png)](./assets/Screenshot%202025-08-17%20221439.png) | [![Edit Profile](./assets/Screenshot%202025-08-17%20221549.png)](./assets/Screenshot%202025-08-17%20221549.png) |

---

> ⚠️ **Disclaimer:** This project is intended for demonstration and educational purposes only. It is **not** configured for a production environment. Do not deploy it with the default settings or expose sensitive API keys on a public server.

## 🛠️ Tech Stack

*   **Backend:** Flask, Python
*   **Database:** Flask-SQLAlchemy (with SQLite for development)
*   **AI & APIs:**
    *   Google Gemini Pro & Vision
    *   SerpApi (Google Search, Images, Videos)
    *   Giphy API
    *   gTTS (Text-to-Speech)
*   **Frontend:** HTML, CSS, Vanilla JavaScript
*   **Image Processing:** OpenCV, Pillow

## ⚙️ How It Works (Architecture)

1.  **Input:** The user either types a message or speaks into the microphone.
2.  **Session Management:** The frontend maintains the current conversation log in `sessionStorage` and sends it to the backend with every new message.
3.  **Intent Detection:** The backend sends the user's raw text to a Gemini model to classify the user's **intent** (e.g., `fact_check`, `find_image`, `answer_text`).
4.  **Tool Use:** Based on the detected intent, the backend routes the request to the appropriate tool (SerpApi, Giphy API, etc.).
5.  **Response Generation:** The tool returns a result. A text summary is generated and converted to an MP3 file using gTTS.
6.  **Rendering:** The backend sends a JSON object to the frontend with the text response and any media URLs, which the JavaScript then dynamically renders in the chat window.

## 🚀 Local Setup and Installation

Follow these steps to run the project on your local machine.

### 1. Prerequisites
*   [Git](https://git-scm.com/) installed.
*   [Python 3.10+](https://www.python.org/downloads/) installed.

### 2. Clone the Repository
```bash
git clone https://github.com/YourUsername/chatbot_final.git
cd chatbot_final
3. Set Up a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.
code
Bash
# Create the virtual environment
python -m venv venv

# Activate the environment (on Windows)
venv\Scripts\activate
4. Install Dependencies
Install all the required Python libraries from the requirements.txt file.
code
Bash
pip install -r requirements.txt
5. Set Up Environment Variables
This is the most important step. Create a new file in the root directory named .env and paste the following, replacing the placeholders with your actual keys.
code
Env
# Flask Secret Key (can be any random string)
SECRET_KEY='a_very_long_and_random_secret_key_for_security'

# Google AI API Key (from https://aistudio.google.com/app/apikey)
GOOGLE_API_KEY='YOUR_GOOGLE_API_KEY'

# SerpApi API Key (from https://serpapi.com/)
SERPAPI_API_KEY='YOUR_SERPAPI_KEY'

# Giphy API Key (from https://developers.giphy.com/)
GIPHY_API_KEY='YOUR_GIPHY_API_KEY'
6. Run the Application
The application will automatically create the site.db database file on the first run.
code
Bash
flask run --port=5001
You can now access the chatbot in your web browser at http://12.0.0.1:5001. You will need to register a new user to start chatting.