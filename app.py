import static_ffmpeg
static_ffmpeg.add_paths()
import os
import glob
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 1. Quick Info Fetch API
@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'URL thevai!'}), 400

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
                'title': info.get('title', 'Media'),
                'thumbnail': info.get('thumbnail', '')
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# 2. High-Speed Download API
@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    download_type = request.args.get('type', 'mp4')

    if not url:
        return "URL missing", 400

    # Old downloads clean panna
    for f in glob.glob(os.path.join(DOWNLOAD_FOLDER, "*")):
        try:
            os.remove(f)
        except Exception:
            pass

    out_template = os.path.join(DOWNLOAD_FOLDER, "%(title).40s.%(ext)s")

    # Common Speed Booster Settings
    speed_boost_opts = {
        'outtmpl': out_template,
        'quiet': True,
        'no_warnings': True,
        'concurrent_fragment_downloads': 8,  # 8 Threads Parallel Download (Rocket Speed)
        'buffersize': 1024 * 64,             # 64KB Buffer
        'http_chunk_size': 10485760,         # 10MB Chunk Size
    }

    if download_type == 'mp3':
        # Fast MP3 Settings
        ydl_opts = {
            **speed_boost_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',   # Fast encoding & Crystal Clear sound
            }],
        }
    else:
        # Fast 720p HD MP4 Settings (Fast download + Super Clarity)
        ydl_opts = {
            **speed_boost_opts,
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*"))
        if downloaded_files:
            filename = downloaded_files[0]
            return send_file(filename, as_attachment=True)
        else:
            return "File processing error", 500
    except Exception as e:
        return f"Download failed: {str(e)}", 500


if __name__ == '__main__':
    print("--------------------------------------------------")
    print("High-Speed Backend Running: http://127.0.0.1:5000")
    print("--------------------------------------------------")
    app.run(port=5000, debug=True)