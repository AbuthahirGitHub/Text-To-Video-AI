import os 
import requests
import random
import time
import json
from utility.utils import log_response, LOG_TYPE_PEXEL

# Check for Pexels API key
PEXELS_API_KEY = os.environ.get('PEXELS_KEY')
if not PEXELS_API_KEY:
    print("WARNING: No Pexels API key found in environment variables (PEXELS_KEY)")
    print("Video search functionality will be limited")

# Set this to False to disable generic fallback terms completely and only reuse successful videos
USE_GENERIC_FALLBACKS = False

# Define a list of generic fallback search terms (only used if USE_GENERIC_FALLBACKS is True)
GENERIC_FALLBACK_TERMS = [
    "ocean",
    "sky",
    "sunset",
    "mountains",
    "forest",
    "water",
    "beach",
    "clouds",
    "waterfall",
    "lake",
    "city",
    "stars",
    "nature",
    "desert",
    "snow",
    "river",
    "trees",
    "flowers",
    "sunrise",
    "planet"
]

# Local cache for video searches to avoid redundant API calls
VIDEO_SEARCH_CACHE = {}

def search_videos(query_string, orientation_landscape=True):
    """Search for videos using the Pexels API with proper error handling."""
    # Check cache first
    cache_key = f"{query_string}_{orientation_landscape}"
    if cache_key in VIDEO_SEARCH_CACHE:
        print(f"Using cached results for '{query_string}'")
        return VIDEO_SEARCH_CACHE[cache_key]
    
    # Default empty response
    empty_response = {"videos": []}
    
    # Check for API key
    if not PEXELS_API_KEY:
        print(f"No Pexels API key provided. Cannot search for '{query_string}'")
        return empty_response
   
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15,
        "size": "large"
    }

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 401:
                print(f"ERROR: Unauthorized - Invalid Pexels API key")
                return empty_response
            elif response.status_code == 429:
                if attempt < max_retries - 1:
                    print(f"Rate limit hit, waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                print(f"ERROR: Rate limit exceeded after {max_retries} attempts")
                return empty_response
            elif response.status_code != 200:
                print(f"ERROR: Pexels API returned status code {response.status_code}")
                return empty_response

            data = response.json()
            
            if 'videos' not in data:
                print(f"ERROR: Invalid response format from Pexels API")
                return empty_response
                
            # Cache successful response
            VIDEO_SEARCH_CACHE[cache_key] = data
            
            # Log response for debugging
            log_response(LOG_TYPE_PEXEL, query_string, data)
            
            # Print video count and resolutions
            videos = data.get('videos', [])
            if videos:
                resolutions = {}
                for video in videos:
                    for file in video.get('video_files', []):
                        res = f"{file.get('width', '?')}x{file.get('height', '?')}"
                        resolutions[res] = resolutions.get(res, 0) + 1
                print(f"Found {len(videos)} videos for '{query_string}'")
                print(f"Available resolutions: {resolutions}")
            else:
                print(f"No videos found for '{query_string}'")
            
            return data

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Request failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            print(f"ERROR: Failed to connect to Pexels API after {max_retries} attempts: {str(e)}")
            return empty_response

    return empty_response


def getBestVideo(query_string, orientation_landscape=True, used_vids=[], attempt=0):
    """
    Get the best video for a search term, without using generic fallback terms.
    """
    # Search for videos
    try:
    vids = search_videos(query_string, orientation_landscape)
        
        # Verify videos exist in the response
        if 'videos' not in vids or not vids['videos']:
            print(f"No videos found for '{query_string}'")
            return None
                
    videos = vids['videos']  # Extract the videos list from JSON

        # Print detailed diagnostics about available videos
        if videos:
            print(f"Found {len(videos)} videos for '{query_string}'")
            
            # Analyze video resolutions
            resolutions = {}
            for video in videos:
                for file in video.get('video_files', []):
                    res_key = f"{file.get('width', 0)}x{file.get('height', 0)}"
                    if res_key not in resolutions:
                        resolutions[res_key] = 0
                    resolutions[res_key] += 1
            
            print(f"Available resolutions for '{query_string}': {resolutions}")
        
        # Try exact resolution match first (1920x1080)
        filtered_videos = []
        for video in videos:
            if orientation_landscape:
                if video.get('width', 0) == 1920 and video.get('height', 0) == 1080:
                    filtered_videos.append(video)
            else:
                if video.get('width', 0) == 1080 and video.get('height', 0) == 1920:
                    filtered_videos.append(video)
        
        # If no exact matches, try approximate matches with flexible aspect ratio
        if not filtered_videos:
            print(f"No exact resolution matches for '{query_string}', trying flexible matching")
            for video in videos:
                if orientation_landscape:
                    # More flexible landscape criteria
                    width = video.get('width', 0)
                    height = video.get('height', 0)
                    if width >= 1280 and height >= 720 and width > height:
                        filtered_videos.append(video)
                else:
                    # More flexible portrait criteria
                    width = video.get('width', 0)
                    height = video.get('height', 0)
                    if width >= 720 and height >= 1280 and height > width:
                        filtered_videos.append(video)
        
        # If still no matches, take any video
        if not filtered_videos and videos:
            print(f"No resolution matches for '{query_string}', using any available video")
            filtered_videos = videos
        
        # Sort the filtered videos by duration in ascending order
        sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x.get('duration', 15))))
        
        # Extract any usable video URL
        for video in sorted_videos:
            best_file = None
            best_quality = 0
            
            # Find the best quality file for this video
            for video_file in video.get('video_files', []):
                width = video_file.get('width', 0)
                height = video_file.get('height', 0)
                quality = width * height
                
                # Skip files we've already used
                if video_file.get('link', '').split('.hd')[0] in used_vids:
                    continue
                    
                # Find highest quality
                if quality > best_quality:
                    best_quality = quality
                    best_file = video_file
            
            # Use the best file if found
            if best_file and 'link' in best_file:
                return best_file['link']
        
        # If we get here, we couldn't find a usable video for this term
        print(f"No usable videos found for '{query_string}'")
    return None
            
    except Exception as e:
        print(f"Error searching for videos: {str(e)}")
        return None


def use_default_video():
    """
    Create a text-only background if no videos are available at all.
    This is a last resort when even fallbacks fail.
    """
    # For now, return None but in the future could generate a solid color or pattern
    print("CRITICAL: All video searches failed. Using default background.")
    return "DEFAULT"


def generate_video_url(search_terms, video_server):
    """Generate video URLs for each search term using Pexels API."""
    if video_server != "pexel":
        return None
    
    # Check for Pexels API key
    pexels_key = os.getenv('PEXELS_KEY')
    if not pexels_key:
        print("WARNING: PEXELS_KEY environment variable not set. Video search may fail.")
        return None
    
    # Initialize cache
    video_cache = {}
    successful_videos = {}  # Track successful video matches
    
    # First pass: Try to find videos for each term
    print("\nFirst pass: Searching for videos...")
    direct_matches = 0
    total_segments = len(search_terms)
    
    for i, ((t1, t2), term) in enumerate(search_terms):
        try:
            # Skip if we already have a successful video for this term
            if term in successful_videos:
                continue
                
            # Check cache first
            if term in video_cache:
                print(f"Using cached results for '{term}'")
                videos = video_cache[term]
            else:
                # Add delay between API calls to avoid rate limits
                time.sleep(0.5)  # 500ms delay between requests
                
                # Make API request with retries
                max_retries = 3
                retry_delay = 2  # seconds
                
                for attempt in range(max_retries):
                    try:
                        headers = {
                            "Authorization": pexels_key,
                            "Accept": "application/json"
                        }
                        response = requests.get(
                            f"https://api.pexels.com/videos/search?query={term}&per_page=15",
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 429:  # Rate limit
                            if attempt < max_retries - 1:
                                print(f"Rate limit hit for '{term}', retrying in {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                                continue
                            else:
                                print(f"Rate limit exceeded for '{term}' after {max_retries} attempts")
                                break
                                
                        response.raise_for_status()
                        data = response.json()
                        
                        if not data.get('videos'):
                            print(f"No videos found for '{term}'")
                            break
                            
                        videos = data['videos']
                        video_cache[term] = videos
                        
                        # Print available resolutions for debugging
                        resolutions = {}
                        for video in videos:
                            for file in video.get('video_files', []):
                                res = f"{file.get('width', '?')}x{file.get('height', '?')}"
                                resolutions[res] = resolutions.get(res, 0) + 1
                        print(f"Found {len(videos)} videos for '{term}'")
                        print(f"Available resolutions for '{term}': {resolutions}")
                        
                        # Try to find a suitable video
                        video_url = None
                        for video in videos:
                            for file in video.get('video_files', []):
                                # First try exact 1920x1080 match
                                if file.get('width') == 1920 and file.get('height') == 1080:
                                    video_url = file.get('link')
                                    break
                            if video_url:
                                break
                                
                        # If no exact match, try flexible resolution
                        if not video_url:
                            for video in videos:
                                for file in video.get('video_files', []):
                                    width = file.get('width', 0)
                                    height = file.get('height', 0)
                                    if width >= 1280 and height >= 720:
                                        video_url = file.get('link')
                                        break
                                if video_url:
                                    break
                                    
                        # If still no match, use highest quality available
                        if not video_url and videos:
                            best_quality = max(
                                videos[0].get('video_files', []),
                                key=lambda x: (x.get('width', 0) * x.get('height', 0))
                            )
                            video_url = best_quality.get('link')
                        
                        if video_url:
                            successful_videos[term] = video_url
                            direct_matches += 1
                            break
                            
                    except requests.exceptions.RequestException as e:
                        if attempt < max_retries - 1:
                            print(f"Request failed for '{term}', retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                        else:
                            print(f"Failed to fetch videos for '{term}': {str(e)}")
                            break
                            
        except Exception as e:
            print(f"Error processing term '{term}': {str(e)}")
            continue
    
    # Report direct match statistics
    print(f"\nFound direct video matches for {direct_matches}/{total_segments} segments ({direct_matches/total_segments*100:.1f}%)")
    
    # Second pass: Reuse successful videos for segments without matches
    print("\nSecond pass: Reusing successful videos...")
    reuse_count = 0
    
    for i, ((t1, t2), term) in enumerate(search_terms):
        if term not in successful_videos:
            # Find the most similar successful term
            best_match = None
            best_similarity = 0
            
            for successful_term in successful_videos:
                similarity = len(set(term.split()) & set(successful_term.split())) / len(set(term.split()) | set(successful_term.split()))
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = successful_term
            
            if best_match and best_similarity > 0.3:  # Only reuse if there's significant similarity
                successful_videos[term] = successful_videos[best_match]
                reuse_count += 1
                print(f"Reusing existing video for segment {t1:.2f}-{t2:.2f}")
    
    print(f"\nReused videos for {reuse_count}/{total_segments} segments")
    
    # Create final video URL list
    video_urls = []
    for (t1, t2), term in search_terms:
        if term in successful_videos:
            video_urls.append(((t1, t2), successful_videos[term]))
        else:
            print(f"WARNING: No video found for term '{term}'")
            video_urls.append(((t1, t2), None))
    
    return video_urls
