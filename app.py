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

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'success': True,
                'title': info.get('title', 'Media Video'),
                'thumbnail': info.get('thumbnail', '')
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# 2. File Download API (Guaranteed Sound & MP3 Conversion)
@app.route('/download', methods=['GET'])
def download():
    raw_url = request.args.get('url')
    download_type = request.args.get('type', 'mp4')

    if not raw_url:
        return "URL missing", 400

    url = clean_url(raw_url)

    # Old files clean panrom
    for f in glob.glob(os.path.join(DOWNLOAD_FOLDER, "*")):
        try:
            os.remove(f)
        except Exception:
            pass

    out_template = os.path.join(DOWNLOAD_FOLDER, "media_raw.%(ext)s")

    # Best quality with sound for both Video and Audio
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'outtmpl': out_template,
        'format': 'bestvideo+bestaudio/best',
    }
    if download_type == 'mp4':
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*"))
        if not downloaded_files:
            return "File download aagala", 500

        downloaded_file = downloaded_files[0]

        # MP3 AUDIO EXTRACTION (Direct FFmpeg without ffprobe)
        if download_type == 'mp3':
            mp3_output = os.path.join(DOWNLOAD_FOLDER, "audio.mp3")
            cmd = ['ffmpeg', '-y', '-i', downloaded_file, '-vn', '-acodec', 'libmp3lame', '-b:a', '192k', mp3_output]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return send_file(mp3_output, as_attachment=True, download_name="song.mp3")

        # MP4 VIDEO WITH 100% SOUND
        if not downloaded_file.endswith('.mp4'):
            mp4_output = os.path.join(DOWNLOAD_FOLDER, "video.mp4")
            cmd = ['ffmpeg', '-y', '-i', downloaded_file, '-c', 'copy', mp4_output]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(mp4_output):
                downloaded_file = mp4_output

        return send_file(downloaded_file, as_attachment=True, download_name="video.mp4")

    except Exception as e:
        return f"Download failed: {str(e)}", 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
