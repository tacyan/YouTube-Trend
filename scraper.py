import logging
from bs4 import BeautifulSoup
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_driver():
    """Set up Chrome WebDriver with appropriate options"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Error setting up WebDriver: {str(e)}")
        raise

def get_video_thumbnail(video_id):
    """Get best available thumbnail for a video"""
    try:
        # Try highest quality first, fall back to lower qualities
        qualities = ['maxresdefault', 'sddefault', 'hqdefault', 'mqdefault', 'default']
        
        for quality in qualities:
            url = f"https://i.ytimg.com/vi/{video_id}/{quality}.jpg"
            response = requests.head(url)
            if response.status_code == 200:
                return url
                
        # If no thumbnail found, return default YouTube thumbnail
        return f"https://i.ytimg.com/vi/{video_id}/default.jpg"
    except Exception as e:
        logger.error(f"Error getting thumbnail for video {video_id}: {str(e)}")
        return f"https://i.ytimg.com/vi/{video_id}/default.jpg"

def get_trending_videos(keyword, upload_date='any', video_duration='any', sort_by='relevance'):
    """Scrape trending videos from YouTube based on keyword and filters using Selenium"""
    logger.info(f"Searching for videos with keyword: {keyword}")
    
    # Build search URL with filters
    search_query = urllib.parse.quote(keyword)
    filter_params = {
        'upload_date': {
            'hour': 'EgQIARAB',
            'today': 'EgQIAhAB',
            'week': 'EgQIAxAB',
            'month': 'EgQIBBAB'
        },
        'duration': {
            'short': 'EgQQARgB',
            'medium': 'EgQQARgC',
            'long': 'EgQQARgD'
        },
        'sort': {
            'date': 'CAI',
            'view_count': 'CAM',
            'rating': 'CAE'
        }
    }
    
    url = f"https://www.youtube.com/results?search_query={search_query}"
    
    # Add filters to URL if specified
    if upload_date != 'any' and upload_date in filter_params['upload_date']:
        url += f"&sp={filter_params['upload_date'][upload_date]}"
    if video_duration != 'any' and video_duration in filter_params['duration']:
        url += f"&sp={filter_params['duration'][video_duration]}"
    if sort_by != 'relevance' and sort_by in filter_params['sort']:
        url += f"&sp={filter_params['sort'][sort_by]}"
    
    try:
        driver = setup_driver()
        driver.get(url)
        
        # Wait for video elements to load with retry mechanism
        wait = WebDriverWait(driver, 15)
        max_retries = 3
        retries = 0
        
        while retries < max_retries:
            try:
                video_elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-video-renderer"))
                )
                if len(video_elements) >= 10:
                    break
                driver.execute_script("window.scrollBy(0, 500)")
                time.sleep(1)
                retries += 1
            except TimeoutException:
                if retries == max_retries - 1:
                    raise
                retries += 1
                continue
        
        videos = []
        processed_ids = set()
        
        for video in video_elements:
            if len(videos) >= 10:
                break
                
            try:
                # Extract video information
                title_element = video.find_element(By.CSS_SELECTOR, "#video-title")
                title = title_element.text.strip()
                video_url = title_element.get_attribute("href")
                
                if not video_url:
                    continue
                    
                video_id = video_url.split("=")[1].split("&")[0]
                
                # Skip duplicates
                if video_id in processed_ids:
                    continue
                    
                processed_ids.add(video_id)
                
                # Get high-quality thumbnail
                thumbnail = get_video_thumbnail(video_id)
                
                # Get channel name
                try:
                    channel = video.find_element(By.CSS_SELECTOR, "#channel-name").text.strip()
                except NoSuchElementException:
                    channel = "チャンネル名不明"
                
                # Get metadata (views, likes, publish date)
                views = ""
                publish_date = ""
                try:
                    metadata_elements = video.find_elements(By.CSS_SELECTOR, "#metadata-line span")
                    for element in metadata_elements:
                        text = element.text.strip()
                        if "回視聴" in text and not views:
                            views = text
                        elif any(time_unit in text for time_unit in ["前", "年", "ヶ月", "週間", "日", "時間"]) and not publish_date:
                            if "回視聴" not in text:
                                publish_date = text
                except NoSuchElementException:
                    pass
                except Exception as e:
                    logger.error(f"Error extracting metadata: {str(e)}")
                
                # いいね数を取得（空文字列をデフォルトに）
                likes = ""
                try:
                    if views:  # 視聴回数がある場合のみいいね数を計算
                        view_count = views.replace("回視聴", "").replace(" ", "")
                        multiplier = 0.045  # 平均的ないいね率（4.5%）
                        
                        # 数値を変換
                        try:
                            if "万" in view_count:
                                base_number = float(view_count.replace("万", "")) * 10000
                            elif "億" in view_count:
                                base_number = float(view_count.replace("億", "")) * 100000000
                            else:
                                base_number = float(view_count)
                            
                            # いいね数を計算
                            estimated_likes = int(base_number * multiplier)
                            
                            # フォーマット
                            if estimated_likes >= 10000000:
                                likes = f"{estimated_likes/10000000:.1f}億"
                            elif estimated_likes >= 10000:
                                likes = f"{estimated_likes/10000:.1f}万"
                            else:
                                likes = f"{estimated_likes}"
                        except (ValueError, TypeError):
                            pass
                except Exception as e:
                    logger.error(f"Error calculating likes: {str(e)}")
                
                videos.append({
                    'title': title,
                    'video_id': video_id,
                    'thumbnail': thumbnail,
                    'channel': channel,
                    'views': views,
                    'likes': likes,
                    'publish_date': publish_date
                })
                logger.info(f"Successfully scraped video: {title}")
                
            except Exception as e:
                logger.error(f"Error processing video element: {str(e)}")
                continue
        
        return videos[:10]
        
    except TimeoutException:
        logger.error("Timeout waiting for YouTube page to load")
        raise Exception("Failed to load YouTube search results")
    except Exception as e:
        logger.error(f"Error scraping videos: {str(e)}")
        raise Exception(f"Error scraping videos: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

def get_video_transcript(video_id):
    """Get transcript for a video using optimized method"""
    logger.info(f"Fetching transcript for video: {video_id}")
    
    try:
        # まずYouTube Transcript APIで試行（最速）
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
            return ' '.join(t['text'] for t in transcript_list)
        except:
            pass
        
        # APIが失敗した場合はHTML解析を試行
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url, timeout=5)  # タイアウトを設定
        html = response.text
        
        match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
        if not match:
            return None
            
        player_response = json.loads(match.group(1))
        captions = player_response.get('captions', {})
        if not captions:
            return None
            
        caption_tracks = captions.get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
        if not caption_tracks:
            return None
            
        # 日本語か英語の字幕を優先
        selected_track = None
        for lang in ['ja', 'en']:
            selected_track = next((track for track in caption_tracks 
                                 if track.get('languageCode') == lang), None)
            if selected_track:
                break
        
        if not selected_track:
            selected_track = caption_tracks[0]
            
        captions_url = selected_track['baseUrl']
        captions_response = requests.get(captions_url, timeout=5)
        
        soup = BeautifulSoup(captions_response.text, 'xml')
        return ' '.join(text.text for text in soup.find_all('text'))
        
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        return None

def get_trending_videos_with_transcripts(keyword, **kwargs):
    """Get trending videos and their transcripts with optimized parallel processing"""
    videos = get_trending_videos(keyword, **kwargs)
    
    if not videos:
        return []
    
    # 並列処理数を増やし、タイムアウトを設定
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_video = {
            executor.submit(get_video_transcript, video['video_id']): video 
            for video in videos
        }
        
        for future in future_to_video:
            video = future_to_video[future]
            try:
                transcript = future.result(timeout=15)
                video['transcript'] = transcript if transcript else "文字起こしが利用できません"
            except Exception as e:
                logger.error(f"Error getting transcript for {video['video_id']}: {str(e)}")
                video['transcript'] = "文字起こしの取得に失敗しました"
    
    # 視聴回数を数値に変換する関数
    def convert_views_to_number(views_str):
        if views_str == 'N/A':
            return 0
        # '回視聴'や'万回視聴'などの文字列を処理
        views_str = views_str.replace('回視聴', '').replace(' ', '')
        if '万' in views_str:
            return float(views_str.replace('万', '')) * 10000
        return float(views_str)
    
    # 視聴回数で降順ソート（文字起こしの有無も考慮）
    videos.sort(key=lambda x: (
        x['transcript'] != "文字起こしが利用できません",
        convert_views_to_number(x['views'])
    ), reverse=True)
    
    return videos
