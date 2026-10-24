import os
import re
import glob
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import static_ffmpeg

# Automatic FFmpeg & FFprobe Setup
static_ffmpeg.add_paths()

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def clean_url(url):
    shorts_match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
    if shorts_match:
        return f"https://www.youtube.com/watch?v={shorts_match.group(1)}"
    return url

COMMON_OPTS = {
    'quiet': True,
    'no_warnings': True,
}

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
        **COMMON_OPTS,
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


# 2. File Download API (With Guaranteed Audio & Sound)
@app.route('/download', methods=['GET'])
def download():
    raw_url = request.args.get('url')
    download_type = request.args.get('type', 'mp4')

    if not raw_url:
        return "URL missing", 400

    url = clean_url(raw_url)

    # Pazhaya files clean panrom
    for f in glob.glob(os.path.join(DOWNLOAD_FOLDER, "*")):
        try:
            os.remove(f)
        except Exception:
            pass

    out_template = os.path.join(DOWNLOAD_FOLDER, "%(title).40s.%(ext)s")

    if download_type == 'mp3':
        # Fast MP3 Audio Download
        ydl_opts = {
            **COMMON_OPTS,
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        # Guaranteed Video + Full Sound MP4 (Merging with Audio)
        ydl_opts = {
            **COMMON_OPTS,
            'format': 'best[ext=mp4]/bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': out_template,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*"))
        if downloaded_files:
            # Sariyaana file-ah pick panrom
            filename = max(downloaded_files, key=os.path.getctime)
            return send_file(filename, as_attachment=True)
        else:
            return "File processing error", 500
    except Exception as e:
        return f"Download failed: {str(e)}", 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
