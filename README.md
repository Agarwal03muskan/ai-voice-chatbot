# AI Voice Chatbot

An intelligent, voice-powered AI assistant featuring a dynamic, animated user interface. This project allows for seamless, real-time spoken conversations with an AI, built on a robust Flask backend with user authentication and conversation history.


## ✨ Core Features

-   **🎙️ Voice-to-Text & Text-to-Speech:** Full conversational experience using the browser's Web Speech API.
-   **👤 User Authentication:** Secure user registration and login to keep conversations private.
-   **📜 Conversation History:** The sidebar automatically saves and displays a history of your past conversations.
-   **⌨️ Dual Input:** Supports both voice commands and traditional text-based input.
-   **🎨 Animated UI:** A modern, responsive interface with a dynamic avatar that provides visual feedback for listening and speaking states.
-   **🔐 Secure & Organized:** Properly handles API keys and project structure, ignoring unnecessary files with a well-configured `.gitignore`.

---

## 🛠️ Tech Stack

-   **Backend:**
    -   Python 3
    -   Flask (for routing, logic, and serving the application)
    -   Flask-SQLAlchemy (for database management)
    -   Flask-Login (for handling user sessions)
-   **Frontend:**
    -   HTML5
    -   CSS3 (with animations and a responsive, mobile-first design)
    -   Vanilla JavaScript (for DOM manipulation and API handling)
-   **Core APIs:**
    -   Web Speech API (`SpeechRecognition` & `SpeechSynthesis`)
    -    chosen AI model API (e.g., OpenAI, Google Gemini)

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Make sure you have the following installed on your system:
-   Python 3.8+ and Pip
-   Git for version control
-   A modern web browser that supports the Web Speech API (like Google Chrome or Microsoft Edge).

### Installation & Setup

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/Agarwal03muskan/ai-voice-chatbot.git
    cd ai-voice-chatbot
    ```

2.  **Create and Activate a Virtual Environment**
    A virtual environment is crucial for managing project dependencies.
    ```sh
    # Create the environment
    python -m venv venv

    # Activate it on Windows
    .\venv\Scripts\activate
    
    # Activate it on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Required Packages**
    This command reads the `requirements.txt` file and installs all necessary Python libraries.
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    Your API keys and secret keys should be kept private.
    -   Create a new file in the root directory named `.env`
    -   Open it and add your keys in the following format:
        ```
        SECRET_KEY='your_strong_random_secret_key'
        YOUR_AI_API_KEY='your_ai_api_key_from_the_provider'
        ```

5.  **Initialize the Database**
    This will create the `site.db` file and set up the necessary tables for users and their conversations.
    ```sh
    flask shell
    ```
    Once inside the Python shell, type the following and press Enter:
    ```py
    from app import db
    db.create_all()
    exit()
    ```

6.  **Run the Application**
    ```sh
    flask run
    ```
    Your AI Voice Chatbot will now be running at `http://127.0.0.1:5000/`.

---

## 📜 License

Distributed under the MIT License. See the `LICENSE` file for more information.
