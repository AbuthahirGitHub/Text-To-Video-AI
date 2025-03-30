import os 
import requests
import random
from utility.utils import log_response,LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_KEY')

# Expanded list of generic fallback video search terms for more variety
FALLBACK_SEARCHES = [
    # Office/Business related
    "office work",
    "typing computer",
    "busy office",
    "professional work",
    "business meeting",
    "data analysis",
    "computer screen",
    "keyboard typing",
    "business handshake",
    "office view",
    
    # Technology related
    "technology background",
    "digital technology",
    "computer code",
    "tech abstract",
    "digital network",
    "circuit board",
    "technology future",
    "digital data",
    
    # Nature related
    "nature timelapse",
    "clouds timelapse",
    "ocean waves",
    "forest trees",
    "mountain landscape",
    "flowing water",
    "sunset beach",
    "sunrise mountains",
    "desert sand",
    "waterfall",
    
    # Abstract/Artistic
    "abstract background",
    "particle animation",
    "light patterns",
    "colorful abstract",
    "geometric shapes",
    "creative background",
    "animated texture",
    "artistic visuals"
]

def search_videos(query_string, orientation_landscape=True):
   
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

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL,query_string,response.json())
   
    return json_data


def getBestVideo(query_string, orientation_landscape=True, used_vids=[], prefer_variety=False):
    """
    Get the best video for a query string.
    
    Args:
        query_string: The search query
        orientation_landscape: True for landscape, False for portrait
        used_vids: List of already used video links to avoid repetition
        prefer_variety: If True, returns a random video instead of the "best" one
        
    Returns:
        Video URL or None if not found
    """
    vids = search_videos(query_string, orientation_landscape)
    
    # Check if 'videos' key exists in the response
    if 'videos' not in vids or not vids['videos']:
        print(f"NO LINKS found for this round of search with query: {query_string}")
        return None
        
    videos = vids['videos']  # Extract the videos list from JSON

    # Filter and extract videos with width and height as 1920x1080 for landscape or 1080x1920 for portrait
    if orientation_landscape:
        filtered_videos = [video for video in videos if video['width'] >= 1920 and video['height'] >= 1080 and video['width']/video['height'] == 16/9]
    else:
        filtered_videos = [video for video in videos if video['width'] >= 1080 and video['height'] >= 1920 and video['height']/video['width'] == 16/9]

    # No videos found after filtering
    if not filtered_videos:
        return None
        
    # If we prefer variety, shuffle the videos first
    available_videos = []
    
    for video in filtered_videos:
        for video_file in video['video_files']:
            if orientation_landscape:
                if video_file['width'] == 1920 and video_file['height'] == 1080:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        available_videos.append(video_file['link'])
            else:
                if video_file['width'] == 1080 and video_file['height'] == 1920:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        available_videos.append(video_file['link'])
    
    if available_videos:
        if prefer_variety:
            # Return a random video from available ones
            return random.choice(available_videos)
        else:
            # Return the first available video (typically the "best" one)
            return available_videos[0]
    
    print(f"NO LINKS found for this round of search with query: {query_string}")
    return None


def get_fallback_video(used_vids=[], attempts=0, used_terms=None):
    """Try to get a generic fallback video when specific searches fail"""
    if attempts >= 5:  # Limit recursion
        print("Failed to find any suitable videos after multiple attempts")
        return None
    
    # Keep track of which terms we've already tried
    if used_terms is None:
        used_terms = set()
    
    # Get terms we haven't tried yet
    available_terms = [term for term in FALLBACK_SEARCHES if term not in used_terms]
    
    # If we've tried all terms, reset and try again with random selection
    if not available_terms:
        available_terms = FALLBACK_SEARCHES
    
    # Choose a random fallback search term
    fallback_term = random.choice(available_terms)
    used_terms.add(fallback_term)
    print(f"Trying fallback search term: {fallback_term}")
    
    # Try to get a varied video (random selection)
    url = getBestVideo(fallback_term, orientation_landscape=True, used_vids=used_vids, prefer_variety=True)
    if url:
        return url
    else:
        # Try again with a different term
        return get_fallback_video(used_vids, attempts + 1, used_terms)


def generate_video_url(timed_video_searches, video_server):
    timed_video_urls = []
    if video_server == "pexel":
        used_links = []
        overall_success = False
        
        # Keep track of which fallback terms we've already used
        used_fallback_terms = set()
        
        for i, ((t1, t2), search_terms) in enumerate(timed_video_searches):
            url = None
            # Try each term in the search terms
            for query in search_terms:
                url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    overall_success = True
                    break
            
            # If no URL was found for any search term, try a different fallback for each segment
            if not url:
                print(f"No videos found for segment {i+1}/{len(timed_video_searches)} [{t1}-{t2}], trying random fallback video...")
                # Get available fallback terms that haven't been used yet
                available_terms = [term for term in FALLBACK_SEARCHES if term not in used_fallback_terms]
                
                # If all terms have been used, reset the list
                if not available_terms:
                    used_fallback_terms.clear()
                    available_terms = FALLBACK_SEARCHES
                
                # Choose a random unused term
                fallback_term = random.choice(available_terms)
                used_fallback_terms.add(fallback_term)
                
                print(f"Using random fallback term for segment {i+1}: {fallback_term}")
                url = getBestVideo(fallback_term, orientation_landscape=True, used_vids=used_links, prefer_variety=True)
                
                # If that specific term didn't work, try the general fallback function
                if not url:
                    url = get_fallback_video(used_vids=used_links, used_terms=used_fallback_terms)
                
                if url:
                    used_links.append(url.split('.hd')[0])
                    overall_success = True
            
            timed_video_urls.append([[t1, t2], url])
        
        # If no videos were found at all, ensure we have at least one fallback
        if not overall_success and timed_video_searches:
            print("No videos found at all. Adding several random videos for different segments...")
            
            # Calculate total duration
            start_time = timed_video_searches[0][0][0]
            end_time = timed_video_searches[-1][0][1]
            total_duration = end_time - start_time
            
            # Create several segments with different random videos
            num_segments = min(4, len(timed_video_searches))  # Use at most 4 segments
            segment_duration = total_duration / num_segments
            
            new_video_urls = []
            used_terms = set()
            
            for i in range(num_segments):
                seg_start = start_time + (i * segment_duration)
                seg_end = start_time + ((i + 1) * segment_duration)
                
                # Get available terms
                available_terms = [term for term in FALLBACK_SEARCHES if term not in used_terms]
                if not available_terms:
                    used_terms.clear()
                    available_terms = FALLBACK_SEARCHES
                
                # Choose random term
                fallback_term = random.choice(available_terms)
                used_terms.add(fallback_term)
                
                print(f"Using random term for segment {i+1}/{num_segments}: {fallback_term}")
                url = getBestVideo(fallback_term, orientation_landscape=True, used_vids=used_links, prefer_variety=True)
                
                if not url:
                    url = get_fallback_video(used_vids=used_links)
                
                if url:
                    used_links.append(url.split('.hd')[0])
                    new_video_urls.append([[seg_start, seg_end], url])
            
            # If we found at least one video, use the new segmentation
            if new_video_urls:
                return new_video_urls
    
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)

    return timed_video_urls
