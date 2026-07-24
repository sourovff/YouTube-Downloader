from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_links', methods=['POST'])
def get_links():
    data = request.get_json()
    url = data.get('url')
    
    if not url or ("youtube.com" not in url and "youtu.be" not in url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'YouTube Video')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', None)
            uploader = info.get('uploader', 'Unknown Channel')

            formats = info.get('formats', [])
            
            # Extract MP3 direct stream link
            audio_url = next((f['url'] for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none'), info.get('url'))

            # Extract specific resolutions (360p, 480p, 720p, 1080p)
            resolutions = {}
            for res in ['360', '480', '720', '1080']:
                for f in formats:
                    if f.get('height') and str(f.get('height')) == res and f.get('ext') == 'mp4':
                        resolutions[res] = f.get('url')
                        break
            
            # Fallback if specific resolution not found
            if not resolutions:
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    