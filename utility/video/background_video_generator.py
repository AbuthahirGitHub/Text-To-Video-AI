import os 
import requests
import random
from utility.utils import log_response, LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_KEY')

# Fallback query terms that typically have many available videos
FALLBACK_QUERIES = [
    "office", "business", "professional", "workplace", "meeting", 
    "teamwork", "computer", "technology", "document", "data",
    "corporate", "presentation", "collaboration", "working", "desk"
]

def search_videos(query_string, orientation_landscape=True):
    """
    Search for videos using the Pexels API.
    
    Args:
        query_string (str): The search query
        orientation_landscape (bool): Whether to search for landscape videos
        
    Returns:
        dict: JSON response from Pexels API
    """
    if not PEXELS_API_KEY:
        print("Warning: No Pexels API key found. Set the PEXELS_KEY environment variable.")
        return {"videos": []}
   
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
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            json_data = response.json()
            log_response(LOG_TYPE_PEXEL, query_string, json_data)
            return json_data
        else:
            print(f"Error from Pexels API: {response.status_code}")
            return {"videos": []}
    except Exception as e:
        print(f"Error searching videos: {str(e)}")
        return {"videos": []}

def try_alternative_terms(query_string):
    """Generate alternative search terms for a query"""
    alternatives = []
    
    # Try to make the query more visual
    query_words = query_string.lower().split()
    
    # Add related terms for common words
    related_terms = {
        'medical': ['healthcare', 'hospital', 'doctor'],
        'business': ['office', 'corporate', 'professional'],
        'technology': ['computer', 'digital', 'tech'],
        'finance': ['money', 'financial', 'bank'],
        'education': ['school', 'learning', 'classroom'],
        'legal': ['law', 'justice', 'court'],
        'insurance': ['protection', 'coverage', 'safety']
    }
    
    # Check if any query word has related terms
    for word in query_words:
        if word in related_terms:
            alternatives.extend(related_terms[word])
    
    # Always add some general business terms as fallbacks
    alternatives.extend(random.sample(FALLBACK_QUERIES, min(3, len(FALLBACK_QUERIES))))
    
    # Remove duplicates while preserving order
    seen = set()
    alternatives = [x for x in alternatives if not (x in seen or seen.add(x))]
    
    return alternatives

def getBestVideo(query_string, orientation_landscape=True, used_vids=None):
    """
    Get the best video for a search query.
    
    Args:
        query_string (str): Search query
        orientation_landscape (bool): Whether to get landscape videos
        used_vids (list): List of already used video URLs
    
    Returns:
        str: URL of the best video, or None if no suitable video found
    """
    if used_vids is None:
        used_vids = []
        
    # Try the original query first
    vids = search_videos(query_string, orientation_landscape)
    videos = vids.get('videos', [])
    
    # If no videos found, try alternative terms
    if not videos:
        alternative_terms = try_alternative_terms(query_string)
        for term in alternative_terms:
            print(f"Trying alternative search term: {term}")
            vids = search_videos(term, orientation_landscape)
            videos = vids.get('videos', [])
            if videos:
                break
    
    # If still no videos found, use a random fallback term
    if not videos:
        fallback = random.choice(FALLBACK_QUERIES)
        print(f"Using fallback search term: {fallback}")
        vids = search_videos(fallback, orientation_landscape)
        videos = vids.get('videos', [])

    # Filter and extract videos with width and height as 1920x1080 for landscape or 1080x1920 for portrait
    if orientation_landscape:
        filtered_videos = [video for video in videos if video.get('width', 0) >= 1920 and video.get('height', 0) >= 1080 and video.get('width', 0)/video.get('height', 1) >= 16/9]
    else:
        filtered_videos = [video for video in videos if video.get('width', 0) >= 1080 and video.get('height', 0) >= 1920 and video.get('height', 0)/video.get('width', 1) >= 16/9]

    # Sort the filtered videos by duration in ascending order
    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x.get('duration', 15))))

    # Extract the top videos' URLs
    for video in sorted_videos:
        for video_file in video.get('video_files', []):
            if orientation_landscape:
                if video_file.get('width', 0) >= 1280 and video_file.get('height', 0) >= 720:
                    if not (video_file.get('link', '').split('.hd')[0] in used_vids):
                        return video_file.get('link')
            else:
                if video_file.get('width', 0) >= 720 and video_file.get('height', 0) >= 1280:
                    if not (video_file.get('link', '').split('.hd')[0] in used_vids):
                        return video_file.get('link')
                        
    print(f"No suitable videos found for query: {query_string}")
    return None

def generate_video_url(timed_video_searches, video_server):
    """
    Generate video URLs for the timed video searches.
    
    Args:
        timed_video_searches (list): List of timed video searches
        video_server (str): Server to use for videos
    
    Returns:
        list: List of timed video URLs
    """
    if not timed_video_searches:
        print("No video searches provided")
        return []
        
    timed_video_urls = []
    if video_server == "pexel":
        used_links = []
        for i, ((t1, t2), search_terms) in enumerate(timed_video_searches):
            url = None
            
            # Try each search term
            for query in search_terms:
                url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    break
            
            # If no URL found, try a fallback from the standard list
            if not url and FALLBACK_QUERIES:
                fallback_query = FALLBACK_QUERIES[i % len(FALLBACK_QUERIES)]
                print(f"Using fallback query: {fallback_query}")
                url = getBestVideo(fallback_query, orientation_landscape=True, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
            
            timed_video_urls.append([[t1, t2], url])
        
        # Check if any video was found
        if all(url is None for _, url in timed_video_urls):
            print("No videos found for any search term. Using a generic fallback.")
            # Use a single generic video for the entire duration if nothing else worked
            total_duration = timed_video_searches[-1][0][1]
            return [[[0, total_duration], getBestVideo("office work", orientation_landscape=True)]]
            
    elif video_server == "stable_diffusion":
        # Stable diffusion not implemented
        print("Stable diffusion video generation not implemented")
        return []

    return timed_video_urls
