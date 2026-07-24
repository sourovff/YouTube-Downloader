from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_links', methods=['POST'])
def get_links():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        url = data.get('url')
        
        if not url or ("youtube.com" not in url and "youtu.be" not in url):
            return jsonify({'error': 'Please enter a valid YouTube URL'}), 400

        # YouTube Bot Detection Bypass Configuration
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web']
                }
            }
        }

        # Check if cookies.txt exists in the project and use it
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({'error': 'Could not fetch video info'}), 400

            title = info.get('title', 'YouTube Video')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', '')
            uploader = info.get('uploader', 'Unknown Channel')

            formats = info.get('formats', [])
            
            # Extract Audio stream
            audio_url = None
            for f in formats:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio_url = f.get('url')
                    break
            if not audio_url:
                audio_url = info.get('url')

            # Extract Resolutions
            resolutions = {}
            for res in ['360', '480', '720', '1080']:
                for f in formats:
                    if f.get('height') and str(f.get('height')) == res and f.get('ext') == 'mp4' and f.get('url'):
                        resolutions[res] = f.get('url')
                        break
            
            if not resolutions and info.get('url'):
                resolutions['720'] = info.get('url')

        return jsonify({
            'title': title,
            'duration': duration,
            'thumbnail': thumbnail,
            'uploader': uploader,
            'audio_url': audio_url,
            'resolutions': resolutions
        })

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': f"Failed to fetch video: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
