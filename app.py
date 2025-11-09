# app.py

import os
import json
import base64
import requests
import uuid
import io

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler 
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, Response
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import google.generativeai as genai
from urllib.parse import urlparse, parse_qs
from werkzeug.utils import secure_filename
from PIL import Image
import pillow_heif
import click  # Flask's command-line interface library

# Correctly import db, User, and History from the models file
from models import db, User, History
from forms import RegistrationForm, LoginForm, UpdateAccountForm
from utils.gemini_answer import (
    get_gemini_answer, get_meme_suggestion, google_search_for_answer, 
    generate_conversational_answer, search_for_image_on_google, 
    search_for_video_on_youtube, search_for_gif_on_giphy
)
from utils.text_to_speech import convert_text_to_speech
from utils.sketch_generator import generate_sketch
from utils.meme_generator import generate_meme

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-very-secret-key-for-dev')
# Use environment variable for database URL with fallback to SQLite
instance_path = os.path.join(app.root_path, 'instance')
os.makedirs(instance_path, exist_ok=True)

# Set SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    f'sqlite:///{os.path.join(instance_path, "site.db")}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db object with the app
db.init_app(app)

def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully")

# Initialize the database
init_db()

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

in_memory_audio_store = {}

# --- NEW: DATABASE CREATION COMMAND ---
@app.cli.command("init-db")
def init_db_command():
    """Clears existing data and creates new tables."""
    db.create_all()
    click.echo("Initialized the database.")

def delete_old_history():
    """A function that runs in the background to delete old history."""
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=15)
        old_records = History.query.filter(History.date_posted < cutoff_date).all()
        
        if old_records:
            print(f"[{datetime.now()}] Deleting {len(old_records)} records older than {cutoff_date}...")
            for record in old_records:
                db.session.delete(record)
            db.session.commit()
            print("Cleanup complete.")
        else:
            print(f"[{datetime.now()}] No old history records to delete.")

def process_uploaded_image(file_storage):
    filename = secure_filename(file_storage.filename)
    file_storage.seek(0)
    if filename.lower().endswith(('.heic', '.heif')):
        try:
            pillow_heif.register_heif_opener()
            image = Image.open(file_storage).convert("RGB")
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            return buffer.getvalue(), ".jpg"
        except Exception as e:
            print(f"Error converting HEIC in memory: {e}")
            return None, None
    else:
        _, ext = os.path.splitext(filename)
        return file_storage.read(), ext

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def extract_youtube_id(url: str):
    if not url: return None
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if "youtube.com" in parsed_url.hostname:
            return query_params.get("v", [None])[0]
        elif "youtu.be" in parsed_url.hostname:
            return parsed_url.path[1:]
        elif "google.com" in parsed_url.hostname and "url" in query_params:
            return extract_youtube_id(query_params["url"][0])
    except Exception:
        return None
    return None

@app.route('/')
@login_required
def index():
    user_history = History.query.filter_by(user_id=current_user.id).order_by(History.id.desc()).all()
    return render_template('index.html', history=user_history)

# ... (All other @app.route functions are correct and unchanged) ...
@app.route('/favicon.ico')
def favicon():
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
        print(f"Error streaming video: {e}")
        return "Failed to stream video.", 500

@app.route('/stream-audio/<audio_id>')
@login_required
def stream_audio(audio_id):
    audio_data = in_memory_audio_store.get(audio_id)
    if audio_data:
        in_memory_audio_store.pop(audio_id, None)
        return Response(audio_data, mimetype='audio/mpeg')
    else:
        return "Audio not found.", 404

@app.route('/process-text', methods=['POST'])
@login_required
def process_text_route():
    data = request.get_json()
    user_text = data['text_input']
    conversation_history = data.get('history', [])
    db_id = data.get('db_id')
    response_data = {}
    answer_for_db = ""
    status_code = 200
    gemini_response = get_gemini_answer(user_text)
    intent = gemini_response.get("intent")
    content = gemini_response.get("content")

    if intent == "fact_check":
        model_response = google_search_for_answer(content, conversation_history)
        answer_for_db = model_response
    elif intent == "find_image":
        image_url, attribution = search_for_image_on_google(content)
        answer_for_db = attribution or f"Couldn't find an image for '{content}'."
        response_data["image_url"] = image_url
    elif intent == "find_gif":
        gif_url, attribution = search_for_gif_on_giphy(content)
        answer_for_db = attribution or f"Couldn't find a GIF for '{content}'."
        response_data["gif_url"] = gif_url
    elif intent == "find_youtube_video":
        video_url, attribution = search_for_video_on_youtube(content)
        video_id = extract_youtube_id(video_url)
        answer_for_db = attribution or f"Couldn't find a video for '{content}'."
        if video_id:
            response_data["youtube_embed_url"] = f"https://www.youtube.com/embed/{video_id}"
    elif intent == "answer_text":
        model_response = generate_conversational_answer(content, conversation_history)
        answer_for_db = model_response
    else:
        answer_for_db = "Sorry, I couldn't understand that."
        status_code = 400

    summary_for_speech = (answer_for_db.split('.')[0] + '.') if '.' in answer_for_db else answer_for_db
    audio_bytes = convert_text_to_speech(summary_for_speech)

    if audio_bytes:
        audio_id = str(uuid.uuid4())
        in_memory_audio_store[audio_id] = audio_bytes
        audio_url = url_for('stream_audio', audio_id=audio_id)
        response_data["audio_url"] = audio_url
    else:
        response_data["audio_url"] = None

    response_data["text_response"] = answer_for_db

    if answer_for_db and status_code == 200:
        full_conversation = conversation_history + [{"role": "user", "parts": [{"text": user_text}]}, {"role": "model", "parts": [{"text": answer_for_db}]}]
        if not db_id:
            new_log = History(question=user_text, answer=json.dumps(full_conversation), author=current_user)
            db.session.add(new_log)
            db.session.commit()
            response_data['db_id'] = new_log.id
        else:
            existing_log = db.session.get(History, db_id)
            if existing_log and existing_log.user_id == current_user.id:
                existing_log.answer = json.dumps(full_conversation)
                db.session.commit()
    return jsonify(response_data), status_code

@app.route('/delete-history/<int:history_id>', methods=['POST'])
@login_required
def delete_history(history_id):
    history_item = db.session.get(History, history_id)
    if history_item and history_item.user_id == current_user.id:
        db.session.delete(history_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'History deleted.'})
    return jsonify({'success': False, 'message': 'Item not found or unauthorized.'}), 404

@app.route('/upload-image', methods=['POST'])
@login_required
def upload_image_route():
    if 'image' not in request.files: return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '': return jsonify({'error': 'No image selected'}), 400

    if file:
        image_bytes, ext = process_uploaded_image(file)
        if not image_bytes:
            return jsonify({'error': 'Failed to process image file.'}), 500

        sketch_folder = os.path.join(app.static_folder, 'sketches')
        os.makedirs(sketch_folder, exist_ok=True)
        
        base_name, _ = os.path.splitext(secure_filename(file.filename))
        unique_filename = f"{current_user.id}_{os.urandom(8).hex()}_{base_name}{ext}"
        output_path = os.path.join(sketch_folder, unique_filename)
        
        success = generate_sketch(image_bytes, output_path)
        
        if success:
            sketch_url = url_for('static', filename=f'sketches/{unique_filename}')
            return jsonify({'sketch_url': sketch_url})
        else:
            return jsonify({'error': 'Failed to generate sketch'}), 500

@app.route('/generate-meme', methods=['POST'])
@login_required
def generate_meme_route():
    if 'image' not in request.files: return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    top_text = request.form.get('top_text', '')
    bottom_text = request.form.get('bottom_text', '')
    if file.filename == '': return jsonify({'error': 'No image selected'}), 400

    if file:
        image_bytes, ext = process_uploaded_image(file)
        if not image_bytes:
            return jsonify({'error': 'Failed to process image file.'}), 500
            
        meme_folder = os.path.join(app.static_folder, 'memes')
        os.makedirs(meme_folder, exist_ok=True)

        base_name, _ = os.path.splitext(secure_filename(file.filename))
        unique_filename = f"{current_user.id}_{os.urandom(8).hex()}_{base_name}{ext}"
        output_path = os.path.join(meme_folder, unique_filename)

        success = generate_meme(image_bytes, output_path, top_text, bottom_text)

        if success:
            meme_url = url_for('static', filename=f'memes/{unique_filename}')
            return jsonify({'meme_url': meme_url})
        else:
            return jsonify({'error': 'Failed to generate meme'}), 500

@app.route('/suggest-meme-text', methods=['POST'])
@login_required
def suggest_meme_text_route():
    if 'image' not in request.files: return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '': return jsonify({'error': 'No image selected'}), 400

    if file:
        image_bytes, _ = process_uploaded_image(file)
        if not image_bytes:
            return jsonify({'error': 'Could not process image for suggestion.'}), 500
            
        success, suggestion = get_meme_suggestion(image_bytes)
        if success:
            return jsonify(suggestion)
        else:
            return jsonify(suggestion), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('index'))
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
    if current_user.is_authenticated: return redirect(url_for('index'))
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

# --- START THE SCHEDULER ---
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(delete_old_history, 'interval', hours=24)
scheduler.start()