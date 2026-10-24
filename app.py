import os
import re
import glob
import subprocess
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import static_ffmpeg

# Cloud-la FFmpeg setup
static_ffmpeg.add_paths()

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = os.path.abspath("downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def clean_url(url):
    shorts_match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
    if shorts_match:
        return f"https://www.youtube.com/watch?v={shorts_match.group(1)}"
    return url

@app.route('/')
def home():
    return "Server is Active & Working 100%!"

# 1. Video Info API
@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.get_json()
    raw_url = data.get('url') if data else None

    if not raw_url:
        return jsonify({'success': False, 'error': 'URL thevai!'}), 400

    url = clean_url(raw_url)

    y
