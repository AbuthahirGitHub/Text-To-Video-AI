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
    """
    Search for videos using the Pexels API with caching and diagnostics.
    
    Args:
        query_string: The search term to look for
        orientation_landscape: Whether to search for landscape videos
        
    Returns:
        dict: The API response JSON or a fallback empty response
    """
    # Check cache first
    cache_key = f"{query_string}_{orientation_landscape}"
    if cache_key in VIDEO_SEARCH_CACHE:
        print(f"Using cached results for '{query_string}'")
        return VIDEO_SEARCH_CACHE[cache_key]
    
    # Default empty response in case of errors
    empty_response = {"videos": []}
    
    # Check if we have an API key
    if not PEXELS_API_KEY:
        print(f"No Pexels API key provided. Cannot search for '{query_string}'")
        return empty_response
   
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        # Check for API errors
        if response.status_code == 401:
            print(f"ERROR: Unauthorized - Invalid Pexels API key")
            return empty_response
        elif response.status_code == 429:
            print(f"ERROR: Rate limit exceeded for Pexels API")
            # Sleep and try again with a reduced timeout
            time.sleep(2)
            response = requests.get(url, headers=headers, params=params, timeout=5)
        elif response.status_code != 200:
            print(f"ERROR: Pexels API returned status code {response.status_code}")
            return empty_response
        
        json_data = response.json()
        
        # Diagnostic info
        total_videos = len(json_data.get('videos', []))
        print(f"Found {total_videos} videos for '{query_string}'")
        
        # Cache the result
        VIDEO_SEARCH_CACHE[cache_key] = json_data
        
        # Log the response
        log_response(LOG_TYPE_PEXEL, query_string, json_data)
        
        return json_data

    except Exception as e:
        print(f"ERROR in Pexels API call for '{query_string}': {str(e)}")
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


def generate_video_url(timed_video_searches, video_server):
    """
    Generate video URLs for each time segment with improved error handling and video reuse.
    """
    timed_video_urls = []
    
    if video_server == "pexel":
        used_links = []
        successful_videos = []  # Store successfully found videos
        
        # First pass: Try to find videos for each segment with its specific keywords
        for (t1, t2), search_terms in timed_video_searches:
            url = None
            
            # Try the specific search terms first
            for query in search_terms:
                url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    successful_videos.append(url)  # Store successful videos
                    break
            
            # Add this segment with its URL (or None if not found)
            timed_video_urls.append([[t1, t2], url])
        
        # Count how many segments found videos directly
        direct_matches = sum(1 for _, url in timed_video_urls if url is not None)
        total_segments = len(timed_video_urls)
        print(f"Found direct video matches for {direct_matches}/{total_segments} segments ({direct_matches/total_segments*100:.1f}%)")
        
        # Second pass: For segments with no video, reuse one of the successful videos
        if successful_videos:
            reuse_count = 0
            for i, ((t1, t2), url) in enumerate(timed_video_urls):
                if url is None:
                    # Choose a random video from our successful ones
                    reused_url = random.choice(successful_videos)
                    timed_video_urls[i] = [[t1, t2], reused_url]
                    print(f"Reusing existing video for segment {t1}-{t2}")
                    reuse_count += 1
            
            print(f"Reused videos for {reuse_count}/{total_segments} segments")
        
        # If USE_GENERIC_FALLBACKS is True and we still don't have enough videos, try generic terms
        if USE_GENERIC_FALLBACKS and len(successful_videos) < len(timed_video_urls) / 2:
            print("Using generic fallback terms to find additional videos...")
            no_video_indices = [i for i, ((_, _), url) in enumerate(timed_video_urls) if url is None]
            
            if no_video_indices:
                used_fallback_terms = []
                
                for i in no_video_indices:
                    (t1, t2) = timed_video_urls[i][0]
                    
                    # Get a random term we haven't used yet
                    available_terms = [term for term in GENERIC_FALLBACK_TERMS if term not in used_fallback_terms]
                    if not available_terms:
                        # If all terms are used, reset
                        available_terms = GENERIC_FALLBACK_TERMS
                        used_fallback_terms = []
                    
                    fallback_term = random.choice(available_terms)
                    used_fallback_terms.append(fallback_term)
                    
                    # Try with the fallback term
                    url = getBestVideo(fallback_term, orientation_landscape=True, used_vids=used_links)
                    if url:
                        used_links.append(url.split('.hd')[0])
                        timed_video_urls[i] = [[t1, t2], url]
                        print(f"Using generic fallback video for segment {t1}-{t2}: '{fallback_term}'")
                        
                        # Add this successful video to our list for potential reuse
                        successful_videos.append(url)
        
        # Final pass: For any remaining segments without videos, reuse successful ones again
        missing_segments = [i for i, ((_, _), url) in enumerate(timed_video_urls) if url is None]
        if missing_segments and successful_videos:
            print(f"Final pass: Reusing videos for {len(missing_segments)} remaining segments")
            for i in missing_segments:
                (t1, t2) = timed_video_urls[i][0]
                reused_url = random.choice(successful_videos)
                timed_video_urls[i] = [[t1, t2], reused_url]
                print(f"Last resort: Reusing existing video for segment {t1}-{t2}")
        
        # Ultra-final pass: If absolutely nothing worked, use a default
        if not any(url for _, url in timed_video_urls):
            print("EMERGENCY FALLBACK: No videos found at all. Using default background.")
            default_url = use_default_video()
            for i in range(len(timed_video_urls)):
                timed_video_urls[i][1] = default_url
            
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)

    return timed_video_urls
