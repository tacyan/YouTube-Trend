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
                channel = video.find_element(By.CSS_SELECTOR, "#channel-name").text.strip()
                
                # Get view count and upload date
                metadata = video.find_elements(By.CSS_SELECTOR, "#metadata-line span")
                views = metadata[0].text.strip() if len(metadata) > 0 else "N/A"
                upload_date = metadata[1].text.strip() if len(metadata) > 1 else "N/A"
                
                videos.append({
                    'title': title,
                    'video_id': video_id,
                    'thumbnail': thumbnail,
                    'channel': channel,
                    'views': views,
                    'upload_date': upload_date
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
    """Get transcript for a video with improved error handling and UI interaction"""
    logger.info(f"Fetching transcript for video: {video_id}")
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            driver = setup_driver()
            url = f"https://www.youtube.com/watch?v={video_id}"
            driver.get(url)
            
            wait = WebDriverWait(driver, 10)
            
            # Try UI method first
            try:
                # Wait for and click the "More actions" button
                more_actions = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='More actions']"))
                )
                more_actions.click()
                
                # Wait for and click "Show transcript"
                transcript_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Show transcript']"))
                )
                
                # Use JavaScript click as a fallback
                driver.execute_script("arguments[0].click();", transcript_button)
                
                # Wait for transcript panel
                time.sleep(2)  # Allow animation to complete
                
                # Try to click timestamp toggle if available
                try:
                    toggle_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Toggle timestamp']"))
                    )
                    toggle_button.click()
                except:
                    logger.info("Timestamp toggle not available")
                
                # Extract transcript
                transcript_elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-transcript-segment-renderer"))
                )
                
                transcript = []
                for element in transcript_elements:
                    try:
                        timestamp = element.find_element(By.CSS_SELECTOR, ".segment-timestamp").text
                        text = element.find_element(By.CSS_SELECTOR, ".segment-text").text
                        transcript.append(f"[{timestamp}] {text}")
                    except:
                        continue
                
                if transcript:
                    return "\n".join(transcript)
                raise Exception("No transcript segments found")
                
            except (TimeoutException, ElementClickInterceptedException) as e:
                logger.info(f"UI method failed, falling back to API: {str(e)}")
                raise  # Trigger API fallback
                
        except Exception as e:
            logger.info(f"Attempt {retry_count + 1} failed, trying API method: {str(e)}")
            try:
                # Fall back to YouTube Transcript API
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                formatted_transcript = []
                for t in transcript_list:
                    minutes = int(t['start'] // 60)
                    seconds = int(t['start'] % 60)
                    timestamp = f"{minutes:02d}:{seconds:02d}"
                    formatted_transcript.append(f"[{timestamp}] {t['text']}")
                return "\n".join(formatted_transcript)
                
            except Exception as api_error:
                logger.error(f"API method failed: {str(api_error)}")
                retry_count += 1
                if retry_count == max_retries:
                    return "Transcript not available for this video"
                continue
                
        finally:
            if 'driver' in locals():
                driver.quit()
    
    return "Transcript not available for this video"
