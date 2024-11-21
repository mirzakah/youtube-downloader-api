from http.server import BaseHTTPRequestHandler
from yt_dlp import YoutubeDL
import json

def download_video(url):
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Extracting info for URL: {url}")
            info = ydl.extract_info(url, download=False)
            
            formats = info.get('formats', [])
            # Get best MP4 format
            mp4_formats = [f for f in formats if f.get('ext') == 'mp4']
            if mp4_formats:
                best_format = max(mp4_formats, key=lambda f: f.get('filesize', 0))
                return {
                    'title': info.get('title'),
                    'downloadUrl': best_format.get('url'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail')
                }
            else:
                raise Exception('No MP4 format found')
    except Exception as e:
        print(f"Error in download_video: {str(e)}")
        raise

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            if 'url' not in data:
                self.send_error_response(400, 'URL is required')
                return

            print(f"Processing request for URL: {data['url']}")
            result = download_video(data['url'])
            
            self.send_response(200)
            self.send_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"Error in handler: {str(e)}")
            self.send_error_response(500, str(e))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_headers()
        self.end_headers()

    def send_headers(self):
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
