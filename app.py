import os
import logging
from flask import Flask, render_template, request, jsonify
from scraper import get_trending_videos, get_video_transcript
from ai_generator import generate_script

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "youtube_trends_secret")

@app.route('/')
def index():
    try:
        if not os.environ.get('GEMINI_API_KEY'):
            return render_template('index.html', error="Gemini APIキーが設定されていません。管理者に連絡してください。")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return render_template('index.html', error="予期せぬエラーが発生しました")

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if not os.environ.get('GEMINI_API_KEY'):
            return render_template('index.html', error="Gemini APIキーが設定されていません。管理者に連絡してください。")
            
        keyword = request.form.get('keyword')
        if not keyword:
            return render_template('index.html', error="キーワードを入力してください")
            
        duration = int(request.form.get('duration', 5))
        upload_date = request.form.get('upload_date', 'any')
        video_duration = request.form.get('video_duration', 'any')
        sort_by = request.form.get('sort_by', 'relevance')
        
        logger.info(f"Analyzing trends for keyword: {keyword}")
        
        # Get trending videos with filters
        videos = get_trending_videos(
            keyword,
            upload_date=upload_date,
            video_duration=video_duration,
            sort_by=sort_by
        )
        
        if not videos:
            return render_template('index.html', error="条件に一致する動画が見つかりませんでした")
        
        # Get transcript for first video
        transcript = get_video_transcript(videos[0]['video_id'])
        
        # Generate script using Gemini
        new_script = generate_script(transcript, duration)
        
        return render_template('results.html', 
                             videos=videos[:10], 
                             generated_script=new_script,
                             keyword=keyword)
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return render_template('index.html', error=f"エラーが発生しました: {str(e)}")

@app.route('/get_transcript/<video_id>')
def get_transcript_route(video_id):
    try:
        transcript = get_video_transcript(video_id)
        return jsonify({'transcript': transcript})
    except Exception as e:
        logger.error(f"Error getting transcript for video {video_id}: {str(e)}")
        return jsonify({'error': f"文字起こしの取得に失敗しました: {str(e)}"}), 400

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        raise
