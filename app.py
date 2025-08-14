# app.py

import os
import json
import base64
import requests
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, Response
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

# Import all models, forms, and utility functions
from models import db, User, History
from forms import RegistrationForm, LoginForm, UpdateAccountForm
from utils.gemini_answer import (
    get_gemini_answer, 
    search_for_image_on_pexels, 
    search_for_video_on_pexels, 
    search_for_image_on_google,
    search_for_video_on_youtube,
    search_for_gif_on_giphy
)
from utils.text_to_speech import convert_text_to_speech

# Load environment variables from .env file
load_dotenv()

# --- App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-very-secret-key-for-dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return User.query.get(int(user_id))

# --- Utility Routes ---

@app.route('/favicon.ico')
def favicon():
    """Handle browser's automatic request for a favicon to prevent 404 errors."""
    return '', 204

@app.route('/stream-video/<encoded_url>')
@login_required
def stream_video(encoded_url):
    try:
        video_url = base64.urlsafe_b64decode(encoded_url).decode('utf-8')
        req = requests.get(video_url, stream=True, proxies={"http": None, "https": None})
        req.raise_for_status()
        return Response(req.iter_content(chunk_size=1024*1024), content_type=req.headers['content-type'])
    except Exception as e:
        print(f"Error streaming video from {video_url}: {e}")
        return "Failed to stream video.", 500


# --- Core Application Routes ---

@app.route('/')
@login_required
def index():
    """Render the main chat page."""
    user_history = History.query.filter_by(user_id=current_user.id).order_by(History.id.desc()).all()
    return render_template('index.html', history=user_history)

@app.route('/process-text', methods=['POST'])
@login_required
def process_text_route():
    """
    Main endpoint to process user input.
    """
    data = request.get_json()
    if not data or 'text_input' not in data:
        return jsonify({"error": "No text provided"}), 400

    user_text = data['text_input']
    gemini_response = get_gemini_answer(user_text)
    
    intent = gemini_response.get("intent")
    content = gemini_response.get("content")

    audio_dir = os.path.join(app.static_folder, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    response_audio_filename = f"response_{current_user.id}_{os.urandom(4).hex()}.mp3"
    response_audio_path = os.path.join(audio_dir, response_audio_filename)

    # --- Intent Router ---

    if intent == "find_image":
        image_type = gemini_response.get("image_type", "generic_concept")
        image_url, attribution = search_for_image_on_google(content) if image_type == "specific_entity" else search_for_image_on_pexels(content)
        
        if image_url:
            convert_text_to_speech(attribution, response_audio_path)
            audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
            return jsonify({"image_url": image_url, "text_response": attribution, "audio_url": audio_url})
        else:
            attribution = attribution or f"I couldn't find an image for '{content}'."
            convert_text_to_speech(attribution, response_audio_path)
            audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
            return jsonify({"text_response": attribution, "audio_url": audio_url})

    elif intent == "find_gif":
        gif_url, attribution = search_for_gif_on_giphy(content)
        if gif_url:
            convert_text_to_speech(attribution, response_audio_path)
            audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
            return jsonify({"gif_url": gif_url, "text_response": attribution, "audio_url": audio_url})
        else:
            attribution = attribution or f"I couldn't find a GIF for '{content}'."
            convert_text_to_speech(attribution, response_audio_path)
            audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
            return jsonify({"text_response": attribution, "audio_url": audio_url})

    elif intent == "find_pexels_video":
        video_url, attribution = search_for_video_on_pexels(content)
        if video_url:
            encoded_url = base64.urlsafe_b64encode(video_url.encode('utf-8')).decode('utf-8')
            stream_url = url_for('stream_video', encoded_url=encoded_url)
            convert_text_to_speech(attribution, response_audio_path)
            audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
            return jsonify({"stream_url": stream_url, "text_response": attribution, "audio_url": audio_url})
        else:
            attribution = attribution or f"I couldn't find a stock video for '{content}'."
            convert_text_to_speech(attribution, response_audio_path)
            audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
            return jsonify({"text_response": attribution, "audio_url": audio_url})

    elif intent == "find_youtube_video":
        video_url, attribution = search_for_video_on_youtube(content)
        if video_url and 'v=' in video_url:
            video_id = video_url.split('v=')[1].split('&')[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            convert_text_to_speech(attribution, response_audio_path)
            audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
            return jsonify({"youtube_embed_url": embed_url, "text_response": attribution, "audio_url": audio_url})
        else:
            attribution = attribution or f"I couldn't find a YouTube video for '{content}'."
            convert_text_to_speech(attribution, response_audio_path)
            audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
            return jsonify({"text_response": attribution, "audio_url": audio_url})

    elif intent == "answer_text":
        model_response = content
        summary_for_speech = (model_response.split('.')[0] + '.') if '.' in model_response else model_response
        convert_text_to_speech(summary_for_speech, response_audio_path)
        audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
        return jsonify({"text_response": model_response, "audio_url": audio_url})

    else:
        error_message = "I'm sorry, I couldn't understand that. Could you rephrase?"
        convert_text_to_speech(error_message, response_audio_path)
        audio_url = url_for('static', filename=f'audio/{response_audio_filename}')
        return jsonify({'text_response': error_message, 'audio_url': audio_url}), 400


# --- Authentication and Profile Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    form = UpdateAccountForm()
    form.username.data = current_user.username
    form.email.data = current_user.email
    return render_template('profile.html', title='My Profile', form=form)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)